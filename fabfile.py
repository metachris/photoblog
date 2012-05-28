import re
import os.path
import tempfile
import datetime
import commands

from fabric.api import run, local, cd, lcd, put, env, hosts

from app.settings import settings_dev
from app.settings import settings_production


# List of production hosts (specified in ssh config file)
HOSTS_PROD = ["hetzner1"]

# Tell Fabric to use ssh config file
env.use_ssh_config = True

# Deployment history file
DEPLOYMENTS_HISTFILE = "deployments.log"


def pack():
    """ Pack app and static directory with tar.gz """
    dir_tmp_local = tempfile.mkdtemp()
    print "Temp directory: %s" % dir_tmp_local

    # Pack app
    local("tar -czf %s/app.tar.gz --exclude='static' --exclude='*.pyc' app" % dir_tmp_local)

    # Pack static: 1. copy, 2. create gz files, 3. pack
    local("cp -pr app/static %s" % dir_tmp_local)
    with lcd(os.path.join(dir_tmp_local, "static")):
        # Original bootstrap files take a lot of space and are not needed anymore
        local("rm -rf twitter-bootstrap")

        # Pre-gzip js and css files so nginx can serve them with gzip_static
        local("sh gzip_static.sh")

    # Finally pack the adapted static dir
    with lcd(dir_tmp_local):
        local("tar -czhf static.tar.gz --exclude='.DS_Store' --exclude='twitter-bootstrap' static")

    return dir_tmp_local

@hosts(HOSTS_PROD)
def deploy_prod():
    """ Deploy to production servers """
    _log_deployment()

    # Set production target variables
    REMOTE_DIR = settings_production.APP_ROOT

    # Pack the current code and static dirs
    dir_tmp_local = pack()

    # Upload
    put('%s/app.tar.gz' % dir_tmp_local, "%s/" % REMOTE_DIR)
    put('%s/static.tar.gz' % dir_tmp_local, "%s/" % REMOTE_DIR)
    put('dependencies.txt', "%s/" % REMOTE_DIR)
    put(DEPLOYMENTS_HISTFILE, "%s/" % REMOTE_DIR)

    # Remove old version
    run("rm -rf %s/app" % (REMOTE_DIR))
    run("rm -rf %s/static" % (REMOTE_DIR))

    # Unpack and remove
    with cd(REMOTE_DIR):
        # Extract app
        run("tar zxf app.tar.gz")

        # Extract static files to dir specified in production settings
        run("mkdir -p %s" % settings_production.STATIC_ROOT)
        run("tar zxf static.tar.gz -C %s --strip-components 1" % settings_production.STATIC_ROOT)

        # Remove tar.gz files
        run("rm -f app.tar.gz media.tar.gz static.tar.gz")

        # Reload uwsgi (http://projects.unbit.it/uwsgi/wiki/Management)
        run("kill -TERM `cat /tmp/uwsgi_chrishager_at.pid`")

    # Delete local tmp dir
    local("rm -rf %s" % dir_tmp_local)


def _log_deployment():
    # read log contents
    log_content = ""
    if os.path.isfile(DEPLOYMENTS_HISTFILE):
        f = open(DEPLOYMENTS_HISTFILE, "r")
        log_content = f.read()
        f.close()

    # get deploy id
    regex = re.compile("([0-9]* [|])")
    r = regex.search(log_content)
    last_build = int(r.group(0)[:-1].strip()) if r else 0
    deploy_id = last_build + 1

    # build log entry
    cmd = """git log --pretty=format:"%h - %s [%an]" -n 1"""
    log_entry = "{deploy_id} | {datetime} | last commit: {git_info}".format(
            deploy_id=deploy_id,
            datetime=datetime.datetime.now(),
            git_info=commands.getoutput(cmd))

    print "Logging deployment: %s" % (log_entry)
    f = open(DEPLOYMENTS_HISTFILE, "w")
    f.write("%s\n%s" % (log_entry, log_content))
    f.close()
