from sanic import  Blueprint
from co6co_sanic_ext.api import add_routes
from ..view_model.verify.drapVerify import drap_verify_view
from ..view_model.verify.captcha import CaptchaView 


verify_api = Blueprint("verify_api", url_prefix="/verify")
add_routes(verify_api, drap_verify_view,CaptchaView) 
