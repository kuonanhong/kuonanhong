# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("../")

#import jieba
import jieba.posseg as pseg
#import jieba.analyse

words = pseg.cut("我爱北京天安门")
for word, flag in words:
    print('%s %s' % (word, flag))