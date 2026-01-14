# coding: utf-8

"""
    mistune_contrib.highlight
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Support highlight code features for mistune.

    :copyright: (c) 2014 - 2015 by Hsiaoming Yang.
"""

import mistune
import urllib.parse

def parseWidthHeight(link, w=0, h=0):
    o = urllib.parse.urlparse(link)
    if o.query:
        params = urllib.parse.parse_qs(o.query)
        if "md_width" in params:
            w = params.get("md_width")[0]
        if "md_height" in params:
            h = params.get("md_height")[0]
    return w, h

class MediaMixin(object):
    HARMFUL_PROTOCOLS = {
        'javascript:',
        'vbscript:',
        'data:',
    }
    def _safe_url(self, url):
        schemes = self.HARMFUL_PROTOCOLS
        if schemes:
            for s in schemes:
                if url.startswith(s):
                    url = '#harmful-link'
                    break
        return url

    def link(self, link, text=None, title=None):
        label = text
        if text is None:
            text = link
        o = urllib.parse.urlparse(link)
        if o.path.endswith(".mp4"):
            return self.video(link, text, title)
        href = self._safe_url(link)
        params = {"href":href}
        if title:
            params["title"] = title

        if not href.startswith("http") and not href.startswith("#"):
            params["data-action"] = "local_page"
        elif label and href.startswith("http"):
            params["download"] = label
        flat_params = ' '.join("{}='{}'".format(key,val) for (key,val) in list(params.items()))
        return """<a {}>{}</a>""".format(flat_params, (text or link))

    def video(self, link, text=None, title=None, w=0, h=0):
        w, h = parseWidthHeight(link, w, h)
        params = {}
        if title:
            params["title"] = title
        if w:
            params["width"] = w
        if h:
            params["height"] = h
        flat_params = ' '.join("{}='{}'".format(key,val) for (key,val) in list(params.items()))
        return """<video controls {}><source src="{}" type="video/mp4"></video>""".format(flat_params, link)

    def image(self, src, alt="", title=None):
        if not src:
            return ""
        o = urllib.parse.urlparse(src)
        if o.path.endswith(".mp4"):
            return self.video(src, alt, title)
        w, h = parseWidthHeight(src)
        params = {}
        if title:
            params["title"] = title
        if w:
            params["width"] = w
        if h:
            params["height"] = h
        if alt:
            params["alt"] = alt
        params["src"] = src

        flat_params = ' '.join("{}='{}'".format(key,val) for (key,val) in list(params.items()))
        return '<img {} />'.format(flat_params)
