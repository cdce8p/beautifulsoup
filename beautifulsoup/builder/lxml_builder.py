from lxml import etree
from beautifulsoup.element import Comment, Doctype
from beautifulsoup.builder import TreeBuilder, HTMLTreeBuilder
from beautifulsoup.dammit import UnicodeDammit

class LXMLTreeBuilderForXML(TreeBuilder):
    DEFAULT_PARSER_CLASS = etree.XMLParser

    def __init__(self, parser_class=None):
        # strip_cdata only has an effect on XMLParser. HTMLParser's
        # constructor accepts strip_cdata but ignores it.
        parser_class = parser_class or self.DEFAULT_PARSER_CLASS
        self.parser = parser_class(target=self, strip_cdata=False)
        self.soup = None

    def prepare_markup(self, markup, user_specified_encoding=None,
                       document_declared_encoding=None):
        """
        :return: A 3-tuple (markup, original encoding, encoding
        declared within markup).
        """
        if isinstance(markup, unicode):
            return markup, None, None

        try_encodings = [user_specified_encoding, document_declared_encoding]
        dammit = UnicodeDammit(markup, try_encodings, isHTML=True)
        return (dammit.markup, dammit.original_encoding,
                dammit.declared_html_encoding)

    def feed(self, markup):
        self.parser.feed(markup)
        self.parser.close()

    def close(self):
        pass

    def start(self, name, attrs):
        self.soup.handle_starttag(name, attrs)

    def end(self, name):
        self.soup.handle_endtag(name)

    def pi(self, target, data):
        pass

    def data(self, content):
        self.soup.handle_data(content)

    def doctype(self, name, pubid, system):
        self.soup.endData()
        doctype = Doctype.for_name_and_ids(name, pubid, system)
        self.soup.object_was_parsed(doctype)

    def comment(self, content):
        "Handle comments as Comment objects."
        self.soup.endData()
        self.soup.handle_data(content)
        self.soup.endData(Comment)

    def test_fragment_to_document(self, fragment):
        """See `TreeBuilder`."""
        return u'<html><body>%s</body></html>' % fragment


class LXMLTreeBuilder(LXMLTreeBuilderForXML, HTMLTreeBuilder):

    DEFAULT_PARSER_CLASS = etree.HTMLParser