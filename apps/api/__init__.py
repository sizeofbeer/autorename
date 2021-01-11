from flask_restful import Api
from .auth.controllers import (
    Login,
    UserSearch,
    UserAdd,
    UserUpdate,
    UserDel,
)
from .store.controllers import (
    ParamConfig,
    UpStatusSearch,
    PicUpload,
    ModelSelect,
    WarehouseSelect,
)
# from .ocr.controllers import (
    
# )

rest_api = Api()


def create_module(app, **kwargs):
    rest_api.add_resource(Login, '/EPD/login')
    rest_api.add_resource(UserSearch, '/EPD/UserSearch')
    rest_api.add_resource(UserAdd, '/EPD/UserAdd')
    rest_api.add_resource(UserUpdate, '/EPD/UserUpdate')
    rest_api.add_resource(UserDel, '/EPD/UserDel')
    rest_api.add_resource(PicUpload, '/EPD/PicUpload')
    rest_api.add_resource(ModelSelect, '/EPD/ModelSelect')
    rest_api.add_resource(WarehouseSelect, '/EPD/WarehouseSelect')
    rest_api.add_resource(ParamConfig, '/EPD/ParameterConfiguration')
    rest_api.add_resource(UpStatusSearch, '/EPD/PrintAndUpStatusSearch')
    

    rest_api.init_app(app)