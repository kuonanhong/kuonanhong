# -*- coding: utf-8 -*-
from __future__ import unicode_literals
#使用示例：python -m jieba news.txt > cut_result.txt
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("../")

#使用: python -m jieba [options] filename

#结巴命令行界面。

#固定参数:
#  filename              输入文件

#可选参数:
#  -h, --help            显示此帮助信息并退出
#  -d [DELIM], --delimiter [DELIM]
#                        使用 DELIM 分隔词语，而不是用默认的' / '。
#                        若不指定 DELIM，则使用一个空格分隔。
#  -p [DELIM], --pos [DELIM]
#                        启用词性标注；如果指定 DELIM，词语和词性之间
#                        用它分隔，否则用 _ 分隔
#  -D DICT, --dict DICT  使用 DICT 代替默认词典
#  -u USER_DICT, --user-dict USER_DICT
#                        使用 USER_DICT 作为附加词典，与默认词典或自定义词典配合使用
#  -a, --cut-all         全模式分词（不支持词性标注）
#  -n, --no-hmm          不使用隐含马尔可夫模型
#  -q, --quiet           不输出载入信息到 STDERR
#  -V, --version         显示版本信息并退出

#如果没有指定文件名，则使用标准输入。
#--help 选项输出：

#可在anaconda 底下輸入下面指令
#python -m jieba --help