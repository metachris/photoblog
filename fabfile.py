from fabric.api import *

env.use_ssh_config = True
env.hosts = ["hetzner1"]

REMOTE_DIR = "/var/www/chrishager.at/django-photoblog"


def deploy():
    local("tar -czf app.tar.gz app/")
    run("rm -rf %s" % REMOTE_DIR)
    put('app.tar.gz', "%s/" % REMOTE_DIR)
    put('dependencies.txt', "%s/" % REMOTE_DIR)
    with cd(REMOTE_DIR):
        run("tar zxf app.tar.gz")
    restart()


def restart():
    pass
