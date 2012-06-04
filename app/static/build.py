#!/usr/bin/env python
# encoding: utf-8
"""
Build tools for static/. Available commands:

    $ build.py boostrap
    $ build.py css
    $ build.py gzip

    $ build.py all (all of these three, in this order)
"""

import sys
import os
import shutil

CMD_RECESS = "/usr/local/bin/recess"  # must be same on server and dev machines
CUR_PATH = os.path.abspath(os.path.dirname(__file__))


def show_help():
    print """Available commands:

        $ %(cmd)s boostrap
        $ %(cmd)s css
        $ %(cmd)s gzip

        $ %(cmd)s all (all of these three, in this order)
    """ % { "cmd": sys.argv[0] }


def build_bootstrap():
    print "Building Bootstrap..."
    path = os.path.join(CUR_PATH, "twitter-bootstrap")
    os.system("cd %s && rm -rf bootstrap && make bootstrap" % path)


def build_css():
    print "Building css..."
    path_source = os.path.join(CUR_PATH, "less")
    path_dest = os.path.join(CUR_PATH, "css")

    # Create css dir if not exists
    if not os.path.exists(path_dest):
        os.makedirs(path_dest)

    # Build all the less files
    for (path, dirs, files) in os.walk(path_source):
        if not path == path_source:
            # Skip subdirectories
            continue
        for file in files:
            if file.endswith("less"):
                fn = os.path.join(path, file)
                fn_to = "%s.css" % os.path.join(path_dest, file)[:-5]
                cmd = "%s --compile %s > %s" % (CMD_RECESS, fn, fn_to)
                print "- %s" % fn
                os.system(cmd)

    print "Finished building css files."


def build_gzip():
    """
    Traverse directories and subdirectories and pre-gzip all files
    """
    print "Building gzip..."
    build_paths = ["css", "img", "js", "twitter-bootstrap/bootstrap"]
    build_abspaths = [os.path.join(CUR_PATH, path) for path in build_paths]
    for root_path in build_abspaths:
        for (path, dirs, files) in os.walk(root_path):
            for file in files:
                if file.endswith(".gz"):
                    continue
                fn = os.path.join(path, file)
                print "- %s" % fn
                cmd = "gzip -c %(file)s > %(file)s.gz" % { "file": fn }
                os.system(cmd)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()

    else:
        cmd = sys.argv[1]
        if cmd == "bootstrap":
            build_bootstrap()

        elif cmd == "css":
            build_css()

        elif cmd == "gzip":
            build_gzip()

        elif cmd == "all":
            build_bootstrap()
            build_css()
            build_gzip()

        else:
            show_help()

