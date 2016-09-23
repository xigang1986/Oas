import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MASTER_SERVER = '192.168.101.1'


FILE_SERVER = '192.168.101.200'

FILE_STORE_PATH = "%s/var/scripts/" % BASE_DIR

#tmp config
NEEDLE_CLIENT_ID = 2

MQ_CONN = {
    'host':'192.168.101.100',
    'port': 5672,
    'password': ''
}

