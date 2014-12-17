#!/usr/bin/env python
from hadoop_wrappers import reduce_stdin


def process_section(page_section, data):
    if not page_section:
        return

    if len(data) > 1:
        data = list(set(data))
    print '%s\t%s' % (page_section, '\t'.join(data))


if __name__ == '__main__':
    reduce_stdin(process_section)
