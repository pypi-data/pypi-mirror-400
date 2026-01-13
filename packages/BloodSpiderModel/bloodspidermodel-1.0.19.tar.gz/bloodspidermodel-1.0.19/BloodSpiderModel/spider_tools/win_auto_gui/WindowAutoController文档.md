# WindowAutoController 窗口自动化控制器文档

**作者**: BS  
**微信**: duyanbz  
**版本**: 1.0  
**更新时间**: 2026-01-05


## 概述

`WindowAutoController` 是一个Python类，用于对指定窗口进行自动化操作。所有鼠标坐标都是相对于绑定窗口的本地坐标，而不是整个屏幕的全局坐标。支持窗口置顶、鼠标操作、键盘输入等功能。

## 依赖库

```bash
pip install pyautogui
pip install pywin32
pip install pyperclip
```

**依赖说明：**
- `pyautogui`: 自动化操作库
- `pywin32`: Windows API调用库  
- `pyperclip`: 剪切板操作库（用于支持中文输入）

## 类初始化

### 构造函数

```python
WindowAutoController(window_handle=None, window_title=None, always_on_top=True)
```

**参数：**
- `window_handle` (int, optional): Windows窗口句柄
- `window_title` (str, optional): 窗口标题（用于查找窗口）
- `always_on_top` (bool): 是否在绑定后自动将窗口置顶，默认`True`

**说明：**
- 至少需要提供 `window_handle` 或 `window_title` 中的一个
- 如果提供 `window_title`，会查找匹配的可见窗口
- `always_on_top=True` 时，绑定后窗口会自动置顶显示在所有窗口之上

## 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `window_handle` | int | 绑定的窗口句柄 |
| `window_title` | str | 窗口标题 |
| `window_rect` | tuple | 窗口位置和大小 `(left, top, right, bottom)` |
| `is_active` | bool | 控制器是否已激活（窗口是否成功绑定） |
| `always_on_top` | bool | 是否自动置顶的配置 |
| `original_style` | int | 原始窗口样式（用于恢复） |

## 窗口绑定与状态管理

### 1. `bind_by_handle(window_handle)`
通过窗口句柄绑定窗口

**参数：**
- `window_handle` (int): Windows窗口句柄

**返回：**
- `bool`: 绑定是否成功

**示例：**
```python
controller = WindowAutoController()
success = controller.bind_by_handle(123456)
```

### 2. `bind_by_title(window_title, exact_match=True)`
通过窗口标题绑定窗口

**参数：**
- `window_title` (str): 窗口标题
- `exact_match` (bool): 是否精确匹配标题，默认`True`

**返回：**
- `bool`: 绑定是否成功

**示例：**
```python
controller = WindowAutoController()
# 精确匹配
success = controller.bind_by_title("记事本", exact_match=True)
# 模糊匹配（包含指定文本）
success = controller.bind_by_title("记事本", exact_match=False)
```

### 3. `unbind()`
解绑窗口，恢复窗口原始状态

**示例：**
```python
controller.unbind()
```

## 窗口置顶控制

### 4. `set_always_on_top(enable=True)`
设置或取消窗口全局置顶

**参数：**
- `enable` (bool): `True`置顶，`False`取消置顶

**返回：**
- `bool`: 操作是否成功

**示例：**
```python
# 置顶窗口
controller.set_always_on_top(True)

# 取消置顶
controller.set_always_on_top(False)
```

### 5. `toggle_always_on_top()`
切换窗口置顶状态

**返回：**
- `bool`: 切换后的状态（`True`为置顶）

**示例：**
```python
# 切换置顶状态
new_state = controller.toggle_always_on_top()
print(f"窗口现在{'已置顶' if new_state else '未置顶'}")
```

### 6. `is_always_on_top()`
检查窗口是否处于置顶状态

**返回：**
- `bool` or `None`: `True`为置顶，`False`为不置顶，`None`为无法判断

**示例：**
```python
if controller.is_always_on_top():
    print("窗口已置顶")
```

### 7. `bring_to_front(force_focus=True)`
将窗口提到前台

**参数：**
- `force_focus` (bool): 是否强制获取焦点，默认`True`

**返回：**
- `bool`: 操作是否成功

**示例：**
```python
# 提到前台并获取焦点
controller.bring_to_front(force_focus=True)

# 提到前台但不获取焦点
controller.bring_to_front(force_focus=False)
```

### 8. `set_window_position(x, y, width=None, height=None, keep_on_top=None)`
设置窗口位置和大小

**参数：**
- `x` (int): 窗口左上角X坐标
- `y` (int): 窗口左上角Y坐标
- `width` (int, optional): 窗口宽度，`None`表示保持原宽度
- `height` (int, optional): 窗口高度，`None`表示保持原高度
- `keep_on_top` (bool, optional): 是否保持置顶状态，`None`表示保持当前状态

**返回：**
- `bool`: 操作是否成功

**示例：**
```python
# 移动窗口到(100,100)，大小不变，保持当前置顶状态
controller.set_window_position(100, 100)

# 移动窗口并改变大小，强制取消置顶
controller.set_window_position(100, 100, 800, 600, keep_on_top=False)
```

## 鼠标操作

所有鼠标坐标都是相对于绑定窗口的本地坐标。

### 9. `move_to(x, y, duration=0.0, activate_window=True)`
移动鼠标到窗口内的指定位置

**参数：**
- `x` (int): 窗口本地X坐标
- `y` (int): 窗口本地Y坐标
- `duration` (float): 移动耗时（秒），0表示立即移动
- `activate_window` (bool): 是否先激活窗口，默认`True`

**返回：**
- `bool`: 操作是否成功

**示例：**
```python
# 立即移动到窗口内的(100, 150)位置
controller.move_to(100, 150)

# 用0.5秒时间平滑移动到指定位置
controller.move_to(200, 300, duration=0.5)
```

### 10. `click(x=None, y=None, button='left', clicks=1, interval=0.1, move_before_click=True, duration=0.0)`
在窗口内点击

**参数：**
- `x` (int, optional): 窗口本地X坐标，`None`则在当前位置点击
- `y` (int, optional): 窗口本地Y坐标，`None`则在当前位置点击
- `button` (str): 鼠标按钮，可选：`'left'`、`'right'`、`'middle'`
- `clicks` (int): 点击次数
- `interval` (float): 多次点击之间的间隔（秒）
- `move_before_click` (bool): 是否先移动到目标位置
- `duration` (float): 移动到目标位置的耗时（秒）

**返回：**
- `bool`: 操作是否成功

**示例：**
```python
# 在(100, 150)位置左键单击
controller.click(100, 150)

# 在当前位置右键单击
controller.click(button='right')

# 在(200, 250)位置双击
controller.click(200, 250, clicks=2)

# 不移动鼠标，直接在当前鼠标位置点击
controller.click(move_before_click=False)
```

### 11. `double_click(x=None, y=None, button='left', duration=0.0)`
在窗口内双击（`click`方法的快捷方式）

**示例：**
```python
# 在(100, 150)位置双击
controller.double_click(100, 150)
```

### 12. `right_click(x=None, y=None, duration=0.0)`
在窗口内右击（`click`方法的快捷方式）

**示例：**
```python
# 在(100, 150)位置右击
controller.right_click(100, 150)
```

### 13. `scroll(clicks, x=None, y=None, duration=0.0)`
在窗口内滚动鼠标滚轮

**参数：**
- `clicks` (int): 滚动次数，正数向上，负数向下
- `x` (int, optional): 窗口本地X坐标
- `y` (int, optional): 窗口本地Y坐标
- `duration` (float): 移动到目标位置的耗时（秒）

**返回：**
- `bool`: 操作是否成功

**示例：**
```python
# 在当前鼠标位置向上滚动5次
controller.scroll(5)

# 在(400, 300)位置向下滚动10次
controller.scroll(-10, 400, 300)
```

### 14. `drag_to(start_x, start_y, end_x, end_y, duration=0.5, button='left')`
在窗口内拖拽

**参数：**
- `start_x` (int): 起始位置窗口本地X坐标
- `start_y` (int): 起始位置窗口本地Y坐标
- `end_x` (int): 结束位置窗口本地X坐标
- `end_y` (int): 结束位置窗口本地Y坐标
- `duration` (float): 拖拽耗时（秒）
- `button` (str): 鼠标按钮

**返回：**
- `bool`: 操作是否成功

**示例：**
```python
# 从(50, 50)拖拽到(200, 200)
controller.drag_to(50, 50, 200, 200, duration=0.5)
```

## 键盘操作

### 15. `typewrite(text, interval=0.1, activate_window=True, use_clipboard=None)`
在窗口内输入文本（支持中文）

**参数：**
- `text` (str): 要输入的文本
- `interval` (float): 按键间隔（秒）
- `activate_window` (bool): 是否先激活窗口，默认`True`
- `use_clipboard` (bool, optional): 是否使用剪切板粘贴方式输入中文，None表示自动检测

**返回：**
- `bool`: 操作是否成功

**功能说明：**
- **自动检测中文**：如果文本包含中文字符（Unicode码>127），会自动使用剪切板粘贴方式
- **英文优化**：纯英文文本使用传统的键盘输入方式，速度更快
- **中文支持**：通过剪切板粘贴完美支持中文字符输入

**示例：**
```python
# 自动检测并输入中英文混合文本
controller.typewrite("Hello 世界！这是测试文本。")

# 强制使用剪切板方式（适用于纯中文）
controller.typewrite("你好世界！", use_clipboard=True)

# 纯英文文本（使用快速键盘输入）
controller.typewrite("Hello World!", use_clipboard=False)

# 快速输入英文
controller.typewrite("Fast typing", interval=0.05)

# 混合文本自动选择最佳方式
controller.typewrite("中英混合123ABC文本测试")
```

### 16. `typewrite_chinese(text, interval=0.1, activate_window=True)`
专门用于中文输入的方法（强制使用剪切板方式）

**参数：**
- `text` (str): 要输入的中文文本
- `interval` (float): 操作间隔时间
- `activate_window` (bool): 是否先激活窗口，默认`True`

**返回：**
- `bool`: 输入是否成功

**功能说明：**
- **强制剪切板方式**：无论什么文本都使用剪切板粘贴方式
- **中文优化**：专门针对中文输入优化，确保中文显示正确
- **兼容性**：对各种中文字符都支持（简体中文、繁体中文、特殊字符等）

**示例：**
```python
# 专门输入中文文本
controller.typewrite_chinese("这是纯中文输入测试！")

# 输入中文并带标点符号
controller.typewrite_chinese("今天天气真不错，适合出去走走。")

# 输入中文数字混合文本
controller.typewrite_chinese("2024年是龙年，祝大家新年快乐！")

# 输入中文特殊字符
controller.typewrite_chinese("★☆※◎●○◇◆□■△▲▽▼")
```

### 17. `press_key(key, presses=1, interval=0.1, activate_window=True)`
按下键盘按键

**参数：**
- `key` (str): 按键名称（如 `'enter'`、`'tab'`、`'ctrl'`、`'a'`等）
- `presses` (int): 按键次数
- `interval` (float): 多次按键之间的间隔（秒）
- `activate_window` (bool): 是否先激活窗口，默认`True`

**返回：**
- `bool`: 操作是否成功

**示例：**
```python
# 按一次回车键
controller.press_key('enter')

# 按三次Tab键
controller.press_key('tab', presses=3)
```

### 18. `hotkey(*keys, activate_window=True)`
按下组合键

**参数：**
- `*keys` (str): 组合键序列
- `activate_window` (bool): 是否先激活窗口，默认`True`

**返回：**
- `bool`: 操作是否成功

**示例：**
```python
# 按下Ctrl+C（复制）
controller.hotkey('ctrl', 'c')

# 按下Alt+F4（关闭窗口）
controller.hotkey('alt', 'f4')
```

## 信息获取

### 19. `get_window_size()`
获取窗口大小

**返回：**
- `tuple` or `None`: `(宽度, 高度)`，失败返回`None`

**示例：**
```python
size = controller.get_window_size()
if size:
    width, height = size
    print(f"窗口大小: {width}x{height}")
```

### 20. `get_current_mouse_position()`
获取当前鼠标在窗口内的位置

**返回：**
- `tuple` or `None`: `(窗口本地X, 窗口本地Y)`，鼠标不在窗口内返回`None`

**示例：**
```python
position = controller.get_current_mouse_position()
if position:
    x, y = position
    print(f"鼠标在窗口内的位置: ({x}, {y})")
```

### 21. `is_mouse_in_window()`
检查鼠标是否在窗口内

**返回：**
- `bool`: 鼠标是否在窗口内

**示例：**
```python
if controller.is_mouse_in_window():
    print("鼠标在窗口内")
else:
    print("鼠标在窗口外")
```

## 截图功能

### 22. `screenshot(region=None, save_path=None)`
对窗口区域进行截图

**参数：**
- `region` (tuple, optional): 截图区域 `(x, y, width, height)`，相对于窗口本地坐标
- `save_path` (str, optional): 保存路径

**返回：**
- `PIL.Image` or `None`: PIL Image对象或None

**示例：**
```python
# 截取整个窗口
screenshot = controller.screenshot()
if screenshot:
    screenshot.show()

# 截取窗口的特定区域并保存
controller.screenshot(region=(50, 50, 200, 100), save_path="region.png")

# 截取整个窗口并保存
controller.screenshot(save_path="full_window.png")
```

## 中文输入专项说明

### 中文输入特点

本类对中文输入进行了深度优化，解决了传统自动化工具无法输入中文的问题：

1. **自动检测机制**：智能识别文本中的中文字符，自动选择最佳输入方式
2. **双引擎架构**：支持传统键盘输入（英文优化）和剪切板粘贴输入（中文优化）
3. **性能优化**：英文文本使用快速键盘输入，中文文本使用可靠的剪切板方式

### 中文输入方法对比

| 输入场景 | 推荐方法 | 输入速度 | 支持程度 |
|---------|---------|---------|----------|
| 纯英文文本 | `typewrite(text, use_clipboard=False)` | 快速 | 完美支持 |
| 纯中文文本 | `typewrite(text)` 或 `typewrite_chinese(text)` | 中等 | 完美支持 |
| 中英文混合 | `typewrite(text)` (自动检测) | 智能选择 | 完美支持 |
| 特殊中文字符 | `typewrite_chinese(text)` | 中等 | 完美支持 |
| 大量中文文本 | `typewrite_chinese(text)` | 中等 | 完美支持 |

### 中文输入最佳实践

```python
# 场景1：用户交互界面自动化
controller = WindowAutoController(window_title="用户界面")

# 自动检测中文并输入
controller.typewrite("用户名：张三")
controller.typewrite("密码：123456")

# 场景2：文本编辑器自动化
# 专门输入中文内容
controller.typewrite_chinese("这是一个中文文本编辑测试。")
controller.typewrite_chinese("支持各种中文标点符号：，。！？；：""''（）【】")

# 场景3：表单填写自动化
# 混合输入个人信息
controller.typewrite("姓名：李四")
controller.typewrite("性别：男")
controller.typewrite("地址：北京市朝阳区")

# 场景4：聊天应用自动化
controller.typewrite("你好！很高兴认识你 😊")
controller.typewrite_chinese("今天天气真不错，一起去公园走走吧！")
```

### 剪切板工作原理

中文输入通过以下步骤实现：

1. **保存原始剪切板内容**：避免影响用户当前剪切板数据
2. **复制中文文本到剪切板**：使用 `pyperclip.copy()`
3. **执行粘贴操作**：使用 `Ctrl+V` 组合键
4. **恢复剪切板**（可选）：恢复原始剪切板内容

### 常见中文输入问题解决

**Q: 中文显示乱码怎么办？**
A: 确保目标应用支持UTF-8编码，或尝试使用 `typewrite_chinese()` 方法

**Q: 中文输入速度太慢？**
A: 对于纯英文文本，使用 `use_clipboard=False` 参数，或适当调整 `interval` 参数

**Q: 特殊中文字符无法输入？**
A: 使用 `typewrite_chinese()` 方法，它对特殊字符支持更好

**Q: 在某些应用中中文输入无效？**
A: 可能是应用的安全限制，尝试先激活窗口：`controller.bring_to_front(force_focus=True)`

## 内部方法（通常不需要直接调用）

### 23. `_update_window_rect()`
更新窗口位置和大小信息（内部使用）

### 24. `_local_to_global(x, y)`
将窗口本地坐标转换为全局屏幕坐标（内部使用）

### 25. `_ensure_window_active()`
确保窗口处于活动状态（内部使用）

## 完整使用示例

```python
from window_auto_controller import WindowAutoController
import time

# 1. 绑定窗口（自动置顶）
controller = WindowAutoController(window_title="记事本", always_on_top=True)

if controller.is_active:
    print(f"已绑定窗口: {controller.window_title}")
    
    # 2. 获取窗口信息
    size = controller.get_window_size()
    print(f"窗口大小: {size[0]}x{size[1]}")
    print(f"是否置顶: {controller.is_always_on_top()}")
    
    # 3. 鼠标操作
    # 点击窗口中心
    center_x = size[0] // 2
    center_y = size[1] // 2
    controller.click(center_x, center_y)
    
    # 输入文本
    controller.typewrite("自动化测试文本")
    time.sleep(0.5)
    
    # 按回车
    controller.press_key('enter')
    time.sleep(0.5)
    
    # 继续输入
    controller.typewrite("第二行内容")
    
    # 4. 切换窗口置顶状态
    controller.toggle_always_on_top()
    
    # 5. 移动窗口
    controller.set_window_position(100, 100, 800, 600)
    
    # 6. 截图
    controller.screenshot(save_path="screenshot.png")
    print("截图已保存")
    
    # 7. 解绑窗口（恢复原始状态）
    controller.unbind()
    print("窗口已解绑")
else:
    print("绑定窗口失败")
```

## 注意事项

1. **坐标系统**：所有坐标都是相对于绑定窗口左上角的本地坐标
2. **窗口激活**：大部分操作会自动激活窗口，但某些安全软件可能阻止自动激活
3. **权限要求**：某些操作可能需要管理员权限
4. **性能考虑**：频繁的操作之间建议添加适当的延迟（如 `time.sleep(0.1)`）
5. **异常处理**：所有方法都有异常捕获，但建议在实际使用中添加自己的异常处理
6. **线程安全**：非线程安全，建议在单线程中使用或自行添加线程同步

## 常见问题

**Q: 为什么鼠标操作没有反应？**
A: 检查窗口是否被其他窗口遮挡，尝试先用 `bring_to_front()` 激活窗口

**Q: 如何获取窗口内某个按钮的坐标？**
A: 使用窗口追踪器获取坐标，或使用 `get_current_mouse_position()` 获取鼠标当前位置

**Q: 窗口置顶后如何取消？**
A: 使用 `set_always_on_top(False)` 或 `toggle_always_on_top()`

**Q: 支持哪些特殊按键？**
A: 支持所有pyautogui支持的按键，如：`'enter'`、`'tab'`、`'esc'`、`'shift'`、`'ctrl'`、`'alt'`等

**Q: 如何输入中文字符？**
A: 需要先确保窗口处于中文输入状态，然后使用 `typewrite()` 方法

**Q: 窗口最小化时能操作吗？**
A: 不能，大部分操作会自动恢复窗口，但如果窗口被强制最小化可能需要手动恢复