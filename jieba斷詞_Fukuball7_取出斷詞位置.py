#encoding=utf-8
import jieba
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

jieba.set_dictionary('dict.txt.big')

content = open('lyric.txt', 'rb').read()

print "Input：", content

words = jieba.tokenize(unicode(content, 'utf-8'))

print "Output 精確模式 Full Mode："
for tk in words:
    print "word %s\t\t start: %d \t\t end:%d" % (tk[0],tk[1],tk[2])
