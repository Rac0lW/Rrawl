import numpy as np
import sys
sys.path.append('E://Project/Rrawl')

from functools import reduce
from math import sqrt


class CosineSimilarity(object):
    """
    余弦相似性计算相似度
    """

    def __init__(self, init_query, target_data):
        """
        初始化相似度计算类
        :param init_query: 输入文本分词后向量
        :param target_data: 对比文本以及文本向量构成的字典 key 分别为index 以及value
        """
        self.init_query = init_query
        self.target_data = target_data

    def create_vector(self):
        """
        创建兴趣向量
        :return: word_vector = {} 文本以及文本向量 index: value 例如：[[1, 2, 1, 1, 2, 0, 1], [1, 2, 1, 2, 2, 1, 1]]
        """
        # 该方法首先从 target_data 中获取文本的索引和向量，然后创建一个空字典 word_vector
        index, value = self.target_data['index'], self.target_data['value']
        word_vector = {
            'index': index,
            'value': []
        }

        # 将输入文本和对比文本的所有词汇放在一起，去重
        title_vector, value_vector = [], []
        all_word = set(self.init_query + value)

        # 遍历所有词汇，统计输入文本和对比文本中每个词汇出现的次数
        for each_Word in all_word:
            title_num = self.init_query.count(each_Word)
            value_num = value.count(each_Word)
            # 将统计的结果添加到 title_vector 和 value_vector 中
            title_vector.append(title_num)
            value_vector.append(value_num)
        
        # 将统计的结果添加到 word_vector 中
        word_vector['value'].append(title_vector)
        word_vector['value'].append(value_vector)
        return word_vector

    def calculate(self, wordVector):
        """
        计算余弦相似度
        :param word_vector: word_vector = {} 文本以及文本向量 key 分别为index 以及value
        :return: 返回各个用户相似度值
        """
        result_dic = {}
        value = wordVector['value']
        # 将列表转换为数组
        value_arr = np.array(value)
        # 保存分母的平方和，分别计算两个向量的模，然后相乘，最后计算余弦相似度
        squares = []
        # 计算余弦相似度的分子，累积相加
        numerator = reduce(lambda x, y: x + y, value_arr[0] * value_arr[1])
        # 计算余弦相似度的分母，分别计算两个向量的模，然后相乘
        square_title, square_data = 0.0, 0.0
        for num in range(len(value_arr[0])):
            square_title += pow(value_arr[0][num], 2)
            square_data += pow(value_arr[1][num], 2)
        squares.append(sqrt(square_title))
        squares.append(sqrt(square_data))
        mul_of_squares = reduce(lambda x, y: x * y, squares)
        # 计算余弦相似度
        value = float(('%.5f' % (numerator / mul_of_squares)))

        result_dic['index'] = wordVector['index']
        result_dic['value'] = value
        return result_dic


if __name__ == '__main__':
    """
    示例文件：

    分词：默认去停用词
        c 语言学习之路：['c', '语言', '学习', '路']
        学习 c 语言的教材：['学习', 'c', '语言', '教材']

    词频向量：所有出现词语在单个文档中出现的次数构成的向量：
        词语总数为：['c', '语言', '学习', '路', '教材']
        c 语言学习之路：[1, 1, 1, 1, 0]
        学习 c 语言的教材：[1, 1, 1, 0, 1]  
    """
    value = ['c', '语言', '学习', '路']
    data = {
        'index': '学习c语言的教材',
        'value': ['学习', 'c', '语言', '教材']
    }

    cos = CosineSimilarity(value, data)

    vector = cos.create_vector()
    result = cos.calculate(vector)
    print(result)