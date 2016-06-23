#encoding=utf-8
import jieba
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
jieba.set_dictionary('dict.txt.big')

content = open('lyric_tw.txt', 'rb').read()

print "Input：", content

words = jieba.cut(content, cut_all=False)

print "Output 精確模式 Full Mode："
for word in words:
    print word
