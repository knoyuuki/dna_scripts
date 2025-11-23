# 这是一个更高级的示例，使用 ctypes 调用 Windows API
import ctypes
import time
from pynput import keyboard

# --- Windows API 定义 ---
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000

# --- 测试脚本 ---
class ViewRotationTester:
    def __init__(self):
        self.running = True
        self.sensitivity = 1000  # 灵敏度，需要大幅调整

    def rotate_view(self, direction, duration):
        if not self.running: return
        
        dx, dy = 0, 0
        if direction == 'left':
            dx = -self.sensitivity
        elif direction == 'right':
            dx = self.sensitivity
        elif direction == 'up':
            dy = -self.sensitivity
        elif direction == 'down':
            dy = self.sensitivity
            
        print(f"\n[测试] 开始向{direction}转动 (SendInput)")
        
        # SendInput 移动的是绝对坐标或相对位移（以像素为单位）
        # 这里我们模拟相对位移
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.mi = MouseInput(dx, dy, 0, MOUSEEVENTF_MOVE, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(0), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        
        time.sleep(duration)
        
        print(f"[测试] 向{direction}转动完成")

    # ... (on_press 和 run_test_sequence 方法与之前类似) ...

# 注意：这个示例只是演示了如何调用 SendInput，
# 实际使用时需要更复杂的逻辑来实现平滑和持续的移动，
# 并且灵敏度参数需要重新进行大量调试。