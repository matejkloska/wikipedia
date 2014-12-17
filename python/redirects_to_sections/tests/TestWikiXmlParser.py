# -*- coding: utf-8 -*-
from kloska_wiki.parsers import *
from .helpers import *
from nose.tools import *
from ddt import ddt, data


l = lambda x: x


def _test_def(x):
    pass


class _test_cls(object):
    def __call__(self):
        pass


@ddt
class TestWikiXmlParser():
    def test_init(self):
        handler = WikiXmlParserHandler(lambda x: x)
        assert_is_instance(WikiXmlParser(handler), WikiXmlParser)

    @data(l, _test_def, _test_cls(), None)
    @raises(ValueError)
    def test_init_error(self, clbck):
        WikiXmlParser(lambda x: x)

    def test_parse_structure(self):
        handler = WikiXmlParserHandler(self.handle_parse_structure)
        parser = WikiXmlParser(handler)
        parser.parse(fixture_path('parser.xml'))

    def handle_parse_structure(self, data):
        combined_keys = {
            'parentid': 2,
        }

        simple_keys = [
            'title', 'comment', 'username', 'format', 'model', 'sha1'
        ]

        combined_keys.update(dict(zip(simple_keys, simple_keys)))

        for (k, v) in combined_keys.iteritems():
            assert_equal(data[k], v)

        lines = data['text'].split('\n')
        lines = [l.strip() for l in lines]
        assert_equal(lines, ['line 1', 'line 2', 'line 3'])
