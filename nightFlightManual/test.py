import time
import threading
from pynput import mouse, keyboard

# --- 配置区 ---
CONFIG = {
    'sequence': {
        # 主循环间隔时间(秒) - 3分钟 = 180秒
        'interval': 80,
        # 重复repeat_options的次数
        'repeat_count': 1,
        # 按键持续时间配置(秒)
        'hold_durations': {
            'w_first': 3.5,
            'a': 8,
            'w_second': 6.5,
            'w_third': 26,  # 这个时段将添加空格键间隔按压
            'w_last': 4.5,
            'a2': 2,
            'w2': 1,
            'a3': 2.5,
            's1': 5
        },
        # 空格键间隔时间(秒) - 新增配置
        'space_interval': 2,  # 每2秒按一次空格键
        # 视角转动参数(度)
        'view_rotation': {
            'left': 90,    # 向左转动角度
            'up': 45       # 向上转动角度(可根据实际需求调整)
        },
        # 数字按键
        'number_key': '4'
    },
    'mouse': {
        'enabled': True,
        'repeat_options': [  
            (1477, 829, 'left'),    # 再次挑战 
            (1085, 646, 'left')     # 开始挑战
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
        
        self.main_thread = None
        
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

    def _rotate_view(self, angle, direction):
        """
        模拟视角转动
        angle: 转动角度
        direction: 'left' 或 'up'
        """
        # 估算转动所需的鼠标移动距离(可根据实际灵敏度调整)
        pixels_per_degree = 2  # 每度对应的像素移动
        move_pixels = angle * pixels_per_degree
        
        start_x, start_y = self.mouse_controller.position
        
        if direction == 'left':
            target_x = start_x - move_pixels
            target_y = start_y
        elif direction == 'up':
            target_x = start_x
            target_y = start_y - move_pixels
        
        self._smooth_move_mouse(target_x, target_y, 0.5)  # 0.5秒内完成转动

    def _wait_if_paused(self):
        """如果程序处于暂停状态，则循环等待直到恢复"""
        while self.paused and self.running:
            time.sleep(0.1)

    def _execute_sequence(self):
        """执行单次操作序列"""
        # 1. 重复repeat_options指定次数
        repeat_count = self.config['sequence']['repeat_count']
        repeat_ops = self.config['mouse']['repeat_options']
        
        # print(f"开始执行repeat_options，共{repeat_count}次")
        for _ in range(repeat_count):
            self._wait_if_paused()
            if not self.running: break
            
            for x, y, click_type in repeat_ops:
                self._wait_if_paused()
                if not self.running: break
                
                self._smooth_move_mouse(x, y, self.config['mouse']['move_duration'])
                
                if click_type == 'left':
                    self.mouse_controller.click(mouse.Button.left, 1)
                elif click_type == 'right':
                    self.mouse_controller.click(mouse.Button.right, 1)
                elif click_type == 'double':
                    self.mouse_controller.click(mouse.Button.left, 2)
                
                time.sleep(0.5)  # 点击后短暂停顿

        if not self.running: return
        
        # 等待5秒 进入副本
        time.sleep(5)
        # 2. 按住w键
        # print(f"按住w键{self.config['sequence']['hold_durations']['w_first']}秒")
        self._wait_if_paused()
        self.keyboard_controller.press('w')
        self._sleep_with_pause_check(self.config['sequence']['hold_durations']['w_first'])
        self.keyboard_controller.release('w')

        # 3. 按住a键
        # print(f"按住a键{self.config['sequence']['hold_durations']['a']}秒")
        self._wait_if_paused()
        self.keyboard_controller.press('a')
        self._sleep_with_pause_check(self.config['sequence']['hold_durations']['a'])
        self.keyboard_controller.release('a')

        # 4. 按住w键
        # print(f"按住w键{self.config['sequence']['hold_durations']['w_second']}秒")
        self._wait_if_paused()
        self.keyboard_controller.press('w')
        self._sleep_with_pause_check(self.config['sequence']['hold_durations']['w_second'])
        self.keyboard_controller.release('w')

        # 6. 按住w键并间隔按压空格键
        w_third_duration = self.config['sequence']['hold_durations']['w_third']
        space_interval = self.config['sequence']['space_interval']
        # print(f"按住w键{w_third_duration}秒，每{space_interval}秒按一次空格键")
        self._wait_if_paused()
        self.keyboard_controller.press('a')
        
        # 计算需要按空格键的次数和时间点
        start_time = time.time()
        elapsed = 0
        press_count = 0
        
        while elapsed < w_third_duration and self.running:
            self._wait_if_paused()
            if not self.running:
                break
                
            # 每隔指定间隔按一次空格键
            if elapsed >= (press_count + 1) * space_interval:
                # print(f"第{press_count + 1}次按空格键")
                self.keyboard_controller.press(keyboard.Key.space)
                time.sleep(0.1)  # 短暂按住
                self.keyboard_controller.release(keyboard.Key.space)
                press_count += 1
                # 间隔1s
                time.sleep
                
            # 检查是否到达总时长
            elapsed = time.time() - start_time
            time.sleep(0.1)  # 短间隔检查
            
        self.keyboard_controller.release('a')

        # 9. 按住w键
        print(f"按住w键{self.config['sequence']['hold_durations']['w_last']}秒")
        self._wait_if_paused()
        self.keyboard_controller.press('w')
        self._sleep_with_pause_check(self.config['sequence']['hold_durations']['w_last'])
        self.keyboard_controller.release('w')

        # 自定义部分
        self.keyboard_controller.press('a')
        self._sleep_with_pause_check(self.config['sequence']['hold_durations']['a2'])
        self.keyboard_controller.release('a')                   

        self.keyboard_controller.press('w')
        self._sleep_with_pause_check(self.config['sequence']['hold_durations']['w2'])
        self.keyboard_controller.release('w')

        self.keyboard_controller.press('a')
        self._sleep_with_pause_check(self.config['sequence']['hold_durations']['a3'])
        self.keyboard_controller.release('a')

        self.keyboard_controller.press('s')
        self._sleep_with_pause_check(self.config['sequence']['hold_durations']['s1'])
        self.keyboard_controller.release('s')

    def _sleep_with_pause_check(self, duration):
        """带暂停检查的睡眠函数"""
        start_time = time.time()
        while time.time() - start_time < duration and self.running:
            if self.paused:
                time.sleep(0.1)
            else:
                remaining = duration - (time.time() - start_time)
                sleep_time = min(0.1, remaining)
                time.sleep(sleep_time)

    def main_worker(self):
        """主工作线程，循环执行操作序列"""
        workCount = 0
        while self.running:
            self._wait_if_paused()
            if not self.running: break
            
            # 执行一次完整序列
            self._execute_sequence()
            
            # 等待下一个周期(检查暂停状态)
            workCount += 1
            print(f"等待{self.config['sequence']['interval']}秒后执行下一轮 当前轮次:{workCount}")
            self._sleep_with_pause_check(self.config['sequence']['interval'])

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

    def start(self):
        print(f"将在 {self.config['global']['start_delay']} 秒后开始自动操作...")
        print(f"按 {self.config['global']['pause_key']} 键暂停/恢复程序")
        print(f"按 {self.config['global']['exit_key']} 键停止程序")
        time.sleep(self.config['global']['start_delay'])
        
        self.running = True
        
        # 启动主工作线程
        self.main_thread = threading.Thread(target=self.main_worker, daemon=True)
        self.main_thread.start()
        
        # 启动监听器
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

    def stop(self):
        self.running = False
        self.paused = False  # 停止时解除暂停，以便线程可以退出
        if self.main_thread:
            self.main_thread.join()
        print("自动操作已停止")

if __name__ == "__main__":
    try:
        controller = AutoGameController(CONFIG)
        controller.start()
    except KeyboardInterrupt:
        controller.stop()
    except Exception as e:
        print(f"程序发生错误: {e}")