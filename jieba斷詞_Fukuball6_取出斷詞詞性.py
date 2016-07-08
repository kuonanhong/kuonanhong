# -*- coding: utf-8 -*-
import jieba
#底下三行是去網路找到來解決coding的問題
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#經過實驗過後,下面這段程式碼需放在import_sys到setdefaultingencoding之後
#不能放在那三行之前,否則會出錯(coding之後)
import jieba.posseg as pseg

jieba.set_dictionary('dict.txt.big')
content = open('lyric.txt', 'rb').read()
print "Input：", content

words = pseg.cut(content)
print "Output 精確模式 Full Mode："
for word in words:
    print word.word, word.flag
