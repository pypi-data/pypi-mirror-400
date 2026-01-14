from sanic.response import text
from sanic import Request
from co6co_sanic_ext.utils import JSON_util
from co6co_sanic_ext.model.res.result import Result
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.sql import Select, Delete

from co6co_db_ext.db_utils import db_tools, DbCallable
from co6co_web_db.model.params import associationParam

from co6co.utils import log
from ..base_view import BaseMethodView
from ..aop import exist, ObjectExistRoute
from ...model.filters.config_filter import Filter
from ...model.pos.other import sysConfigPO
from ..aop.config_aop import ConfigEntry
from ...services .configCache import ConfigCache


class UI_Config_View(BaseMethodView):
    """
    不需要认证
    获取UI基础配置
    """
    routePath = "/ui" 
    async def post(self, request: Request):
        """ 
        获取配置
        code: 配置代码

        return str,配置值
        """
        cache = ConfigCache(request)
        code="SYS_CONFIG_BASE_UI"
        config = cache.getConfig(code)
        if not config:
            config = await cache .queryConfig(code)
        if config is None: 
            log.warn(f"未能获取配置项'{code}'，请检查是否有配置项'{code}',或检查配置的json对象是否正确")
            return self.response_json(Result.fail(message="未能获取配置，请检查是否有配置项'{}',或检查配置的json对象是否正确".format(code)))
        return self.response_json(Result.success(config))

