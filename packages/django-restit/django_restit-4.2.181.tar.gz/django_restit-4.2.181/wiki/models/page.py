from django.db import models as dm
from rest import models as rm
from rest import settings
from rest import helpers as rh
from medialib import models as medialib
import re
import mistune
from wiki.renderers import WikiRenderer
from wiki.renderers.mistune import task_list

WIKI_PAGE_VIEW_PERMS = settings.get("WIKI_PAGE_VIEW_PERMS", ["view_wiki", "edit_wiki"])
WIKI_PAGE_EDIT_PERMS = settings.get("WIKI_PAGE_EDIT_PERMS", ["edit_wiki"])


class Page(dm.Model, rm.RestModel, rm.MetaDataModel):
    """
    Blog (a collection of articles)
    """
    class RestMeta:
        SEARCH_FIELDS = ["title", "body"]
        SEARCH_TERMS = ["title", "body"]
        QUERY_FIELDS = ["all_fields", "parent__path"]
        VIEW_PERMS = WIKI_PAGE_VIEW_PERMS
        EDIT_PERMS = WIKI_PAGE_EDIT_PERMS
        UNIQUE_LOOKUP = ["path"]
        DEFAULT_SORT = "-order"
        CAN_DELETE = True
        GRAPHS = {
            "basic": {
                "fields": [
                    "id",
                    "path",
                    "created",
                    "modified",
                    "title",
                    "parent",
                    "order",
                    "path",
                    "slug",
                    "perms"
                ],
            },
            "default": {
                "fields": [
                    "id",
                    "path",
                    "created",
                    "modified",
                    "title",
                    "parent",
                    "order",
                    "slug",
                    "children_paths",
                    "body",
                    ("toHTML", "html")
                ],
                "recurse_into": ["media"],
                "graphs": {
                    "media": "default",
                    "member": "basic",
                    "parent": "basic"
                }
            },
            "rendered": {
                "graphs": {
                    "self": "default",
                    "member": "basic"
                }
            },
            "list": {
                "graphs": {
                    "self": "basic",
                    "member": "basic"
                }
            },
            "toc_child": {
                "graphs": {
                    "self": "basic",
                    "parent": "basic"
                }
            },
            "toc": {
                "extra": ["children", "metadata"],
                "graphs": {
                    "self": "basic",
                    "children": "toc_child"
                }
            },
        }

    created = dm.DateTimeField(auto_now_add=True, editable=False)
    modified = dm.DateTimeField(db_index=True, auto_now=True)

    member = dm.ForeignKey(
        "account.Member", related_name="+",
        blank=True, null=True, default=None,
        on_delete=dm.SET_NULL)

    group = dm.ForeignKey(
        "account.Group", related_name="+", 
        blank=True, null=True, default=None,
        on_delete=dm.SET_NULL)

    parent = dm.ForeignKey(
        "Page", related_name="children",
        default=None, null=True, blank=True,
        on_delete=dm.CASCADE)

    order = dm.IntegerField(default=0, blank=True)

    title = dm.CharField(max_length=255)
    path = dm.CharField(max_length=255, db_index=True)
    slug = dm.SlugField(db_index=True)
    perms = dm.CharField(max_length=255, db_index=True, null=True, default=None)

    body = dm.TextField(blank=True)

    is_active = dm.BooleanField(blank=True, default=True)

    @property
    def children_paths(self):
        return list(self.children.all().values_list("path", flat=True))

    def upload__file(self, fobj, name):
        if fobj is None:
            return

        request = self.getActiveRequest()
        if not self.group:
            lib = request.member.getMediaLibrary("wiki")
        else:
            lib = self.group.getMediaLibrary("wiki")
        kind = medialib.MediaItem.guessMediaKind(fobj)
        media = medialib.MediaItem(library=lib, name=fobj.name, member=request.member, kind=kind, newfile=fobj)
        media.save()
        wmedia = PageMedia(media=media, entry=self, group=self.group, member=request.member)
        wmedia.save()

    def set_remove_media(self, value):
        wmedia = PageMedia.objects.filter(pk=value).last()
        if wmedia:
            wmedia.delete()
    
    def set_slug(self, value):
        sanitized_slug = value.strip().lower().replace(' ', '_')
        sanitized_slug = re.sub(r'\W+', '', sanitized_slug)
        sanitized_slug = re.sub(r'__+', '_', sanitized_slug).strip('_')
        if self.slug != sanitized_slug:
            self._recordRestChange("slug", self.slug)
            self.slug = sanitized_slug
            # confirm slug is unique
            qset = Page.objects.filter(parent=self.parent, slug=sanitized_slug)
            if qset.count():
                self.slug = f"{sanitized_slug}_{qset.count()+1}"

    def on_rest_can_get(self, request):
        if request is None:
            return True
        if self.perms:
            perms = [p.strip() for p in self.perms.split(',')]
        elif self.parent and self.parent.perms:
            perms = [p.strip() for p in self.parent.perms.split(',')]
        else:
            perms = getattr(self.RestMeta, "VIEW_PERMS", None)
        if perms:
            if "public" in perms:
                return True
            if "owner" in perms and self.checkIsOwner(request.member):
                return True
            # we need to check if this user has permission
            group_field = "group"
            status, error, code = rh.requestHasPerms(request, perms, getattr(self, group_field, None))
            if not status:
                return False
        return True

    @classmethod
    def on_rest_list_ready(cls, request, qset=None):
        # need to first sort our list
        qset = cls.restListSort(request, qset)
        out = []
        for page in qset:
            if page.on_rest_can_get(request):
                out.append(page)
        return out

    def on_rest_pre_save(self, request):
        if not self.slug:
            self.set_slug(self.title)
        self.generatePath()

    def on_rest_saved(self, request, is_new=False):
        if self.hasFieldChanged("slug"):
            self.generatePath(True)

    def generatePath(self, propagate=False):
        paths = [self.slug]
        parent = self.parent
        while parent is not None:
            paths.append(parent.slug)
            parent = parent.parent
        paths.reverse()
        path = "/".join(paths)
        if self.path != path:
            self._recordRestChange("path", self.path)
            self.path = path
            if propagate:
                self.save()
        if propagate:
            for child in self.children.all():
                child.generatePath(propagate=True)
        return self.path

    def toHTML(self):
        renderer = WikiRenderer()
        md_engine = mistune.create_markdown(
            renderer=renderer,
            plugins=['def_list', 'url', 'abbr'])
        md_engine.use(task_list.plugin_task_lists)
        md = md_engine(self.body)
        return {
            "toc": renderer.render_toc(),
            "body": md
        }

    @classmethod
    def path_first_existing_parent(cls, path):
        paths = path.split("/")
        while len(paths):
            paths.pop()
            parent = cls.objects.filter(path="/".join(paths)).first()
            if parent is not None:
                return parent
        return None

    @classmethod
    def path_parent(cls, path):
        paths = path.split("/")
        paths.pop()
        return cls.objects.filter(path="/".join(paths)).first()


class PageMetaData(rm.MetaDataBase):
    parent = dm.ForeignKey(Page, related_name="properties", on_delete=dm.CASCADE)


class PageMedia(dm.Model, rm.RestModel):
    class RestMeta:
        VIEW_PERMS = WIKI_PAGE_VIEW_PERMS
        EDIT_PERMS = WIKI_PAGE_EDIT_PERMS
        GRAPHS = {
            "basic": {
                "graphs": {
                    "media": "default"
                }
            },
            "default": {
                "graphs": {
                    "media": "default"
                }
            }
        }
    created = dm.DateTimeField(auto_now_add=True, editable=False)

    member = dm.ForeignKey(
        "account.Member", related_name="+",
        blank=True, null=True, default=None,
        on_delete=dm.SET_NULL)

    group = dm.ForeignKey(
        "account.Group", related_name="+", 
        blank=True, null=True, default=None,
        on_delete=dm.SET_NULL)

    entry = dm.ForeignKey(Page, related_name="media_library", on_delete=dm.CASCADE)
    media = dm.ForeignKey("medialib.MediaItem", related_name="+", on_delete=dm.CASCADE)
