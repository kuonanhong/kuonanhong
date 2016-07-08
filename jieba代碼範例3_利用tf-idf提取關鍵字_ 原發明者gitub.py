# -*- coding: utf-8 -*-
#encoding=utf-8
#https://github.com/fxsjy/jieba/blob/master/test/extract_tags.py
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('../')

import jieba
import jieba.analyse
from optparse import OptionParser

USAGE = "usage:  python jieba代碼範例3_利用tf-idf提取關鍵字_ 原發明者gitub.py [TripAdvistor東京京都大阪神戶光觀活動大項目字典檔.txt] -k [20]"
#USAGE = "usage:    python extract_tags.py [file name] -k [top k]"

parser = OptionParser(USAGE)
parser.add_option("-k", dest="topK")
opt, args = parser.parse_args()


#if len(args) < 1:
#    print(USAGE)
#    sys.exit(1)

#file_name = args[0]
#print file_name
#print ('--------------------')
#if opt.topK is None:
#    topK = 10
#else:
#    topK = int(opt.topK)

#content = open('file_name', 'rb').read()
content = open('TripAdvisor飯店評論關東地區精簡版.txt', 'rb').read()

tags = jieba.analyse.extract_tags(content, topK=20)

print(",".join(tags))