
from sanic.response import text, raw
from sanic import Request
from co6co_sanic_ext.utils import JSON_util
from co6co_sanic_ext.model.res.result import Result
from co6co_permissions.view_model.base_view import BaseMethodView
from PIL import Image, ImageDraw, ImageFont
import os
from time import time
import random
import string
from io import BytesIO
from co6co.utils import log
from ...configs.captcha import CaptchaConfig
def generate_captcha():
    """生成验证码图片和验证码字符串"""
    try:
        # 创建空白图片
        image = Image.new('RGB', (CaptchaConfig.WIDTH, CaptchaConfig.HEIGHT), CaptchaConfig.BACKGROUND_COLOR)
        draw = ImageDraw.Draw(image)

        # 生成随机字符
        chars = ''.join(random.choices(string.ascii_letters + string.digits, k=CaptchaConfig.CHAR_LENGTH))

        # 加载字体
        try:
            font = ImageFont.truetype(CaptchaConfig.FONT_PATH, CaptchaConfig.FONT_SIZE)
        except IOError as e:
            log.err(f"无法加载字体文件: {e}")
            # 使用默认字体作为备选
            font = ImageFont.load_default()

        # 计算文本起始位置
        bbox = draw.textbbox((0, 0), chars[0], font=font)
        char_width = bbox[2] - bbox[0]
        char_height = bbox[3] - bbox[1]
        start_x = (CaptchaConfig.WIDTH - CaptchaConfig.CHAR_LENGTH * char_width) // 2
        start_y = (CaptchaConfig.HEIGHT - char_height) // 2

        # 绘制字符，每个字符使用随机颜色
        for i, char in enumerate(chars):
            x = start_x + i * char_width + random.randint(-5, 5)  # 添加轻微偏移
            y = start_y + random.randint(-5, 5)
            text_color = random.choice(CaptchaConfig.TEXT_COLORS)
            draw.text((x, y), char, fill=text_color, font=font)

        # 添加干扰线，使用随机颜色
        line_count = random.randint(*CaptchaConfig.LINE_COUNT_RANGE)
        for _ in range(line_count):
            x1 = random.randint(0, CaptchaConfig.WIDTH)
            y1 = random.randint(0, CaptchaConfig.HEIGHT)
            x2 = random.randint(0, CaptchaConfig.WIDTH)
            y2 = random.randint(0, CaptchaConfig.HEIGHT)
            line_color = random.choice(CaptchaConfig.LINE_COLORS)
            draw.line((x1, y1, x2, y2), fill=line_color, width=2)

        # 添加干扰点，使用随机颜色
        for _ in range(CaptchaConfig.POINT_COUNT):
            x = random.randint(0, CaptchaConfig.WIDTH)
            y = random.randint(0, CaptchaConfig.HEIGHT)
            point_color = random.choice(CaptchaConfig.POINT_COLORS)
            draw.point((x, y), fill=point_color)

        return image, chars
    except Exception as e:
        log.err(f"生成验证码失败: {e}")
        return None, None


class CaptchaView(BaseMethodView):
    routePath = "/captcha"

    async def get(self, request: Request):
        """
        获取验证码图片
        """
        img, code = generate_captcha()
        if not img or not code:
            return raw(b"Error generating captcha", status=500)

        # 存储验证码到会话，包含过期时间戳
        _, session = self.get_Session(request)
        session["captcha_code"] = code
        session["captcha_timestamp"] = int(time())  # 记录生成时间
        #log.info(f"验证码已生成: {code}")

        # 将图片转换为字节流
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()

        # 返回图片响应
        return raw(image_bytes, content_type="image/png")

    async def post(self, request: Request):
        """
        校验验证码 
        
        一般和其他表达内容一起验证
        例如登录时需要校验验证码，及用户名密码等。
        不建议单独调用该方法，建议在登录方法中实现相关逻辑。
        """
        data: dict = request.json
        code:str = data.get("code", "").strip()
        
        if not code:
            return self.response_json(Result.fail(message="验证码不能为空！"))

        _, session = self.get_Session(request)
        stored_code:str = session.pop('captcha_code', '')  # 使用pop移除会话中的验证码
        stored_timestamp = session.pop('captcha_timestamp', 0)

        # 检查验证码是否存在
        if not stored_code:
            return self.response_json(Result.fail(message="验证码已过期，请重新获取!"))
        # 检查验证码是否过期
        if int(time()) - stored_timestamp > CaptchaConfig.EXPIRE_SECONDS:
            return self.response_json(Result.fail(message="验证码已过期，请重新获取！"))

        # 验证验证码
        if CaptchaConfig.CASE_SENSITIVE:
            is_valid = code == stored_code
        else:
            is_valid = code.lower() == stored_code.lower()

        if not is_valid:
            return self.response_json(Result.fail(message="验证码错误！"))

        return  self.response_json(Result.success(message="验证码正确！"))

 
    
