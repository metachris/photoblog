"""
Fabric deployment script.


Usage:

    fab <target> <command1> <command2> ...


Targets:

    production ... Production target


Commands:

    init_server ....... Creates the project directory, checks out the git repo and submodules,
                        Finally runs `upload_files_notingit` and `init_virtualenv`.

    init_virtualenv ... Sets up virtualenv with dependencies.

    upload_files_notingit ... upload files from local machine that are not in git (besides
                              settings). Also runs `upload_settings`.

    upload_settings ... Uploads the target specific setting file from the current machine.

    make bootstrap .... Builds twitter bootstrap.

    make_static ....... Converts /static/css/*.less files to css, and pre-gzips certain files


Example Server Setup:

    $ fab production init_server make_bootstrap make_static

"""
import os.path

from fabric.api import run, local, cd, lcd, put, env, hosts, hide
from fabric.contrib.files import exists

from app.settings import settings_dev
from app.settings import settings_production


# List of production hosts (specified in ssh config file)
HOSTS_PROD = ["hetzner1"]

# The git origin is where we the repo is.
# Use the user@host syntax
GIT_ORIGIN = "git://github.com/metachris/photoblog.git"

# Deployment history file
DEPLOYMENTS_HISTFILE = "deployments.log"


def production():
    "Setup production settings"
    env.use_ssh_config = True
    env.hosts = HOSTS_PROD
    env.git_origin = GIT_ORIGIN
    env.dir_remote = settings_production.APP_ROOT
    env.dir_local  = settings_dev.APP_ROOT
    env.file_settings = "app/settings/settings_production.py"


# Tasks

def init_server():
    """Setup project directory and clone repo"""
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
        run("mkdir media")

    # Upload target-specific settings file and other files not in git
    upload_files_notingit()

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


def upload_settings():
    """Upload the respective settings file"""
    settings_fn = os.path.join(env.dir_local, env.file_settings)
    put(settings_fn, os.path.join(env.dir_remote, env.file_settings))


def upload_files_notingit():
    """Upload files not in git"""
    upload_settings()
    files = ["app/templates/footer_private.html"]
    for fn in files:
        fn_from = os.path.join(env.dir_local, fn)
        fn_to = os.path.join(env.dir_remote, fn)
        put(fn_from, fn_to)


def init_virtualenv():
    """Creates the virtualenv directory and installs all dependencies"""
    with cd(env.dir_remote):
        run("virtualenv env")
        run("source env/bin/activate && pip install -r dependencies.txt")


def make_bootstrap():
    """Build Twitter Bootstrap with 'make bootstrap'"""
    with cd(os.path.join(env.dir_remote, "app/static/twitter-bootstrap/")):
        run("rm -rf bootstrap")
        run("make bootstrap")


def make_static():
    """Prepare static dir for collection for deployment"""
    # 1. convert static/css/*.less files to css files
    with cd(os.path.join(env.dir_remote, "app/static/css/")):
        run("sh less_build_all.sh")

    # 2. pre-gzip all css, js files in static/
    with cd(os.path.join(env.dir_remote, "app/static/")):
        run("sh gzip_static.sh")

    # 3. collect final static files into separate dir outside of project
    with cd(env.dir_remote):
        run("source env/bin/activate && cd app && python manage.py collectstatic --noinput")


def reload_uwsgi():
    print "Reloading uwsgi..."
    run("kill -TERM `cat /tmp/uwsgi-chrishager_at.pid`")


def _get_cur_hash():
    with cd(env.dir_remote):
        with hide('running', 'stdout', 'stderr'):
            return run('git log --pretty=format:"%h - %s [%an]" -n 1')


def deploy():
    hash_before = _get_cur_hash()
    with cd(env.dir_remote):
        run("git pull")
    upload_files_notingit()
    hash_after = _get_cur_hash()
    print "Deployment summary:"
    print
    print "  from: %s" % hash_before
    print "    to: %s" % hash_after
    reload_uwsgi()


def rollback(hash):
    """
    Rollback git repositories to specified hash.
    Usage:
    fab rollback:hash=etcetc123
    """
    print "Rolling back to %s" % hash
    with cd(env.dir_remote):
        run("git reset --hard %(hash)s" % env)
