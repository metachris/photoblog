# Django settings for development
DEBUG = True
TEMPLATE_DEBUG = DEBUG
IS_TESTENV = True

ADMINS = (
    # ('Your Name', 'name@example.com'),
)

MANAGERS = ADMINS

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'MAKE_THIS_UNIQUE'

# To send email via GMail with tools.sendmail.gmail(), set the credentials here
SENDMAIL_GMAIL_USER = ""
SENDMAIL_GMAIL_PASS = ""

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '<DB_NAME>',
        'USER': '<DB_USER>',
        'PASSWORD': '<DB_PASS>',
        'HOST': '<DB_IP>',
        'PORT': '<DB_PORT>',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': '192.168.1.11:6379',
        "KEY_PREFIX": 'sportlog_',
        'OPTIONS': {
            'DB': 1,
            'PASSWORD': 'yadayada',
            'PARSER_CLASS': 'redis.connection.HiredisParser'
        },
    },
}

DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False,
}

# Directory with app/ and env/ subdirectories
APP_ROOT = "/Users/chris/Projects/private/django/photosite"

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
# Change in accordance with STATIC_ROOT to serve with outside webserver too
MEDIA_ROOT = '/opt/photosite/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
#MEDIA_URL = 'http://localhost:8080/media/'
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/opt/photosite/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files [dev only; prod serves with nginx]
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "/Users/chris/Projects/private/django/photosite/app/static/",
)

# List of finder classes that know how to find static files in
# various locations. Only for dev; prod serves static files with
# another nginx directive.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates"
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "%s/app/templates" % APP_ROOT,
    "%s/env/lib/python2.7/site-packages/treebeard/templates" % APP_ROOT,
)
