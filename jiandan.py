# coding=utf-8

# __author__ = 'kyu'
import re
import os
import hashlib
import base64

import requests
from lxml import etree
from requests import ConnectionError


def get_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0'
    }
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return resp
        return None
    except ConnectionError:
        print('Error.')
    return None

def get_js_file():
    base_url = 'http://jandan.net/ooxx/'
    html = get_html(base_url).text
    js_url = ''
    try:
        pattern = r'.*<script\ssrc=\"\/\/(cdn.jandan.net\/static\/min.*?)\"><\/script>.*'
        result = re.findall(pattern, html)
        js_url = "http://" + result[len(result) - 1]
    except Exception as e:
        print(e)
    js = get_html(js_url).text

    return js

def get_salt(js):
    pattern = r'jandan_load_img.*?var c.*?"(.*?)"'
    salt = re.findall(pattern, js, re.S)[0]
    # print(salt)
    return salt

def all_img_hash(page_url):
    html = get_html(page_url).text
    doc = etree.HTML(html)
    img_hash = doc.xpath('//span[@class="img-hash"]/text()')
    # print(img_hash)
    return img_hash

def init_md5(str):
    md5 = hashlib.md5()
    md5.update(str.encode('utf-8'))
    return md5.hexdigest()

def decode_base64(data):
    missing_padding = 4 - len(data) % 4
    if missing_padding:
        data += '=' * missing_padding
    return base64.b64decode(data)

def simulation_js(img_hash, salt):
    r = salt if salt else ''
    d = 0
    q = 4
    r = init_md5(r)
    o = init_md5(r[:16])
    n = init_md5(r[16:32])
    if q:
        l = img_hash[:q]
    else: l = ''

    c = o + init_md5(o + l)
    img_hash = img_hash[q:]
    k = decode_base64(img_hash)

    h = list(range(256))
    b = list(range(256))
    for g in range(256):
        b[g] = ord(c[g % len(c)])
    f = 0
    for g in range(256):
        f = (f + h[g] + b[g]) % 256
        h[g], h[f] = h[f], h[g]

    t = ''
    p = f = 0
    for g in range(len(k)):
        p = (p + 1) % 256
        f = (f + h[p]) % 256
        h[p], h[f] = h[f], h[p]
        t += chr(k[g] ^ (h[(h[p] + h[f]) % 256]))
    t = t[26:]
    # print(t)
    return t

def parse_hash(salt, page_url):

    img_hash = all_img_hash(page_url)
    # print(img_hash)
    for i in img_hash:
        yield simulation_js(i, salt)

def download_img(dir_path, img_url):
    filename = img_url[-14:]
    img_content = get_html(img_url).content
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    try:
        with open(os.path.join(dir_path, filename), 'wb') as f:
            f.write(img_content)
            return True
    except Exception as e:
        print(e)
        return False

def main(dir_path, page=10):
    js = get_js_file()
    salt = get_salt(js)
    base_url = 'http://jandan.net/ooxx/'
    for i in range(page+1):
        page_url = base_url + 'page-{}/'.format(58-i)
        print(page_url)

        for img_url in parse_hash(salt, page_url):
            print(img_url)
            r = download_img(dir_path, 'http:' + img_url)

            if r: print('success')


if __name__ == '__main__':
    dir_path = 'E:\jiandan\\'
    main(dir_path)
