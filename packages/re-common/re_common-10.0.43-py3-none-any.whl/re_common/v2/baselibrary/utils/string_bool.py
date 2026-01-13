import re

import regex
import unicodedata


def is_ascii_alnum(char: str) -> bool:
    #  精准判断是否为英文或数字字符（ASCII 范围）
    # char.isalnum() 字母或数字（Unicode）包含中文等非英文字符
    return char.isascii() and char.isalnum()


def is_all_english_chars(s):
    return bool(re.match(r'^[A-Za-z]+$', s))


def contains_chinese_chars(s):
    """
    判断字符串中是否包含中文（汉字）字符

    使用 regex 库（不是内置 re），通过 Unicode 属性 IsHan
    来匹配任意一个汉字。

    参数:
        s (str): 待检测的字符串

    返回:
        bool:
            True  - 字符串中至少包含一个中文字符
            False - 字符串中不包含任何中文字符
    """
    return bool(regex.search(r"[\p{IsHan}]", s))


def is_empty(value):
    """
    判断一个值是否为空。

    支持的类型：
    - None
    - 空字符串（去除空白后）
    - pandas 的 NaN
    - 其他可迭代类型（如列表、字典等）的长度为 0
    - 其他情况返回 False
    """
    # 如果是 None，直接返回 True
    if value is None:
        return True

    # 尝试处理 pandas 的 NaN
    try:
        import pandas as pd
        if pd.isna(value):
            return True
    except:
        pass  # 如果没有安装 pandas，跳过

    # 如果是字符串，检查去除空白后是否为空
    if isinstance(value, str):
        return value.strip() == ""

    # 处理其他可迭代类型（如列表、字典等）
    if hasattr(value, "__len__"):
        return len(value) == 0

    # 默认情况下，非 None、非空类型返回 False
    return False


class InvalidCharLengthError(Exception):
    """自定义异常类，用于处理输入字符长度不为 1 的情况"""
    pass


def is_single_cjk_char(char):
    """
    判断单个字符是否为中日韩字符
    :param char: 要判断的单个字符
    :return: 如果是中日韩字符返回 True，否则返回 False
    """
    # 检查输入字符的长度
    if len(char) != 1:
        raise InvalidCharLengthError("输入的字符串长度必须为 1，请提供单个字符进行判断。")
    code_point = ord(char)
    # 中日韩统一表意文字
    ranges = [
        (0x4E00, 0x9FFF),  # CJK 统一表意符号
        (0x3400, 0x4DBF),  # CJK 统一表意符号扩展 A
        (0x20000, 0x2A6DF),  # CJK 统一表意符号扩展 B
        (0x2A700, 0x2B73F),  # CJK 统一表意符号扩展 C
        (0x2B740, 0x2B81F),  # CJK 统一表意符号扩展 D
        (0x2B820, 0x2CEAF),  # CJK 统一表意符号扩展 E
        (0x2CEB0, 0x2EBEF),  # CJK 统一表意符号扩展 F
        (0x30000, 0x3134F),  # CJK 统一表意符号扩展 G
        (0x31350, 0x323AF),  # CJK 统一表意符号扩展 H
        (0x3300, 0x33FF),  # CJK 兼容符号
        (0xFE30, 0xFE4F),  # CJK 兼容形式
        (0xF900, 0xFAFF),  # CJK 兼容表意符号
        (0x2F800, 0x2FA1F),  # CJK 兼容表意符号补充
        (0x3105, 0x3129),  # 注音字母
        (0x31A0, 0x31BF),  # 注音字母扩展
        (0x3040, 0x309F),  # 平假名
        (0x30A0, 0x30FF),  # 片假名
        (0x31F0, 0x31FF),  # 片假名扩展
        (0xAC00, 0xD7AF),  # 韩文音节
        (0x1100, 0x11FF),  # 韩文字母
        (0xA960, 0xA97F),  # 韩文字母扩展 A
        (0xD7B0, 0xD7FF),  # 韩文字母扩展 B
    ]
    for start, end in ranges:
        if start <= code_point <= end:
            return True
    return False


def is_all_symbols(text):
    # 是否全是符号
    # 如果字符串为空，返回 False
    if not text:
        return False

    # 检查每个字符是否属于符号类别
    return all(unicodedata.category(char).startswith(('P', 'S')) for char in text)

def is_whole_word_en_re(organ: str, ele_organ: str) -> bool:
    """
    与 is_whole_word_en 效果一致
    """
    if not organ or not ele_organ:
        return False

    pattern = rf"(^|[^a-z0-9-]){re.escape(organ)}([^a-z0-9-]|$)"
    return re.search(pattern, ele_organ) is not None

def is_whole_word_en(sub_str: str, long_str: str) -> bool:
    regex_pattern = re.compile(r"[^a-z0-9-]", re.IGNORECASE)

    if not sub_str or not long_str:
        return False

    # 使用 startsWith 和 endsWith 检查边界
    if long_str.startswith(sub_str) and long_str.endswith(sub_str) and len(sub_str) == len(long_str):
        return True

    # 检查是否在中间位置，且前后有非字母数字字符
    # index = long_str.find(sub_str)
    index_list = [m.start() for m in re.finditer(re.escape(sub_str), long_str)]

    def get_bools(index):
        if index >= 0:
            is_start = False
            is_end = False
            if index == 0:
                is_start = True
            else:
                is_start = bool(regex_pattern.match(long_str[index - 1]))

            if len(long_str) == len(sub_str) + index:
                is_end = True
            else:
                is_end = bool(regex_pattern.match(long_str[index + len(sub_str)]))

            return is_start and is_end
        else:
            return False

    return any([get_bools(index) for index in index_list])


def is_whole_word(sub_str: str, long_str: str) -> bool:
    """
    判断 sub_str 是否为 long_str 中的一个完整词（适配中英文）。
    中文采用“包含”判断，英文采用完整词匹配。

    参数:
        sub_str: 要搜索的子串（中英文均可）
        long_str: 被搜索的字符串

    返回:
        True 表示 sub_str 是一个完整词；False 否则。
    """
    if contains_chinese_chars(sub_str):
        # 子字符串完全包含在长字符串
        is_contain = sub_str in long_str
        # 是否是字母数字
        if is_ascii_alnum(sub_str[0]) or is_ascii_alnum(sub_str[-1]):
            # 表示中英文混合 看是否是截断单词即可
            return is_whole_word_en_re(sub_str, long_str)
        else:
            # 中文子串只要被包含即可视为“完整词”
            return is_contain
    else:
        # 英文使用完整单词判断逻辑
        return is_whole_word_en_re(sub_str, long_str)
