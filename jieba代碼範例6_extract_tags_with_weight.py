# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('../')

import jieba
import jieba.analyse
from optparse import OptionParser

#USAGE = "usage:    python extract_tags_idfpath.py [file name] -k [top k]"

#parser = OptionParser(USAGE)
#parser.add_option("-k", dest="topK")
#opt, args = parser.parse_args()


#if len(args) < 1:
#    print(USAGE)
#    sys.exit(1)

#file_name = args[0]

#if opt.topK is None:
#    topK = 10
#else:
#    topK = int(opt.topK)

content = open('TripAdvistor中國地區觀光活動細項目條列與旅遊評論字典檔.txt', 'rb').read()

#jieba.analyse.set_stop_words("stop_words.txt")
#jieba.analyse.set_idf_path("idf.txt.big");

tags = jieba.analyse.extract_tags(content, 50, withWeight=True)

#if withWeight is True:
for tag in tags:
    print("tag: %s\t\t weight: %f" % (tag[0],tag[1]))
#else:
#print(",".join(tags))
