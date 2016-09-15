#!/usr/bin/python3
# -*- coding: utf-8 -*-

# pip3 install pyquery requests reportlab

import json
import pyquery
import re
import requests
import reportlab.lib.utils
import reportlab.pdfgen.canvas
import sys


def main():
    link = sys.argv[1]
    resp = requests.get(link)
    if resp.status_code == 200:
        if 'slideshare.net' in link:
            query = pyquery.PyQuery(resp.text)
            title = re.findall('<h1.*?>(.*)</h1>', resp.text)
            title = re.sub(r'[^a-zA-Z0-9%!-_*.]', ' ', title[0])
            if resp.text.find('"type":"presentation"') != -1:
                images = query('img.slide_image')
                c = reportlab.pdfgen.canvas.Canvas(title + '.pdf')
                for image in images:
                    link = image.attrib['data-full']
                    page = reportlab.lib.utils.ImageReader(link)
                    pagew, pageh = page.getSize()
                    c.setPageSize((pagew, pageh))
                    c.drawImage(page, 0, 0, pagew, pageh)
                    c.showPage()
                    print(link)
                c.save()
            if resp.text.find('"type":"video"') != -1:
                match = re.search(
                    r'"ppt_location":"\
                    (?P<filename>.+?)".+?"video_bucket":"\
                    (?P<domain>.+?)".+?"video_extension":"\
                    (?P<extension>.+?)"', resp.text)
                if match is not None:
                    # this combination rule comes from
                    # http://public.slidesharecdn.com/b/slideview/scripts/combined_video_init.js
                    # line 232: var
                    # d=this.config.videoBucket+"/"+this.config.pptLocation+"-SD."+this.config.videoExtension
                    link = 'http:%s/%s-SD.%s' % (
                        match.group('domain'),
                        match.group('filename'),
                        match.group('extension'))
                    resp = requests.get(link)
                    with open('output.mp4', 'wb') as f:
                        for chunk in resp.iter_content():
                            f.write(chunk),
                        f.close()
                    print(link)
        if 'speakerdeck.com' in link:
            query = pyquery.PyQuery(resp.text)
            title = re.findall('<h1>(.*)</h1>', resp.text)
            title = re.sub(r'[^a-zA-Z0-9]', ' ', title[1])
            embeds = query('div.speakerdeck-embed')
            for embed in embeds:
                code = embed.attrib['data-id']
                resp = requests.get(
                    'https://speakerdeck.com/player/%s' % (code))
                if resp.status_code == 200:
                    match = re.search(r'"slides":(?P<list>\[.+?\])', resp.text)
                    images = json.loads(match.group('list'))
                    c = reportlab.pdfgen.canvas.Canvas(title + '.pdf')
                    for image in images:
                        link = image['original']
                        page = reportlab.lib.utils.ImageReader(link)
                        pagew, pageh = page.getSize()
                        c.setPageSize((pagew, pageh))
                        c.drawImage(page, 0, 0, pagew, pageh)
                        c.showPage()
                        print(link)
                    c.save()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('python slidesaver.py [URL]')
    else:
        main()
