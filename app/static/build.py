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
        $ %(cmd)s minify
        $ %(cmd)s gzip

        $ %(cmd)s all (all of them, in this order)
    """ % {"cmd": sys.argv[0]}


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
                fn_to_min = "%s.min.css" % os.path.join(path_dest, file)[:-5]

                print "- %s" % fn
                cmd1 = "%s --compile %s > %s" % (CMD_RECESS, fn, fn_to)
                cmd2 = "%s --compress %s > %s" % (CMD_RECESS, fn, fn_to_min)
                os.system(cmd1)
                os.system(cmd2)

    print "Finished building css files."


def minify_js():
    """Minifies js files. css files are already minified on compilation"""
    print "Minify js files"
    d = os.path.join(CUR_PATH, "js")
    for (path, dirs, files) in os.walk(d):
        for file in files:
            if file.endswith("js") and not file.endswith(".min.js"):
                fn = os.path.join(path, file)
                fn_to = "%s.min.js" % fn[:-3]

                print "- %s" % fn
                cmd = "uglifyjs -nc %s > %s" % (fn, fn_to)
                os.system(cmd)


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
                cmd = "gzip -c %(file)s > %(file)s.gz" % {"file": fn}
                os.system(cmd)


def run(cmds):
    if "-h" in cmds or "--help" in cmds:
        show_help()
        return

    if "bootstrap" in cmds:
        build_bootstrap()

    if "css" in cmds:
        build_css()

    if "minify" in cmds:
        minify_js()

    if "gzip" in cmds:
        build_gzip()

    if "all" in cmds:
        build_bootstrap()
        build_css()
        minify_js()
        build_gzip()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()

    else:
        run(sys.argv[1:])
