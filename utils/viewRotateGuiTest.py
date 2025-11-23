import pyautogui
import time

# 获取屏幕尺寸
screen_width, screen_height = pyautogui.size()

def rotate_view(x_offset, y_offset, duration=0.1):
    """
    旋转游戏视角
    x_offset: X轴移动距离（正数向右，负数向左）
    y_offset: Y轴移动距离（正数向下，负数向上）
    duration: 移动持续时间
    """
    pyautogui.moveRel(x_offset, y_offset, duration=duration)

time.sleep(5)
# 示例：向右转动视角
rotate_view(100, 0)

# 示例：向上看
rotate_view(0, -50)

# 连续转动
for i in range(10):
    rotate_view(20, 0, 0.05)
    time.sleep(0.1)