#!/usr/bin/env python3
# engines/python/engines.py

import os
import django
from django.conf import settings
from django.template import Engine as DjangoEngine, Context

from bottle import SimpleTemplate
from chameleon import PageTemplate
from Cheetah.Template import Template as CheetahTemplate
import pystache
from jinja2 import Environment, BaseLoader
from mako.template import Template as MakoTemplate
from tornado.template import Template as TornadoTemplate

# Django standalone configuration
settings.configure(
    TEMPLATES=[{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': False,
        'OPTIONS': {},
    }]
)
django.setup()

django_engine = DjangoEngine()

def render_bottle(tpl: str) -> str:
    return SimpleTemplate(tpl).render()

def render_chameleon(tpl: str) -> str:
    return PageTemplate(tpl)()

def render_cheetah(tpl: str) -> str:
    return str(CheetahTemplate(tpl, searchList=[{}]))

def render_pystache(tpl: str) -> str:
    return pystache.render(tpl, {})

def render_jinja2(tpl: str) -> str:
    env = Environment(loader=BaseLoader())
    return env.from_string(tpl).render()

def render_mako(tpl: str) -> str:
    return MakoTemplate(tpl).render()

def render_django(tpl: str) -> str:
    template = django_engine.from_string(tpl)
    return template.render(Context({}))

def render_tornado(tpl: str) -> str:
    return TornadoTemplate(tpl).generate().decode('utf-8')

ENGINES = {
    'bottle':    render_bottle,
    'chameleon': render_chameleon,
    'cheetah':   render_cheetah,
    'django':    render_django,
    'jinja2':    render_jinja2,
    'mako':      render_mako,
    'pystache':  render_pystache,
    'tornado':   render_tornado,
}
