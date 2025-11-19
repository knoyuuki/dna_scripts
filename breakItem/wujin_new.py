import time
import threading
from pynput import mouse, keyboard

# --- 配置区 ---
CONFIG = {
    'keyboard': {
        'enabled': False,
        'interval': 5.0,
        'key': keyboard.Key.space,  # 使用 pynput 的 Key 对象
        'press_type': 'press',
        'hold_duration': 0.5
    },
    # 副本中 继续挑战：987, 541 开始挑战 798, 514
    # 撤离： xxx,xxx  再次挑战： xxx,xxx
    'mouse': {
        'enabled': True,
        'interval': 3.0,
        'positions': [
                    (987, 541, 'left'),        # 点击类型：'left'（左键）、'right'（右键）、'double'（双击）
                    (798, 514, 'left')
        ],
        'move_duration': 0.5  # 移动时间（秒），用于平滑移动
    },
    'global': {
        'exit_key': keyboard.Key.esc,
        'pause_key': keyboard.Key.delete,
        'start_delay': 5
    }
}
# --- 配置区结束 ---

class AutoGameController:
    def __init__(self, config):
        self.config = config
        self.running = False
        self.keyboard_thread = None
        self.mouse_thread = None
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()

    def _smooth_move_mouse(self, target_x, target_y, duration):
        """平滑移动鼠标"""
        start_x, start_y = self.mouse_controller.position
        dx = target_x - start_x
        dy = target_y - start_y
        steps = int(duration * 60)  # 假设每秒60帧
        for i in range(steps + 1):
            if not self.running:
                break
            x = start_x + (dx * i) / steps
            y = start_y + (dy * i) / steps
            self.mouse_controller.position = (x, y)
            time.sleep(duration / steps)

    def keyboard_worker(self):
        while self.running and self.config['keyboard']['enabled']:
            try:
                key = self.config['keyboard']['key']
                press_type = self.config['keyboard']['press_type']
                
                if press_type == 'hold':
                    print(f"[键盘] 按住 {key} 键 {self.config['keyboard']['hold_duration']} 秒")
                    self.keyboard_controller.press(key)
                    time.sleep(self.config['keyboard']['hold_duration'])
                    self.keyboard_controller.release(key)
                else:
                    print(f"[键盘] 按下 {key} 键")
                    self.keyboard_controller.press(key)
                    self.keyboard_controller.release(key)
                    
                time.sleep(self.config['keyboard']['interval'])
            except Exception as e:
                print(f"[键盘] 操作出错: {e}")
                time.sleep(1)

    def mouse_worker(self):
        pos_index = 0
        positions = self.config['mouse']['positions']
        
        while self.running and self.config['mouse']['enabled'] and positions:
            try:
                x, y, click_type = positions[pos_index]
                print(f"[鼠标] 移动到 ({x}, {y}) 并{click_type}点击")
                
                # 移动鼠标
                self._smooth_move_mouse(x, y, self.config['mouse']['move_duration'])
                
                # 执行点击
                if click_type == 'left':
                    self.mouse_controller.click(mouse.Button.left, 1)
                elif click_type == 'right':
                    self.mouse_controller.click(mouse.Button.right, 1)
                elif click_type == 'double':
                    self.mouse_controller.click(mouse.Button.left, 2)
                
                pos_index = (pos_index + 1) % len(positions)
                time.sleep(self.config['mouse']['interval'])
            except Exception as e:
                print(f"[鼠标] 操作出错: {e}")
                time.sleep(1)

    def on_press(self, key):
        if key == self.config['global']['exit_key']:
            print("\n检测到退出按键，正在停止...")
            self.stop()
            return False

    def start(self):
        print(f"将在 {self.config['global']['start_delay']} 秒后开始自动操作...")
        print(f"按 {self.config['global']['exit_key']} 键停止程序")
        time.sleep(self.config['global']['start_delay'])
        
        self.running = True
        
        if self.config['keyboard']['enabled']:
            self.keyboard_thread = threading.Thread(target=self.keyboard_worker, daemon=True)
            self.keyboard_thread.start()
        
        if self.config['mouse']['enabled']:
            self.mouse_thread = threading.Thread(target=self.mouse_worker, daemon=True)
            self.mouse_thread.start()
        
        # 启动监听器
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

    def stop(self):
        self.running = False
        if self.keyboard_thread:
            self.keyboard_thread.join()
        if self.mouse_thread:
            self.mouse_thread.join()
        print("自动操作已停止")

if __name__ == "__main__":
    try:
        controller = AutoGameController(CONFIG)
        controller.start()
    except KeyboardInterrupt:
        controller.stop()
    except Exception as e:
        print(f"程序发生错误: {e}")