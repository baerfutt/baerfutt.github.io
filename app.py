#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pdb 
import time
import datetime
import sys

from flask import Flask
from flask_flatpages import FlatPages
from flask_frozen import Freezer
from flask import render_template, url_for
from flask_flatpages.utils import pygmented_markdown
from flask_flatpages.page import Page

from itertools import takewhile
import operator
import pypandoc
import re


def convert_org_to_html(text):
    md = pypandoc.convert_text(text, to="markdown_strict",
                               format='org'
                               # , extra_args=['']
                               )
    # print(md)
    # import IPython; IPython.embed()
    # raise
    output = pygmented_markdown(md)
    return output


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


# Build the website
app = Flask(__name__)

app.config.from_pyfile('settings.py')

app.config['FLATPAGES_HTML_RENDERER'] = convert_org_to_html

# pages = OrgPages(app)
pages = FlatOrgPages(app)


# pdb.set_trace()

# Views
@app.route('/')
def home():
    info = [page for page in pages if 'date' not in page.meta]
    events = [page for page in pages if 'date' in page.meta]
    # Sort pages by date
    sorted_events = sorted(events, reverse=True,
                           key=lambda event: event.meta['date'])
    upcoming = [page for page in sorted_events if 'date' in page.meta
                and page.meta['date']
                > datetime.date(*time.localtime(time.time()-86400)[0:3])]
    past_events = [event for event in sorted_events if event not in upcoming]

    # print(info[0].meta)
    # print(sorted_events)
    return render_template('home.html',
                           title='Natural Movement for Humans',
                           name=u'Bærfutt',
                           location='Zurich, Switzerland<br>8053',
                           cards='Projects',
                           header_pic="img/header_pic.jpg",
                           personal_bit="Equiping you with the skills and \
                           knowledge for Natural Movement",
                           copyleft=u"Copyright &copy; Bærfutt %i"
                           % time.localtime().tm_year,
                           info=info,
                           events=upcoming,
                           past_events=past_events
    )


@app.route('/info/<path:path>/')
def info(path):
    # 'path' is the filename of a page, without the file extension
    singlepage = pages.get_or_404(path)
    return render_template('page.html', page=singlepage)


@app.route('/events/<path:path>/')
def page(path):
    # 'path' is the filename of a page, without the file extension
    singlepage = pages.get_or_404(path)
    return render_template('page.html', page=singlepage)


@app.route('/archive/')
def archive():
    past = [page for page in pages if 'date' in page.meta
            and page.meta['date']
            < datetime.date(*time.localtime(time.time()-14*86400)[0:3])]
    sorted_events = sorted(past, reverse=True,
                           key=lambda event: event.meta['date'])
    return render_template('archive.html', events=sorted_events)

if __name__ == '__main__':
    if "freeze" in sys.argv:
        # Freezer for static website
        freezer = Freezer(app)
        # pdb.set_trace()
        freezer.freeze()
    else:
        app.run(debug=True)


# pdb.set_trace()
