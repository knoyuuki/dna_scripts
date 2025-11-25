from pynput.mouse import Listener

def on_click(x, y, button, pressed):
    """
    监听鼠标点击事件的回调函数
    :param x: 鼠标x坐标
    :param y: 鼠标y坐标
    :param button: 点击的按键（左键、右键等）
    :param pressed: 布尔值，True表示按下，False表示释放
    """
    if pressed:  # 只在按下时输出（避免释放时重复输出）
        print(f"鼠标点击位置：({x}, {y})，按键：{button}")
    
    # 可选：按右键退出监听（示例）
    if button == button.right:
        return False  # 返回False终止监听

# 启动监听
with Listener(on_click=on_click) as listener:
    listener.join()  # 持续监听