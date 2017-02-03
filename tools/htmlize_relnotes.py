#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import threading
import sys
import re
import cgi
import io
try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

def determine_url(numstr):
    """ Accesses a github issue URL, and returns the forwarded URL
        This allows us to distinguish pull requests from issues.
    """
    probe_url = 'https://github.com/fish-shell/fish-shell/issues/' + numstr
    req = urlopen(probe_url)
    res = req.geturl()
    return res

def annotate_items(contents):
    """ Looks for text of the form (#123), and annotates it with the URL to the
        appropriate github item
    """
    # Determine item numbers
    pattern = r'#(\d+)'
    matches = re.finditer(pattern, contents)
    # Resolve numstrs to URLs
    numstr_to_url = {}

    def resolve_numstr(numstr):
        numstr_to_url[numstr] = determine_url(numstr)
    threads = []
    for match in matches:
        numstr = match.group(1)
        threads.append(threading.Thread(target=resolve_numstr, args=(numstr,)))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # Perform annotation
    def annotate_1(match):
        numstr = match.group(1)
        if not numstr in numstr_to_url:
            return match.group(0)
        url = numstr_to_url[numstr]
        return '<a href="%s">#%s</a>' % (url, match.group(1))

    return re.sub(pattern, annotate_1, contents)

def backticks_to_code(contents):
    """ Replaces `foo` with <code>foo</code> """
    result_lines = []
    for line in contents.split('\n'):
        comps = line.split('`')
        # <code> goes around every odd item
        for idx in range(len(comps)):
            if idx % 2 == 1:
                comps[idx] = '<code>%s</code>' % comps[idx]
        result_lines.append(''.join(comps))
    return '\n'.join(result_lines)

class Markdown2HTML(object):
    """ Extraordinarily stupid markdown to HTML converter. This only handles ## and - """
    def __init__(self):
        self.in_list = False
        self.result_lines = []

    def emit_surround(self, line, tag):
        indent = ' '*4 if self.in_list else ''
        self.result_lines.append('%s<%s>%s</%s>' % (indent, tag, cgi.escape(line.strip()), tag))

    def emit_open_close_list(self, is_open):
        if is_open and not self.in_list:
            self.in_list = True
            self.result_lines.append('<ul>')
        elif not is_open and self.in_list:
            self.in_list = False
            self.result_lines.append('</ul>')

    def emit_line(self, line):
        self.result_lines.append(cgi.escape(line))

def markdown_2_html(text):
    cv = Markdown2HTML()
    for line in text.split('\n'):
        line = line.strip()
        if not line: continue
        if re.match(r'^-+$', line): continue # skip all dash lines
        cv.emit_open_close_list(line.startswith('-'))
        if line.startswith('-'):
            cv.emit_surround(line[1:], 'li')
        elif line.startswith('###'):
            cv.emit_surround(line[3:], 'h4')
        elif line.startswith('##'):
            cv.emit_surround(line[2:], 'h3')
        else:
            cv.emit_line(line)
    cv.emit_open_close_list(False)
    return '\n'.join(cv.result_lines)

def htmlize(src_path):
    with io.open(src_path, 'r') as fd:
        contents = fd.read()

    contents = markdown_2_html(contents)
    contents = annotate_items(contents)
    contents = backticks_to_code(contents)
    print(contents)

def usage():
    print("""\
Usage: htmlize_relnotes.py file…

htmlize_relnotes.py builds HTML relnotes from GitHub relnotes.
""")

if __name__ == "__main__":
    paths = sys.argv[1:]
    if not paths or "--help" in paths:
        usage()
        sys.exit(-1)
    for path in paths:
        htmlize(path)
