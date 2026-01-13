import pyautogui
import win32gui
import win32con
import time
import threading
import pyperclip
from typing import Optional, Tuple, Union, List


class WindowAutoController:
    """
    窗口自动化控制器
    所有坐标都是相对于绑定窗口的本地坐标
    
    主要功能：
    - 窗口绑定和管理（支持句柄和标题绑定）
    - 鼠标操作（移动、点击、拖拽等）
    - 键盘操作（按键、组合键、文本输入）
    - 文本输入（支持中文，通过剪切板粘贴）
    - 窗口信息获取
    - 全局置顶功能
    - 错误处理和调试日志
    
    特性：
    - 自动检测中文文本并使用剪切板粘贴方式输入
    - 支持手动控制是否使用剪切板
    - 专门的中文输入方法
    """

    def __init__(self, window_handle: Optional[int] = None,
                 window_title: Optional[str] = None,
                 always_on_top: bool = True):
        """
        初始化窗口自动化控制器

        Args:
            window_handle: 窗口句柄，如果为None则使用window_title查找
            window_title: 窗口标题，用于查找窗口
            always_on_top: 绑定后是否全局置顶窗口
        """
        self.window_handle = None
        self.window_title = None
        self.window_rect = None  # (left, top, right, bottom)
        self.is_active = False
        self.always_on_top = always_on_top
        self.original_style = None  # 保存原始窗口样式

        if window_handle:
            self.bind_by_handle(window_handle)
        elif window_title:
            self.bind_by_title(window_title)

    def bind_by_handle(self, window_handle: int) -> bool:
        """
        通过窗口句柄绑定窗口

        Args:
            window_handle: 窗口句柄

        Returns:
            bool: 绑定是否成功
        """
        try:
            if not win32gui.IsWindow(window_handle):
                return False

            self.window_handle = window_handle
            self.window_title = win32gui.GetWindowText(window_handle)

            # 保存原始窗口样式
            self.original_style = win32gui.GetWindowLong(self.window_handle, win32con.GWL_EXSTYLE)

            self._update_window_rect()
            self.is_active = True

            # 根据设置进行置顶
            if self.always_on_top:
                self.set_always_on_top(True)

            return True
        except Exception as e:
            print(f"绑定窗口句柄失败: {e}")
            return False

    def bind_by_title(self, window_title: str, exact_match: bool = True) -> bool:
        """
        通过窗口标题绑定窗口

        Args:
            window_title: 窗口标题
            exact_match: 是否精确匹配

        Returns:
            bool: 绑定是否成功
        """
        try:
            def enum_windows_callback(hwnd, windows):
                try:
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        if exact_match:
                            if title == window_title and win32gui.IsWindowVisible(hwnd):
                                windows.append(hwnd)
                        else:
                            if window_title in title and win32gui.IsWindowVisible(hwnd):
                                windows.append(hwnd)
                except:
                    pass
                return True

            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)

            if not windows:
                return False

            self.window_handle = windows[0]
            self.window_title = win32gui.GetWindowText(self.window_handle)

            # 保存原始窗口样式
            self.original_style = win32gui.GetWindowLong(self.window_handle, win32con.GWL_EXSTYLE)

            self._update_window_rect()
            self.is_active = True

            # 根据设置进行置顶
            if self.always_on_top:
                self.set_always_on_top(True)

            return True
        except Exception as e:
            print(f"绑定窗口标题失败: {e}")
            return False

    def set_always_on_top(self, enable: bool = True) -> bool:
        """
        设置或取消窗口全局置顶

        Args:
            enable: True为置顶，False为取消置顶

        Returns:
            bool: 操作是否成功
        """
        if not self.window_handle:
            return False

        try:
            if enable:
                # 设置窗口置顶
                win32gui.SetWindowPos(
                    self.window_handle,
                    win32con.HWND_TOPMOST,  # 置顶
                    0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
                )
                print(f"窗口 '{self.window_title}' 已置顶")
            else:
                # 恢复原始状态
                if self.original_style:
                    # 恢复原始窗口样式
                    win32gui.SetWindowLong(
                        self.window_handle,
                        win32con.GWL_EXSTYLE,
                        self.original_style
                    )

                # 取消置顶
                win32gui.SetWindowPos(
                    self.window_handle,
                    win32con.HWND_NOTOPMOST,  # 取消置顶
                    0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
                )
                print(f"窗口 '{self.window_title}' 已取消置顶")

            return True
        except Exception as e:
            print(f"设置窗口置顶失败: {e}")
            return False

    def toggle_always_on_top(self) -> bool:
        """
        切换窗口置顶状态

        Returns:
            bool: 切换后的状态（True为置顶，False为取消）
        """
        if not self.window_handle:
            return False

        try:
            # 获取当前窗口样式
            current_style = win32gui.GetWindowLong(self.window_handle, win32con.GWL_EXSTYLE)

            # 检查是否已经是置顶状态
            is_topmost = (current_style & win32con.WS_EX_TOPMOST) != 0

            # 切换状态
            self.set_always_on_top(not is_topmost)

            return not is_topmost
        except Exception as e:
            print(f"切换窗口置顶状态失败: {e}")
            return False

    def is_always_on_top(self) -> Optional[bool]:
        """
        检查窗口是否处于置顶状态

        Returns:
            Optional[bool]: True为置顶，False为不置顶，None为无法判断
        """
        if not self.window_handle:
            return None

        try:
            current_style = win32gui.GetWindowLong(self.window_handle, win32con.GWL_EXSTYLE)
            return (current_style & win32con.WS_EX_TOPMOST) != 0
        except:
            return None

    def set_window_position(self, x: int, y: int, width: Optional[int] = None,
                            height: Optional[int] = None, keep_on_top: Optional[bool] = None) -> bool:
        """
        设置窗口位置和大小

        Args:
            x: 窗口左上角X坐标
            y: 窗口左上角Y坐标
            width: 窗口宽度，None表示保持原宽度
            height: 窗口高度，None表示保持原高度
            keep_on_top: 是否保持置顶状态，None表示保持当前状态

        Returns:
            bool: 操作是否成功
        """
        if not self.window_handle:
            return False

        try:
            # 获取当前窗口大小
            if width is None or height is None:
                current_rect = win32gui.GetWindowRect(self.window_handle)
                if width is None:
                    width = current_rect[2] - current_rect[0]
                if height is None:
                    height = current_rect[3] - current_rect[1]

            # 确定置顶标志
            if keep_on_top is None:
                # 保持当前置顶状态
                flags = 0
            elif keep_on_top:
                flags = win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW
                # 先设置置顶
                win32gui.SetWindowPos(
                    self.window_handle,
                    win32con.HWND_TOPMOST,
                    x, y, width, height,
                    flags
                )
                return True
            else:
                flags = win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW
                # 先取消置顶
                win32gui.SetWindowPos(
                    self.window_handle,
                    win32con.HWND_NOTOPMOST,
                    x, y, width, height,
                    flags
                )
                return True

            # 设置窗口位置和大小
            win32gui.SetWindowPos(
                self.window_handle,
                win32con.HWND_TOP,  # 放在最前面但不置顶
                x, y, width, height,
                flags
            )

            # 更新窗口位置信息
            self._update_window_rect()

            return True
        except Exception as e:
            print(f"设置窗口位置失败: {e}")
            return False

    def bring_to_front(self, force_focus: bool = True) -> bool:
        """
        将窗口提到前台

        Args:
            force_focus: 是否强制获取焦点

        Returns:
            bool: 操作是否成功
        """
        if not self.window_handle:
            return False

        try:
            # 恢复窗口（如果最小化）
            if win32gui.IsIconic(self.window_handle):
                win32gui.ShowWindow(self.window_handle, win32con.SW_RESTORE)

            if force_focus:
                # 将窗口置顶并获取焦点
                win32gui.SetForegroundWindow(self.window_handle)
                win32gui.BringWindowToTop(self.window_handle)
                win32gui.SetActiveWindow(self.window_handle)
            else:
                # 只将窗口置顶但不获取焦点
                win32gui.SetWindowPos(
                    self.window_handle,
                    win32con.HWND_TOP,  # 放在最前面
                    0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
                )

            # 更新窗口位置信息
            self._update_window_rect()

            return True
        except Exception as e:
            print(f"将窗口提到前台失败: {e}")
            return False

    def _update_window_rect(self) -> None:
        """更新窗口位置和大小信息"""
        if self.window_handle:
            try:
                self.window_rect = win32gui.GetWindowRect(self.window_handle)
            except:
                self.window_rect = None

    def _local_to_global(self, x: int, y: int) -> Tuple[int, int]:
        """
        将窗口本地坐标转换为全局屏幕坐标

        Args:
            x: 窗口本地X坐标
            y: 窗口本地Y坐标

        Returns:
            Tuple[int, int]: 全局屏幕坐标 (global_x, global_y)
        """
        if not self.window_rect:
            self._update_window_rect()

        if not self.window_rect:
            raise ValueError("窗口未绑定或无法获取窗口位置")

        left, top, right, bottom = self.window_rect
        global_x = left + x
        global_y = top + y

        # 确保坐标在窗口范围内
        global_x = max(left, min(global_x, right))
        global_y = max(top, min(global_y, bottom))

        return global_x, global_y

    def _ensure_window_active(self) -> bool:
        """
        确保窗口处于活动状态

        Returns:
            bool: 窗口是否成功激活
        """
        if not self.window_handle:
            return False

        try:
            # 恢复窗口（如果最小化）
            if win32gui.IsIconic(self.window_handle):
                win32gui.ShowWindow(self.window_handle, win32con.SW_RESTORE)

            # 将窗口提到前台
            self.bring_to_front()

            # 短暂延迟确保窗口激活
            time.sleep(0.1)

            # 更新窗口位置信息
            self._update_window_rect()

            return True
        except Exception as e:
            print(f"激活窗口失败: {e}")
            return False

    # 以下是原有的自动化操作方法，保持不变
    def move_to(self, x: int, y: int, duration: float = 0.0,
                activate_window: bool = True) -> bool:
        """移动鼠标到窗口内的指定位置"""
        if not self.is_active:
            return False

        try:
            if activate_window:
                self._ensure_window_active()

            global_x, global_y = self._local_to_global(x, y)
            pyautogui.moveTo(global_x, global_y, duration=duration)
            return True
        except Exception as e:
            print(f"移动鼠标失败: {e}")
            return False

    def click(self, x: Optional[int] = None, y: Optional[int] = None,
              button: str = 'left', clicks: int = 1, interval: float = 0.1,
              move_before_click: bool = True, duration: float = 0.0) -> bool:
        """在窗口内点击"""
        if not self.is_active:
            return False

        try:
            if x is not None and y is not None and move_before_click:
                if not self.move_to(x, y, duration=duration):
                    return False
                time.sleep(0.05)

            pyautogui.click(button=button, clicks=clicks, interval=interval)
            return True
        except Exception as e:
            print(f"点击失败: {e}")
            return False

    def double_click(self, x: Optional[int] = None, y: Optional[int] = None,
                     button: str = 'left', duration: float = 0.0) -> bool:
        """在窗口内双击"""
        return self.click(x, y, button=button, clicks=2, interval=0.0,
                          move_before_click=(x is not None and y is not None),
                          duration=duration)

    def right_click(self, x: Optional[int] = None, y: Optional[int] = None,
                    duration: float = 0.0) -> bool:
        """在窗口内右击"""
        return self.click(x, y, button='right', move_before_click=(x is not None and y is not None),
                          duration=duration)

    def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None,
               duration: float = 0.0) -> bool:
        """在窗口内滚动鼠标滚轮"""
        if not self.is_active:
            return False

        try:
            if x is not None and y is not None:
                if not self.move_to(x, y, duration=duration):
                    return False
                time.sleep(0.05)

            pyautogui.scroll(clicks)
            return True
        except Exception as e:
            print(f"滚动失败: {e}")
            return False

    def drag_to(self, start_x: int, start_y: int, end_x: int, end_y: int,
                duration: float = 0.5, button: str = 'left') -> bool:
        """在窗口内拖拽"""
        if not self.is_active:
            return False

        try:
            self._ensure_window_active()

            start_global_x, start_global_y = self._local_to_global(start_x, start_y)
            end_global_x, end_global_y = self._local_to_global(end_x, end_y)

            pyautogui.moveTo(start_global_x, start_global_y)
            time.sleep(0.05)

            pyautogui.mouseDown(button=button)
            time.sleep(0.1)

            pyautogui.moveTo(end_global_x, end_global_y, duration=duration)
            time.sleep(0.05)

            pyautogui.mouseUp(button=button)

            return True
        except Exception as e:
            print(f"拖拽失败: {e}")
            return False

    def typewrite(self, text: str, interval: float = 0.1,
                  activate_window: bool = True, use_clipboard: bool = None) -> bool:
        """
        在窗口内输入文本（支持中文）

        Args:
            text: 要输入的文本
            interval: 按键间隔时间（秒）
            activate_window: 是否先激活窗口
            use_clipboard: 是否使用剪切板粘贴方式输入中文，None表示自动检测

        Returns:
            bool: 输入是否成功
        """
        if not self.is_active:
            return False

        try:
            if activate_window:
                self._ensure_window_active()

            # 自动检测是否需要使用剪切板
            if use_clipboard is None:
                # 如果文本包含中文字符，使用剪切板方式
                use_clipboard = any(ord(char) > 127 for char in text)

            if use_clipboard:
                # 使用剪切板粘贴方式输入（支持中文）
                return self._input_via_clipboard(text, interval)
            else:
                # 使用传统键盘输入方式
                pyautogui.typewrite(text, interval=interval)
                return True

        except Exception as e:
            print(f"输入文本失败: {e}")
            return False

    def _input_via_clipboard(self, text: str, interval: float = 0.1) -> bool:
        """
        通过剪切板粘贴的方式输入文本（支持中文）

        Args:
            text: 要输入的文本
            interval: 操作间隔时间

        Returns:
            bool: 输入是否成功
        """
        try:
            # 保存当前剪切板内容
            original_clipboard = pyperclip.paste()

            # 将文本复制到剪切板
            pyperclip.copy(text)

            # 清空输入框（可选）
            # pyautogui.hotkey('ctrl', 'a', interval=0.1)
            # time.sleep(0.1)

            # 粘贴文本
            pyautogui.hotkey('ctrl', 'v', interval=interval)

            # 恢复原始剪切板内容（可选）
            # pyperclip.copy(original_clipboard)

            return True

        except Exception as e:
            print(f"剪切板输入失败: {e}")
            return False

    def typewrite_chinese(self, text: str, interval: float = 0.1,
                         activate_window: bool = True) -> bool:
        """
        专门用于中文输入的方法（强制使用剪切板方式）

        Args:
            text: 要输入的中文文本
            interval: 操作间隔时间
            activate_window: 是否先激活窗口

        Returns:
            bool: 输入是否成功
        """
        return self.typewrite(text, interval, activate_window, use_clipboard=True)

    def press_key(self, key: str, presses: int = 1, interval: float = 0.1,
                  activate_window: bool = True) -> bool:
        """按下键盘按键"""
        if not self.is_active:
            return False

        try:
            if activate_window:
                self._ensure_window_active()

            pyautogui.press(key, presses=presses, interval=interval)
            return True
        except Exception as e:
            print(f"按下按键失败: {e}")
            return False

    def hotkey(self, *keys: str, activate_window: bool = True) -> bool:
        """按下组合键"""
        if not self.is_active:
            return False

        try:
            if activate_window:
                self._ensure_window_active()

            pyautogui.hotkey(*keys)
            return True
        except Exception as e:
            print(f"按下组合键失败: {e}")
            return False

    def get_window_size(self) -> Optional[Tuple[int, int]]:
        """获取窗口大小"""
        if not self.window_rect:
            self._update_window_rect()

        if not self.window_rect:
            return None

        left, top, right, bottom = self.window_rect
        return (right - left, bottom - top)

    def get_current_mouse_position(self) -> Optional[Tuple[int, int]]:
        """获取当前鼠标在窗口内的位置"""
        if not self.window_rect:
            self._update_window_rect()

        if not self.window_rect:
            return None

        global_x, global_y = pyautogui.position()
        left, top, right, bottom = self.window_rect

        if left <= global_x <= right and top <= global_y <= bottom:
            local_x = global_x - left
            local_y = global_y - top
            return (local_x, local_y)

        return None

    def is_mouse_in_window(self) -> bool:
        """检查鼠标是否在窗口内"""
        return self.get_current_mouse_position() is not None

    def screenshot(self, region: Optional[Tuple[int, int, int, int]] = None,
                   save_path: Optional[str] = None) -> Optional:
        """对窗口区域进行截图"""
        if not self.is_active:
            return None

        try:
            self._ensure_window_active()

            left, top, right, bottom = self.window_rect
            window_region = (left, top, right - left, bottom - top)

            if region:
                reg_x, reg_y, reg_width, reg_height = region
                global_x = left + reg_x
                global_y = top + reg_y
                screenshot_region = (global_x, global_y, reg_width, reg_height)
            else:
                screenshot_region = window_region

            screenshot = pyautogui.screenshot(region=screenshot_region)

            if save_path:
                screenshot.save(save_path)

            return screenshot
        except Exception as e:
            print(f"截图失败: {e}")
            return None

    def unbind(self) -> None:
        """解绑窗口"""
        # 取消置顶
        if self.window_handle:
            try:
                self.set_always_on_top(False)
            except:
                pass

        self.window_handle = None
        self.window_title = None
        self.window_rect = None
        self.is_active = False
        self.original_style = None
    
    def enable_element_locate(self) -> 'ElementLocator':
        """
        启用元素定位功能
        
        Returns:
            ElementLocator: 元素定位器实例
            
        Usage:
            # 启用元素定位
            controller = WindowAutoController(window_title="记事本")
            locator = controller.enable_element_locate()
            
            # 扫描控件
            elements = locator._scan_window_elements()
            
            # 通过文本查找按钮
            button = locator.find_element_by_text("Button", "确定")
            if button:
                locator.click_element(button)
        """
        try:
            from element_locator import ElementLocator
            
            # 创建元素定位器
            locator = ElementLocator()
            locator.controller = self
            
            # 立即扫描控件（如果窗口已绑定）
            if self.is_active:
                locator.current_elements = locator._scan_window_elements()
            
            return locator
            
        except ImportError as e:
            raise ImportError(f"无法导入元素定位器: {e}")
        except Exception as e:
            raise Exception(f"启用元素定位失败: {e}")
    
    def find_element_by_text(self, class_name: str, text: str, 
                           use_cache: bool = True) -> Optional['ControlElement']:
        """
        通过类名和文本查找控件元素
        
        Args:
            class_name: 控件类名
            text: 控件文本
            use_cache: 是否使用缓存的扫描结果
            
        Returns:
            ControlElement: 匹配的控件元素，None表示未找到
        """
        try:
            if not hasattr(self, '_element_cache') or not use_cache:
                # 创建临时定位器并扫描
                locator = self.enable_element_locate()
                locator.current_elements = locator._scan_window_elements()
                self._element_cache = locator.current_elements
            
            # 在缓存中查找
            for element in self._element_cache:
                if element.class_name == class_name and element.text == text:
                    return element
            
            return None
            
        except Exception as e:
            print(f"查找控件失败: {e}")
            return None
    
    def find_element_by_class(self, class_name: str, index: int = 0, 
                            use_cache: bool = True) -> Optional['ControlElement']:
        """
        通过类名查找控件元素
        
        Args:
            class_name: 控件类名
            index: 返回第index个匹配的控件（从0开始）
            use_cache: 是否使用缓存的扫描结果
            
        Returns:
            ControlElement: 匹配的控件元素，None表示未找到
        """
        try:
            if not hasattr(self, '_element_cache') or not use_cache:
                # 创建临时定位器并扫描
                locator = self.enable_element_locate()
                locator.current_elements = locator._scan_window_elements()
                self._element_cache = locator.current_elements
            
            # 查找匹配的控件
            matching_elements = [e for e in self._element_cache if e.class_name == class_name]
            
            return matching_elements[index] if index < len(matching_elements) else None
            
        except Exception as e:
            print(f"查找控件失败: {e}")
            return None
    
    def find_element_by_handle(self, handle: int, 
                             use_cache: bool = True) -> Optional['ControlElement']:
        """
        通过句柄查找控件元素
        
        Args:
            handle: 控件句柄
            use_cache: 是否使用缓存的扫描结果
            
        Returns:
            ControlElement: 匹配的控件元素，None表示未找到
        """
        try:
            if not hasattr(self, '_element_cache') or not use_cache:
                # 创建临时定位器并扫描
                locator = self.enable_element_locate()
                locator.current_elements = locator._scan_window_elements()
                self._element_cache = locator.current_elements
            
            # 在缓存中查找
            for element in self._element_cache:
                if element.handle == handle:
                    return element
            
            return None
            
        except Exception as e:
            print(f"查找控件失败: {e}")
            return None
    
    def click_element_by_text(self, class_name: str, text: str, 
                            button: str = 'left') -> bool:
        """
        通过类名和文本点击控件
        
        Args:
            class_name: 控件类名
            text: 控件文本
            button: 鼠标按钮
            
        Returns:
            bool: 点击是否成功
        """
        try:
            element = self.find_element_by_text(class_name, text)
            if element:
                # 计算相对于窗口的坐标
                local_x = element.center_x - self.window_rect[0]
                local_y = element.center_y - self.window_rect[1]
                
                return self.click(local_x, local_y, button=button)
            
            return False
            
        except Exception as e:
            print(f"点击控件失败: {e}")
            return False
    
    def click_element_by_class(self, class_name: str, index: int = 0, 
                             button: str = 'left') -> bool:
        """
        通过类名点击控件
        
        Args:
            class_name: 控件类名
            index: 第index个匹配的控件（从0开始）
            button: 鼠标按钮
            
        Returns:
            bool: 点击是否成功
        """
        try:
            element = self.find_element_by_class(class_name, index)
            if element:
                # 计算相对于窗口的坐标
                local_x = element.center_x - self.window_rect[0]
                local_y = element.center_y - self.window_rect[1]
                
                return self.click(local_x, local_y, button=button)
            
            return False
            
        except Exception as e:
            print(f"点击控件失败: {e}")
            return False
    
    def input_text_to_element(self, class_name: str, text: str, 
                            target_text: str = "", interval: float = 0.1) -> bool:
        """
        向指定控件输入文本
        
        Args:
            class_name: 控件类名
            text: 要输入的文本
            target_text: 控件的文本（用于定位），空字符串表示第一个匹配的
            interval: 输入间隔
            
        Returns:
            bool: 输入是否成功
        """
        try:
            # 查找控件
            if target_text:
                element = self.find_element_by_text(class_name, target_text)
            else:
                element = self.find_element_by_class(class_name, 0)
            
            if element:
                # 移动到控件位置并点击
                local_x = element.center_x - self.window_rect[0]
                local_y = element.center_y - self.window_rect[1]
                
                self.move_to(local_x, local_y)
                time.sleep(0.1)
                self.click()
                time.sleep(0.1)
                
                # 输入文本
                return self.typewrite(text, interval=interval)
            
            return False
            
        except Exception as e:
            print(f"输入文本失败: {e}")
            return False
    
    def get_all_elements(self, use_cache: bool = True) -> List:
        """
        获取窗口中的所有控件元素
        
        Args:
            use_cache: 是否使用缓存的扫描结果
            
        Returns:
            List: 控件元素列表
        """
        try:
            if not hasattr(self, '_element_cache') or not use_cache:
                # 创建临时定位器并扫描
                locator = self.enable_element_locate()
                locator.current_elements = locator._scan_window_elements()
                self._element_cache = locator.current_elements
            
            return self._element_cache
            
        except Exception as e:
            print(f"获取控件列表失败: {e}")
            return []
    
    def clear_element_cache(self):
        """清除控件缓存"""
        if hasattr(self, '_element_cache'):
            delattr(self, '_element_cache')


# 使用示例
if __name__ == "__main__":
    import time
    print("=== 窗口自动化控制器测试 ===\n")

    # 示例1: 绑定窗口并自动置顶（默认行为）
    print("1. 绑定窗口并自动置顶:")
    controller1 = WindowAutoController(window_handle=3608176, always_on_top=True)

    if controller1.is_active:
        print(f"  已绑定窗口: {controller1.window_title}")
        print(f"  是否置顶: {controller1.is_always_on_top()}")

        controller1.click(286,178, button='left', duration=2)

        # 演示中文输入功能
        print("\n  测试中文输入功能:")
        



        # 鼠标移动到输入框
        controller1.move_to(565,751, duration=1)
        time.sleep(1)
        controller1.click()
        time.sleep(1)

        # 方法1: 自动检测中文并使用剪切板
        print("  - 自动检测中文输入:")
        controller1.typewrite("你好，DeepSeek！这是一个中文测试。", interval=0.2)
        # 鼠标移动到发送按钮
        controller1.move_to(957,861, duration=1)
        time.sleep(1)
        # 按下键盘回车
        controller1.press_key("enter")

    print("\n" + "=" * 50 + "\n")
    # 自动取消置顶
    print("2. 自动取消置顶:")
    controller1.unbind()


