#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pdb 
import time
import datetime
import sys
import os
import inspect

# Python 2: urlencoding
# from urllib import quote_plus
# Python 3
# from urllib.parse import quote_plus

from flask import Flask
from flask_frozen import Freezer
from flask import render_template, url_for

from flask_flatorgpages import FlatOrgPages


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
    'personal_bit': 'Equiping you with the skills and '
    'knowledge for Natural Running',
    'mission': u'Bærfutt Mission',
    'contact_message': 'Get in touch',
    'copyleft': u'Copyright &copy; Bærfutt %i' % time.localtime().tm_year,
    'name': u'Bærfutt',
    'location': 'Rüschlikon, Switzerland<br>8803',
    'page_title': 'Baerfutt Running',
    'description': 'Natural Running for Humans. Coaching and training for'
    'barefoot running, minimalist running. Product reviews development of'
    'shoes, sandals, other footware,  and relevant innovations.',
    'slogan': 'Natural Running for Humans'
}

special_content = {
    'home': {
        'template': 'home.html',
        'header_pic': "img/logo.svg",
        'email_subject': 'From Baerfutt Homepage: ',
        'email_body': 'Dear Baerfutt,\nI want to learn to run barefoot!'
        '\nKind Regards,\nMe!',
    },
    'event': {
        'template': 'page.html',
        'blurb': 'Event:',
        'email_subject': 'Baerfutt: %s %s',
        'email_body': 'Please give me some information about you.\nName:'
        '\nTelephone Number: \nNormal running distance: ',
        'contact_message': 'Sign me up',
        'feedback_message': 'Give feedback',
    },
    'info': {
        'template': 'page.html',
        'email_subject': 'I want more information: ',
        'email_body': 'Dear Baerfutt,\nI want some more info.'
        '\nKind Regards,\nMe!',
    },
    'archive': {
        'template': 'archive.html',
        'title': 'Baerfutt Event Archive',
        'email_subject': 'From Baerfutt archive: ',
        'email_body': 'Dear Baerfutt,\nWhat about this event archive?'
        '\nKind Regards,\nMe!',
    },
    'impressum': {
        'template': 'page.html',
        'title': 'Impressum / Datenschutz',
        'email_subject': 'Über das Impressum',
        'email_body': '',
    },
}


page_content = {}
for route in special_content:
    page_content[route] = default_content.copy()
    page_content[route].update(special_content[route])


# Views
@app.route('/')
def home():
    route = whoami()
    info = [page for page in pages if 'date' not in page.meta
            and 'Impressum' not in page.meta['title']]
    events = [page for page in pages if 'date' in page.meta]
    # Sort pages by date
    sorted_events = sorted(events, reverse=True,
                           key=lambda event: event.meta['date'])
    upcoming = [page for page in sorted_events if 'date' in page.meta
                and page.meta['date'] >= datetime.date.today()]
    upcoming.reverse()
    past_events = [event for event in sorted_events if event not in upcoming
                   and event.meta['date']
                   >= datetime.date(*time.localtime(time.time()-30*86400)[0:3])]
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
    # set title etc. from org-file
    singlepage = pages.get_or_404(path)
    page_content[route].update(singlepage.meta)
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
    if 'Baerfutt' not in singlepage.meta['title']:
        singlepage.meta['title'] = 'Baerfutt ' + \
                                   singlepage.meta['title']
    # set title etc. from org-file
    page_content[route].update(singlepage.meta)
    # page_content[route]['email_subject'] = \
    #     special_content[route]['email_subject'] % (
    #     singlepage.meta['title'], singlepage.meta['date'].strftime("%F"))
    # page_content[route]['email_body'] = page_content[route]['email_body']
    # pdb.set_trace()
    return render_template(
        page_content[route]['template'],
        page=singlepage,
        past=singlepage.meta['date'] < datetime.date.today(),
        **page_content[route]
    )


@app.route('/archive/')
def archive():
    route = whoami()
    past = [page for page in pages if 'date' in page.meta
            and page.meta['date']
            < datetime.date(*time.localtime(time.time()-30*86400)[0:3])]
    sorted_events = sorted(past, reverse=True,
                           key=lambda event: event.meta['date'])
    keywords = set(event.meta['description'] for event in past
                   if 'description' in event.meta)
    # pdb.set_trace()
    return render_template(
        page_content[route]['template'],
        events=sorted_events,
        keywords=keywords,
        **page_content[route]
    )


@app.route('/impressum/')
def impressum():
    singlepage = pages.get_or_404('impressum')
    route = whoami()
    # pdb.set_trace()
    return render_template(
        page_content[route]['template'],
        page=singlepage,
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
