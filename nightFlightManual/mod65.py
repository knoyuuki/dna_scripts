import time
import threading
from pynput import mouse, keyboard

# --- 配置区 ---
CONFIG = {
    'sequence': {
        # 主循环间隔时间(秒)
        'interval': 85,
        'repeat_count': 1,
        'hold_durations': {
            'w_first': 3.5,
            'a': 8,
            'w_second': 7,
            'w_third': 25,  # 这个时段将添加空格键间隔按压
            'w_last': 4.5,
            'a2': 2,
            'w2': 1,
            'a3': 2.5,
            's1': 5
        },
        'space_interval': 2,  # 每2秒按一次空格键
        'view_rotation': {
            'left': 90,
            'up': 45
        },
        'number_key': '4'
    },
    'mouse': {
        'enabled': True,
        'repeat_options': [  
            (1477, 829, 'left'),    # 再次挑战 
            (1085, 646, 'left')     # 开始挑战
        ],
        'move_duration': 0.5
    },
    'global': {
        'exit_key': keyboard.Key.f2,  # 退出键改为F2
        'pause_key': keyboard.Key.f1,
        'start_delay': 5,
        # 10分钟检测一次
        'periodic_interval': 600  # 30分钟 = 1800秒
    }
}
# --- 配置区结束 ---

class AutoGameController:
    def __init__(self, config):
        self.config = config
        self.running = False
        self.paused = False
        
        self.main_thread = None
        self.last_periodic_time = time.time()  # 记录上次定期操作时间
        
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
        """模拟视角转动"""
        pixels_per_degree = 2
        move_pixels = angle * pixels_per_degree
        
        start_x, start_y = self.mouse_controller.position
        
        if direction == 'left':
            target_x = start_x - move_pixels
            target_y = start_y
        elif direction == 'up':
            target_x = start_x
            target_y = start_y - move_pixels
        
        self._smooth_move_mouse(target_x, target_y, 0.5)

    def _wait_if_paused(self):
        """暂停状态等待"""
        while self.paused and self.running:
            time.sleep(0.1)

    def _periodic_operation(self):
        """30分钟定期操作"""
        print("执行30分钟定期操作...")
        
        # 按下ESC键
        self.keyboard_controller.press(keyboard.Key.esc)
        time.sleep(0.1)
        self.keyboard_controller.release(keyboard.Key.esc)
        print("按下ESC键")
        
        # 等待2秒
        self._sleep_with_pause_check(2)
        
        # 点击(1800,854) 退出挑战
        self._smooth_move_mouse(1800, 854, self.config['mouse']['move_duration'])
        self.mouse_controller.click(mouse.Button.left, 1)
        print("点击退出挑战")
        time.sleep(0.5)
        
        # 点击(1086,563) 确认
        self._smooth_move_mouse(1086, 563, self.config['mouse']['move_duration'])
        self.mouse_controller.click(mouse.Button.left, 1)
        print("点击确认")
        time.sleep(0.5)
        
        # 等待5秒
        self._sleep_with_pause_check(5)
        
        # 更新上次执行时间
        self.last_periodic_time = time.time()
        print("定期操作完成，继续执行序列")

    def _execute_sequence(self):
        """执行单次操作序列"""
        # 1. 执行鼠标操作
        repeat_count = self.config['sequence']['repeat_count']
        repeat_ops = self.config['mouse']['repeat_options']
        
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
                
                time.sleep(0.5)

        if not self.running: return
        
        # 如果正常流程则会在加载副本时按下esc键 不会对正常流程产生影响 非正常流程则重置副本 开启下一次循环
        time.sleep(0.5)
        # 鼠标操作完成后，检查是否需要执行30分钟定期操作
        current_time = time.time()
        if current_time - self.last_periodic_time >= self.config['global']['periodic_interval']:
            self._periodic_operation()
            return 1
        
        # 2. 开始执行键盘操作（定期操作之后）
        # 等待5秒 进入副本
        time.sleep(6)

        
        # 按住w键
        self._wait_if_paused()
        self.keyboard_controller.press('w')
        self._sleep_with_pause_check(self.config['sequence']['hold_durations']['w_first'])
        self.keyboard_controller.release('w')

        # 按住a键
        self._wait_if_paused()
        self.keyboard_controller.press('a')
        self._sleep_with_pause_check(self.config['sequence']['hold_durations']['a'])
        self.keyboard_controller.release('a')

        # 按住w键
        self._wait_if_paused()
        self.keyboard_controller.press('w')
        self._sleep_with_pause_check(self.config['sequence']['hold_durations']['w_second'])
        self.keyboard_controller.release('w')

        # 按住a键并间隔按压空格键
        w_third_duration = self.config['sequence']['hold_durations']['w_third']
        space_interval = self.config['sequence']['space_interval']
        self._wait_if_paused()
        self.keyboard_controller.press('a')
        
        start_time = time.time()
        elapsed = 0
        press_count = 0
        
        while elapsed < w_third_duration and self.running:
            self._wait_if_paused()
            if not self.running:
                break
                
            if elapsed >= (press_count + 1) * space_interval:
                self.keyboard_controller.press(keyboard.Key.space)
                time.sleep(0.1)
                self.keyboard_controller.release(keyboard.Key.space)
                press_count += 1
                
            elapsed = time.time() - start_time
            time.sleep(0.1)
            
        self.keyboard_controller.release('a')

        # 按住w键
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

        return self.config['sequence']['interval']

    def _sleep_with_pause_check(self, duration):
        """带暂停检查的睡眠"""
        start_time = time.time()
        while time.time() - start_time < duration and self.running:
            if self.paused:
                time.sleep(0.1)
            else:
                remaining = duration - (time.time() - start_time)
                sleep_time = min(0.1, remaining)
                time.sleep(sleep_time)

    def main_worker(self):
        """主工作线程"""
        workCount = 0
        while self.running:
            self._wait_if_paused()
            if not self.running: break
            
            # 执行一次完整序列
            timeInterval = self._execute_sequence()
            if(not timeInterval or timeInterval <= 0):
                timeInterval = self.config['sequence']['interval']
            
            # 等待下一个周期
            workCount += 1
            print(f"等待{timeInterval}秒后执行下一轮 当前轮次:{workCount}")
            self._sleep_with_pause_check(timeInterval)

    def on_press(self, key):
        """键盘监听"""
        if key == self.config['global']['exit_key']:
            print("\n检测到退出按键，正在停止...")
            self.stop()
            return False
        elif key == self.config['global']['pause_key']:
            self.paused = not self.paused
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
        self.last_periodic_time = time.time()  # 初始化定期操作时间
        
        self.main_thread = threading.Thread(target=self.main_worker, daemon=True)
        self.main_thread.start()
        
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

    def stop(self):
        self.running = False
        self.paused = False
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