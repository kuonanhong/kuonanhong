# -*- coding: utf-8 -*-
#from __future__ import unicode_literals
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
#sys.path.append("../")
import time
sys.path.append("../../")
import jieba

#jieba.enable_parallel(4) # 开启并行分词模式，参数为并行进程数
#jieba.disable_parallel() # 关闭并行分词模式
#例子：https://github.com/fxsjy/jieba/blob/master/test/parallel/test_file.py
#实验结果：在 4 核 3.4GHz Linux 机器上，对金庸全集进行精确分词，获得了 1MB/s 的速度，是单进程版的 3.3 倍。
#注意：并行分词仅支持默认分词器 jieba.dt 和 jieba.posseg.dt

jieba.enable_parallel()

#url = sys.argv[1]
#須從網路抓一段url
#content = open(url,"rb").read()
content = open('TripAdvistor中國地區觀光活動細項目條列與旅遊評論字典檔.txt',"rb").read()
t1 = time.time()
words = "/ ".join(jieba.cut(content))

t2 = time.time()
tm_cost = t2-t1

log_f = open("1.log","wb")
log_f.write(words.encode('utf-8'))

print('speed %s bytes/second' % (len(content)/tm_cost))