#!/usr/bin/env python
import sys
import os
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import hashlib
import zlib
import base64
import logging
from results_parser import find_results
from parsers import pairwise

logging.basicConfig()
logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.INFO)


def parse_results(path):
    es = Elasticsearch(port=9201)
    hashes = {}
    found = 0
    processed_files = 0
    processed_lines = 0
    skipped_links = 0
    empty_doc = 0
    created_documents = 1
    for r_file in find_results(path):
        processed_files += 1
        logger.info('Processing file: %s' % r_file)
        with open(r_file) as res_file:
            logger.info('Preparing documents')
            operations = []
            for line in res_file:
                try:
                    (
                        target_page, section, text, links
                    ) = line.split('\t', 3)
                    target_page = base64.b64decode(target_page)
                    section = base64.b64decode(section)
                    text = zlib.decompress(base64.b64decode(text))
                    if text:
                        text = text.strip()

                    links = [base64.b64decode(l_) for l_ in links.split('\t')]
                    for (link_text, source_page) in pairwise(links):
                        if source_page == target_page:
                            skipped_links += 1
                            continue
                        if text == '':
                            empty_doc += 1
                        doc_id = hashlib.sha224(
                            source_page+target_page+section+link_text
                        ).hexdigest()
                        try:
                            hashes[doc_id]
                            found = found + 1
                            continue
                        except:
                            hashes[doc_id] = None

                        operations.append({
                            '_op_type': 'index',
                            '_index': 'my-index',
                            '_type': 'document',
                            '_id': doc_id,
                            'source_page': source_page,
                            'target_page': target_page,
                            'section': section,
                            'redirect_text': link_text,
                            'text': text
                        })
                        created_documents += 1
                    processed_lines += 1
                except ValueError as e:
                    logger.error('Could not parse line')
            logger.info('Updating index')
            bulk(es, operations, stats_only=True)
    logger.info('Processing done')
    logger.info('Processed files: %d' % (processed_files))
    logger.info('Processed lines total: %d' % (processed_lines))
    logger.info('Created documnets: %d' % (created_documents))
    logger.info('Skipped links: %d' % (skipped_links))
    logger.info('Empty document texts: %d' % (empty_doc))
    logger.info('Found: %d' % (found))

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print "Invalid path argument!"
        print "Usage: %s <es host> <es port> <es index> <path_to_results>" % (os.path.basename(__file__))
        exit(1)

    results_path = sys.argv[1]

    if not os.path.isdir(results_path):
        print "Invalid results path. Path is not directory"
        exit(1)

    parse_results(results_path)
