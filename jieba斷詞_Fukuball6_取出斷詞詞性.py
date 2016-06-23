#encoding=utf-8
import jieba
import jieba.posseg as pseg
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
jieba.set_dictionary('dict.txt.big')

content = open('lyric.txt', 'rb').read()

print "Input：", content

words = pseg.cut(content)

print "Output 精確模式 Full Mode："
for word in words:
    print word.word, word.flag
