#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import pyquery
import re
import reportlab.lib.utils
import reportlab.pdfgen.canvas
import requests
import sys

def main():
	link = sys.argv[1]
	resp = requests.get(link)
	if resp.status_code == 200:
		if link.startswith('http://www.slideshare.net/') or link.startswith('https://www.slideshare.net/'):
			query = pyquery.PyQuery(resp.text)
			if resp.text.find('"type":"presentation"') != -1:
				images = query('img.slide_image')
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
		if link.startswith('http://speakerdeck.com/') or link.startswith('https://speakerdeck.com/'):
			query = pyquery.PyQuery(resp.text)
			embeds = query('div.speakerdeck-embed')
			for embed in embeds:
				code = embed.attrib['data-id']
				resp = requests.get('https://speakerdeck.com/player/%s' % (code))
				if resp.status_code == 200:
					match = re.search(r'"slides":(?P<list>\[.+?\])', resp.text)
					images = json.loads(match.group('list'))
					c = reportlab.pdfgen.canvas.Canvas('output.pdf')
					for image in images:
						link = image['original']
						page = reportlab.lib.utils.ImageReader(link)
						pagew, pageh = page.getSize()
						c.setPageSize((pagew, pageh))
						c.drawImage(page, 0, 0, pagew, pageh)
						c.showPage()
						print link
					c.save()

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print 'python slidesaver.py [URL]'
	else:
		main()
