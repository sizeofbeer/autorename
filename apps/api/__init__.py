from flask_restful import Api
from .auth.controllers import (
    Login,
    UserSearch,
    UserAdd,
    UserUpdate,
    UserDel,
    GetAllID,
)
from .store.controllers import (
    ParamConfig,
    ClientParamConfig,
    AuthorConfig,
    UpStatusSearch,
    ModelSelect,
    WarehouseSelect,
)
from .ocr.controllers import (
    PicUpload,
    StartHandSelectUpload,
    CombinHandSelectPic,
)

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
    rest_api.add_resource(AuthorConfig, '/EPD/AuthorConfig')
    rest_api.add_resource(ClientParamConfig, '/EPD/ClientParamConfig')
    rest_api.add_resource(ParamConfig, '/EPD/ParameterConfiguration')
    rest_api.add_resource(UpStatusSearch, '/EPD/PrintAndUpStatusSearch')
    rest_api.add_resource(GetAllID, '/EPD/GetAllID')
    rest_api.add_resource(StartHandSelectUpload, '/EPD/StartHandSelectUpload')
    rest_api.add_resource(CombinHandSelectPic, '/EPD/CombinHandSelectPic')


    rest_api.init_app(app)