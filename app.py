#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pdb 
import time
import datetime
import sys
import os
import inspect


from flask import Flask
from flask_frozen import Freezer
from flask import render_template, url_for

from content_parsers import FlatOrgPages


def whoami():
    return inspect.stack()[1][3]


def my_render(**args):
    """Simple feeding of args to render_template"""


# Build the website
app = Flask(__name__)

app.config.from_pyfile('settings.py')


# pages = OrgPages(app)
pages = FlatOrgPages(app)


# pdb.set_trace()

default_content = {
    'personal_bit': 'Equiping you with the skills and \
    knowledge for Natural Movement',
    'mission': u'Bærfutt Mission',
    'contact_message': 'Get directly in touch',
    'copyleft': u'Copyright &copy; Bærfutt %i' % time.localtime().tm_year,
    'name': u'Bærfutt',
    'location': 'Zurich, Switzerland<br>8053',
    'title': 'Natural Movement for Humans',
    'description': 'Coaching and training for barefoot running, minimalist \
    running. Product reviews development of shoes, sandals, other footware, \
    and relevant innovations.'
}

page_content = {
    'home': {
        'template': 'home.html',
        'header_pic': "img/header_pic.jpg",
    },
    'event': {
        'template': 'page.html',
        'blurb': 'Event:',
    },
    'info': {
        'template': 'page.html',
    },
    'archive': {
        'template': 'archive.html',
    }
}
for route in page_content:
    page_content[route].update(default_content)


# Views
@app.route('/')
def home():
    route = whoami()
    info = [page for page in pages if 'date' not in page.meta]
    events = [page for page in pages if 'date' in page.meta]
    # Sort pages by date
    sorted_events = sorted(events, reverse=True,
                           key=lambda event: event.meta['date'])
    upcoming = [page for page in sorted_events if 'date' in page.meta
                and page.meta['date'] >= datetime.date.today()]
    past_events = [event for event in sorted_events if event not in upcoming]
    # pdb.set_trace()
    return render_template(
        page_content[route]['template'],
        past_events=past_events,
        upcoming=upcoming,
        info=info,
        **page_content[route]
    )


@app.route('/info/<path:path>/')
def info(path):
    # 'path' is the filename of a page, without the file extension
    route = whoami()
    singlepage = pages.get_or_404(path)
    # pdb.set_trace()
    return render_template(
        page_content[route]['template'],
        page=singlepage,
        **page_content[route]
    )


@app.route('/events/<path:path>/')
def event(path):
    # 'path' is the filename of a page, without the file extension
    singlepage = pages.get_or_404(path)
    route = whoami()
    # description
    page_content[route].update(singlepage.meta)
    # pdb.set_trace()
    return render_template(
        page_content[route]['template'],
        page=singlepage,
        **page_content[route]
    )


@app.route('/archive/')
def archive():
    route = whoami()
    past = [page for page in pages if 'date' in page.meta
            and page.meta['date']
            < datetime.date(*time.localtime(time.time()-14*86400)[0:3])]
    sorted_events = sorted(past, reverse=True,
                           key=lambda event: event.meta['date'])
    keywords = set(event.meta['description'] for event in past
                   if event.meta['description'])
    # pdb.set_trace()
    return render_template(
        page_content[route]['template'],
        events=sorted_events,
        keywords=keywords,
        **page_content[route]
    )


if __name__ == '__main__':
    if "freeze" in sys.argv:
        # Freezer for static website
        freezer = Freezer(app)
        # pdb.set_trace()
        freezer.freeze()
    else:
        port = int(os.environ.get('PORT', 5000))
        # Port 0.0.0.0 so I can see things on a local network
        app.run(host='0.0.0.0', port=port, debug=True)
        # otherwise use the default for localhost (127.0.0.1)
        # app.run(debug=True)
