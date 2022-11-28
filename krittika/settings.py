import os
import bleach
from krittika import data
import dotenv
import django_on_heroku

# Timezone:
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_ROOT = os.path.join(BASE_DIR, 'assets')
SETTINGS_PATH = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# dotenv_file = os.path.join(BASE_DIR, ".env")
# if os.path.isfile(dotenv_file):
#     config = dotenv.dotenv_values(dotenv_file)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
DEBUG_PROPAGATE_EXCEPTIONS = False

ALLOWED_HOSTS = ['127.0.0.1', 'krittika-iitb.herokuapp.com','itc.gymkhana.iitb.ac.in', 'krittika.herokuapp.com']

# Application definition
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # User-defined
    'blog',
    'events',
    'forum',
    'users',

    # Third-Party:
    'taggit',
    'mptt',
    # 'notifications',

    # For CKEditor rendering.
    'ckeditor',
    'ckeditor_uploader',
]

TAGGIT_CASE_INSENSITIVE = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'krittika.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(SETTINGS_PATH, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'krittika.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/
LANGUAGE_CODE = 'en-us'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

# For static files.
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# For images and media
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')


####################################
##  BLEACH CONFIGURATION ##
####################################

bleach.sanitizer.ALLOWED_TAGS += ['p', 'h1',
                                  'h2', 'h3', 'h4', 'h5', 'h6', 'img']
bleach.sanitizer.ALLOWED_ATTRIBUTES.update({'img': ['src', 'alt']})

####################################
##  CKEDITOR CONFIGURATION ##
####################################

CKEDITOR_JQUERY_URL = 'https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js'

CKEDITOR_UPLOAD_PATH = 'ckMedia/'
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_ALLOW_NONIMAGE_FILES = False
CKEDITOR_BROWSE_SHOW_DIRS = True

CKEDITOR_CONFIGS = {
    'default': {

        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Cut', 'Copy', 'Paste', 'PasteText',
                'PasteFromWord', '-', 'Undo', 'Redo'],
            ['Bold', 'Italic', 'Underline', 'Strike',
                'Subscript', 'Superscript', '-', 'RemoveFormat'],
            ['NumberedList', 'BulletedList', 'Blockquote', '-', 'Outdent', 'Indent',
                'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink', 'Anchor'],
            ['Find', 'Replace', '-', 'Scayt'],
            ['Image', 'Table', 'HorizontalRule', 'SpecialChar'],
            ['Styles', 'Format', 'Font', 'FontSize'],
            ['TextColor'],
            ['Maximize']
        ],

        # Responsive editor:
        'height': '20vh',
        'width': '100%',
    },
}


###################################
## GYMKHANA SSO CONFIGS ##
###################################

SSO_CLIENT_ID = 'cobLnZLMTKMLynLI5AzprMEnaXayfTBp2u4dDjpP'
SSO_URL = 'https://gymkhana.iitb.ac.in/profiles/oauth/authorize/'
SCOPE = 'basic profile ldap program'
SSO_REDIRECT_URL = 'https://itc.gymkhana.iitb.ac.in/krittika/authorization/'

SSO_TOKEN_URL = 'https://gymkhana.iitb.ac.in/sso/oauth/token/'
SSO_CLIENT_ID_SECRET_BASE64 = data.SSO_Client_ID_Secret_Base64

SSO_PROFILE_URL = 'https://gymkhana.iitb.ac.in/sso/user/api/user/?fields=first_name,last_name,username,email,roll_number'

admin_list = [
     '19D110019',
    '160050102',  # Chaithanya
    '170260028',  # Vedant
    '180070059',  # Siddhant
    '180100060',  # Kritti
    '190100044',  # Devansh
    '190100055',  # Harshit
    '190260021',  # Harshda
    '190070029',  # Sreeman
    '190260006',  # Aneesh
    '190110080',  # Omkar
    '190100117',  # Soham
    '190260045',  # Vaishnav
    '190020012',  # Ananya
    '190020082',  # Unnatee
    '190260028',  # Manan
    '200020012',  # Adish
    '210050016',  # Arhaan
]

###################################
## RECAPTCHA CONFIGS ##
###################################

GOOGLE_RECAPTCHA_SECRET_KEY = data.Google_reCaptcha_Secret_Key

###################################
## EMAIL CONFIGS ##
###################################

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-auth.iitb.ac.in'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = data.Email_Host_User
EMAIL_HOST_PASSWORD = data.Email_Host_Password
MAILING_LIST = [
    'dave.junior.dvj@gmail.com',
]

# import os
# import psycopg2

# DATABASE_URL = os.environ['DATABASE_URL']

# conn = psycopg2.connect(DATABASE_URL, sslmode='require')

# import dj_database_url
# DATABASES['default'] = dj_database_url.config()


#django_on_heroku.settings(locals())
##################################
