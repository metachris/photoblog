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
* [exiftool](http://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&ved=0CFMQFjAA&url=http%3A%2F%2Fwww.sno.phy.queensu.ca%2F~phil%2Fexiftool%2F&ei=gNLIT62XEMae-Qa6m7lg&usg=AFQjCNFAlpvMDz6UOjAFtqrYQdOn7Vprkw)

