#!/usr/bin/env python

import sys
import re
from parsers import WikiMarkupParser
import base64
import zlib

pages = "<page>" + "".join(sys.stdin.readlines())

with open('/Development/t.txt', 'wb') as f:
    f.write(pages)

c = re.compile("<page>(.*?)</page>", re.MULTILINE | re.DOTALL)
t = re.compile(
    '<text xml:space="preserve">(.*?)</text>',  # boundaries
    re.MULTILINE | re.DOTALL
)
title = re.compile(".*<title>(.*?)</title>.*", re.MULTILINE | re.DOTALL)

parser = WikiMarkupParser()

i = 0

for item in c.finditer(pages):
    i += 1
    page = item.groups(0)[0]
    txt = t.search(page)  # match
    tit = title.match(page)
    tit_p = ''
    if tit:
        tit_p = tit.group(1)
    if txt:
        parser.parse(txt.group(1))
        for s in parser.redirects_sections():
            try:
                (page, section, link) = parser.parse_section_redirect(s)
                print "\t".join(
                    (
                        page+'$'+section,
                        '#LNK#'+link+'\t'+tit_p
                    )
                )
            except (ValueError, TypeError) as e:
                pass

        for p in parser.section_texts(txt.group(1)):
            print "\t".join(
                (
                    tit_p+'$'+p[0],
                    '#TXT#'+base64.b64encode(zlib.compress(p[1]))
                    #'#TXT#SECTION TEXT'
                )
            )
