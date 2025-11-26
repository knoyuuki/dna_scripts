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
        'hold_duration': 0.5,
        # 新增：q键自动按下配置
        'auto_q': {
            'enabled': True,  # 开关
            'interval': 10,   # 按下间隔(秒)
            'key': 'e'
        }
    },
    'mouse': {
        'enabled': True,
        'interval': 1.0,
        'switch_time': 380.0,  # 切换到escape_options的时间(秒)
        'continue_options': [
            (1192,674, 'left'),       
            (964,653, 'left')
        ],
        'escape_options':[
            (724,675, 'left'),    # 撤离   
            (1500,833, 'left'),    # 再次挑战 
            (1093,654, 'left')     # 开始挑战
        ],
        'move_duration': 0.5  # 移动时间（秒），用于平滑移动
    },
    'global': {
        'exit_key': keyboard.Key.esc,
        'pause_key': keyboard.Key.f1,  # 用于暂停/恢复的按键
        'start_delay': 5
    }
}
# --- 配置区结束 ---

class AutoGameController:
    def __init__(self, config):
        self.config = config
        self.running = False  # 程序主开关
        self.paused = False   # 暂停状态标志
        
        self.keyboard_thread = None
        self.mouse_thread = None
        self.q_press_thread = None  # 新增：q键按下线程
        
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        
        # 新增：鼠标操作切换相关变量
        self.switch_time = config['mouse']['switch_time']
        self.start_time = 0  # 记录开始/恢复运行的时间
        self.use_escape = True  # 是否使用escape_options

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

    # 新增：q键自动按下工作线程
    def q_press_worker(self):
        while self.running and self.config['keyboard']['auto_q']['enabled']:
            # 只有在使用continue_options且未暂停时才按下q键
            if not self.use_escape and not self.paused:
                pressKey = self.config['keyboard']['auto_q']['key']
                try:
                    print(f"[自动Q键] 按下 q 键")
                    self.keyboard_controller.press(pressKey)
                    self.keyboard_controller.release(pressKey)
                except Exception as e:
                    print(f"[自动Q键] 操作出错: {e}")
            
            # 等待间隔中检查状态
            for _ in range(int(self.config['keyboard']['auto_q']['interval'] * 10)):
                if not self.running or self.paused:
                    break
                time.sleep(0.1)

    def keyboard_worker(self):
        while self.running and self.config['keyboard']['enabled']:
            self._wait_if_paused()  # 检查是否暂停
            if not self.running: break # 如果在暂停时退出，则直接结束
            
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
        
        while self.running and self.config['mouse']['enabled']:
            self._wait_if_paused()  # 检查是否暂停
            if not self.running: break  # 如果在暂停时退出，则直接结束

            try:
                # 计算运行时间，判断是否需要切换操作列表
                elapsed = time.time() - self.start_time
                print(f"当前运行时间:{elapsed} 秒 , 切换时间 {self.switch_time} 秒")
                
                # 更新操作模式标志
                self.use_escape = (elapsed >= self.switch_time)
                current_options = self.config['mouse']['escape_options'] if self.use_escape else self.config['mouse']['continue_options']
           
                if not current_options:
                    time.sleep(0.1)
                    continue

                # 获取当前要操作的位置和类型
                x, y, click_type = current_options[pos_index]
                print(f"[鼠标] 移动到 ({x}, {y}) 并{click_type}点击 (已运行: {elapsed:.1f}秒)")
                
                self._smooth_move_mouse(x, y, self.config['mouse']['move_duration'])
                
                if click_type == 'left':
                    self.mouse_controller.click(mouse.Button.left, 1)
                elif click_type == 'right':
                    self.mouse_controller.click(mouse.Button.right, 1)
                elif click_type == 'double':
                    self.mouse_controller.click(mouse.Button.left, 2)
                
                # 更新索引，循环操作
                pos_index = (pos_index + 1) % len(current_options)

                # 在等待间隔中检查状态
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
            self.paused = not self.paused  # 切换暂停状态
            if self.paused:
                print("\n程序已暂停。")
            else:
                # 恢复运行时重置计时并切换回continue_options
                print("\n程序已恢复运行，重置计时并使用continue操作")
                self.start_time = time.time()  # 重置计时起点

    def start(self):
        print(f"将在 {self.config['global']['start_delay']} 秒后开始自动操作...")
        print(f"按 {self.config['global']['pause_key']} 键暂停/恢复程序（恢复后重置计时）")
        print(f"按 {self.config['global']['exit_key']} 键停止程序")
        print(f"程序运行 {self.switch_time} 秒后将自动切换到escape操作")
        # 新增：显示Q键自动按下配置
        if self.config['keyboard']['auto_q']['enabled']:
            print(f"启用自动按Q键，间隔 {self.config['keyboard']['auto_q']['interval']} 秒（仅在continue模式下生效）")
        time.sleep(self.config['global']['start_delay'])
        
        self.running = True
        self.start_time = time.time()  # 记录开始时间
        
        # 新增：启动Q键按下线程
        if self.config['keyboard']['auto_q']['enabled']:
            self.q_press_thread = threading.Thread(target=self.q_press_worker, daemon=True)
            self.q_press_thread.start()
        
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
        self.paused = False  # 停止时解除暂停，以便线程可以退出
        if self.keyboard_thread:
            self.keyboard_thread.join()
        if self.mouse_thread:
            self.mouse_thread.join()
        if self.q_press_thread:  # 新增：等待Q键线程结束
            self.q_press_thread.join()
        print("自动操作已停止")

if __name__ == "__main__":
    try:
        controller = AutoGameController(CONFIG)
        controller.start()
    except KeyboardInterrupt:
        controller.stop()
    except Exception as e:
        print(f"程序发生错误: {e}")