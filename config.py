import os
from flask_env import MetaFlaskEnv

class Configuration(metaclass=MetaFlaskEnv):

    # Flask settings
    SECRET_KEY = 'S3CR3T'
    HOST = '0.0.0.0'
    DEBUG = True
    PORT = 5000

    # Printer settings
    PRINT_WIDTH = 40
    PRINT_HEIGHT = 89
    PRINT_FONT_SIZE = 40
    