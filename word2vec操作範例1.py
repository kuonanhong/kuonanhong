# -*- coding: utf-8 -*-
#%load_ext autoreload
#%autoreload 2
#text8是訓練的data
import word2vec
# 以下步驟可分段進行:
#1. Training(訓練過程):
#word2vec.word2phrase('text8', 'text8-phrases', verbose=True)
#word2vec.word2vec('text8-phrases', 'text8.bin', size=100, verbose=True)
#word2vec.word2clusters('text8', 'text8-clusters.txt', 100, verbose=True)

#2. Predictions(預測過程):
model = word2vec.load('text8.bin')
#print model.vocab
#print model.vectors.shape
#print model.vectors
#print model['dog'].shape
#print model['dog'][:10]
#indexes, metrics = model.cosine('socks')
#print indexes, metrics
#print model.vocab[indexes]
#print model.generate_response(indexes, metrics)
#print model.generate_response(indexes, metrics).tolist()

#3. Phrases(相位):
#indexes, metrics = model.cosine('los_angeles')
#print model.generate_response(indexes, metrics).tolist()

#4.Analogies(類似):
#indexes, metrics = model.analogy(pos=['king', 'woman'], neg=['man'], n=10)
#print indexes, metrics
#print model.generate_response(indexes, metrics).tolist()

#Clusters(分群):
clusters = word2vec.load_clusters('text8-clusters.txt')
#print clusters['dog']
#print clusters.get_words_on_cluster(90).shape
#print clusters.get_words_on_cluster(90)[:10]
model.clusters = clusters
indexes, metrics = model.analogy(pos=['paris', 'germany'], neg=['france'], n=10)
print model.generate_response(indexes, metrics).tolist()