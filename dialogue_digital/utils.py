import re
from pypinyin import pinyin, lazy_pinyin, Style  # 需要安装 pypinyin 模块
import logging

# 初始化日志模块
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s %(filename)s:%(lineno)d - %(message)s')


def starts_with_chinese_pinyin(sentence, chinese_word):
    """
    判断字符串是否以某个中文词的发音开头
    :param text: 待检查的字符串
    :param chinese_word: 中文词
    :return: 如果以该中文词的发音开头，返回 True，否则返回 False
    """

    # 判断句子长度是否大于等于4
    if len(sentence) < 4:
        return False

    # text = sentence[:4]
    text = sentence

    # 将中文词转换为拼音
    word_pinyin = lazy_pinyin(chinese_word)
    text_pinyin = lazy_pinyin(text)

    logging.info(f"word_pinyin: {word_pinyin}")
    logging.info(f"text_pinyin: {text_pinyin}")

    word_pinyin_str = ''.join(word_pinyin)
    text_pinyin_str = ''.join(text_pinyin)

    return contains_substring(text_pinyin_str.lower(), word_pinyin_str.lower())


def contains_substring(text, substring):
    """
    判断字符串是否包含某个子字符串
    :param text: 待检查的字符串
    :param substring: 需要匹配的子字符串
    :return: 如果包含子字符串，返回 True，否则返回 False
    """
    escaped_substring = re.escape(substring)
    if re.search(escaped_substring, text):
        return True
    else:
        return False

#
# if __name__ == '__main__':
#     # 示例
#     text = "。小鲸同学"
#     chinese_word = "小京同学"
#     result = starts_with_chinese_pinyin(text, chinese_word)
#     print(result)  # 输出: True
