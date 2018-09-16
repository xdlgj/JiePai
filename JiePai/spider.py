import requests
import json
from requests.exceptions import RequestException
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import re
from config import * 
import pymongo
import os
from hashlib import md5
from multiprocessing import Pool

#content=False为了解决多进程的警告
conn = pymongo.MongoClient(MONGO_URL,content=False)
db = conn[MONGO_DB]


def get_page_index(keyword,offset):
	'''获取JSON对象字符串'''
	data = {
		'autoload':	'true',
		'count':'20',
		'cur_tab':'1',
		'format':'json',
		'from':	'search_tab',
		'keyword':keyword,
		'offset':offset
	}
	headers = {"User-Agent":"Mozilla/5.0"}
	url = "https://www.toutiao.com/search_content/?" + urlencode(data)
	try:
		resopnse = requests.get(url,headers=headers)
		resopnse.encoding = 'utf-8'
		if resopnse.status_code == 200:
			return resopnse.text
		return None
	except RequestException:
		print("请求索引页出错！")
		return None

def parse_page_index(html):
	'''获取每个组图的url'''
	data = json.loads(html)
	if data and 'data' in data.keys():
		for item in data.get('data'):
			#item是一个列表，article_url是图片的路径
			yield item.get("article_url")

def get_page_detail(url):
	'''获取详细页面'''
	headers = {"User-Agent":"Mozilla/5.0"}
	try:
		resopnse = requests.get(url,headers=headers)
		resopnse.encoding = 'utf-8'
		if resopnse.status_code == 200:
			return resopnse.text
		return None
	except RequestException:
		print("请求详细页出错！")
		return None	

def parse_page_detail(html,url):
	'''解析详细页面'''
	soup = BeautifulSoup(html,'lxml')
	title = soup.select("title")[0].get_text()
	images_pattern = re.compile(r'gallery: JSON.parse\("(.*?)"\),',re.S)
	result = images_pattern.search(html)
	if result:
		'''此出花费了我大概2个小时的时间，一直无法解决JSON转换的问题，首先百度好多都说是使用了单引号之类，但是不管怎么修改都
			无法解决，最后想到一个办法，就是将result.group(1)的返回值打印出来，然后复制到一个此时模块，结果是可以转换为JSON
			对象的，然后我觉得应该是编码的问题，事实证明不是编码的问题。因为测试模块是可以转换的，心想一定是python解释器为我们
			做了什么转换，于是print打印出字符串，发现了不同，不同之处就是 \" 变为了 " \\/ 变为了 \/  于是我手动转换，问题终于解决了,'''
		jsonStr = result.group(1).replace(r'\"',r'"').replace(r'\\/',r'\/')
		#jsonStr = '{\"count\":9,\"sub_images\":[{\"url\":\"http:\\/\\/p3.pstatp.com\\/origin\\/pgc-image\\/15308911861360624e6e374\",\"width\":4000,\"url_list\":[{\"url\":\"http:\\/\\/p3.pstatp.com\\/origin\\/pgc-image\\/15308911861360624e6e374\"},{\"url\":\"http:\\/\\/pb9.pstatp.com\\/origin\\/pgc-image\\/15308911861360624e6e374\"},{\"url\":\"http:\\/\\/pb1.pstatp.com\\/origin\\/pgc-image\\/15308911861360624e6e374\"}],\"uri\":\"origin\\/pgc-image\\/15308911861360624e6e374\",\"height\":6000},{\"url\":\"http:\\/\\/p99.pstatp.com\\/origin\\/pgc-image\\/1530891187640293d64a75b\",\"width\":4000,\"url_list\":[{\"url\":\"http:\\/\\/p99.pstatp.com\\/origin\\/pgc-image\\/1530891187640293d64a75b\"},{\"url\":\"http:\\/\\/pb3.pstatp.com\\/origin\\/pgc-image\\/1530891187640293d64a75b\"},{\"url\":\"http:\\/\\/pb1.pstatp.com\\/origin\\/pgc-image\\/1530891187640293d64a75b\"}],\"uri\":\"origin\\/pgc-image\\/1530891187640293d64a75b\",\"height\":6000},{\"url\":\"http:\\/\\/p1.pstatp.com\\/origin\\/pgc-image\\/15308911869350d7e224617\",\"width\":4000,\"url_list\":[{\"url\":\"http:\\/\\/p1.pstatp.com\\/origin\\/pgc-image\\/15308911869350d7e224617\"},{\"url\":\"http:\\/\\/pb3.pstatp.com\\/origin\\/pgc-image\\/15308911869350d7e224617\"},{\"url\":\"http:\\/\\/pb9.pstatp.com\\/origin\\/pgc-image\\/15308911869350d7e224617\"}],\"uri\":\"origin\\/pgc-image\\/15308911869350d7e224617\",\"height\":6000},{\"url\":\"http:\\/\\/p3.pstatp.com\\/origin\\/pgc-image\\/1530891187266752e4a248a\",\"width\":4000,\"url_list\":[{\"url\":\"http:\\/\\/p3.pstatp.com\\/origin\\/pgc-image\\/1530891187266752e4a248a\"},{\"url\":\"http:\\/\\/pb9.pstatp.com\\/origin\\/pgc-image\\/1530891187266752e4a248a\"},{\"url\":\"http:\\/\\/pb1.pstatp.com\\/origin\\/pgc-image\\/1530891187266752e4a248a\"}],\"uri\":\"origin\\/pgc-image\\/1530891187266752e4a248a\",\"height\":6000},{\"url\":\"http:\\/\\/p99.pstatp.com\\/origin\\/pgc-image\\/1530891187573e72c879774\",\"width\":4000,\"url_list\":[{\"url\":\"http:\\/\\/p99.pstatp.com\\/origin\\/pgc-image\\/1530891187573e72c879774\"},{\"url\":\"http:\\/\\/pb3.pstatp.com\\/origin\\/pgc-image\\/1530891187573e72c879774\"},{\"url\":\"http:\\/\\/pb1.pstatp.com\\/origin\\/pgc-image\\/1530891187573e72c879774\"}],\"uri\":\"origin\\/pgc-image\\/1530891187573e72c879774\",\"height\":6000},{\"url\":\"http:\\/\\/p1.pstatp.com\\/origin\\/pgc-image\\/153089118689443f3c70490\",\"width\":4000,\"url_list\":[{\"url\":\"http:\\/\\/p1.pstatp.com\\/origin\\/pgc-image\\/153089118689443f3c70490\"},{\"url\":\"http:\\/\\/pb3.pstatp.com\\/origin\\/pgc-image\\/153089118689443f3c70490\"},{\"url\":\"http:\\/\\/pb9.pstatp.com\\/origin\\/pgc-image\\/153089118689443f3c70490\"}],\"uri\":\"origin\\/pgc-image\\/153089118689443f3c70490\",\"height\":6000},{\"url\":\"http:\\/\\/p99.pstatp.com\\/origin\\/pgc-image\\/1530891186908d2f0efbf63\",\"width\":4000,\"url_list\":[{\"url\":\"http:\\/\\/p99.pstatp.com\\/origin\\/pgc-image\\/1530891186908d2f0efbf63\"},{\"url\":\"http:\\/\\/pb3.pstatp.com\\/origin\\/pgc-image\\/1530891186908d2f0efbf63\"},{\"url\":\"http:\\/\\/pb1.pstatp.com\\/origin\\/pgc-image\\/1530891186908d2f0efbf63\"}],\"uri\":\"origin\\/pgc-image\\/1530891186908d2f0efbf63\",\"height\":6000},{\"url\":\"http:\\/\\/p9.pstatp.com\\/origin\\/pgc-image\\/15308911853816554ab3238\",\"width\":4000,\"url_list\":[{\"url\":\"http:\\/\\/p9.pstatp.com\\/origin\\/pgc-image\\/15308911853816554ab3238\"},{\"url\":\"http:\\/\\/pb1.pstatp.com\\/origin\\/pgc-image\\/15308911853816554ab3238\"},{\"url\":\"http:\\/\\/pb3.pstatp.com\\/origin\\/pgc-image\\/15308911853816554ab3238\"}],\"uri\":\"origin\\/pgc-image\\/15308911853816554ab3238\",\"height\":6000},{\"url\":\"http:\\/\\/p99.pstatp.com\\/origin\\/pgc-image\\/15308912219659b671a7fad\",\"width\":4000,\"url_list\":[{\"url\":\"http:\\/\\/p99.pstatp.com\\/origin\\/pgc-image\\/15308912219659b671a7fad\"},{\"url\":\"http:\\/\\/pb3.pstatp.com\\/origin\\/pgc-image\\/15308912219659b671a7fad\"},{\"url\":\"http:\\/\\/pb1.pstatp.com\\/origin\\/pgc-image\\/15308912219659b671a7fad\"}],\"uri\":\"origin\\/pgc-image\\/15308912219659b671a7fad\",\"height\":6000}],\"max_img_width\":4000,\"labels\":[\"\\u4e09\\u91cc\\u5c6f\",\"\\u6444\\u5f71\"],\"sub_abstracts\":[\" \",\" \",\" \",\" \",\" \",\" \",\" \",\" \",\" \"],\"sub_titles\":[\"\\u8857\\u62cd\\u5317\\u4eac\\uff0c\\u771f\\u5b9e\\u7684\\u4e09\\u91cc\\u5c6f\\u8857\\u62cd\\uff0c\\u6709\\u4f60\\u559c\\u6b22\\u7684\\u5417\\uff1f\",\"\\u8857\\u62cd\\u5317\\u4eac\\uff0c\\u771f\\u5b9e\\u7684\\u4e09\\u91cc\\u5c6f\\u8857\\u62cd\\uff0c\\u6709\\u4f60\\u559c\\u6b22\\u7684\\u5417\\uff1f\",\"\\u8857\\u62cd\\u5317\\u4eac\\uff0c\\u771f\\u5b9e\\u7684\\u4e09\\u91cc\\u5c6f\\u8857\\u62cd\\uff0c\\u6709\\u4f60\\u559c\\u6b22\\u7684\\u5417\\uff1f\",\"\\u8857\\u62cd\\u5317\\u4eac\\uff0c\\u771f\\u5b9e\\u7684\\u4e09\\u91cc\\u5c6f\\u8857\\u62cd\\uff0c\\u6709\\u4f60\\u559c\\u6b22\\u7684\\u5417\\uff1f\",\"\\u8857\\u62cd\\u5317\\u4eac\\uff0c\\u771f\\u5b9e\\u7684\\u4e09\\u91cc\\u5c6f\\u8857\\u62cd\\uff0c\\u6709\\u4f60\\u559c\\u6b22\\u7684\\u5417\\uff1f\",\"\\u8857\\u62cd\\u5317\\u4eac\\uff0c\\u771f\\u5b9e\\u7684\\u4e09\\u91cc\\u5c6f\\u8857\\u62cd\\uff0c\\u6709\\u4f60\\u559c\\u6b22\\u7684\\u5417\\uff1f\",\"\\u8857\\u62cd\\u5317\\u4eac\\uff0c\\u771f\\u5b9e\\u7684\\u4e09\\u91cc\\u5c6f\\u8857\\u62cd\\uff0c\\u6709\\u4f60\\u559c\\u6b22\\u7684\\u5417\\uff1f\",\"\\u8857\\u62cd\\u5317\\u4eac\\uff0c\\u771f\\u5b9e\\u7684\\u4e09\\u91cc\\u5c6f\\u8857\\u62cd\\uff0c\\u6709\\u4f60\\u559c\\u6b22\\u7684\\u5417\\uff1f\",\"\\u8857\\u62cd\\u5317\\u4eac\\uff0c\\u771f\\u5b9e\\u7684\\u4e09\\u91cc\\u5c6f\\u8857\\u62cd\\uff0c\\u6709\\u4f60\\u559c\\u6b22\\u7684\\u5417\\uff1f\"]}'

		data = json.loads(jsonStr)
		if data and 'sub_images' in data.keys():
			sub_images = data.get('sub_images')
			images = [item.get('url') for item in sub_images]
			for image in images:
				download_image(image)
			return {
				'title':title,
				'url':url,
				'images':images
			}

def save_to_mongo(result):
	if db[MONGO_TABLE].insert(result):
		return True
	return False

def download_image(url):
	print("正在下载 %s"%url)
	try:
		resopnse = requests.get(url)
		if resopnse.status_code == 200:
			save_image(resopnse.content)
		return None
	except RequestException:
		print("请求图片出错",url)
		return None

def save_image(content):
	file_path ='{0}/{1}.{2}'.format(os.getcwd(),md5(content).hexdigest(),'jpg')
	if not os.path.exists(file_path):
		with open(file_path,'wb') as f:
			f.write(content)

def main(offset):
	html = get_page_index(KEYWORD,offset)
	for url in parse_page_index(html):
		if url:#存在空的url
			html = get_page_detail(url)
			if html:
				result = parse_page_detail(html,url)
				if result:
					save_to_mongo(result)

if __name__ == "__main__":
	groups = [x * 20 for x in  range(GROUP_START,GROUP_END+1)]
	pool = Pool(4)
	pool.map(main,groups)
