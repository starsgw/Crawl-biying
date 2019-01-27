# -*- coding: utf-8 -*-
# @Time    : 2018/9/7 11:31
import threading
import os

path = os.path.abspath(os.path.dirname(os.getcwd()))
import sys

sys.path.append(path)
import requests
import pymongo, re
import config, log
from random import randint
from hashlib import md5
from time import sleep
from collections import OrderedDict
from lxml.html import etree
from multiprocessing import Process, Queue, Pool

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.12 Safari/537.36',
    'Cookie': 'SNRHOP=I=&TS=; _EDGE_S=mkt=zh-cn&F=1&SID=00F966C9D22C64C91B2E6A20D30265A3; _EDGE_V=1; MUID=0CCBC30295EF6F351F79CFEB94C16E9B; MUIDB=0CCBC30295EF6F351F79CFEB94C16E9B; SRCHD=AF=QBLH; SRCHUID=V=2&GUID=1D704B081EAB4C7D8175C3FE1690E5E8&dmnchg=1; SRCHUSR=DOB=20190119&T=1547864923000; _SS=SID=00F966C9D22C64C91B2E6A20D30265A3&HV=1547865289; SRCHHPGUSR=CW=677&CH=739&DPR=1&UTC=480&WTS=63683461725&NEWWND=1&NRSLT=30&SRCHLANG=&AS=1&NNT=1&HAP=0; ipv6=hit=1547868527108&t=4',
    'Referer': 'https://cn.bing.com/search?q=filetype%3Apdf+%E6%95%99%E8%82%B2&qs=n&form=QBRE&sp=-1&pq=filetype%3Apdf+%E6%95%99%E8%82%B2&sc=3-15&sk=&cvid=A108F0EEEA064BD6B8AC2030B1C365E1'
}
new_url_biying = config.new_li_db_biying
li_db_words = config.li_db_words
con_proxy_dongtai = config.con_proxy_dongtai
log_biying = log.Log("biying_pdf")


class BiYing(object):
    def __init__(self):
        self.pro = self.get_pro()

    def get_pro(self):
        db_one = config.con_proxy
        li_db_one = db_one['proxies_ip']
        xx_pro = []
        li_db_two = li_db_one.find()
        for i in li_db_two:
            ip = i['ip']
            xx_pro.append({"http": ip, "https": ip})
        return xx_pro

    def find_cookie(self, proxies):
        while True:
            try:
                self.ses = requests.session()
                self.ses.get("https://cn.bing.com/", headers=headers, proxies=proxies, timeout=360)
                self.ses.cookies.set('SRCHHPGUSR',
                                     'CW=1172&CH=756&DPR=1&UTC=480&WTS=63683395133&NEWWND=1&NRSLT=30&SRCHLANG=&AS=1&NNT=1&HAP=0')
                self.ses.cookies.set('ipv6', 'hit=1547807555181&t=4')
                self.cookies = self.ses.cookies.get_dict()
                print(self.cookies['_SS'])
                return
            except:
                pass
                # sys.exit()

    def find_ones(self, data, proxies, word_type):
        num = 20
        for x in range(0, 20):
            try:
                data['first'] = str(1 + int(30 * x))
                sleep(0.1)
                try:
                    ip = con_proxy_dongtai.find()[randint(0, 25)]['ip']
                    proxies = {"http": ip, "https": ip}
                    req = requests.get('https://cn.bing.com/search?', params=data, headers=headers, proxies=proxies,
                                       timeout=360)
                    req.close()
                except Exception as e:
                    continue

                if req.status_code == 200:
                    con_et = etree.HTML(req.text)
                    if x == 1:
                        try:
                            num = int(int(re.findall(r'\d+', (con_et.xpath(
                                '//div[@id="b_tween"]/span[@class="sb_count"]/text()')[0]).replace(',', ""))[-1]) / 30)
                        except:
                            pass
                    result_s = con_et.xpath('//ol//li[@class="b_algo"]')
                    res_len = len(result_s)
                    if (x + 1) % 5 == 0:
                        # log_biying.info("page: %s  keyword:%s " % (str(x + 1), data['q']))
                        print("jiansuo_url len(): %s  page: %s  keyword:%s " % (res_len, str(x + 1), data['q']))
                    if res_len == 0:
                        return
                    for xiabiao, nr in enumerate(result_s):
                        try:
                            href = nr.xpath('.//h2/a/@href')[0]
                            update_logo = nr.xpath('.//div[@class="inner"]/a[@class="sb_fav"]')
                            title_s = nr.xpath('.//h2/a//text()')
                            title = "".join(title_s)
                            content_s = nr.xpath('.//div[@class="b_caption"]/p//text()')
                            summary = self.repl("".join(content_s))
                            # print(title)
                            try:
                                logo = update_logo[0]
                                self.insert_mongo_biying(href, title, summary, word_type, data['q'])
                                if xiabiao == (res_len - 1) and (x + 1) % 5 == 0:
                                    print("charu :%s" % (title))
                            except Exception as e:
                                if xiabiao == (res_len - 1) and (x + 1) % 5 == 0:
                                    print(e)
                        except Exception as e:
                            print(e)
                            continue
                    if x >= 1:
                        if res_len < 30:
                            print(res_len, data['q'])
                            return
                        if x >= num - 1:
                            print(data['q'] + "     ", num)
                            return
                else:
                    if req.status_code == 404:
                        continue
                    print("error status_code:%s " % (str(req.status_code)))
            except Exception as e:
                print(e)

    def insert_mongo_biying(self, url, title, summary, word_type, q):
        url_md5 = self.md5_generator(url)
        # num = self.quchong(url_md5)
        # if num != 0:
        #     return
        save = OrderedDict()
        save['url'] = url
        save['title'] = title
        save['summary'] = summary
        save['state'] = 0  # 状态
        save['url_md5'] = url_md5
        save['type'] = word_type  # 类型
        save['q'] = q
        try:
            new_url_biying.insert(save)
        except Exception as e:
            if str(e).find("E11000") > -1:
                # 找到
                nr = new_url_biying.find_one({"url_md5": url_md5})
                # 查看长度
                if len(nr) != 8:
                    # 小于八个字段
                    save['state'] = nr['state']
                    save['_id'] = nr['_id']
                    try:
                        # 删除重插
                        new_url_biying.save(save)
                    #     new_url_biying.update_one({"url_md5":url_md5},{'$set':save})
                    except Exception as e:
                        print(e)

                return
            print("插入失败：%s" % (e))

    def repl(self, text):
        try:
            new_text = re.sub(r"[\n\t\r\u3000\xa0\u2002]", "", text).strip()
            return new_text
        except:
            return text

    def delete_mongo(self, proxies=None):
        print("stare : %s  :%s" % (os.getpid(), proxies))
        # 进入必应获取cookie
        # self.find_cookie(proxies)
        log_biying.info("stare : %s   :%s" % (os.getpid(), proxies))
        data = {
            'q': 'filetype:pdf α反义寡核苷酸 ',
            'qs': 'n',
            'sp': '-1',
            'pq': 'filetype:pdf α反义寡核苷酸 ',
            'sc': '1-15',
            'sk': '',
            'cvid': 'C90A160D0DE54E7693EEEF48C9E5F007',
            'first': '1',
            'FORM': 'PORE',
        }
        while True:
            try:
                # 关键词
                item = li_db_words.find_and_modify({'state_google': 0}, {'$set': {"state_google": 1}})
                if not item:
                    return
                name = item['word']
                # 搜索查询关键词
                data['q'] = 'filetype:%s %s' % ('pdf', name)
                data['pq'] = 'filetype:%s %s' % ('pdf', name)
                self.find_ones(data, proxies, 'pdf')
            except Exception as e:
                print(e)
                # biying_log.info("error delete_mongo: %s"%(e))

    def md5_generator(self, url):
        return md5(url.encode()).hexdigest()

    def proce(self):
        trader = []
        for i in range(1):
            proxies = self.pro[i+150]
            pr = Process(target=self.delete_mongo, args=(proxies,))
            sleep(0.5)
            pr.start()
            trader.append(pr)
        for i in trader:
            i.join()
        print('proce this is pid: %s' % os.getpid())


if __name__ == '__main__':
    BiYing().proce()
