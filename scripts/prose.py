"""Read Markdown editorial content using the bundled Python-Markdown renderer."""
from pathlib import Path
from html.parser import HTMLParser
from html import escape
from urllib.parse import urlsplit
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / 'vendor'))
import markdown

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

def read(root, language, key):
    base = (Path(root) / 'content' / language).resolve()
    path = (base / (key + '.md')).resolve()
    if not path.is_relative_to(base):
        raise ValueError(f'Content path is outside {base}: {key}')
    try:
        return path.read_text(encoding='utf-8-sig')
    except FileNotFoundError as error:
        raise ValueError(f'Missing Markdown file: {path}') from error

def render(root, language, key):
    text = read(root, language, key)
    output = markdown.markdown(text, extensions=['fenced_code', 'tables', 'sane_lists'])
    # Content-root-relative links work from both language routes and Pages subpaths.
    # External URLs and same-page fragments are unchanged.
    def local_link(match):
        attr, quote, value = match.groups()
        if urlsplit(value).scheme or value.startswith(('//', '#')):
            return match.group(0)
        value = value.lstrip('/')
        if value.startswith(('images/', 'Files/', 'assets/')) and language == 'en':
            value = '../' + value
        return f'{attr}={quote}{value}{quote}'
    return re.sub(r'(href|src)=([\"\'])(.*?)\2', local_link, output)

def plain(root, language, key):
    parser = TextExtractor()
    parser.feed(render(root, language, key))
    return ' '.join(' '.join(parser.parts).split())
