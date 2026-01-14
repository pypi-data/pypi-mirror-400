
from enum import Flag
from functools import wraps
from sanic.request import Request
from ...model.pos.right import LoginLogPO

from co6co_sanic_ext.utils import JSON_util
from datetime import datetime
from sanic.response import JSONResponse

from co6co.utils import log
from co6co_sanic_ext.model.res.result import Result
from co6co_web_db.view_model import peraseRequest

from co6co_db_ext.db_utils import db_tools, InsertCallable
from ...services import getCurrentUserId
import json
import time
from ...configs.captcha import CaptchaConfig


async def _loginLog(response: JSONResponse, request: Request):
    try:
        po = LoginLogPO()
        po.ipAddress = request.client_ip  # p.ip=self.forwarded['for']
        po.createTime = datetime.now()
        res = json.loads(str(response.body, encoding='utf-8'))
        result = Result.success()
        result.__dict__.update(res)
        po.name = request.json.get("userName")
        if result.code == 0:
            po.createUser = getCurrentUserId(request)
            po.state = "成功"
        else:
            po.state = "失败"
        # log.warn(po.__dict__)
        insert = InsertCallable(request.ctx.session)
        await insert(po)
    except Exception as e:
        log.err("写登录日志失败")


def loginLog(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        request: Request = None
        for a in args:
            if type(a) == Request:
                request = a
            # log.warn("第一个参数",type(a))
        '''
        for a,v in kwargs:
            log.warn("第er个参数",type(a),type(v))
        '''
        response = await f(*args, **kwargs)
        await _loginLog(response, request)
        return response
    return decorated_function
 

def _checkVerifycode(request: Request):
    """
    检查验证码
    """
    verifyCode:str = request.json.get("verifyCode", "")
    if verifyCode == "":
        log.warn("验证码不能为空！")
        return False,"验证码不能为空！"
    _,sessionDict,_=peraseRequest(request) 
    # 方案1 拖拉方式验证

    memCode=sessionDict.get("verifyCode", None) 
    if memCode:  
        # 如果没有 key  
        memCode = sessionDict.pop("verifyCode" ) 
        if memCode != verifyCode:
            return False,"验证码错误！"
        return True,"验证成功！"
    # 方案2 验证码方法
    stored_code:str = sessionDict.pop('captcha_code', '')  # 使用pop移除会话中的验证码
    #log.warn("验证码",stored_code)
    stored_timestamp = sessionDict.pop('captcha_timestamp', 0)

    # 检查验证码是否存在
    if not stored_code:
        return False,"验证码不存在！"
    # 检查验证码是否过期
    if int(time.time()) - stored_timestamp > CaptchaConfig.EXPIRE_SECONDS:
        #log.warn("验证码已过期，请重新获取！")
        return False,"验证码已过期，请重新获取！"
    # 检查验证码是否匹配
    if not CaptchaConfig.CASE_SENSITIVE:
        stored_code = stored_code.lower()
        verifyCode = verifyCode.lower()
    result=stored_code == verifyCode
    #log.warn("验证码匹配结果",stored_code == verifyCode,stored_code ,verifyCode)
    return result,"验证成功！" if result else "验证码错误！"
     
def verifyCode(f):
    """
    验证码装饰器
    """
    @wraps(f)
    async def _function(*args, **kwargs):
        request: Request = None
        for a in args:
            if type(a) == Request:
                request = a
        result,msg=_checkVerifycode(request)
        if not result:
            log.warn(msg,result)
            return JSON_util.response(Result.fail(message=msg))
        return await f(*args, **kwargs)  
    return _function
