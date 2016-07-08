#encoding=utf-8
import jieba

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#經過實驗過後,下面這段程式碼需放在import_sys到setdefaultingencoding之後
#不能放在那三行之前,否則會出錯(coding之後)
import jieba.analyse
jieba.set_dictionary('dict.txt.big')

content = open('TripAdvistor東京京都大阪神戶觀光活動細項目條列與旅遊評論字典檔.txt', 'rb').read()

print "Input：", content

tags = jieba.analyse.extract_tags(content, 20)

print "Output："
print ",".join(tags)

#一開始使用這個功能的時候，會不知道 jieba 的 idf 值是從哪裡來的，
# 看了一下 souce code 才知道原來 jieba 有提供一個 idf 的語料庫，
# 但在實務上每個人所使用的語料庫可能會不太一樣，有時我們會想要使用自己的idf 語料庫，
# stop words 的語料庫也可能會想換成自己的，比如目前的結果中，最重要的「座右銘」並沒有出現在關鍵詞裡，
# 我就會想要將「座右銘」加到 idf 語料庫，並讓 idf 值高一點，而「沒有」這個關鍵詞對我來說是沒有用的，
# 我就會想把它加到 stop words 語料庫，這樣「沒有」就不會出現在關鍵詞裡。
#可惜目前 pip 安裝的 jieba 版本並不能切換 idf 及 stop words 語料庫，
# 所以我才會修改了一下 jieba，讓它可以支援 idf 及 stop words 語料庫的切換，
# 目前在 github 上的版本已經可以支援 idf 及 stop words 切換的功能了！
# (p.s. https://github.com/fxsjy/jieba.git)