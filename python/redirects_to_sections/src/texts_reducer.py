#!/usr/bin/env python

import sys

def process_section(page_section, data):
    if not page_section:
        return

    if len(data) > 1:
        data = list(set(data))
    print '%s\t%s' % (page_section, '\t'.join(data))

    '''(page, section) = page_section.split('$', 1)

    for r in data:
        if r.startswith('#LNK#'):
            try:
                (link_text, original_page) = r[5:].split('\t', 1)
                links[original_page] = link_text
            except Exception as e:
                print '1', e
        else:
            try:
                txt = r[5:]
            except Exception as e:
                print '2', e

    if txt:
        for lnk in links:
            try:
                print '___'.join((page, section, lnk, links[lnk], txt))
            except Exception as e:
                print '3', e'''


if __name__ == '__main__':
    last_key = None
    this_key = None
    running_total = []

    for input_line in sys.stdin:
        input_line = input_line.strip()
        try:
            this_key, value = input_line.split("\t", 1)
            if last_key == this_key:
                running_total.append(value)
            else:
                if last_key:
                    process_section(last_key, running_total)
                running_total = [value]
                last_key = this_key
        except Exception as e:
            pass

    if last_key == this_key:
        process_section(last_key, running_total)
