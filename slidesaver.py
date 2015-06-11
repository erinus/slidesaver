#!/usr/bin/python
# -*- coding: utf-8 -*-

import pyquery
import re
import reportlab.lib.utils
import reportlab.pdfgen.canvas
import requests
import sys

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
				pagew, pageh = page.getSize()
				c.setPageSize((pagew, pageh))
				c.drawImage(page, 0, 0, pagew, pageh)
				c.showPage()
				print link
			c.save()
		if resp.text.find('"type":"video"') != -1:
			match = re.search(r'"ppt_location":"(?P<filename>.+?)".+?"video_bucket":"(?P<domain>.+?)".+?"video_extension":"(?P<extension>.+?)"', resp.text)
			if match is not None:
				name = match.group(1)
				# this combination rule comes from http://public.slidesharecdn.com/b/slideview/scripts/combined_video_init.js
				# line 232: var d=this.config.videoBucket+"/"+this.config.pptLocation+"-SD."+this.config.videoExtension
				link = 'http:%s/%s-SD.%s' % (match.group('domain'), match.group('filename'), match.group('extension'))
				resp = requests.get(link)
				with open('output.mp4', 'wb') as f:
					for chunk in resp.iter_content():
						f.write(chunk), 
					f.close()
				print link

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print 'python slidesaver.py [URL]'
	else:
		main()
