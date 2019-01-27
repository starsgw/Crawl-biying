# -*- coding: utf-8 -*-
# @Time    : 2018/8/1 11:11
import os

path = os.path.abspath(os.path.dirname(os.getcwd()))
import sys

sys.path.append(path)
import pymongo

# from baidu import env
# 百度元数据mongdb 名字
# COLLECTION_NAME_baidu = 'baidu_20180928'
# sougou元数据mongdb 名字
# COLLECTION_NAME_sougou = 'sougou_20180930'
# google元数据mongdb 名字
# COLLECTION_NAME_google = 'google_20180930'
# 关键词 mongodb名字

# 所下载文档的路径
# 示例"E:\\baidu\\"
# file_path = "D:\\bbsg_file\\"
# 日志名字

# 线上mongo
MONGODB_URI = 'mongodb://59.175.128.24:10327'
MONGODB_NAME = "Two_hundred_million"
WORDS_NAME = 'words_bbsg'
biying = 'biying'

db = pymongo.MongoClient(MONGODB_URI,
                         username='admin',
                         password='123qwe',
                         authSource="admin",
                         authMechanism='SCRAM-SHA-1')
li_two = db[MONGODB_NAME]
li_db_words = li_two[WORDS_NAME]
li_db_words_guoji = li_two['keywords_en']
li_db_biying = li_two[biying]
con_proxy_dongtai = db['proxy']['proxies_ip_dongtai']
new_li_db_biying = li_two["new_biying"]
new_li_db_google = li_two["google"]
new_path_biying = li_two["biying_file_path"]

# MONGODB_NAME_million = "document_download"
# db_million = db[MONGODB_NAME_million]
con_proxy = db['proxy']

file_biying_file = "E:\\files\\%s\\"
