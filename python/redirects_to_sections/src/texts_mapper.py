#!/usr/bin/env python

import sys
import re
import os
from parsers import WikiMarkupParser
import base64
import zlib
from results_parser import fetch_redirects_results

links = fetch_redirects_results(
    os.path.realpath(sys.argv[1])
)

pages = "<page>" + "".join(sys.stdin.readlines())

c = re.compile("<page>(.*?)</page>", re.MULTILINE | re.DOTALL)
t = re.compile(
    '<text xml:space="preserve">(.*?)</text>',  # boundaries
    re.MULTILINE | re.DOTALL
)
title = re.compile(".*<title>(.*?)</title>.*", re.MULTILINE | re.DOTALL)
title_skip = re.compile('.*Wikipedia:Categories for deletion.*')

parser = WikiMarkupParser()

i = 0

for item in c.finditer(pages):
    i += 1
    page = item.groups(0)[0]
    txt = t.search(page)  # match
    tit = title.match(page)
    tit_p = ''
    if tit and txt:
        tit_p = tit.group(1)
        if title_skip.match(tit_p):
            continue
    else:
        # skip page with no title
        continue

    try:
        links[tit_p]
    except KeyError:
        continue
    parser.parse(txt.group(1))
    for l in links[tit_p]:
        section_txt = parser.whole_section_text(txt.group(1), l)
        if section_txt:
            print '%s\t%s\t%s\t%s' % (
                base64.b64encode(tit_p),
                base64.b64encode(l),
                base64.b64encode(
                    zlib.compress(section_txt[1], 9)
                ),
                links[tit_p][l]
            )
        continue
    del links[tit_p]