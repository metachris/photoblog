Django backend for the photo website [chrishager.at](http://www.chrishager.at).

This project is not yet in a release state, but it should be fairly straightforward to
configure and get running. It's not a lot of code and I've tried to keep things modular,
but since this is just a fun hacking side project for me, some parts of the code are
'experimental' and may need refactoring.

The code is dual licensed under the [GPLv3](http://www.gnu.org/copyleft/gpl.html) and a commercial license. Under the GPL you can freely use this project to build your own photo-blog as long as you share your modifications. Please create your own theme with custom styles instead of using the included styles.


Server Requirements
-------------------

* Python 2.7, python-dev
* Node.js for npm (-> bootstrap/recess/uglifyjs)
* Bootstrap/Less dependencies: `npm install recess uglify-js jshint -g`
* [ExifTool](http://www.sno.phy.queensu.ca/~phil/exiftool/) for exif operations
* Python module dependencies:
 * See [dependencies.txt](https://github.com/metachris/photoblog/blob/master/dependencies.txt)
 * Virtualenv in `app/env/`
 * Before building PIL and sorl, install `libjpeg-dev` to make them like jpegs
 * Postgres is used default; remove dependency if you want another data store
 * [itsdangerous](http://packages.python.org/itsdangerous/) module for cryptographic signing



What's Inside
-------------

* Django Debug Toolbar
* DB migrations with South
* Heavy caching with Redis by default
* Model caching with django-cache-machine
* Model hierarchies with django-treebeard
* Dynamic thumbnails with sorl-thumbnail
* nginx & uwsgi config files
* Markdown image descriptions
* Public models all use slugs
* Image upload with EXIF preservation and pre-processing
* ...


Various
-------

Important `manage.py` commands

* [SORL Thumbnails](http://thumbnail.sorl.net/management.html#thumbnail-clear)
 * `python manage.py thumbnail cleanup` cleans up the Key Value Store from stale cache. It removes references to images that do not exist and thumbnail references and their actual files for images that do not exist. It removes thumbnails for unknown images.
 * `python manage.py thumbnail clear`  totally empties the Key Value Store from all keys that start with the settings.THUMBNAIL_KEY_PREFIX. It does not delete any files. It is generally safe to run this if you do not reference the generated thumbnails by name somewhere else in your code. The Key Value store will update when you hit the template tags, and if the thumbnails still exist they will be used and not overwritten.

