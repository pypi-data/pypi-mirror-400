from .mistune.highlight import HighlightMixin
from .mistune.toc import TocMixin
from .mistune.media import MediaMixin
import mistune
import re

try:
    HTMLRenderer = mistune.HTMLRenderer
except Exception:
    HTMLRenderer = mistune.Renderer


def slugify(text):
    return re.sub(r'\W+', '-', text.strip().lower()).strip('-')

class WikiRenderer(TocMixin, HighlightMixin, MediaMixin, HTMLRenderer):
    def __init__(self, *args, **kwargs):
        # self.enable_math()
        self.reset_toc()
        super(WikiRenderer, self).__init__(*args, **kwargs)

    def heading(self, text, level):
        slug = slugify(text)
        return f'<h{level} id="{slug}">{text}</h{level}>\n'
