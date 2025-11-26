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
            'w_first': 4.5,    # w冲刺4秒
            'a_first': 4,    # a冲刺4秒
            'w_second': 0.8,   # w冲刺1秒
            'a_space': 13,   # a冲刺12秒（带空格）
            'w_third': 3,    # w冲刺3秒
            'a_second': 2,   # a冲刺4秒
            's_first': 3     # s冲刺3秒
        },
        'space_interval': 1,  # 每1秒按一次空格键（修改为1秒间隔）
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

    # 新增：基础冲刺方法（键盘按下0.2秒后按鼠标右键）
    def _sprint(self, key, duration):
        """按住指定键盘按键后，延迟0.2秒按住鼠标右键进行冲刺"""
        self._wait_if_paused()
        if not self.running:
            return
            
        # 先按下键盘按键
        self.keyboard_controller.press(key)
        print(f"按下{key}键，准备冲刺")
        
        # 延迟0.2秒
        self._sleep_with_pause_check(0.2)
        
        # 再按下鼠标右键
        self.mouse_controller.press(mouse.Button.right)
        print(f"0.2秒后按下鼠标右键，开始{key}键冲刺，持续{duration}秒")
        
        # 保持冲刺状态（总时长减去0.2秒延迟）
        remaining_duration = max(0, duration - 0.2)
        self._sleep_with_pause_check(remaining_duration)
        
        # 释放按键（先释放鼠标右键，再释放键盘按键）
        self.mouse_controller.release(mouse.Button.right)
        self.keyboard_controller.release(key)
        print(f"{key}键冲刺结束")

    # 新增：带空格键的冲刺方法
    def _sprint_with_space(self, key, duration, space_interval):
        """按住指定键盘按键后延迟0.2秒按鼠标右键，同时间隔按空格键"""
        self._wait_if_paused()
        if not self.running:
            return
            
        # 先按下键盘按键
        self.keyboard_controller.press(key)
        print(f"按下{key}键，准备带空格冲刺")
        
        # 延迟0.2秒
        self._sleep_with_pause_check(0.2)
        
        # 再按下鼠标右键
        self.mouse_controller.press(mouse.Button.right)
        print(f"0.2秒后按下鼠标右键，开始{key}键带空格冲刺，持续{duration}秒")
        
        # 计算剩余有效时间（总时长减去0.2秒延迟）
        effective_duration = max(0, duration - 0.2)
        start_time = time.time()
        elapsed = 0
        press_count = 0
        
        while elapsed < effective_duration and self.running:
            self._wait_if_paused()
            if not self.running:
                break
                
            if elapsed >= (press_count + 1) * space_interval:
                self.keyboard_controller.press(keyboard.Key.space)
                time.sleep(0.1)
                self.keyboard_controller.release(keyboard.Key.space)
                press_count += 1
                print(f"第{press_count}次按下空格键")
                
            elapsed = time.time() - start_time
            time.sleep(0.1)
            
        # 释放按键
        self.mouse_controller.release(mouse.Button.right)
        self.keyboard_controller.release(key)
        print(f"{key}键带空格冲刺结束")

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
        
        # 检查是否需要执行30分钟定期操作
        current_time = time.time()
        if current_time - self.last_periodic_time >= self.config['global']['periodic_interval']:
            self._periodic_operation()
            return 1
        
        # 等待5秒 进入副本
        time.sleep(6)

        
        # 执行新的冲刺序列
        # w 冲刺（同时按住鼠标右键）4秒
        self._sprint('w', self.config['sequence']['hold_durations']['w_first'])

        # a 冲刺 4秒
        self._sprint('a', self.config['sequence']['hold_durations']['a_first'])

        # w 冲刺 1秒
        self._sprint('w', self.config['sequence']['hold_durations']['w_second'])

        # a 冲刺 同时间隔1秒不断按下space键 12秒
        self._sprint_with_space(
            'a', 
            self.config['sequence']['hold_durations']['a_space'],
            self.config['sequence']['space_interval']
        )

        # w 冲刺 3秒
        self._sprint('w', self.config['sequence']['hold_durations']['w_third'])

        # a 冲刺 4秒
        self._sprint('a', self.config['sequence']['hold_durations']['a_second'])

        # s 冲刺 3秒
        self._sprint('s', self.config['sequence']['hold_durations']['s_first'])

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