# -*- coding: utf-8 -*-
import xml.sax
import os
import re
import itertools
from copy import copy


def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)


class WikiXmlParserHandler(xml.sax.ContentHandler):
    parse_tags = [
        'title', 'text', 'comment', 'username', 'parentid', 'sha1',
        'model', 'format'
    ]
    format_tags = {
        'parentid': int
    }

    def __init__(self, page_parsed):
        self.current_tag = ''
        self.data = {}
        self.page_parsed = page_parsed

    def flush(self):
        self.data = {}

    def startElement(self, tag, attributes):
        self.current_tag = tag

    def endElement(self, tag):
        if tag == 'page':
            for k in self.data.keys():
                self.data[k] = self.data[k].strip()
            for (k, v) in self.format_tags.iteritems():
                self.data[k] = v(self.data[k])
            self.page_parsed(self.data)
            self.data = {}

    def characters(self, content):
        if self.current_tag in self.parse_tags:
            try:
                self.data[self.current_tag] += content
            except KeyError:
                self.data[self.current_tag] = content


class WikiXmlParser:
    def __init__(self, handler):
        if not isinstance(handler, xml.sax.ContentHandler):
            raise ValueError('Invalid parse handler')

        self.parse_handler = handler

    def parse(self, xml_file):
        if not os.path.exists(xml_file):
            raise IOError('XML file not found')

        parser = xml.sax.make_parser()
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        parser.setContentHandler(self.parse_handler)
        parser.parse(xml_file)


class WikiMarkupParser:
    def __init__(self):
        self.re = {
            'sections': re.compile(
                '([=]{2,4}\s*([^=]+?)\s*[=]{2,4})',
                re.MULTILINE | re.DOTALL
            ),

            'redirects': re.compile(
                '''
                (
                    \[\[       # REDIRECT START
                    ([^\]]+?)
                    \]\]       # REDIRECT END
                )+?
                ''',
                re.MULTILINE | re.VERBOSE
            )
        }

    def parse(self, markup):
        # parse sections
        self._sections = []
        for m in self.re['sections'].finditer(markup):
            self._sections.append(m.groups()[1])

        self._redirects = []
        self._redirects_sections = []
        for m in self.re['redirects'].finditer(markup):
            redirect = m.groups()[1].strip()
            try:
                redirect.split('#')[1]
                self._redirects_sections.append(redirect)
            except IndexError:
                self._redirects.append(redirect)

    def sections(self):
        return self._sections

    def section_texts(self, markup):
        d = []
        for pair in pairwise(copy(self.sections())):
            txt = re.search(
                "(==[=]{0,4}.?%s.?==[=]{0,4}?)(.*)==[=]{0,4}.?%s.?[=]{2,6}"
                %
                (re.escape(pair[0]), re.escape(pair[1])),
                markup,
                re.DOTALL | re.MULTILINE
            )
            if txt and txt.group(2):
                d.append((pair[0].strip(), txt.group(2).strip().rstrip('=')))
        return d

    def redirects(self):
        return self._redirects

    def redirects_sections(self):
        return self._redirects_sections

    def parse_section_redirect(self, redirect):
        try:
            (page, params) = redirect.split('#')
            ps = [p.strip() for p in params.split('|')]
            params = [page.strip()] + ps
            return params
        except ValueError:
            return None
