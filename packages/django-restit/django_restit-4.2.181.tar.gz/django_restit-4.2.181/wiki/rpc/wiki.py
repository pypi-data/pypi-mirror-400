from rest import decorators as rd
from rest import views as rv
from wiki import models as wiki


@rd.url('page')
@rd.url('page/<int:pk>')
@rd.login_required
def rest_on_manage_wiki(request, pk=None):
    return wiki.Page.on_rest_request(request, pk)


@rd.url('path')
@rd.url('path/<path:path>')
@rd.login_required
def rest_on_wiki(request, path=None):
    if path:
        entry = wiki.Page.objects.filter(path=path).last()
        if entry is None:
            # try to find parent
            if request.method == "POST":
                parent = wiki.Page.path_parent(path)
                if parent is not None:
                    slug = path.split("/").pop()
                    entry = wiki.Page.createFromRequest(request, parent=parent, slug=slug)
                    return entry.on_rest_get(request) 
            return rv.restNotFound(request)
        if request.method == "GET":
            return entry.on_rest_get(request)
        elif request.method == "POST":
            return entry.on_rest_post(request)
        elif request.method == "DELETE":
            return entry.on_rest_delete(request)
    return wiki.Page.on_rest_request(request, None)


@rd.url('media')
@rd.url('media/<int:pk>')
@rd.login_required
def rest_on_wiki_media(request, pk=None):
    return wiki.PageMedia.on_rest_request(request, pk)
