# coding: utf-8

"""
    mistune_contrib.highlight
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Support highlight code features for mistune.

    :copyright: (c) 2014 - 2015 by Hsiaoming Yang.
"""

import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


def block_code(text, lang, inlinestyles=False, linenos=False):
    if not lang:
        text = text.strip()
        return '<pre><code>%s</code></pre>\n' % mistune.escape(text)

    try:
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter(
            noclasses=inlinestyles, linenos=linenos
        )
        code = highlight(text, lexer, formatter)
        if linenos:
            return '<div class="highlight-wrapper">%s</div>\n' % code
        return code
    except:
        return '<pre class="%s"><code>%s</code></pre>\n' % (
            lang, mistune.escape(text)
        )


class HighlightMixin(object):
    def block_code(self, text, language="text"):
        # renderer has an options
        inlinestyles = False  #  self.options.get('inlinestyles', False)
        linenos = False  #  self.options.get('linenos', False)
        return block_code(text, language, inlinestyles, linenos)
