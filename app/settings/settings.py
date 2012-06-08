#  -------------------------------------------------------------------------
# | Settings in here will always be included (on any machine, dev or prod), |
# | and either settings_dev.py.py or settings_production.py will be included   |
# | (depending on whether the current host's network name is in the         |
# | HOSTS_PRODUCTION list in hosts.py                                       |
#  -------------------------------------------------------------------------

# First step: Import dev or prod specific settings
# ------------------------------------------------
import platform
import hosts
import os
import datetime


# Number of photos to show in the grid initially and on more pages
PHOTOGRID_ITEMS_INITIAL = 11
PHOTOGRID_ITEMS_PERPAGE = 6

# Number of flow containers to show in the photo-flow,
# One block is a 4x2 container with up to 4 cols
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

# Helper for later
NOW = datetime.datetime.now()
DATE_STR = NOW.strftime("%Y-%m-%d")

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

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default' : {
            'format' : '%(asctime)s %(levelname)-8s %(name)s \t%(message)s'
        },
    },

    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },

        'file':{
            'level':'DEBUG',
            'class':'logging.FileHandler',
            'formatter': 'default',
            'filename': os.path.join(APP_ROOT, "logs", "django-%s.log" % DATE_STR),
        },

        'querylog':{
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'backupCount': 5,
            'maxBytes': 1024 * 1024,
            'filename': os.path.join(APP_ROOT, "logs", "django-%s-queries.log" % DATE_STR),
            'delay': True,
        }
    },

    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },

        'django.db.backends': {
            'handlers': ['querylog'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },

    'root': {
        'handlers': ['file'],
        'level': 'DEBUG',
    }
}

# Step 3: Custom settings
# -----------------------
INTERNAL_IPS = ('127.0.0.1',)
