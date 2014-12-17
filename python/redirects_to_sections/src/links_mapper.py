#!/usr/bin/env python
from parsers import WikiMarkupParser, WikiHadoopXmlParser
import base64
from hadoop_wrappers import get_pages_stdin

if __name__ == '__main__':
    parser = WikiMarkupParser()
    hadoop_parser = WikiHadoopXmlParser()
    i = 0

    for page in hadoop_parser.parse(get_pages_stdin()):
        i += 1
        title = base64.b64encode(page['title'])
        parser.parse(page['text'])
        for section_redirect in parser.redirects_sections():
            try:
                section_redirect = section_redirect.replace('\t', ' ')

                (page, section, link) = parser.parse_section_redirect(
                    section_redirect
                )
                page = base64.b64encode(page)
                section = base64.b64encode(section)
                link = base64.b64encode(link)
                print "\t".join(
                    (
                        page+'$'+section,
                        link+'\t'+title
                    )
                )
            except (ValueError, TypeError) as e:
                pass
