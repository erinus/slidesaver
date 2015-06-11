#!/usr/bin/python
# -*- coding: utf-8 -*-

import lxml.etree
import pyquery
import re
import reportlab.lib.utils
import reportlab.pdfgen.canvas
import requests
import sys
import urlparse

def main():
	resp = requests.get(sys.argv[1])
	if resp.status_code == 200:
		query = pyquery.PyQuery(resp.text)
		if resp.text.find('"type":"presentation"') != -1:
			images = query('img.slide_image')
			page = 0
			c = reportlab.pdfgen.canvas.Canvas('output.pdf')
			for image in images:
				link = image.attrib['data-full']
				page = reportlab.lib.utils.ImageReader(link)
				size = page.getSize()
				c.setPageSize(size)
				c.drawImage(page, 0, 0, size[0], size[1])
				c.showPage()
				print link
			c.save()
		if resp.text.find('"type":"video"') != -1:
			match = re.search(r'"ppt_location":"(.+?)"', resp.text)
			if match is not None:
				name = match.group(1)
				link = 'http://vcdn.slidesharecdn.com/%s-SD.mp4' % (name)
				resp = requests.get(link)
				with open('output.mp4', 'wb') as f:
					for chunk in resp.iter_content():
						f.write(chunk)
					f.close()
				print link

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print 'python slidesaver.py [URL]'
	else:
		main()
