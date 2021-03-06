"""
Fabric deployment script.


Usage:

    fab <target> <command1> <command2> ...


Targets:

    production ... Production target


Commands:

    init_virtualenv ... Sets up virtualenv with dependencies.
    init_server ....... Creates the project directory, checks out the git repo and submodules,
                        Finally runs `upload_files_notingit` and `init_virtualenv`.


    upload_settings ... Uploads the target specific setting file from the current machine.
    upload_files_notingit ... upload files from local machine that are not in git (besides
                              settings). Also runs `upload_settings`.


    make_static ...... Makes bootstrap, converts /static/css/*.less files to css, and
                       pre-gzips js and css files.


    reload_uwsgi ..... Reload uwsgi for this app by sending TERM signal to uwsgi master process.
    deploy ........... Updates the server to git master HEAD and run `reload_uwsgi`.
    rollback:<hash> .. Sets server git repo to commit identified by <hash> and runs `reload_uwsgi`.
                       (Not yet fully functional: does not do a db/settings rollback)


Examples:

    # Server setup
    $ fab production init_server make_static

    # Deployment & Rollback
    $ fab production deploy
    $ fab production rollback:abcacb12

"""
import os.path
import datetime

from fabric.api import run, local, cd, lcd, put, env, hosts, hide
from fabric.contrib.files import exists

from app.settings import settings_dev
from app.settings import settings_production


# List of production hosts (specified in ssh config file)
HOSTS_PROD = ["hetzner1"]

# The git origin is where we the repo is.
# Use the user@host syntax
GIT_ORIGIN = "git://github.com/metachris/photoblog.git"

# Deployments log file (in same path as fabfile)
HISTFILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), "deployments.log")

# Helper for later
NOW = datetime.datetime.now()
NOW_DATE_STR = NOW.strftime("%Y-%m-%d")


# Environments

def production():
    "Set production target"
    env.use_ssh_config = True
    env.hosts = HOSTS_PROD
    env.git_origin = GIT_ORIGIN
    env.dir_remote = settings_production.APP_ROOT
    env.dir_local  = settings_dev.APP_ROOT
    env.db_info = settings_production.DATABASES["default"]
    env.file_settings = "app/settings/settings_production.py"


# Tasks

def init_server():
    """Setup project directory, clone repo, init virtualenv"""
    if exists(env.dir_remote):
        print
        print "Remote directory %s already exists. Please delete and then re-run." % env.dir_remote
        return

    # Build dir tree except last level (git creates that)
    run("mkdir -p %s" % env.dir_remote)
    run("rmdir %s"  % env.dir_remote)

    # Git clone repo and submodules
    run("git clone %s %s" % (GIT_ORIGIN, env.dir_remote))
    with cd(env.dir_remote):
        run("git submodule init")
        run("git submodule update")

        run("mkdir logs")
        run("mkdir media && mkdir media/upload && mkdir media/photos")

    # Upload target-specific settings file and other files not in git
    upload_files_notingit()

    # Collect the static directory
    _make_static()

    # Setup virtualenv
    try:
        init_virtualenv()
    except:
        print
        print "Virtualenv init failed. Please correct problems and re-run `fab <target> init_virtualenv`."
        print
        raise

    # Finally
    print
    print "Code is checked out to %s and settings file is in place (%s)." % (env.dir_remote, env.file_settings)
    print "Now you just need to setup uwsgi and your webserver"


def init_virtualenv():
    """Setup virtualenv in /env and install dependencies"""
    with cd(env.dir_remote):
        run("virtualenv env")
        run("source env/bin/activate && pip install -r dependencies.txt")


def upload_settings():
    """Upload the respective settings file"""
    settings_fn = os.path.join(env.dir_local, env.file_settings)
    put(settings_fn, os.path.join(env.dir_remote, env.file_settings))


def upload_files_notingit():
    """Upload files not in git (from list in code)"""
    upload_settings()
    files = ["app/templates/analytics_snippet.html"]
    for fn in files:
        fn_from = os.path.join(env.dir_local, fn)
        fn_to = os.path.join(env.dir_remote, fn)
        put(fn_from, fn_to)


def _make_static():
    """
    Prepare static assets

    1. Make Bootstrap
    2. Make Less files
    3. Pre-Gzip all static files for nginx
    4. Have django's manage.py collect all the static files
    """
    # Build
    with cd(os.path.join(env.dir_remote, "app/static/")):
        run("./build.py all")

    # Collect
    with cd(env.dir_remote):
        run("source env/bin/activate && cd app && python manage.py collectstatic --noinput")


def reload_uwsgi():
    print "Reloading uwsgi..."
    run("kill -TERM `cat /tmp/uwsgi-chrishager_at.pid`")


def _get_cur_hash():
    """Gets current git commit's hash and shortmsg on remote machine"""
    with cd(env.dir_remote):
        with hide('running', 'stdout', 'stderr'):
            a = run('git log --pretty=format:"|%h - %s [%an]|" -n 1', shell=True)
            b = "|".join(a.split("|")[1:-1]) # remove vt100 escaping
            return b


def deploy():
    """
    Initiate full deployment (server update to git master HEAD), db migration,
    static asset building and uwsgi restart.

    Does not clear cache; admin must do that manually. Not sure whether to add
    this here; leaving it out for the moment.
    """
    if not getattr(env, "dir_local", None):
        print "Error: No target. Run $ fab production deploy"
        return

    # Save remote git hash
    hash_before = _get_cur_hash()

    # Perform deployment
    with cd(env.dir_remote):
        # Update repo to current master HEAD
        run("git pull")

        # Update submodules to currently set revision
        run("git submodule update")

        # Upload files that are not in git (eg. analytics_snippet.html)
        upload_files_notingit()

        # Build i18n db
        run("source env/bin/activate && cd app && django-admin.py compilemessages")

        # Update db schema if needed
        run("source env/bin/activate && cd app && python manage.py migrate mainapp")

    # Update less files submodule
    #with cd(os.path.join(env.dir_remote, "app/static/less")):
    #    run("git pull")

    # Build static assets
    _make_static()

    # Finally reload uwsgi
    reload_uwsgi()

    # Save git hash and add entry to deployments logfile
    hash_after = _get_cur_hash()
    _log(hash_after)

    # Show summary
    print "Deployment summary:"
    print
    print "  from: %s" % hash_before
    print "    to: %s" % hash_after


def rollback(hash):
    """
    Rollback git repositories to specified hash.
    Usage: `fab rollback:hash=etcetc123`
    """
    print "Rolling back to %s" % hash
    hash_before = _get_cur_hash()
    with cd(env.dir_remote):
        run("git reset --hard %s" % hash)
    _make_static()
    hash_after = _get_cur_hash()

    print "Rollback summary:"
    print
    print "  from: %s" % hash_before
    print "    to: %s" % hash_after
    _log(hash_after, "rollback  ")

    reload_uwsgi()


def _log(info, id="deployment"):
    """Log a deployment or rollback"""
    f = open(HISTFILE, "a+")
    f.write("%s | %s | %s\n" % (id, datetime.datetime.now(), info))


def backup_db():
    # Demo DB Backup
    with cd("/tmp/"):
        fn = "/tmp/dbdump_photoblog-%s.sql" % NOW_DATE_STR
        cmd1 = 'export PGPASSWORD="%(PASSWORD)s"' % env.db_info
        cmd2 = "pg_dump -C -h %(HOST)s -p %(PORT)s -U %(USER)s %(NAME)s" % env.db_info
        run("%s && %s > %s" % (cmd1, cmd2, fn))
        print
        print "DB dumped to '%s'" % fn
