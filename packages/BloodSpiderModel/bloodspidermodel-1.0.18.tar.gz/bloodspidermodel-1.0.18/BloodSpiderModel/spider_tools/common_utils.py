import json
import random
import base64
import urllib.parse

import hashlib

import string
from pathlib import Path
from typing import Literal, List
from datetime import datetime
class GeneralToolkit:
    def __init__(self) -> None:
        # 限制最大 JSON 长度为 1MB，防止过大的恶意输入
        self.MAX_JSON_LENGTH = 1024 * 1024

        # 定义不同类型UA对应的文件路径
        self.file_paths = {
            'computer': 'computer_ua.txt',
            'mobile': 'mobile_ua.txt'
        }
        # 获取UA文件所在的目录
        self.ua_dir = Path(__file__).parent / "ua"

        # 初始化时就加载所有UA并缓存
        self.computer_uas = self._read_ua_file('computer')
        self.mobile_uas = self._read_ua_file('mobile')

        # 验证加载结果
        if not self.computer_uas:
            raise ValueError(f"电脑UA文件中没有有效的User-Agent: {self.file_paths['computer']}")
        if not self.mobile_uas:
            raise ValueError(f"手机UA文件中没有有效的User-Agent: {self.file_paths['mobile']}")

    def _read_ua_file(self, device_type: str) -> List[str]:
        """读取指定类型的UA文件并返回非空UA列表"""
        try:
            # 查找对应的文件
            file_path = list(self.ua_dir.glob(self.file_paths[device_type]))[0]

            with open(file_path, 'r', encoding='utf-8') as f:
                # 读取并过滤空行
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            raise FileNotFoundError(f"UA文件不存在: {self.file_paths[device_type]}，请确保文件已创建并包含内容")
        except IndexError:
            raise FileNotFoundError(f"在目录 {self.ua_dir} 中未找到 {self.file_paths[device_type]} 文件")

    def check_common_substrings(self, input_string, substr_list):
        """
        检查字符串是否包含列表中的任何完整子字符串

        参数:
        input_string (str): 需要检查的字符串
        substr_list (list): 用于比较的子字符串列表

        返回:
        bool: 如果存在匹配的子字符串返回 True，否则返回 False
        """
        for substr in substr_list:
            if substr in input_string:
                return True
        return False

    def filter_sensitive_words(self, sensitive_words: list[str], text: str, replacement: str = '*') -> str:
        """
        将文本中的敏感词替换为指定字符串，每个敏感词仅替换一次

        参数:
            sensitive_words: 敏感词列表
            text: 需要过滤的文本
            replacement: 用于替换敏感词的字符串，默认为星号(*)

        返回:
            过滤后的文本
        """
        # 按长度降序排列敏感词，确保长词优先被替换
        sensitive_words = sorted(sensitive_words, key=len, reverse=True)

        filtered_text = text
        for word in sensitive_words:
            filtered_text = filtered_text.replace(word, replacement, 1)  # 仅替换一次

        return filtered_text

    def is_safe_json_structure(self, obj) -> bool:
        """
        验证 JSON 对象结构是否安全（只允许 object 或 array 作为根节点）

        参数:
            obj: 解析后的 JSON 对象

        返回:
            bool: 结构安全返回 True，否则返回 False
        """
        return isinstance(obj, (dict, list))

    def json_format(self, content: str, is_json: bool = True, should_dump: bool = True) -> str | dict | list:
        """
        格式化 JSON 字符串，增加安全性处理

        参数:
            content: 待格式化的字符串
            is_json: 是否强制作为 JSON 处理
            should_dump: 是否对解析后的对象执行 json.dumps，默认为 True

        返回:
            格式化后的 JSON 字符串或解析后的 Python 对象（dict/list）或原始内容

        异常:
            ValueError: 输入不符合 JSON 格式或结构不安全
            TypeError: 输入类型错误
        """
        # 检查输入类型
        if not isinstance(content, str):
            raise TypeError(f"Expected string, got {type(content).__name__}")

        # 检查输入长度
        if len(content) > self.MAX_JSON_LENGTH:
            raise ValueError(f"Input exceeds maximum length of {self.MAX_JSON_LENGTH} characters")

        # 如果明确不是 JSON 且不需要强制处理，直接返回
        if not is_json:
            return content

        try:
            # 解析 JSON
            parsed = json.loads(content)

            # 验证 JSON 结构安全性
            if not self.is_safe_json_structure(parsed):
                raise ValueError("Unsafe JSON structure: root must be object or array")

            # 根据 should_dump 参数决定是否执行 json.dumps
            if should_dump:
                return json.dumps(parsed, indent=4, ensure_ascii=False)
            else:
                return parsed

        except json.JSONDecodeError as e:
            # 处理 JSON 解析错误
            if is_json:
                # 如果强制要求是 JSON，抛出错误
                raise ValueError(f"Invalid JSON format: {str(e)}") from e
            else:
                # 否则返回原始内容
                return content
        except ValueError as e:
            # 重新抛出安全验证错误
            raise ValueError(f"Unsafe JSON structure: {str(e)}") from e
        except Exception as e:
            # 处理其他异常
            raise ValueError(f"Unexpected error processing JSON: {str(e)}") from e

    def get_ua(self, device_type: Literal['computer', 'mobile', 'random'] = 'random') -> str:
        """
        返回指定类型设备的User-Agent（使用预加载的缓存数据）

        参数:
            device_type: 设备类型，可选值为 'computer'(电脑), 'mobile'(手机) 或 'random'(随机)

        返回:
            随机选择的User-Agent字符串
        """
        if device_type == 'computer':
            return random.choice(self.computer_uas)
        elif device_type == 'mobile':
            return random.choice(self.mobile_uas)
        elif device_type == 'random':
            # 随机选择设备类型及其再随机选择UA
            return random.choice(
                self.computer_uas + self.mobile_uas
            )
        else:
            raise ValueError("device_type must be one of 'computer', 'mobile', 'random'")
    def get_headers(self, ua_device_type = 'random') -> dict:
        """返回一个包含随机 User-Agent 的 HTTP 头字典"""
        user_agent = self.get_ua(ua_device_type)
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': user_agent
        }
        return headers

    def get_formatted_time(self) -> str:
        """返回格式为 'YYYY-MM-DD HH:MM:SS' 的当前时间字符串"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def generate_device_id(self, length: int = 22, segments: int = 3, separator: str = '_') -> str:
        """
        生成随机设备ID，格式类似 "WiRsasjclDTQ2eVSz6_SY"

        Args:
            length: 每个段的字符长度（默认22）
            segments: 段的数量（默认3）
            separator: 段之间的分隔符（默认下划线）

        Returns:
            生成的随机设备ID字符串
        """
        # 允许的字符集合（大小写字母和数字）
        allowed_chars = string.ascii_letters + string.digits

        # 生成每个段的随机字符串
        parts = [
            ''.join(random.choice(allowed_chars) for _ in range(length))
            for _ in range(segments)
        ]

        # 使用分隔符连接各段
        return separator.join(parts)

     # 保留两位小数
    def format_decimal(self, value, decimal_places=2):
        """
        修复版：将数值格式化为指定小数位数（截断），支持整数、小数和异常格式
        :param value: 输入数值（int/float/str）
        :param decimal_places: 保留小数位数，默认2位（确保为整数）
        :return: 格式化后的字符串（如 "123.45"）
        """
        try:
            # 1. 确保 decimal_places 是整数
            decimal_places = int(decimal_places)
            if decimal_places < 0:
                decimal_places = 0  # 避免负数小数位数
            
            # 2. 将 value 转换为字符串（处理不同类型输入）
            str_value = str(value)
            
            # 3. 处理科学计数法（如 1e+02 → 100）
            if 'e' in str_value.lower():
                # 转换为普通浮点数字符串
                str_value = "{0:.{1}f}".format(float(value), decimal_places + 10)
            
            # 4. 处理无小数点的情况（整数）
            if "." not in str_value:
                return f"{str_value}.{'0' * decimal_places}"
            
            # 5. 找到小数点位置（确保是整数）
            dot_index = str_value.index(".")
            
            # 6. 计算切片结束位置（确保是整数）
            end_index = dot_index + 1 + decimal_places
            
            # 7. 截取整数部分 + 小数点 + 小数部分前N位
            result = str_value[:end_index]
            
            # 8. 补0：若小数部分不足N位，用0补齐
            result = result.ljust(end_index, "0")
            
            return result
            
        except (ValueError, TypeError) as e:
            # 处理异常情况（如无法转换为字符串、索引错误等）
            return f"0.{'0' * decimal_places}"  # 返回默认值

    def md5_encrypt(self, data: str) -> str:
        md5_obj = hashlib.md5()
        if isinstance(data, str):
            data = data.encode('utf-8')
        md5_obj.update(data)

        return md5_obj.hexdigest()

    def codec_handler(self, content, mode='encode'):
        """
        对内容进行 JSON格式化→URL编码→Base64编码 或 Base64解码→URL解码→JSON解析
        :param content: 输入内容（编码时可传任意JSON可序列化类型：字符串/字节流/字典/列表/数字等；解码时传Base64编码后的字符串/字节流）
        :param mode: 操作模式，'encode'为编码（默认），'decode'为解码
        :return: 处理后的结果（编码返回字符串，解码返回原类型数据）
        :raises ValueError: 模式错误或处理失败时抛出异常
        """
        try:
            if content is None or content == "":
                return None
            if mode == 'encode':
                # ========== 步骤1：JSON序列化（格式化） ==========
                # 处理字节流：先转为字符串
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                # JSON序列化（将任意可序列化类型转为JSON字符串）
                json_str = json.dumps(content, ensure_ascii=False)  # ensure_ascii=False保留中文
                
                # ========== 步骤2：URL编码 ==========
                url_encoded = urllib.parse.quote(json_str)
                
                # ========== 步骤3：Base64编码 ==========
                b64_encoded = base64.b64encode(url_encoded.encode('utf-8'))
                return b64_encoded.decode('utf-8')
            
            elif mode == 'decode':
                # ========== 步骤1：Base64解码 ==========
                # 处理字节流：先转为字符串
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                b64_decoded = base64.b64decode(content)
                
                # ========== 步骤2：URL解码 ==========
                url_decoded = urllib.parse.unquote(b64_decoded.decode('utf-8'))
                
                # ========== 步骤3：JSON反序列化（解析） ==========
                json_data = json.loads(url_decoded)
                return json_data
            
            else:
                raise ValueError(f"无效的模式：{mode}，仅支持 'encode' 或 'decode'")
        
        except base64.binascii.Error as e:
            raise ValueError(f"Base64解码失败：{str(e)}")
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析失败：{str(e)}")
        except UnicodeDecodeError as e:
            raise ValueError(f"字节流转字符串失败（编码格式非UTF-8）：{str(e)}")
        except Exception as e:
            raise ValueError(f"处理失败：{str(e)}")


if __name__ == "__main__":
    common_utils = GeneralToolkit()
    print(common_utils.format_decimal(123.456789))
    