from pynput import mouse
import time

def on_move(x, y):
    """鼠标移动时触发的回调函数"""
    print(f"鼠标位置: ({x}, {y})", end='\r')  # 使用\r实现实时刷新

def main():
    print("正在监听鼠标位置... (按 Ctrl+C 停止)")
    
    # 创建鼠标监听器
    listener = mouse.Listener(on_move=on_move)
    
    # 启动监听器
    listener.start()
    
    try:
        # 保持主线程运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # 按下Ctrl+C时停止监听器
        listener.stop()
        print("\n监听已停止")

if __name__ == "__main__":
    main()