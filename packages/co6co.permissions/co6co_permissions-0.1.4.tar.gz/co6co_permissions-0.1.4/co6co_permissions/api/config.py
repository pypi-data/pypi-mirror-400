
from sanic import Sanic, Blueprint, Request
from ..view_model.config import View, Views, ExistView, ConfigView, ConfigByCacheView
from co6co_sanic_ext.api import add_routes
from ..view_model.config.uiBaseConfig import UI_Config_View


config_api = Blueprint("config_API", url_prefix="/config")
add_routes(config_api, Views, View, ExistView, ConfigView, ConfigByCacheView)
add_routes(config_api, UI_Config_View)
