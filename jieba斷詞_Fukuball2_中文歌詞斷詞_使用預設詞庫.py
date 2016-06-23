#encoding=utf-8
import jieba

content = open('lyric.txt', 'rb').read()

print "Input：", content

words = jieba.cut(content, cut_all=False)

print "Output 精確模式 Full Mode："
for word in words:
    print word
