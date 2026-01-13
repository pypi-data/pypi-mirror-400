import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import win32gui
import win32con
import win32api
import pygetwindow as gw
from ctypes import windll, byref, c_int
import pyperclip
from pynput import keyboard
from pynput.keyboard import Key, Listener


class WindowTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("窗口鼠标坐标追踪器")
        self.root.geometry("500x400")

        # 绑定状态
        self.is_bound = False
        self.bound_window = None
        self.bound_window_title = ""
        self.tracking_thread = None
        self.stop_tracking = False
        
        # 窗口列表数据
        self.windows_data = []  # 存储 (hwnd, title) 对

        # 复制功能相关
        self.copy_history = []  # 存储复制历史 [x, y]
        self.keyboard_listener = None  # 键盘监听器
        self.copy_status = "等待复制..."  # 复制状态显示

        # 调试信息
        self.debug_mode = True  # 设置为True可以显示调试信息

        # 设置样式
        self.setup_styles()

        # 创建UI
        self.create_widgets()

        # 确保程序关闭时清理资源
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 启动键盘监听器
        self.start_keyboard_listener()

        # 启动界面刷新
        self.root.after(100, self.check_thread_status)

    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')

    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(
            main_frame,
            text="窗口鼠标坐标追踪器",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))

        # 窗口列表框架
        list_frame = ttk.LabelFrame(main_frame, text="选择窗口", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 窗口列表和滚动条
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.window_listbox = tk.Listbox(
            list_container,
            height=8,
            font=("Courier New", 9),
            yscrollcommand=scrollbar.set
        )
        self.window_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.window_listbox.yview)

        # 窗口操作按钮
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        refresh_btn = ttk.Button(
            button_frame,
            text="刷新窗口列表",
            command=self.refresh_window_list,
            width=15
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.bind_btn = ttk.Button(
            button_frame,
            text="绑定选中窗口",
            command=self.bind_window,
            width=15
        )
        self.bind_btn.pack(side=tk.LEFT)

        # 状态显示框架
        status_frame = ttk.LabelFrame(main_frame, text="状态信息", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))

        # 绑定状态
        self.status_label = ttk.Label(
            status_frame,
            text="状态: 未绑定",
            font=("Arial", 10)
        )
        self.status_label.pack(anchor=tk.W, pady=(0, 5))

        # 窗口信息
        self.window_info_label = ttk.Label(
            status_frame,
            text="窗口: 无",
            font=("Arial", 9)
        )
        self.window_info_label.pack(anchor=tk.W, pady=(0, 5))

        # 窗口句柄信息
        self.handle_info_label = ttk.Label(
            status_frame,
            text="句柄: 无",
            font=("Arial", 9)
        )
        self.handle_info_label.pack(anchor=tk.W, pady=(0, 10))

        # 坐标显示区域（使用更大的字体和更明显的颜色）
        coord_frame = ttk.Frame(status_frame)
        coord_frame.pack(fill=tk.X)

        self.coord_label = tk.Label(
            coord_frame,
            text="坐标: ---",
            font=("Arial", 12, "bold"),
            fg="blue",
            bg="white",
            relief=tk.SUNKEN,
            width=40,
            height=2
        )
        self.coord_label.pack(fill=tk.X, pady=5)

        # 复制状态和历史显示区域
        copy_frame = ttk.LabelFrame(status_frame, text="复制功能 (按C键复制当前坐标)", padding="5")
        copy_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # 复制状态显示
        self.copy_status_label = ttk.Label(
            copy_frame,
            text="复制状态: 等待复制...",
            font=("Arial", 9)
        )
        self.copy_status_label.pack(anchor=tk.W, pady=(0, 5))

        # 复制历史列表
        history_container = ttk.Frame(copy_frame)
        history_container.pack(fill=tk.BOTH, expand=True)

        # 复制历史滚动区域
        history_scrollbar = ttk.Scrollbar(history_container)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.copy_history_text = tk.Text(
            history_container,
            height=6,
            font=("Courier New", 9),
            yscrollcommand=history_scrollbar.set,
            state=tk.DISABLED,
            bg="#f5f5f5",
            fg="#333333"
        )
        self.copy_history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scrollbar.config(command=self.copy_history_text.yview)

        # 复制历史按钮
        copy_button_frame = ttk.Frame(copy_frame)
        copy_button_frame.pack(fill=tk.X, pady=(5, 0))

        self.clear_history_btn = ttk.Button(
            copy_button_frame,
            text="清空历史",
            command=self.clear_copy_history,
            width=12
        )
        self.clear_history_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.copy_now_btn = ttk.Button(
            copy_button_frame,
            text="复制全部坐标",
            command=self.copy_all_coordinates,
            width=15
        )
        self.copy_now_btn.pack(side=tk.LEFT)

        # 调试信息（如果启用）
        if self.debug_mode:
            self.debug_label = ttk.Label(
                status_frame,
                text="调试信息: 等待...",
                font=("Arial", 8),
                foreground="gray"
            )
            self.debug_label.pack(anchor=tk.W, pady=(5, 0))

        # 控制按钮框架
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X)

        self.unbind_btn = ttk.Button(
            control_frame,
            text="解绑窗口",
            command=self.unbind_window,
            state=tk.DISABLED,
            width=15
        )
        self.unbind_btn.pack(side=tk.LEFT, padx=(0, 10))

        test_btn = ttk.Button(
            control_frame,
            text="测试坐标获取",
            command=self.test_coordinate_getting,
            width=15
        )
        test_btn.pack(side=tk.LEFT)

        # 初始刷新窗口列表
        self.refresh_window_list()

        # 绑定双击事件
        self.window_listbox.bind('<Double-Button-1>', lambda e: self.bind_window())

    def refresh_window_list(self):
        """刷新窗口列表"""
        try:
            # 清空列表
            self.window_listbox.delete(0, tk.END)

            # 存储窗口信息用于选择
            self.windows_data = []  # 存储 (hwnd, title) 对

            # 获取所有窗口
            def enum_windows_callback(hwnd, windows):
                try:
                    title = win32gui.GetWindowText(hwnd)
                    if title and title.strip() and win32gui.IsWindowVisible(hwnd):
                        windows.append((hwnd, title))
                except:
                    pass
                return True

            # 使用EnumWindows获取更准确的窗口列表
            win32gui.EnumWindows(enum_windows_callback, self.windows_data)

            # 添加窗口到列表（显示标题和句柄）
            count = 0
            for hwnd, title in self.windows_data:
                # 限制标题长度并添加句柄信息
                display_text = f"{title[:70]} [句柄: {hwnd}]"
                self.window_listbox.insert(tk.END, display_text)
                count += 1

            if count == 0:
                self.window_listbox.insert(tk.END, "未找到任何窗口")

            if self.debug_mode:
                self.update_debug_info(f"找到 {count} 个窗口")

        except Exception as e:
            messagebox.showerror("错误", f"获取窗口列表失败: {str(e)}")

    def bind_window(self):
        """绑定选中的窗口"""
        try:
            # 获取选中窗口
            selection = self.window_listbox.curselection()
            if not selection:
                messagebox.showwarning("提示", "请先选择一个窗口")
                return

            # 检查是否有窗口数据
            if not hasattr(self, 'windows_data') or not self.windows_data:
                messagebox.showerror("错误", "窗口列表为空，请先刷新窗口列表")
                return

            # 获取选中的窗口索引
            selected_index = selection[0]
            if selected_index >= len(self.windows_data):
                messagebox.showerror("错误", "选中的窗口索引无效")
                return

            # 直接使用之前存储的窗口数据
            self.bound_window, self.bound_window_title = self.windows_data[selected_index]

            # 验证窗口句柄
            if not win32gui.IsWindow(self.bound_window):
                messagebox.showerror("错误", "无效的窗口句柄")
                return

            self.is_bound = True

            # 更新界面
            self.status_label.config(text="状态: 已绑定", foreground="green")
            self.window_info_label.config(text=f"窗口: {self.bound_window_title[:60]}")
            self.handle_info_label.config(text=f"句柄: {self.bound_window}")
            self.bind_btn.config(state=tk.DISABLED)
            self.unbind_btn.config(state=tk.NORMAL)
            self.coord_label.config(text="坐标: 等待鼠标进入窗口...", fg="orange")

            # 将窗口提到前台
            self.bring_window_to_front()

            # 启动追踪线程
            self.stop_tracking = False
            self.tracking_thread = threading.Thread(target=self.track_coordinates, daemon=True)
            self.tracking_thread.start()

            if self.debug_mode:
                self.update_debug_info(f"已绑定窗口: {self.bound_window_title} (句柄: {self.bound_window})")

            messagebox.showinfo("成功", f"已绑定窗口: {self.bound_window_title}\n窗口句柄: {self.bound_window}\n现在可以移动鼠标到该窗口查看坐标。")

        except Exception as e:
            messagebox.showerror("错误", f"绑定窗口失败: {str(e)}")
            if self.debug_mode:
                self.update_debug_info(f"绑定错误: {str(e)}")

    def bring_window_to_front(self):
        """将绑定的窗口提到前台"""
        try:
            if self.bound_window:
                # 恢复窗口（如果最小化）
                if win32gui.IsIconic(self.bound_window):
                    win32gui.ShowWindow(self.bound_window, win32con.SW_RESTORE)

                # 将窗口置顶
                win32gui.SetForegroundWindow(self.bound_window)
                win32gui.BringWindowToTop(self.bound_window)

                # 确保窗口是激活状态
                win32gui.SetActiveWindow(self.bound_window)

        except Exception as e:
            if self.debug_mode:
                self.update_debug_info(f"置顶错误: {e}")

    def track_coordinates(self):
        """追踪鼠标在绑定窗口内的坐标"""
        last_coords = None

        while not self.stop_tracking and self.is_bound:
            try:
                # 检查窗口是否仍然存在
                if not self.bound_window or not win32gui.IsWindow(self.bound_window):
                    self.root.after(0, self.window_lost)
                    break

                # 获取鼠标全局坐标
                cursor_pos = win32api.GetCursorPos()
                global_x, global_y = cursor_pos

                # 获取窗口位置和大小
                try:
                    rect = win32gui.GetWindowRect(self.bound_window)
                    if not rect:
                        continue

                    window_left, window_top, window_right, window_bottom = rect

                    # 检查鼠标是否在窗口内
                    if (window_left <= global_x <= window_right and
                            window_top <= global_y <= window_bottom):

                        # 计算相对于窗口的坐标
                        local_x = global_x - window_left
                        local_y = global_y - window_top

                        # 只在新坐标时更新显示
                        if last_coords != (local_x, local_y):
                            last_coords = (local_x, local_y)
                            self.root.after(0, self.update_coord_display,
                                            local_x, local_y, global_x, global_y)

                            if self.debug_mode:
                                self.root.after(0, self.update_debug_info,
                                                f"窗口内: ({local_x}, {local_y}) 窗口位置: {rect}")
                    else:
                        # 鼠标在窗口外
                        if last_coords != "outside":
                            last_coords = "outside"
                            self.root.after(0, self.update_coord_outside)

                except Exception as e:
                    if self.debug_mode:
                        self.root.after(0, self.update_debug_info, f"获取窗口位置错误: {e}")

                time.sleep(0.02)  # 降低刷新频率为50Hz

            except Exception as e:
                if self.debug_mode:
                    self.root.after(0, self.update_debug_info, f"追踪错误: {e}")
                time.sleep(0.1)

    def update_coord_display(self, local_x, local_y, global_x, global_y):
        """更新坐标显示"""
        try:
            # 更新坐标标签
            coord_text = f"窗口坐标: ({local_x}, {local_y}) | 全局坐标: ({global_x}, {global_y})"
            self.coord_label.config(
                text=coord_text,
                fg="green",
                bg="#f0fff0"  # 浅绿色背景
            )

            # 强制更新界面
            self.coord_label.update()

        except Exception as e:
            if self.debug_mode:
                self.update_debug_info(f"更新坐标显示错误: {e}")

    def update_coord_outside(self):
        """更新鼠标在窗口外的显示"""
        try:
            self.coord_label.config(
                text="鼠标在窗口外",
                fg="red",
                bg="#fff0f0"  # 浅红色背景
            )
            self.coord_label.update()
        except:
            pass

    def window_lost(self):
        """窗口丢失时的处理"""
        self.is_bound = False
        self.status_label.config(text="状态: 窗口已关闭", foreground="red")
        self.coord_label.config(text="窗口已关闭，无法获取坐标", fg="red")
        self.unbind_window()

    def update_debug_info(self, message):
        """更新调试信息"""
        if hasattr(self, 'debug_label'):
            self.debug_label.config(text=f"调试信息: {message}")

    def unbind_window(self):
        """解绑窗口"""
        self.is_bound = False
        self.stop_tracking = True

        # 等待追踪线程结束
        if self.tracking_thread and self.tracking_thread.is_alive():
            for i in range(10):  # 最多等待0.5秒
                if not self.tracking_thread.is_alive():
                    break
                time.sleep(0.05)

        self.bound_window = None
        self.bound_window_title = ""

        # 更新界面
        self.status_label.config(text="状态: 未绑定", foreground="black")
        self.window_info_label.config(text="窗口: 无")
        self.handle_info_label.config(text="句柄: 无")
        self.coord_label.config(text="坐标: ---", fg="blue", bg="white")
        self.bind_btn.config(state=tk.NORMAL)
        self.unbind_btn.config(state=tk.DISABLED)

        if self.debug_mode:
            self.update_debug_info("已解绑窗口")

    def test_coordinate_getting(self):
        """测试坐标获取功能"""
        try:
            # 获取当前鼠标位置
            cursor_pos = win32api.GetCursorPos()
            global_x, global_y = cursor_pos

            # 获取鼠标下的窗口
            hwnd = win32gui.WindowFromPoint(cursor_pos)
            title = win32gui.GetWindowText(hwnd)

            # 获取窗口位置
            if hwnd:
                rect = win32gui.GetWindowRect(hwnd)
                if rect:
                    left, top, right, bottom = rect
                    local_x = global_x - left
                    local_y = global_y - top

                    test_result = f"""
测试结果：
全局坐标: ({global_x}, {global_y})
当前窗口: {title[:50]}
窗口句柄: {hwnd}
窗口位置: ({left}, {top}, {right}, {bottom})
窗口内坐标: ({local_x}, {local_y})
鼠标在窗口内: {left <= global_x <= right and top <= global_y <= bottom}
"""
                    messagebox.showinfo("坐标测试", test_result)
                else:
                    messagebox.showwarning("测试", "无法获取窗口位置")
            else:
                messagebox.showwarning("测试", "无法获取当前窗口")

        except Exception as e:
            messagebox.showerror("测试错误", f"测试失败: {str(e)}")

    def check_thread_status(self):
        """定期检查线程状态"""
        if self.is_bound and (not self.tracking_thread or not self.tracking_thread.is_alive()):
            if self.debug_mode:
                self.update_debug_info("追踪线程已停止，重新启动...")
            # 重新启动追踪线程
            if self.is_bound and not self.stop_tracking:
                self.tracking_thread = threading.Thread(target=self.track_coordinates, daemon=True)
                self.tracking_thread.start()

        # 定期检查
        self.root.after(1000, self.check_thread_status)

    def on_closing(self):
        """程序关闭时的清理"""
        self.unbind_window()
        # 停止键盘监听器
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        self.root.destroy()

    def start_keyboard_listener(self):
        """启动键盘监听器"""
        try:
            def on_press(key):
                try:
                    # 检查是否按下了C键
                    if hasattr(key, 'char') and key.char and key.char.lower() == 'c':
                        # 在主线程中执行复制操作
                        self.root.after(0, self.copy_current_coordinates)
                except AttributeError:
                    # 特殊键的处理
                    pass

            # 启动键盘监听器
            self.keyboard_listener = Listener(on_press=on_press)
            self.keyboard_listener.start()
            
            if self.debug_mode:
                self.update_debug_info("键盘监听器已启动")

        except Exception as e:
            if self.debug_mode:
                self.update_debug_info(f"启动键盘监听器失败: {e}")

    def copy_current_coordinates(self):
        """复制当前坐标到剪贴板"""
        try:
            # 获取当前鼠标位置
            cursor_pos = win32api.GetCursorPos()
            global_x, global_y = cursor_pos

            # 获取当前窗口信息
            hwnd = win32gui.WindowFromPoint(cursor_pos)
            title = win32gui.GetWindowText(hwnd)

            if hwnd and self.bound_window and hwnd == self.bound_window:
                # 计算相对于绑定窗口的坐标
                rect = win32gui.GetWindowRect(self.bound_window)
                if rect:
                    left, top, right, bottom = rect
                    local_x = global_x - left
                    local_y = global_y - top
                    
                    # 添加到复制历史
                    coord_pair = [local_x, local_y]
                    self.copy_history.append(coord_pair)
                    
                    # 格式化坐标文本
                    coord_text = f"[{local_x},{local_y}]"
                    
                    # 复制到剪贴板
                    pyperclip.copy(coord_text)
                    
                    # 更新显示
                    self.update_copy_display(f"已复制: {coord_text}")
                    
                    if self.debug_mode:
                        self.update_debug_info(f"复制坐标: {coord_text}")
                        
                    return True
                else:
                    self.update_copy_display("错误: 无法获取窗口位置")
                    return False
            else:
                self.update_copy_display("错误: 鼠标不在绑定窗口内")
                return False

        except Exception as e:
            error_msg = f"复制失败: {str(e)}"
            self.update_copy_display(error_msg)
            if self.debug_mode:
                self.update_debug_info(error_msg)
            return False

    def update_copy_display(self, message):
        """更新复制状态显示"""
        try:
            self.copy_status_label.config(text=f"复制状态: {message}")
            
            # 更新复制历史显示
            self.update_copy_history_display()
            
        except Exception as e:
            if self.debug_mode:
                self.update_debug_info(f"更新复制显示错误: {e}")

    def update_copy_history_display(self):
        """更新复制历史显示"""
        try:
            # 启用文本控件
            self.copy_history_text.config(state=tk.NORMAL)
            
            # 清空现有内容
            self.copy_history_text.delete(1.0, tk.END)
            
            # 显示复制历史
            if self.copy_history:
                for i, coord in enumerate(self.copy_history):
                    coord_text = f"[{coord[0]},{coord[1]}]"
                    if i == len(self.copy_history) - 1:
                        # 最后一项用特殊颜色标记
                        self.copy_history_text.insert(tk.END, f"▶ {coord_text}\n")
                    else:
                        self.copy_history_text.insert(tk.END, f"  {coord_text}\n")
            else:
                self.copy_history_text.insert(tk.END, "暂无复制历史\n")
            
            # 滚动到底部
            self.copy_history_text.see(tk.END)
            
            # 禁用文本控件（防止编辑）
            self.copy_history_text.config(state=tk.DISABLED)
            
        except Exception as e:
            if self.debug_mode:
                self.update_debug_info(f"更新复制历史错误: {e}")

    def clear_copy_history(self):
        """清空复制历史"""
        try:
            self.copy_history.clear()
            self.update_copy_display("历史已清空")
            if self.debug_mode:
                self.update_debug_info("复制历史已清空")
        except Exception as e:
            if self.debug_mode:
                self.update_debug_info(f"清空历史错误: {e}")

    def copy_all_coordinates(self):
        """复制所有坐标到剪贴板（包含换行符）"""
        try:
            if not self.copy_history:
                self.update_copy_display("没有可复制的坐标历史")
                return False

            # 构建包含换行符的坐标文本
            coord_lines = []
            for coord in self.copy_history:
                coord_text = f"[{coord[0]},{coord[1]}]"
                coord_lines.append(coord_text)

            # 用换行符连接所有坐标
            all_coordinates_text = "\n".join(coord_lines)

            # 复制到剪贴板
            pyperclip.copy(all_coordinates_text)

            # 更新显示
            self.update_copy_display(f"已复制 {len(self.copy_history)} 个坐标到剪贴板")

            if self.debug_mode:
                self.update_debug_info(f"复制全部坐标: {len(self.copy_history)} 个")

            return True

        except Exception as e:
            error_msg = f"复制全部坐标失败: {str(e)}"
            self.update_copy_display(error_msg)
            if self.debug_mode:
                self.update_debug_info(error_msg)
            return False


def main():
    # 创建主窗口
    root = tk.Tk()

    # 设置DPI感知
    try:
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    # 创建应用
    app = WindowTrackerApp(root)

    # 运行主循环
    root.mainloop()


if __name__ == "__main__":
    # 检查依赖库是否安装
    try:
        main()
    except ImportError as e:
        print(f"缺少必要的库: {e}")
        print("请安装以下库：")
        print("pip install pywin32")
        print("pip install pygetwindow")
        print("pip install pyperclip")
        print("pip install pynput")
        input("按回车键退出...")