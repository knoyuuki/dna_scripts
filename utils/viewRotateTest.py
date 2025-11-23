import time
from pynput import mouse, keyboard

# --- 测试配置 ---
TEST_CONFIG = {
    'sensitivity': 5,  # 鼠标灵敏度（每转动90度需要移动的像素数）
    'rotation_angle': 90,  # 每次测试转动的角度（度）
    'test_duration': 0.5,  # 每次转动的持续时间（秒）
    'interval_between_tests': 2.0,  # 两次测试之间的间隔时间（秒）
    'exit_key': keyboard.Key.esc  # 退出测试的按键
}

class ViewRotationTester:
    def __init__(self, config):
        self.config = config
        self.running = True
        self.mouse_controller = mouse.Controller()

    def _calculate_movement(self, angle):
        """根据角度和灵敏度计算需要移动的鼠标像素数"""
        return angle * self.config['sensitivity']

    def rotate_view(self, angle, direction):
        """
        模拟视角转动
        :param angle: 转动角度（度）
        :param direction: 转动方向 ('left', 'right', 'up', 'down')
        """
        if not self.running:
            return

        move_pixels = self._calculate_movement(angle)
        dx, dy = 0, 0

        if direction == 'left':
            dx = -move_pixels
        elif direction == 'right':
            dx = move_pixels
        elif direction == 'up':
            dy = -move_pixels
        elif direction == 'down':
            dy = move_pixels

        print(f"\n[测试] 开始向{direction}转动{angle}度 (预计移动: dx={dx:.1f}, dy={dy:.1f})")
        
        # 平滑移动鼠标
        steps = int(self.config['test_duration'] * 60)
        step_dx = dx / steps
        step_dy = dy / steps

        for _ in range(steps):
            if not self.running:
                break
            self.mouse_controller.move(step_dx, step_dy)
            time.sleep(self.config['test_duration'] / steps)
        
        print(f"[测试] 向{direction}转动完成")

    def on_press(self, key):
        """监听退出按键"""
        if key == self.config['exit_key']:
            print("\n[测试] 检测到退出按键，正在停止...")
            self.running = False
            return False

    def run_test_sequence(self):
        """执行测试序列"""
        print("视角转动测试开始！")
        print(f"配置: 灵敏度={self.config['sensitivity']}, 每次转动={self.config['rotation_angle']}度")
        print(f"操作: 按 {self.config['exit_key']} 键停止测试")
        print("\n准备在3秒后开始第一次测试...")
        time.sleep(3)

        # 启动键盘监听器
        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()

        # 测试序列
        try:
            while self.running:
                # 1. 向左转动
                self.rotate_view(self.config['rotation_angle'], 'left')
                if not self.running: break
                time.sleep(self.config['interval_between_tests'])

                # 2. 向右转动
                self.rotate_view(self.config['rotation_angle'], 'right')
                if not self.running: break
                time.sleep(self.config['interval_between_tests'])

                # 3. 向上转动
                self.rotate_view(self.config['rotation_angle'] / 2, 'up')  # 向上转动角度减半
                if not self.running: break
                time.sleep(self.config['interval_between_tests'])

                # 4. 向下转动
                self.rotate_view(self.config['rotation_angle'] / 2, 'down')  # 向下转动角度减半
                if not self.running: break
                time.sleep(self.config['interval_between_tests'] * 2)  # 延长间隔

        except Exception as e:
            print(f"\n[测试] 发生错误: {e}")
        finally:
            listener.stop()
            listener.join()
            print("\n[测试] 所有测试已完成或被停止")

if __name__ == "__main__":
    tester = ViewRotationTester(TEST_CONFIG)
    tester.run_test_sequence()