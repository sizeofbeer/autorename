from datetime import timedelta


class Config(object):
    SECRET_KEY = 'the quick brown fox jumps over the lazy dog'
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(seconds=1)
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@192.168.15.77:3306/ElectricPaperDocumentsDB?charset=utf8'
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_MAX_OVERFLOW = 5
    POSTS_PER_PAGE = 10


class ProdConfig(Config):
    pass
    

class DevConfig(Config):
    DEBUG = True