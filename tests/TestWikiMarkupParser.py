# -*- coding: utf-8 -*-
from kloska_wiki.parsers import *
from .helpers import *
from nose.tools import *


class TestWikiMarkupParser():
    def setUp(self):
        handler = WikiXmlParserHandler(self.handle_parse_structure)
        self.parser = WikiXmlParser(handler)

    def parse(self, xml_path):
        self.parser.parse(xml_path)

    def handle_parse_structure(self, data):
        self.data = data

    def test_list_sections(self):
        self.parse(fixture_path('parser_comment.xml'))
        markup = WikiMarkupParser()
        markup.parse(self.data['text'])

        assert_equal(
            ['Section 1', 'Section 2', 'Section 3'],
            markup.sections()
        )

        assert_equal(
            ['PAGE#SECTION TITLE|VISIBLE TITLE'],
            markup.redirects_sections()
        )

        assert_equal(
            [],
            markup.redirects()
        )

    def test_list_sample_data(self):
        self.parse(fixture_path('parser_sample.xml'))
        markup = WikiMarkupParser()
        markup.parse(self.data['text'])

        assert_equal(
            [
                'Description', 'History', 'Airfield',
                'LORAN Station Baker', 'Flora and fauna',
                'National Wildlife Refuge', 'Ruins and artifacts',
                'Gallery', 'See also', 'References', 'External links'
            ],
            markup.sections()
        )

        lines = [
            'Starbuck (whaling family)#Obed Starbuck|Obed Starbuck',
            '''Battle of Kwajalein#Gilbert and Marshall Islands
 campaign|Gilbert and Marshall Islands campaign'''
        ]

        assert_equal(
            [l.replace('\n', '') for l in lines],
            markup.redirects_sections()
        )

        assert_equal(
            [
                l.strip() for l in open(
                    fixture_path('parser_sample_redirects_list.txt')
                ).readlines()
            ],
            markup.redirects()
        )
