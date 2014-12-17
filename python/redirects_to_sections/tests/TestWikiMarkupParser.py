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
            [
                ['Section 1', 3],
                ['Section 2', 3],
                ['Section 3', 3]
            ],
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
                ['Description', 2],
                ['History', 2],
                ['Airfield', 2],
                ['LORAN Station Baker', 2],
                ['Flora and fauna', 2],
                ['National Wildlife Refuge', 2],
                ['Ruins and artifacts', 2],
                ['Gallery', 2],
                ['See also', 2],
                ['References', 2],
                ['External links', 2]
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

    def test_subsection_text_parse(self):
        self.parse(fixture_path('parser_subsection_text_parse.xml'))
        markup = WikiMarkupParser()
        markup.parse(self.data['text'])

        assert_equal(
            [
                ['Section 1', 2],
                ['Subsection 1', 3],
                ['SubSubsection 1', 4],
                ['Section 2', 2],
                ['Section 3', 2],
                ['Section 4', 2]
            ],
            markup.sections()
        )



        assert_equal(
            '\n'.join(
                [
                    l.strip() for l in open(
                        fixture_path('parser_subsection_text_parse.txt')
                    ).readlines()
                ]
            ).strip(),
            markup.whole_section_text(
                self.data['text'],
                'Section 1'
            )[1]
        )

        assert_equal(
            'Section 2 Text',
            markup.whole_section_text(
                self.data['text'],
                'Section 2'
            )[1]
        )

        assert_equal(
            'Section 3 Text',
            markup.whole_section_text(
                self.data['text'],
                'Section 3'
            )[1]
        )
