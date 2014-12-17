#!/usr/bin/env python
import os
import re
import base64


def find_results(path):
    file_regex = re.compile('^part-\d+')
    for f in os.listdir(path):
        if file_regex.match(f):
            yield os.path.join(path, f)


def fetch_redirects_results(path):
    redirects = {}

    for r_file in find_results(path):
        with open(r_file) as f:
            for l in f:
                l = l.split('\t', 1)
                (page, section) = [
                    base64.b64decode(l_) for l_ in l[0].split('$')
                ]
                try:
                    redirects[page]
                except:
                    redirects[page] = {}
                redirects[page][section] = l[1].strip()

    return redirects
