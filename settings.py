"""
Django settings
"""

import os
from utils import read_yaml


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app_cfg = read_yaml(os.path.join(os.getcwd(), ".settings_app.yml"))
app_key = app_cfg.get('key')
playback_cfg = read_yaml(os.path.join(os.getcwd(), ".settings_playback.yml"))
play_cfg = dict(playback_cfg.get('file'))
display_columns = list(playback_cfg.get('display_cols'))
audio_dir_path = playback_cfg.get('audio_dir_path')
stream_chunk_size = playback_cfg.get('stream_chunk')

db_config = read_yaml(os.path.join(os.getcwd(), ".settings_db.yml"))


db_host = db_config.get('host')


ALLOWED_HOSTS = [db_host]


# PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': db_config.get('name'),
        'USER': db_config.get('user'),
        'PASSWORD': db_config.get('password'),  # 'bromberg58'
        'HOST': db_host,  # '127.0.0.1'
        'PORT': db_config.get('port'),
    }
}

INSTALLED_APPS = (
    'orm',
)

SECRET_KEY = 'django-insecure-$4fy=p%n8^d(*wzxk32ylu!x)keef&463sl#%3_c6can@n5=-%'
