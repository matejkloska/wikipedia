#!/usr/bin/env python
from hadoop_wrappers import reduce_stdin, reduce_sum_int
import argparse


def process_section(page_section, data):
    if not page_section:
        return

    if len(data) > 1:
        data = list(set(data))
    print '%s\t%s' % (page_section, '\t'.join(data))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-a', '--all', help='Reduce total stats per each page',
        default=False, action='store_true'
    )
    args = vars(parser.parse_args())
    if args['all']:
        reduce_stdin(process_pages_stats)
    else:
        reduce_stdin(reduce_sum_int)
