"""
slide 业务逻辑层
封装 pyautogui 操作，提供 PPT 控制和鼠标控制功能
"""
import os
from typing import Tuple, Optional


# 在 CI 环境中，如果没有 DISPLAY 环境变量，设置一个默认值以避免导入 pyautogui 时出错
if 'DISPLAY' not in os.environ:
    os.environ['DISPLAY'] = ':0'

try:
    import pyautogui
except Exception:
    # 在 CI 环境中，如果 pyautogui 导入失败（例如没有 X 服务器或 Xlib 错误），创建一个模拟对象
    # 捕获所有异常，包括 Xlib.error.DisplayConnectionError, ImportError, OSError 等
    class MockPyAutoGUI:
        FAILSAFE = False
        
        @staticmethod
        def press(*args, **kwargs):
            pass
        
        @staticmethod
        def position():
            return (0, 0)
        
        @staticmethod
        def moveTo(*args, **kwargs):
            pass
        
        @staticmethod
        def click(*args, **kwargs):
            pass
        
        @staticmethod
        def rightClick(*args, **kwargs):
            pass
        
        @staticmethod
        def scroll(*args, **kwargs):
            pass
        
        @staticmethod
        def hscroll(*args, **kwargs):
            pass
    
    pyautogui = MockPyAutoGUI()


class SlideService:
    """PPT 远程控制服务"""
    
    # Socket.io 静态资源配置
    SOCKETIO_VERSION = '4.5.4'
    STATIC_RESOURCES = {
        'socket.io.min.js': f'https://cdn.socket.io/{SOCKETIO_VERSION}/socket.io.min.js',
    }
    
    def __init__(self, password: str):
        """
        初始化服务
        
        Args:
            password: 访问密码
        """
        self.password = password
        # 防止 pyautogui 的安全机制（如果鼠标移到屏幕角落会触发异常）
        pyautogui.FAILSAFE = False
        
    
    def verify_password(self, password: str) -> bool:
        """
        验证密码
        
        Args:
            password: 待验证的密码
            
        Returns:
            密码是否正确
        """
        return password == self.password
    
    # ============ PPT 控制 ============
    
    def next_slide(self) -> Tuple[bool, Optional[str]]:
        """
        下一页
        
        Returns:
            (是否成功, 错误信息)
        """
        try:
            pyautogui.press('right')
            return True, None
        except Exception as e:
            return False, str(e)
    
    def prev_slide(self) -> Tuple[bool, Optional[str]]:
        """
        上一页
        
        Returns:
            (是否成功, 错误信息)
        """
        try:
            pyautogui.press('left')
            return True, None
        except Exception as e:
            return False, str(e)
    
    def home_slide(self) -> Tuple[bool, Optional[str]]:
        """
        回到首页
        
        Returns:
            (是否成功, 错误信息)
        """
        try:
            pyautogui.press('home')
            return True, None
        except Exception as e:
            return False, str(e)
    
    def end_slide(self) -> Tuple[bool, Optional[str]]:
        """
        跳到最后
        
        Returns:
            (是否成功, 错误信息)
        """
        try:
            pyautogui.press('end')
            return True, None
        except Exception as e:
            return False, str(e)
    
    # ============ 鼠标控制 ============
    
    def move_mouse(self, dx: int, dy: int) -> Tuple[bool, Optional[str]]:
        """
        移动鼠标（相对移动）
        
        Args:
            dx: X 轴偏移量
            dy: Y 轴偏移量
            
        Returns:
            (是否成功, 错误信息)
        """
        try:
            current_x, current_y = pyautogui.position()
            pyautogui.moveTo(current_x + dx, current_y + dy, duration=0)
            return True, None
        except Exception as e:
            return False, str(e)
    
    def click_mouse(self) -> Tuple[bool, Optional[str]]:
        """
        鼠标左键点击
        
        Returns:
            (是否成功, 错误信息)
        """
        try:
            pyautogui.click()
            return True, None
        except Exception as e:
            return False, str(e)
    
    def right_click_mouse(self) -> Tuple[bool, Optional[str]]:
        """
        鼠标右键点击
        
        Returns:
            (是否成功, 错误信息)
        """
        try:
            pyautogui.rightClick()
            return True, None
        except Exception as e:
            return False, str(e)
    
    def scroll_mouse(self, dx: int, dy: int) -> Tuple[bool, Optional[str]]:
        """
        鼠标滚动
        
        Args:
            dx: 水平滚动量
            dy: 垂直滚动量
            
        Returns:
            (是否成功, 错误信息)
        """
        try:
            if dy != 0:
                # pyautogui.scroll 需要整数，且值不能太大，限制在合理范围内
                scroll_clicks = int(round(dy))
                scroll_clicks = max(-100, min(100, scroll_clicks))
                if scroll_clicks != 0:
                    pyautogui.scroll(scroll_clicks)
            
            if dx != 0:
                # 水平滚动也需要整数
                hscroll_clicks = int(round(dx))
                hscroll_clicks = max(-100, min(100, hscroll_clicks))
                if hscroll_clicks != 0:
                    pyautogui.hscroll(hscroll_clicks)
            
            return True, None
        except Exception as e:
            return False, str(e)