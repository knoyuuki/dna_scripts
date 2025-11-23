import time
import threading
from pynput import mouse, keyboard

# --- 配置区 ---
CONFIG = {
    'keyboard': {
        'enabled': True,
        'interval': 16.0,
        # 'key': keyboard.Key.space,  # 使用 pynput 的 Key 对象
        'key': ['w', 's'],  # 使用 pynput 的 Key 对象
        'comboKeys': ['w', 'a'],
        # 'press_type': 'press',
        'press_type': 'hold',
        'hold_duration': 8.5
    },
    'mouse': {
        'enabled': True,
        'interval': 2.0,
        'continue_options': [
             # 点击类型：'left'（左键）、'right'（右键）、'double'（双击）
                    (987, 541, 'left'),       
                    (798, 514, 'left')
        ],
        'repeat_options':[  
                    (1477, 829, 'left'),    # 再次挑战 
                    (1085, 646, 'left')     # 开始挑战
        ],
        'move_duration': 0.5  # 移动时间（秒），用于平滑移动
    },
    'global': {
        'exit_key': keyboard.Key.esc,
        'pause_key': keyboard.Key.f1,  # 新增：用于暂停/恢复的按键
        'start_delay': 5
    }
}
# --- 配置区结束 ---

class AutoGameController:
    def __init__(self, config):
        self.config = config
        self.running = False  # 程序主开关
        self.paused = False   # 新增：暂停状态标志
        
        self.keyboard_thread = None
        self.mouse_thread = None
        
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()

    def _smooth_move_mouse(self, target_x, target_y, duration):
        """平滑移动鼠标"""
        start_x, start_y = self.mouse_controller.position
        dx = target_x - start_x
        dy = target_y - start_y
        steps = int(duration * 60)
        for i in range(steps + 1):
            if not self.running or self.paused:
                break
            x = start_x + (dx * i) / steps
            y = start_y + (dy * i) / steps
            self.mouse_controller.position = (x, y)
            time.sleep(duration / steps)

    def _wait_if_paused(self):
        """如果程序处于暂停状态，则循环等待直到恢复"""
        while self.paused and self.running:
            time.sleep(0.1)

    def keyboard_worker(self):
        time.sleep(10)
        while self.running and self.config['keyboard']['enabled']:
            self._wait_if_paused()  # 检查是否暂停
            if not self.running: break # 如果在暂停时退出，则直接结束
            
            try:
                keys = self.config['keyboard']['key']
                press_type = self.config['keyboard']['press_type']
                
                if press_type == 'hold':
                    # print(f"[键盘] 按住 {keys} 键 {self.config['keyboard']['hold_duration']} 秒")
                    if(len(keys) > 1):
                        keyOne, keyTwo = keys
                        self.keyboard_controller.press(keyOne)
                        time.sleep(self.config['keyboard']['hold_duration'])
                        self.keyboard_controller.release(keyOne)
                        time.sleep(0.1)
                        self.keyboard_controller.press(keyTwo)
                        time.sleep(4)
                        self.keyboard_controller.release(keyTwo)

                    else:
                        print("自定义")
                        # 向前8秒 下落
                        self.keyboard_controller.press(keys[0])
                        time.sleep(8.5)
                        self.keyboard_controller.release(keys[0])
                        # 向后4
                        self.keyboard_controller.press(keys[0])
                        time.sleep(3)
                        self.keyboard_controller.release(keys[0])
                   
                else:
                    print(f"[键盘] 按下 {keys} 键")
                    self.keyboard_controller.press(keys[0])
                    self.keyboard_controller.release(keys[0])
                    
                # 在等待间隔中也需要检查暂停状态
                for _ in range(int(self.config['keyboard']['interval'] * 10)):
                    if not self.running or self.paused:
                        break
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"[键盘] 操作出错: {e}")
                time.sleep(1)

    def mouse_worker(self):
        pos_index = 0
        positions = self.config['mouse']['repeat_options']
        # positions = self.config['mouse']['continue_options']
        
        while self.running and self.config['mouse']['enabled'] and positions:
        # while self.running and self.config['mouse']['enabled'] and positions:
            self._wait_if_paused() # 检查是否暂停
            if not self.running: break # 如果在暂停时退出，则直接结束

            try:
                x, y, click_type = positions[pos_index]
                # print(f"[鼠标] 移动到 ({x}, {y}) 并{click_type}点击")
                
                self._smooth_move_mouse(x, y, self.config['mouse']['move_duration'])
                
                if click_type == 'left':
                    self.mouse_controller.click(mouse.Button.left, 1)
                elif click_type == 'right':
                    self.mouse_controller.click(mouse.Button.right, 1)
                elif click_type == 'double':
                    self.mouse_controller.click(mouse.Button.left, 2)
                
                pos_index = (pos_index + 1) % len(positions)

                # 在等待间隔中也需要检查暂停状态
                for _ in range(int(self.config['mouse']['interval'] * 10)):
                    if not self.running or self.paused:
                        break
                    time.sleep(0.1)

            except Exception as e:
                print(f"[鼠标] 操作出错: {e}")
                time.sleep(1)

    def on_press(self, key):
        """监听键盘按键，用于退出和暂停/恢复"""
        if key == self.config['global']['exit_key']:
            print("\n检测到退出按键，正在停止...")
            self.stop()
            return False
        elif key == self.config['global']['pause_key']:
            self.paused = not self.paused # 切换暂停状态
            if self.paused:
                print("\n程序已暂停。")
            else:
                print("\n程序已恢复运行。")

    def start(self):
        print(f"将在 {self.config['global']['start_delay']} 秒后开始自动操作...")
        print(f"按 {self.config['global']['pause_key']} 键暂停/恢复程序")
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
        self.paused = False # 停止时也解除暂停，以便线程可以退出
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