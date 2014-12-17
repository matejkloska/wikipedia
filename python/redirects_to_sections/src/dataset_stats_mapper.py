#!/usr/bin/env python
from parsers import WikiMarkupParser, WikiHadoopXmlParser
from hadoop_wrappers import get_pages_stdin
import base64
import json
import argparse


def stats_stdout_format(stats, compressions=False):
    key = base64.b64encode(stats['title'])
    del stats['title']

    return '%s\t%s' % (key, base64.b64encode(json.dumps(stats)))


def handle_mapping(totals=False):
    parser = WikiMarkupParser()
    hadoop_parser = WikiHadoopXmlParser()

    for page in hadoop_parser.parse(get_pages_stdin()):
        parser.parse(page['text'], sections_groups=True)

        sections_levels = [len(s) for s in parser.sections()]
        total_sections = sum(sections_levels)
        redirects = len(parser.redirects())
        redirects_sections = len(parser.redirects_sections())
        if totals:
            stats = {'title': page['title']}
            stats['totals'] = {
                'sections': total_sections,
                'sections_levels': sections_levels,
                'redirects': redirects,
                'redirects_sections': redirects_sections
            }
            print stats_stdout_format(stats)
        else:
            print "$page\t1"
            print "$sect\t "+str(total_sections)
            for i in xrange(0, 6):
                print "$sect_"+str(i)+"\t"+str(sections_levels[i])
            print "$rd_a\t "+str(redirects)
            print "$rd_s\t "+str(redirects_sections)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-a', '--all', help='Map stats per each page',
        default=False, action='store_true'
    )
    args = vars(parser.parse_args())
    handle_mapping(args['all'])
