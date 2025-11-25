import time
import threading
from pynput import mouse, keyboard

# --- 配置区 ---
SELECT_IRAI = 2
CONFIG = {
    'keyboard': {
        'enabled': True,
        'interval': 3.0,  # 每隔3秒按一次e键
        'key': ['e'],     # 使用e键
        'press_type': 'tap'  # 单次点击类型
    },
    'mouse': {
        'enabled': True,
        'interval': 1.0,  # 默认间隔时间
        # 鼠标循环A方案步骤配置
        'scheme_a': [
            # 步骤0, 选择首位奖励
            {'x': 748, 'y': 619, 'click_type': 'left'},
            # 步骤1: 确认选择奖励（单独配置间隔）
            {'x': 958, 'y': 785, 'click_type': 'left', 'interval': 3.0},
            # 步骤2: 继续挑战
            {'x': 1187, 'y': 674, 'click_type': 'left'},
            # 步骤3: 选择密函（基础位置+偏移量）
            {
                'base_x': 952, 
                'base_y': 508, 
                'click_type': 'left',
                'offset_x': 84,  # 每个选项的x轴偏移量
                'selected_index': SELECT_IRAI  # 选择第几个密函（从0开始计数）
            },
            # 步骤4: 确认选择
            {'x': 1267, 'y': 610, 'click_type': 'left'}
        ],
        # 鼠标循环B方案步骤配置
        'scheme_b': [
            # 步骤0, 选择首位奖励
            {'x': 748, 'y': 619, 'click_type': 'left'},
            # 步骤1: 确认选择奖励（单独配置间隔）
            {'x': 958, 'y': 785, 'click_type': 'left', 'interval': 3.0},
            # 步骤0：撤离
            {'x': 720, 'y': 676, 'click_type': 'left', 'interval': 6.0},
            # 步骤1：再次进行
            {'x': 1501, 'y': 829, 'click_type': 'left'},
            # 步骤2：选择密函
            {
                'base_x': 952, 
                'base_y': 508, 
                'click_type': 'left',
                'offset_x': 84,
                'selected_index': SELECT_IRAI
            },
            # 步骤3：确认选择
            {'x': 1362, 'y': 609, 'click_type': 'left'}
        ],
        'move_duration': 0.5  # 移动时间（秒），用于平滑移动
    },
    'global': {
        'exit_key': keyboard.Key.esc,
        'pause_key': keyboard.Key.f1,  # 用于暂停/恢复的按键
        'start_delay': 5,
        'scheme_switch_time': 410  # 切换到B方案的时间（秒）
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
        
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        
        self.start_time = 0  # 程序开始时间（用于方案切换）
        self.current_mouse_scheme = 'scheme_a'  # 当前鼠标方案

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
        """键盘工作线程：每隔3秒按一次e键"""
        while self.running and self.config['keyboard']['enabled']:
            self._wait_if_paused()  # 检查是否暂停
            if not self.running:
                break
            
            try:
                key = self.config['keyboard']['key'][0]
                press_type = self.config['keyboard']['press_type']
                
                if press_type == 'tap':
                    print(f"[键盘] 按下 {key} 键")
                    self.keyboard_controller.press(key)
                    self.keyboard_controller.release(key)
                elif press_type == 'hold':
                    # 保留长按逻辑（当前配置未使用）
                    self.keyboard_controller.press(key)
                    time.sleep(self.config['keyboard'].get('hold_duration', 1))
                    self.keyboard_controller.release(key)
                
                # 等待间隔中检查暂停状态
                for _ in range(int(self.config['keyboard']['interval'] * 10)):
                    if not self.running or self.paused:
                        break
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"[键盘] 操作出错: {e}")
                time.sleep(1)

    def mouse_worker(self):
        """鼠标工作线程：根据时间切换A/B方案循环"""
        step_index = 0
        
        while self.running and self.config['mouse']['enabled']:
            self._wait_if_paused()  # 检查是否暂停
            if not self.running:
                break

            try:
                # 检查是否需要切换方案
                elapsed_time = time.time() - self.start_time
                if elapsed_time >= self.config['global']['scheme_switch_time']:
                    self.current_mouse_scheme = 'scheme_b'
                else:
                    self.current_mouse_scheme = 'scheme_a'
                
                # 获取当前方案的步骤配置
                current_steps = self.config['mouse'][self.current_mouse_scheme]
                current_step = current_steps[step_index]
                
                # 计算实际点击位置（处理密函选择的偏移量）
                if 'base_x' in current_step and 'base_y' in current_step:
                    # 密函选择步骤
                    x = current_step['base_x'] + current_step['selected_index'] * current_step['offset_x']
                    y = current_step['base_y']
                    click_type = current_step['click_type']
                    print(f"[鼠标-{self.current_mouse_scheme}] 移动到密函位置 ({x}, {y}) 并{click_type}点击 (选择第{current_step['selected_index']+1}个)")
                else:
                    # 普通点击步骤
                    x = current_step['x']
                    y = current_step['y']
                    click_type = current_step['click_type']
                    print(f"[鼠标-{self.current_mouse_scheme}] 移动到 ({x}, {y}) 并{click_type}点击")
                
                # 执行鼠标操作
                self._smooth_move_mouse(x, y, self.config['mouse']['move_duration'])
                
                if click_type == 'left':
                    self.mouse_controller.click(mouse.Button.left, 1)
                elif click_type == 'right':
                    self.mouse_controller.click(mouse.Button.right, 1)
                elif click_type == 'double':
                    self.mouse_controller.click(mouse.Button.left, 2)
                
                # 切换到下一步，循环执行
                step_index = (step_index + 1) % len(current_steps)

                # 确定等待间隔（步骤单独配置优先）
                temp_interval = current_step.get('interval', self.config['mouse']['interval'])
                
                # 等待间隔中检查暂停状态
                for _ in range(int(temp_interval * 10)):
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
                print("\n程序已恢复运行。")
                # 恢复运行时重置计时器和方案
                self.start_time = time.time()
                self.current_mouse_scheme = 'scheme_a'

    def start(self):
        print(f"将在 {self.config['global']['start_delay']} 秒后开始自动操作...")
        print(f"按 {self.config['global']['pause_key']} 键暂停/恢复程序（恢复后从方案A重新开始）")
        print(f"按 {self.config['global']['exit_key']} 键停止程序")
        print(f"程序运行 {self.config['global']['scheme_switch_time']} 秒后将自动切换到鼠标方案B")
        time.sleep(self.config['global']['start_delay'])
        
        self.running = True
        self.start_time = time.time()  # 记录开始时间
        self.current_mouse_scheme = 'scheme_a'  # 初始方案
        
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
        self.paused = False  # 停止时也解除暂停，以便线程可以退出
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