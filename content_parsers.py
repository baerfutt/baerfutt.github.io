from flask_flatpages import FlatPages
from flask_flatpages.utils import pygmented_markdown
from flask_flatpages.page import Page

from itertools import takewhile
import operator
import pypandoc
import re


class FlatOrgPages(FlatPages):
    def _parse(self, content, path):
        """Parse a flatpage file, i.e. read and parse its meta data and body.
        :return: initialized :class:`Page` instance.
        """
        lines = iter(content.split('\n'))

        # Read lines until an empty line is encountered.
        meta = '\n'.join(takewhile(operator.methodcaller('strip'), lines))
        # Translate simple org header

        def to_lower(matchobj):
            return matchobj.group(1).lower()

        meta = re.sub('\#\+([A-Z_]+:)', to_lower, meta)
        # The rest is the content. `lines` is an iterator so it continues
        # where `itertools.takewhile` left it.
        content = '\n'.join(lines)

        # Now we ready to get HTML renderer function
        html_renderer = self.config('html_renderer')

        # # If function is not callable yet, import it
        # if not callable(html_renderer):
        #     html_renderer = import_string(html_renderer)

        # Make able to pass custom arguments to renderer function
        html_renderer = self._smart_html_renderer(html_renderer)

        # Initialize and return Page instance
        return Page(path, meta, content, html_renderer)


class OrgPage(Page):
    """A class that could translate an org-mode header to have the same
    characteristics as a Page object by redefining the meta method.
    """
    import yaml
    from werkzeug.utils import cached_property

    @cached_property
    def meta(self):
        """A dict of metadata parsed as Emacs Org from the header of the file.
        This redefines the normal meta function.
        """
        def org_header_load(_meta):
            text = zip(re.findall('\#\+([A-Z_]+)', _meta),
                       re.findall(': (.*?)\\r', _meta))
            return {x.lower(): y.strip() for x, y in text}
        meta = org_header_load(self._meta)
        if not meta:
            return {}
        if not isinstance(meta, dict):
            raise ValueError("Expected a dict in metadata for '{0}', got {1}".
                             format(self.path, type(meta).__name__))
        return meta


def convert_org_to_html(text):
    md = pypandoc.convert_text(text, to="markdown_strict",
                               format='org'
                               )
    output = pygmented_markdown(md)
    return output

