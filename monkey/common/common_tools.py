import os

import jieba

from monkey.config.config import Config


def gen_stop_words():
    with open(os.path.join(Config.BASE_DIR, "common/stop_words.txt"), "r", encoding='utf-8') as fp:
        stop_words = [_.strip() for _ in fp.readlines()]
    return stop_words

def gen_stop_words_scdx():
    with open(os.path.join(Config.BASE_DIR, "common/scdx_stop_words.txt"), "r", encoding='utf-8') as fp:
        stop_words = [_.strip() for _ in fp.readlines()]
    return stop_words


def text_seg(text: str, stop_words: list = None) -> list:
    """
    样例文件“哥们在这给你说唱”
    对输入的文本利用jieba分词进行分词
    :param text:
    :return: []
    """
    seg_list = []
    if not stop_words:
        stop_words = gen_stop_words()
    for each in jieba.cut(text):
        if each not in stop_words and not each.isspace():
            # 对于单词 全部默认小写
            seg_list.append(each.lower())

    return seg_list


if __name__ == "__main__":
    print(text_seg("哥们在这给你说唱，1！5！"))
    print(text_seg("Why u always so poor"))