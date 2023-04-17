import asyncio
import math
import sys
sys.path.append('E://Project/Rrawl')

from collections import Counter

from monkey.common.common_tools import gen_stop_words, text_seg
from monkey.database.motor_base import MotorBase

mongo_db = MotorBase().get_db()
stop_words = gen_stop_words()


def elias_gamma_encode(X: int) -> str:
    """
    Elias Gamma算法对倒排列表的文档数值之差进行编码压缩
    :return:
    """
    e = int(math.log(X, 2))
    d = int(X - math.pow(2, e))
    unary_code = '1' * e + '0'
    binary_d = bin(d).replace('0b', '')
    binary_code = ('0' * e)[0:(e - len(binary_d))] + binary_d
    return f"{unary_code}:{binary_code}"


def elias_gamma_decode(el_str: str) -> int:
    """
    Elias Gamma算法对倒排列表的文档数值之差进行解码
    :return:
    """
    unary_code, binary_code = el_str.split(':')
    e = len(unary_code) - 1
    d = int(binary_code, 2)
    return pow(2, e) + d


async def gen_doc_word_id():
    """
    为单词以及资源文档生成id
    :return:
    """
    # 为文档生成id(doc_id)
    cursor = mongo_db.source_docs.find({})
    
    word_list = []
    doc_id, word_id = 0, 0
    # 获取所有源数据
    async for document in cursor:
        # 进行分词
        seg_title = text_seg(text=document['title'], stop_words=stop_words)

        doc_id += 1
        cur_item_data = {
            'doc_id': doc_id,
            'seg_title': seg_title,
            "seg_title_counter": Counter(seg_title),
            'title': document['title'],
            'url': document['url']
        }
        # 更新数据库
        await mongo_db.doc_id.update_one(
            {'title': cur_item_data['title']},
            {'$set': cur_item_data},
            # 没有则插入新数据
            upsert=True)

        # 生成单词列表，给下面的函数使用
        word_list += seg_title
    
    # 为单词生成id（word_id）
    # Counter() is a subclass of dict
    for key, value in Counter(word_list).items():
        word_id += 1
        cur_item_data = {
            'word_id': word_id,
            'word': key,
            'tf': value
        }

        await mongo_db.word_id.update_one(
            {'word': cur_item_data['word']},
            {'$set': cur_item_data},
            upsert=True)


# 生成倒排索引表
async def gen_doc_inverted_index():
    """
    倒排索引表构建函数，首先运行程序生成id
    asyncio.get_event_loop().run_until_complete(gen_doc_word_id())
    再运行此函数方可构建倒排索引表
    :return:
    """
    # 为单词生成倒排索引表
    word_cursor = mongo_db.word_id.find({})

    async for each_word in word_cursor:
        # 为某个单词生成其倒排列表
        word_id = each_word['word_id']
        word = each_word['word']
        tf = each_word['tf']
        doc_cursor = mongo_db.doc_id.find({"seg_title": word})
        
        cur_word_data, inverted_list = {}, []
        # 记录当前doc_id
        last_doc_id = 0
        async for each_doc in doc_cursor:
            doc_id = each_doc['doc_id']
            # 取两个文档之间的差值
            cur_doc_id = doc_id - last_doc_id
            last_doc_id = doc_id
            seg_title_counter = each_doc['seg_title_counter']
            # 编码前：{'word_id': 1, 'word_tf': 2, 'inverted_list': [(1, 1), (1352, 1)]}
            # 编码后：{'word_id': 1, 'word_tf': 2, 'inverted_list': [(b'0:0', 1), (b'11111111110:0101000111', 1)]}
            inverted_list.append((cur_doc_id, seg_title_counter[word]))
            # inverted_list.append((elias_gamma_encode(cur_doc_id), seg_title_counter[word]))
        cur_word_data['word_id'] = word_id
        cur_word_data['word_tf'] = tf
        cur_word_data['inverted_list'] = inverted_list

        await mongo_db.inverted_index.update_one({
            'word_id': cur_word_data['word_id']},
            {'$set': cur_word_data},
            upsert=True)
    print("创建索引成功")


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(gen_doc_word_id())
    asyncio.get_event_loop().run_until_complete(gen_doc_inverted_index())
    # el_str = elias_gamma_encode(100)
    # print(elias_gamma_decode(el_str))