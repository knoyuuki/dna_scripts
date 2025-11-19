import pyautogui
import time
import threading
import configparser
from pynput import keyboard  # 用于监听退出按键

# 确保中文显示正常（pyautogui输入中文需系统支持，此处主要处理提示信息）
pyautogui.FAILSAFE = True  # 启用安全模式，鼠标移到左上角可终止程序
pyautogui.PAUSE = 0.1      # 每个操作后暂停0.1秒，防止操作过快

class AutoController:
    def __init__(self):
        # 默认配置 - 可根据需要修改
        self.config = {
            # 键盘配置
            'keyboard': {
                'enabled': False,               # 是否启用键盘自动输入
                'interval': 5,                 # 按键间隔时间（秒）
                'key': 'space',                # 要按下的键（支持字母、数字、'enter'、'space'等）
                'press_type': 'press',         # 操作类型：'press'（按一下）或 'hold'（按住不放，配合interval使用）
                'hold_duration': 0.5           # 按住持续时间（仅press_type为'hold'时有效）
            },
            
            # 鼠标配置
            'mouse': {
                'enabled': True,               # 是否启用鼠标自动操作
                'interval': 3,                 # 鼠标操作间隔时间（秒）
                'positions': [                 # 鼠标要移动到的位置列表（x, y, 点击类型）
                    (1183, 678, 'left'),        # 点击类型：'left'（左键）、'right'（右键）、'double'（双击）
                    (1052, 656, 'left')
                ],
                'move_duration': 0.5           # 鼠标移动到目标位置的时间（秒）
            },
            
            # 全局配置
            'global': {
                'exit_key': 'esc',             # 退出程序的按键
                'start_delay': 10               # 程序启动延迟时间（秒），用于切换到目标窗口
            }
        }
        
        self.running = False
        self.keyboard_thread = None
        self.mouse_thread = None
        
    def load_config(self, config_file=None):
        """从配置文件加载配置（可选功能）"""
        if not config_file:
            return
            
        try:
            config = configparser.ConfigParser()
            config.read(config_file)
            
            # 读取键盘配置
            if 'keyboard' in config:
                self.config['keyboard']['enabled'] = config.getboolean('keyboard', 'enabled', fallback=True)
                self.config['keyboard']['interval'] = config.getfloat('keyboard', 'interval', fallback=5)
                self.config['keyboard']['key'] = config.get('keyboard', 'key', fallback='space')
                self.config['keyboard']['press_type'] = config.get('keyboard', 'press_type', fallback='press')
                self.config['keyboard']['hold_duration'] = config.getfloat('keyboard', 'hold_duration', fallback=0.5)
                
            # 读取鼠标配置
            if 'mouse' in config:
                self.config['mouse']['enabled'] = config.getboolean('mouse', 'enabled', fallback=True)
                self.config['mouse']['interval'] = config.getfloat('mouse', 'interval', fallback=3)
                self.config['mouse']['move_duration'] = config.getfloat('mouse', 'move_duration', fallback=0.5)
                
            print(f"成功从 {config_file} 加载配置")
        except Exception as e:
            print(f"加载配置文件失败: {e}，将使用默认配置")
    
    def keyboard_worker(self):
        """键盘自动操作线程"""
        while self.running and self.config['keyboard']['enabled']:
            try:
                key = self.config['keyboard']['key']
                press_type = self.config['keyboard']['press_type']
                
                if press_type == 'hold':
                    print(f"按住 {key} 键 {self.config['keyboard']['hold_duration']} 秒")
                    pyautogui.keyDown(key)
                    time.sleep(self.config['keyboard']['hold_duration'])
                    pyautogui.keyUp(key)
                else:
                    print(f"按下 {key} 键")
                    pyautogui.press(key)
                    
                time.sleep(self.config['keyboard']['interval'])
            except Exception as e:
                print(f"键盘操作出错: {e}")
                time.sleep(1)
    
    def mouse_worker(self):
        """鼠标自动操作线程"""
        pos_index = 0
        positions = self.config['mouse']['positions']
        
        while self.running and self.config['mouse']['enabled'] and positions:
            try:
                x, y, click_type = positions[pos_index]
                print(f"移动鼠标到 ({x}, {y}) 并{click_type}点击")
                
                # 移动鼠标
                pyautogui.moveTo(x, y, duration=self.config['mouse']['move_duration'])
                
                # 执行点击操作
                if click_type == 'left':
                    pyautogui.click()
                elif click_type == 'right':
                    pyautogui.rightClick()
                elif click_type == 'double':
                    pyautogui.doubleClick()
                
                # 更新位置索引，循环操作
                pos_index = (pos_index + 1) % len(positions)
                
                time.sleep(self.config['mouse']['interval'])
            except Exception as e:
                print(f"鼠标操作出错: {e}")
                time.sleep(1)
    
    def on_press(self, key):
        """监听按键，用于退出程序"""
        try:
            if key == keyboard.Key.esc:  # 按ESC键退出
                self.stop()
                return False
        except AttributeError:
            pass
    
    def start(self):
        """启动自动操作"""
        print(f"将在 {self.config['global']['start_delay']} 秒后开始自动操作...")
        print(f"按 {self.config['global']['exit_key'].upper()} 键停止程序")
        time.sleep(self.config['global']['start_delay'])
        
        self.running = True
        
        # 启动键盘线程
        if self.config['keyboard']['enabled']:
            self.keyboard_thread = threading.Thread(target=self.keyboard_worker, daemon=True)
            self.keyboard_thread.start()
        
        # 启动鼠标线程
        if self.config['mouse']['enabled']:
            self.mouse_thread = threading.Thread(target=self.mouse_worker, daemon=True)
            self.mouse_thread.start()
        
        # 启动按键监听
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()
    
    def stop(self):
        """停止自动操作"""
        print("\n正在停止自动操作...")
        self.running = False
        
        # 等待线程结束
        if self.keyboard_thread and self.keyboard_thread.is_alive():
            self.keyboard_thread.join()
        if self.mouse_thread and self.mouse_thread.is_alive():
            self.mouse_thread.join()
        
        print("自动操作已停止")

if __name__ == "__main__":
    # 安装依赖提示
    try:
        import pyautogui
        from pynput import keyboard
    except ImportError:
        print("请先安装必要的依赖库：")
        print("pip install pyautogui pynput")
        exit(1)
    
    # 创建控制器实例
    controller = AutoController()
    
    # 可以加载外部配置文件（可选）
    # controller.load_config("auto_control.ini")
    
    # 启动自动操作
    try:
        controller.start()
    except KeyboardInterrupt:
        controller.stop()