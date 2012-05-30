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

