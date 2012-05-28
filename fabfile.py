import tempfile

from fabric.api import run, local, cd, lcd, put, env, hosts

from app.settings import settings_dev
from app.settings import settings_production


# List of production hosts
import os.path

HOSTS_PROD = ["hetzner1"]

# Tell Fabric to use ssh config file
env.use_ssh_config = True

# Local variables
LOCAL_TMP_DIR = tempfile.mktemp()
print "Temp directory: %s" % LOCAL_TMP_DIR


def pack():
    """ Pack app and static directory with tar.gz """
    # Clean up temp dir
    local("rm -rf %s" % LOCAL_TMP_DIR)
    local("mkdir -p %s" % LOCAL_TMP_DIR)

    # Pack app
    local("tar -czf %s/app.tar.gz --exclude='static' --exclude='*.pyc' app" % LOCAL_TMP_DIR)

    # Pack static: 1. copy, 2. create gz files, 3. pack
    local("cp -pr app/static %s" % LOCAL_TMP_DIR)
    with lcd(os.path.join(LOCAL_TMP_DIR, "static")):
        # Original bootstrap files take a lot of space and are not needed anymore
        local("rm -rf twitter-bootstrap")

        # Pre-gzip js and css files so nginx can serve them with gzip_static
        local("sh gzip_static.sh")

    # Finally pack the adapted static dir
    with lcd(LOCAL_TMP_DIR):
        local("tar -czhf static.tar.gz --exclude='.DS_Store' --exclude='twitter-bootstrap' static")


@hosts(HOSTS_PROD)
def deploy_prod():
    """ Deploy to production servers """
    # Set production target variables
    REMOTE_DIR = settings_production.APP_ROOT

    # Pack the current code and static dirs
    pack()

    # Upload
    put('%s/app.tar.gz' % LOCAL_TMP_DIR, "%s/" % REMOTE_DIR)
    put('%s/static.tar.gz' % LOCAL_TMP_DIR, "%s/" % REMOTE_DIR)
    put('dependencies.txt', "%s/" % REMOTE_DIR)

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
    local("rm -rf %s" % LOCAL_TMP_DIR)
