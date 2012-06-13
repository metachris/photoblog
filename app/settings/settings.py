#  -------------------------------------------------------------------------
# | Settings in here will always be included (on any machine, dev or prod), |
# | and either settings_dev.py.py or settings_production.py will be included   |
# | (depending on whether the current host's network name is in the         |
# | HOSTS_PRODUCTION list in hosts.py                                       |
#  -------------------------------------------------------------------------
import platform
import hosts
import os
import datetime


# Number of photos to show in the grid initially and on more pages.
# These values may be overwritten with AdminValue objects.
PHOTOGRID_ITEMS_INITIAL = 11
PHOTOGRID_ITEMS_PERPAGE = 6

# Number of flow containers to show in the photo-flow. One block is a 4x2
# container with up to 4 cols These values may be overwritten with AdminValue
# objects.
PHOTOFLOW_BLOCKS_INITIAL = 3
PHOTOFLOW_BLOCKS_PERPAGE = 2

# Import machine/environment specific settings based on the hostname
# (current machine's network name). Specified in settings/hosts.py
if platform.node() in hosts.HOSTS_PRODUCTION:
    print "Loading production settings"
    from settings_production import *
else:
    print "Loading dev settings"
    from settings_dev import *

# Helper for later (log files, etc)
NOW = datetime.datetime.now()
DATE_STR = NOW.strftime("%Y-%m-%d")

# Email setup
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = EMAIL_USER  # comes from settings_dev or _production
EMAIL_HOST_PASSWORD = EMAIL_PASS
EMAIL_USE_TLS = True

# Count cache duration (see http://jbalogh.me/projects/cache-machine/)
CACHE_COUNT_TIMEOUT = 60  # seconds, not too long.

# If set to True, don't cache pages for logged in users (incl. admin)
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'Europe/Vienna'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Paths to the translations (if not app/<subapp>/locale)
LOCALE_PATHS = (
    os.path.join(APP_ROOT, "app/locale"),
)

# Selectable languages
LANGUAGES = (
    ('de', 'German'),
    ('en', 'English'),
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.gzip.GZipMiddleware',
)

if DEBUG:
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

ROOT_URLCONF = 'app.urls'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request"
)

INSTALLED_APPS = (
    # Commonly required django internal apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Django admin interface
    'django.contrib.admin',

    # Thumbnail template tags
    "sorl.thumbnail",

    # South is a tool to document and simplify database schema updates
    'south',

    # Tag hierarchies
    'treebeard',

    # Redis status info for the admin interface
    #'redis_status',

    # Main app from the diary project
    'app.mainapp',
)

if DEBUG:
    INSTALLED_APPS += ('debug_toolbar',)

# Logging configuration. See http://docs.djangoproject.com/en/dev/topics/logging
# for more details.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default': {
            'format': '%(levelname)-8s %(asctime)s %(name)s \t%(message)s'
        },
    },

    # Handlers do something with log messages (eg. write to file, send email)
    'handlers': {
        # Handler for emailing admins on errors
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },

        # Handler for logging to a file
        'file':{
            'level':'INFO',
            'class':'logging.FileHandler',
            'formatter': 'default',
            'filename': os.path.join(APP_ROOT, "logs", "django-%s.log" % DATE_STR),
        },

        # Handler for logging queries to a separate file
        'querylog':{
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'backupCount': 5,
            'maxBytes': 1024 * 1024,
            'filename': os.path.join(APP_ROOT, "logs", "django-%s-queries.log" % DATE_STR),
            'delay': True,
        },

        # Handler for console output
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'default'
        },

        # Handler for /dev/null
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
    },

    # What to log and where to
    'loggers': {
        # Mail admins on errors in request
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },

        # Log db-backend messages
        'django.db.backends': {
            'handlers': ['querylog'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },

    # This catches all python scripts logging messages
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    }
}

# Step 3: Custom settings
# -----------------------
INTERNAL_IPS = ('127.0.0.1',)
