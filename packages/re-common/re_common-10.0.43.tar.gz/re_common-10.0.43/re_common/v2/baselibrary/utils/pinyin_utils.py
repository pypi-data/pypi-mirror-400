import itertools
from typing import List, Any

from pypinyin import pinyin, Style


class PinyinUtils:
    @staticmethod
    def get_pinyin_or_char(text: str) -> str:
        """拼音 + 非中文原样返回 对应 toPinyin"""
        result = []
        for char in text:
            if PinyinUtils.is_chinese(char):
                py_one = pinyin(char, style=Style.NORMAL, v_to_u=True, heteronym=True)
                result.append(py_one[0][0] if py_one else char)
            else:
                result.append(char)
        return "".join(result)

    @staticmethod
    def get_pinyin_or_char_ex(text: str) -> str:
        """拼音 + 非中文原样返回 对应 toPinyin"""
        result = []
        for char in text:
            if PinyinUtils.is_chinese(char):
                py_one = pinyin(char, style=Style.NORMAL, v_to_u=True, heteronym=True)
                result.append("|".join(py_one[0]) if py_one else char)
            else:
                result.append(char)
        return "".join(result)

    @staticmethod
    def is_chinese(char: str) -> bool:
        """判断是否为汉字"""
        return "\u4e00" <= char <= "\u9fff"

    @staticmethod
    def combine(lists: List[List[Any]]) -> list:
        # lists = [[1, 2],['a', 'b'],[True, False]]
        # 计算笛卡尔积
        cartesian_product = list(itertools.product(*lists))

        return [" ".join([str(ii) for ii in list(i)]) for i in cartesian_product]

    @staticmethod
    def to_pinyin_names(name: str) -> List[str]:
        """
        将中文姓名转换为所有可能的拼音组合

        Args:
            name: 中文姓名字符串

        Returns:
            所有可能的拼音组合列表
        """
        if not name:
            return []

        pinyin_options = []

        for char in name:
            py_one = PinyinUtils.get_pinyin_or_char_ex(char)
            variants = []

            if "ü" in py_one:
                # 处理ü的特殊情况，生成u和v两种变体
                for replacement in ["u", "v"]:
                    replaced = py_one.replace("ü", replacement)
                    variants.extend(replaced.split("|"))
                variants = list(set(variants))
            else:
                variants = py_one.split("|")

            pinyin_options.append(variants)

        return PinyinUtils.combine(pinyin_options)

    @staticmethod
    def to_pinyin_name(name: str) -> str:
        """
        将中文姓名转换为拼音字符串

        Args:
            name: 中文字符串

        Returns:
            拼音字符串，用空格分隔每个字的拼音
        """
        result = []
        for char in name:
            py_one = PinyinUtils.get_pinyin_or_char(char).replace("ü", "v")
            result.append(py_one)
        return " ".join(result)


VALID_PINYINS = {
    "a", "o", "e", "ai", "ei", "ao", "ou", "an", "en", "ang", "eng", "er",
    "ba", "bai", "ban", "bang", "bao", "bei", "ben", "beng", "bi", "bian", "biao", "bie", "bin", "bing", "bo", "bu",
    "pa", "pai", "pan", "pang", "pao", "pei", "pen", "peng", "pi", "pian", "piao", "pie", "pin", "ping", "po", "pu",
    "ma", "mai", "man", "mang", "mao", "mei", "men", "meng", "mi", "mian", "miao", "mie", "min", "ming", "mo",
    "mou",
    "mu",
    "fa", "fan", "fang", "fei", "fen", "feng", "fo", "fou", "fu",
    "da", "dai", "dan", "dang", "dao", "dei", "den", "deng", "di", "dian", "diao", "die", "ding", "diu", "dong",
    "dou",
    "du", "duan", "dui", "dun", "duo",
    "ta", "tai", "tan", "tang", "tao", "tei", "teng", "ti", "tian", "tiao", "tie", "ting", "tong", "tou", "tu",
    "tuan",
    "tui", "tun", "tuo",
    "na", "nai", "nan", "nang", "nao", "nei", "nen", "neng", "ni", "nian", "niang", "niao", "nie", "nin", "ning",
    "niu",
    "nong", "nou", "nu", "nuan", "nue", "nv",
    "la", "lai", "lan", "lang", "lao", "lei", "leng", "li", "lia", "lian", "liang", "liao", "lie", "lin", "ling",
    "liu",
    "lo", "long", "lou", "lu", "luan", "lue", "lv",
    "ga", "gai", "gan", "gang", "gao", "ge", "gei", "gen", "geng", "gong", "gou", "gu", "gua", "guai", "guan",
    "guang",
    "gui", "gun", "guo",
    "ka", "kai", "kan", "kang", "kao", "ke", "ken", "keng", "kong", "kou", "ku", "kua", "kuai", "kuan", "kuang",
    "kui",
    "kun", "kuo",
    "ha", "hai", "han", "hang", "hao", "he", "hei", "hen", "heng", "hong", "hou", "hu", "hua", "huai", "huan",
    "huang",
    "hui", "hun", "huo",
    "ji", "jia", "jian", "jiang", "jiao", "jie", "jin", "jing", "jiong", "jiu", "ju", "juan", "jue", "jun",
    "qi", "qia", "qian", "qiang", "qiao", "qie", "qin", "qing", "qiong", "qiu", "qu", "quan", "que", "qun",
    "xi", "xia", "xian", "xiang", "xiao", "xie", "xin", "xing", "xiong", "xiu", "xu", "xuan", "xue", "xun",
    "zha", "zhai", "zhan", "zhang", "zhao", "zhe", "zhei", "zhen", "zheng", "zhong", "zhou", "zhu", "zhua", "zhuai",
    "zhuan", "zhuang", "zhui", "zhun", "zhuo",
    "cha", "chai", "chan", "chang", "chao", "che", "chen", "cheng", "chi", "chong", "chou", "chu", "chua", "chuai",
    "chuan", "chuang", "chui", "chun", "chuo",
    "sha", "shai", "shan", "shang", "shao", "she", "shei", "shen", "sheng", "shi", "shou", "shu", "shua", "shuai",
    "shuan", "shuang", "shui", "shun", "shuo",
    "ra", "ran", "rang", "rao", "re", "ren", "reng", "ri", "rong", "rou", "ru", "rua", "ruan", "rui", "run", "ruo",
    "za", "zai", "zan", "zang", "zao", "ze", "zei", "zen", "zeng", "zong", "zou", "zu", "zuan", "zui", "zun", "zuo",
    "ca", "cai", "can", "cang", "cao", "ce", "cen", "ceng", "cong", "cou", "cu", "cuan", "cui", "cun", "cuo",
    "sa", "sai", "san", "sang", "sao", "se", "sen", "seng", "song", "sou", "su", "suan", "sui", "sun", "suo",
    "ya", "yan", "yang", "yao", "ye", "yi", "yin", "ying", "yo", "yong", "you", "yu", "yuan", "yue", "yun",
    "wa", "wai", "wan", "wang", "wei", "wen", "weng", "wo", "wu"
}


def split_pinyin_all(s):
    s = s.lower()
    results = []

    def dfs(start, path):
        if start == len(s):
            results.append(path[:])
            return
        for end in range(start + 1, min(len(s), start + 6) + 1):
            part = s[start:end]
            if part in VALID_PINYINS:
                path.append(part)
                dfs(end, path)
                path.pop()

    dfs(0, [])
    return results


def is_pinyin(word):
    """检测一个字符串是否是合法拼音（无歧义）"""
    try:
        # 尝试转换为拼音，如果原词是拼音，转换结果应该和原词相近
        pinyin_list = pinyin(word, style=Style.NORMAL)
        reconstructed = "".join([p[0] for p in pinyin_list])
        # 检查转换后的拼音是否与原词相似（忽略大小写）
        return word.lower() == reconstructed.lower()
    except:
        return False

def split_pinyin(word):
    lists = split_pinyin_all(word)
    lists = [" ".join(i) for i in lists]
    if not lists:
        return [word]
    return lists