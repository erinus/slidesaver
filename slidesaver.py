#!/usr/bin/python
# -*- coding: utf-8 -*-

import lxml.etree
import re
import sys
import pyquery
import requests
import urlparse

resp = requests.get(sys.argv[1])

if resp.status_code == 200:
	query = pyquery.PyQuery(resp.text)
	if resp.text.find('"type":"presentation"') != -1:
		images = query('img.slide_image')
		for image in images:
			link = image.attrib['data-full']
			name = urlparse.urlsplit(link).path.split('/')[-1]
			resp = requests.get(link)
			with open(name, 'wb') as f:
				for chunk in resp.iter_content():
					f.write(chunk)
				f.close()
			print link
	if resp.text.find('"type":"video"') != -1:
		match = re.search(r'"ppt_location":"(.+?)"', resp.text)
		if match is not None:
			name = match.group(1)
			link = 'http://vcdn.slidesharecdn.com/%s-SD.mp4' % (name)
			resp = requests.get(link)
			with open('%s.mp4' % (name), 'wb') as f:
				for chunk in resp.iter_content():
					f.write(chunk)
				f.close()
			print link
