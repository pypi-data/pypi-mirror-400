
import os
# 配置参数 -统一管理配置
class CaptchaConfig:
    FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arial.ttf")
    WIDTH, HEIGHT = 120, 40
    BACKGROUND_COLOR = (255, 255, 255)
    # 多种文字颜色增加破解难度
    TEXT_COLORS = [(0, 0, 0), (25, 25, 112), (139, 0, 0), (0, 100, 0)]
    LINE_COLORS = [(0, 0, 255), (255, 0, 0), (0, 128, 0), (128, 0, 128)]
    POINT_COLORS = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (165, 42, 42)]
    FONT_SIZE = 26
    CHAR_LENGTH = 4
    # 添加干扰线数量范围和点数量范围
    LINE_COUNT_RANGE = (4, 6)
    POINT_COUNT = 50
    # 验证码有效期（秒）
    EXPIRE_SECONDS = 300
    # 是否区分大小写
    CASE_SENSITIVE = False

