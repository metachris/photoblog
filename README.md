Server requirement:

* python-dev
* Node.js for npm/bootstrap/recess
* Bootstrap/Less dependencies: `npm install recess uglify-js jshint -g`
* Python module dependencies
 * Virtualenv in `app/env/`
 * `source env/bin/activate && pip install -r dependencies.txt`
 * Postgres installed by default; remove dependency if you want another data store
 * PIL and sorl need libjpeg-dev installed on the system to work with jpegs!
 * I needed Python 2.7 to compile hiredis
 * [itsdangerous](http://packages.python.org/itsdangerous/) module for cryptographic signing
* [exiftool](http://www.sno.phy.queensu.ca/~phil/exiftool/)



Important `manage.py` commands

* [SORL Thumbnails](http://thumbnail.sorl.net/management.html#thumbnail-clear)
 * `python manage.py thumbnail cleanup` cleans up the Key Value Store from stale cache. It removes references to images that do not exist and thumbnail references and their actual files for images that do not exist. It removes thumbnails for unknown images.
 * `python manage.py thumbnail clear`  totally empties the Key Value Store from all keys that start with the settings.THUMBNAIL_KEY_PREFIX. It does not delete any files. It is generally safe to run this if you do not reference the generated thumbnails by name somewhere else in your code. The Key Value store will update when you hit the template tags, and if the thumbnails still exist they will be used and not overwritten.

