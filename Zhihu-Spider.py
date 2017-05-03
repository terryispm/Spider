# -*-coding:utf-8 -*-

import requests
from requests.adapters import HTTPAdapter
# import urllib
# import urllib2
import cookielib
import re
import time
import os
from PIL import Image


user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
headers = {'User-Agent': user_agent}
question_num = '27365286'
store_path = 'D:/Terry/Images/'

session = requests.session()

def get_xsrf():
    '''_xsrf 是一个动态变化的参数'''
    index_url = "http://www.zhihu.com"
    index_page = session.get(index_url, headers=headers)
    html = index_page.text
    pattern = r'name="_xsrf" value="(.*?)"'
    _xsrf = re.findall(pattern, html)
    return _xsrf[0]


def getImageUrl():
    url = "https://www.zhihu.com/node/QuestionAnswerListV2"
    method = 'next'
    size = 10
    allImageUrl = []

    #循环直至爬完整个问题的回答
    while(True):
        print '===========offset: ', size
        postdata = {
            'method': 'next',
            'params': '{"url_token":' + str(question_num) + ',"pagesize": "10",' +\
                      '"offset":' + str(size) + "}",
            '_xsrf':get_xsrf(),

        }
        size += 10
        page = session.post(url, headers=headers, data=postdata)
        ret = eval(page.text)
        listMsg = ret['msg']

        if not listMsg:
            print "PIC URL fetch complete, page num: ", (size-10)/10
            return allImageUrl
        pattern = re.compile('data-actualsrc="(.*?)">', re.S)
        for pageUrl in listMsg:
            items = re.findall(pattern, pageUrl)
            for item in items:      #这里去掉得到的图片URL中的转义字符'\\'
                imageUrl = item.replace("\\", "")
                allImageUrl.append(imageUrl)


def saveImagesFromUrl(filePath):
    imagesUrl = getImageUrl()
    #print "Pic Quantity: ", len(imageUrl)
    if not imagesUrl:
        print 'imagesUrl is empty'
        return
    print "Pic Quantity: ", len(imagesUrl)
    nameNumber = 0;
    for image in imagesUrl:
        suffixNum = image.rfind('.')
        suffix = image[suffixNum:]
        fileName = filePath + os.sep + str(nameNumber) + suffix
        nameNumber += 1
        try:
            # 设置超时重试次数及超时时间单位秒
            session.mount(image, HTTPAdapter(max_retries=3))
            response = session.get(image, timeout=20)
            contents = response.content
            with open(fileName, "wb") as pic:
                pic.write(contents)

        except IOError:
            print 'Io error'
        except requests.exceptions.ConnectionError:
            print 'timeout,URL: ', image
    print 'pic download complete'

saveImagesFromUrl(store_path)
