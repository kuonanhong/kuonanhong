# -*- coding: utf-8 -*-
from __future__ import unicode_literals
#jieba 采用延迟加载，import jieba 和 jieba.Tokenizer() 不会立即触发词典的加载，
# 一旦有必要才开始加载词典构建前缀字典。如果你想手工初始 jieba，也可以手动初始化。

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("../")

import jieba
jieba.initialize()  # 手动初始化（可选）

#在 0.28 之前的版本是不能指定主词典的路径的，
# 有了延迟加载机制后，你可以改变主词典的路径
jieba.set_dictionary('dict.txt.big')
#例子： https://github.com/fxsjy/jieba/blob/master/test/test_change_dictpath.py

def cuttest(test_sent):
    result = jieba.cut(test_sent)
    print("  ".join(result))

def testcase():
    cuttest("这是一个伸手不见五指的黑夜。我叫孙悟空，我爱北京，我爱Python和C++。")
    cuttest("我不喜欢日本和服。")
    cuttest("雷猴回归人间。")
    cuttest("工信处女干事每月经过下属科室都要亲口交代24口交换机等技术性器件的安装工作")
    cuttest("我需要廉租房")
    cuttest("永和服装饰品有限公司")
    cuttest("我爱北京天安门")
    cuttest("abc")
    cuttest("隐马尔可夫")
    cuttest("雷猴是个好网站")

if __name__ == "__main__":
    testcase()
    jieba.set_dictionary("foobar.txt")
    print("================================")
    testcase()