#!/usr/bin/env python
import sys
import os
import re
from elasticsearch import Elasticsearch
import hashlib
import zlib
import base64
import logging

logging.basicConfig()
logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.INFO)


def parse_results(path):
    es = Elasticsearch()
    file_regex = re.compile('^part-.*')
    processed_files = 0
    processed_lines = 0

    for f in os.listdir(path):
        if file_regex.match(f):
            processed_files += 1
            r_file = os.path.join(path, f)
            logger.info('Processing file: %s' % r_file)
            with open(r_file) as res_file:
                for line in res_file:
                    try:
                        (
                            source_page, section, target_page, link_text, text
                        ) = line.split('___', 4)
                        doc_id = hashlib.sha224(source_page+section).hexdigest()
                        document = {
                            'source': source_page,
                            'section': section,
                            'target_page': target_page,
                            'link_text': link_text,
                            'text': zlib.decompress(base64.b64decode(text))
                        }
                        es.index(
                            index="my-index",
                            doc_type="test-type",
                            id=doc_id,
                            body=document
                        )
                        processed_lines += 1
                    except ValueError:
                        logger.error('Could not parse line')
    logger.info('Processing done')
    logger.info('Processed files: %d' % (processed_files))
    logger.info('Processed lines total: %d' % (processed_lines))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Invalid path argument!"
        print "Usage: %s <path_to_results>" % (os.path.basename(__file__))
        exit(1)

    results_path = sys.argv[1]

    if not os.path.isdir(results_path):
        print "Invalid results path. Path is not directory"
        exit(1)

    parse_results(results_path)
