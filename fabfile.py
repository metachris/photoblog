from fabric.api import *

env.use_ssh_config = True
env.hosts = ["hetzner1"]

LOCAL_TMP_DIR = "/tmp/photoblog-build"

LOCAL_STATIC_PARENT_DIR = "/opt/photosite"

REMOTE_DIR = "/var/www/chrishager.at"


def pack():
    # Clean up temp dir
    local("rm -rf %s" % LOCAL_TMP_DIR)
    local("mkdir -p %s" % LOCAL_TMP_DIR)

    # Pack
    local("tar -czf %s/app.tar.gz --exclude='static' --exclude='*.pyc' app/" % LOCAL_TMP_DIR)
    with lcd(LOCAL_STATIC_PARENT_DIR):
        #local("tar -czf %s/media.tar.gz --exclude='.DS_Store' media" % (LOCAL_TMP_DIR))
        local("tar -czhf %s/static.tar.gz --exclude='.DS_Store' --exclude='twitter-bootstrap' static" % (LOCAL_TMP_DIR))


def deploy():
    pack()

    # Upload
    put('%s/app.tar.gz' % LOCAL_TMP_DIR, "%s/" % REMOTE_DIR)
    #put('%s/media.tar.gz'% LOCAL_TMP_DIR, "%s/" % REMOTE_DIR)
    put('%s/static.tar.gz' % LOCAL_TMP_DIR, "%s/" % REMOTE_DIR)
    put('dependencies.txt', "%s/" % REMOTE_DIR)

    # Remove old version
    run("rm -rf %s/app" % (REMOTE_DIR))
    run("rm -rf %s/static" % (REMOTE_DIR))

    # Unpack and remove
    with cd(REMOTE_DIR):
        run("tar zxf app.tar.gz")
        #run("tar zxf media.tar.gz")
        run("tar zxf static.tar.gz")
        run("rm -f app.tar.gz media.tar.gz static.tar.gz")

    # Restart
    restart()


def restart():
    with cd(REMOTE_DIR):
        # Reload uwsgi (http://projects.unbit.it/uwsgi/wiki/Management)
        run("kill -TERM `cat /tmp/uwsgi_chrishager_at.pid`")

        # Start uwsgi
        #run("./env/bin/uwsgi  --ini /etc/uwsgi/apps-available/chrishager_new.ini")
