# -*- coding: utf-8 -*-
import xml.sax
import os
import re
import itertools
from copy import copy
import HTMLParser


def pairwise(iterable):
    a = iter(iterable)
    return itertools.izip(a, a)


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


class WikiHadoopXmlParser:
    def __init__(self):
        self.regex = {}
        self.regex['page'] = re.compile(
            "<page>(.*?)</page>", re.MULTILINE | re.DOTALL
        )
        self.regex['page_text'] = re.compile(
            '<text xml:space="preserve">(.*?)</text>',  # boundaries
            re.MULTILINE | re.DOTALL
        )
        self.regex['title'] = re.compile(
            ".*<title>(.*?)</title>.*", re.MULTILINE | re.DOTALL
        )
        self.regex['title_skip'] = re.compile(
            '.*Wikipedia:Categories for deletion.*'
        )

    def parse(self, pages_xml, skip_empty_title=True,
              skip_empty_text=True, skip_defined_pages=True):
        for page in self.regex['page'].finditer(pages_xml):
            page = page.groups(0)[0]

            page_text = self.regex['page_text'].search(page)
            page_title = ''
            if page_text:
                page_text = page_text.group(1)
                page_title = self.regex['title'].match(page)
                if page_title:
                    page_title = page_title.group(1)
                    if skip_defined_pages and \
                       self.regex['title_skip'].match(page_title):
                        continue
                else:
                    if skip_empty_title:
                        continue
                    else:
                        page_title = ''
            else:
                if skip_empty_text:
                    continue
                page_text = ''

            yield {'title': page_title, 'text': page_text}


class WikiMarkupParser:
    def __init__(self):
        self.re = {
            'sections': re.compile(
                '(([=]{2,4})\s*([^=]+?)\s*[=]{2,4})',
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

        self.html_parser = HTMLParser.HTMLParser()

    def parse(self, markup, sections_groups=False):
        # parse sections
        self._sections = []
        self._sections_grouped = [[] for i in xrange(0, 6)]
        if sections_groups:
            self._sections = [[] for i in xrange(0, 6)]

        for m in self.re['sections'].finditer(markup):
            if sections_groups:
                self._sections[len(m.groups()[1])].append(m.groups()[2])
            else:
                self._sections.append([m.groups()[2], len(m.groups()[1])])
            self._sections_grouped[len(m.groups()[1])].append(m.groups()[2])

        self._redirects = []
        self._redirects_sections = []
        r = re.compile('^[^|]+?#[^#|]+?\|[^|]+$', re.DOTALL)
        for m in self.re['redirects'].finditer(markup):
            redirect = m.groups()[1].strip()
            try:
                s = redirect.split('#')
                s[1]
                if len(s) > 2:
                    raise IndexError
                if s[0].strip() != '' and r.match(redirect):
                    self._redirects_sections.append(redirect)
            except IndexError:
                self._redirects.append(redirect)

    def sections(self):
        return self._sections

    def sections_middle_text(self, markup, section_from, section_to):
        if section_to != '':
            regex = """
                (=[=]{0,5}.?%s.?=[=]{0,5}?)(.*)=[=]{0,5}.?%s.?[=]{1,6}
            """ % (
                re.escape(section_from), re.escape(section_to)
            )
        else:
            regex = """
            (=[=]{0,5}.?%s.?=[=]{0,5}?)(.*)
            """ % (
                re.escape(section_from)
            )
        txt = re.search(
            regex.strip(),
            markup,
            re.DOTALL | re.MULTILINE
        )
        if txt and txt.group(2):
            return (section_from.strip(), txt.group(2).strip().strip('=').strip())

    def section_texts(self, markup):
        for pair in pairwise(copy(self.sections())):
            text = self.sections_middle_text(markup, pair[0], pair[1])
            if text:
                yield text

    def whole_section_text(self, markup, section):
        try:
            original_found = False
            sect_level = -1
            sect_to = ''
            for s in self._sections:
                if not original_found and s[0] == section:
                    sect_level = s[1]
                elif s[1] <= sect_level:
                    sect_to = s[0]
                    break

            return self.sections_middle_text(markup, section, sect_to)
        except IndexError as e:
            print e
            return None

    def redirects(self):
        return self._redirects

    def redirects_sections(self):
        return self._redirects_sections

    def parse_section_redirect(self, redirect):
        try:
            (page, params) = self.html_parser.unescape(
                redirect.decode('utf-8')
            ).split('#')
            ps = [p.strip() for p in params.split('|')]
            params = [page.strip()] + ps
            return params
        except ValueError as e:
            return None
