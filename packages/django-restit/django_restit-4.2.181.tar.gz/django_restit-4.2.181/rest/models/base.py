from datetime import datetime, date, timedelta
from decimal import Decimal
from objict import objict
from io import StringIO
import importlib

from django.db import models as dm
from django.db.transaction import atomic
from django.apps import apps
from django.db import connection

from rest import helpers as rh
from rest import errors as re
from rest.encryption import ENCRYPTER, DECRYPTER
from rest import crypto
from rest import settings
from rest import search
from .metadata import MetaDataBase, MetaDataModel

DB_ROUTING_MAPS = settings.get("DB_ROUTING_MAPS", {})
TWO_DECIMAL_PLACES = Decimal(10) ** -2
EXCEPTION_ON_LIST_PERM_DENIED = settings.get("EXCEPTION_ON_LIST_PERM_DENIED", True)
ALLOW_BATCHING = settings.get("ALLOW_BATCHING", False)

GRAPH_HELPERS = objict()
GRAPH_HELPERS.restGet = None
GRAPH_HELPERS.get_request = None
GRAPH_HELPERS.views = None


class RestModel(object):
    class __RestMeta__:
        NO_SAVE_FIELDS = ["id", "pk", "created", "modified"]
        NO_SHOW_FIELDS = ["password"]
        WHITELISTED = ["merchant", "group", "user", "member"]

    class RestMeta:
        NO_SAVE_FIELDS = []
        SAVE_FIELDS = []
        GRAPHS = {}

    @staticmethod
    def generateUUID(*args, **kwargs):
        return crypto.generateUUID(*args, **kwargs)

    @classmethod
    def buildGraph(cls, name):
        # we need to build it
        if hasattr(cls.RestMeta, "GRAPHS"):
            graphs = cls.RestMeta.GRAPHS
            if isinstance(graphs, tuple):
                # this most likely means a typo in the definition, with an extra ","
                rh.log_error(f"{cls.__name__}.buildGraph({name}) is a tuple, check for comma after RestMeta.GRAPHS")
                graphs = graphs[0]
            if name not in graphs and name != "basic":
                name = "default"
            if name in graphs:
                graph = graphs[name]
            else:
                graph = {}
        else:
            graph = {}

        if "no_uscore" not in graph:
            graph["no_uscore"] = False

        no_show_fields = RestModel.__RestMeta__.NO_SHOW_FIELDS
        if hasattr(cls.RestMeta, "NO_SHOW_FIELDS"):
            no_show_fields = cls.RestMeta.NO_SHOW_FIELDS

        field_names = []
        for f in cls._meta.fields:
            if not f.name.endswith("_ptr"):
                if f.name not in no_show_fields:
                    field_names.append(f.name)

        if "graphs" in graph and name != "basic":
            if "recurse_into" not in graph:
                graph["recurse_into"] = []
            if "fields" in graph:
                graph["fields"] = graph["fields"]
            elif "fields" not in graph and "self" in graph["graphs"]:
                graph["fields"] = []
            else:
                graph["fields"] = field_names

            for field in graph["graphs"]:
                gname = graph["graphs"][field]
                size = None
                ForeignModel = None
                sort = None

                if field.startswith("generic__"):
                    if field not in graph["recurse_into"]:
                        graph["recurse_into"].append((field, gname))
                        continue

                if isinstance(gname, dict):
                    fm_name = gname.get("model")
                    gname = gname.get("graph")
                    if not gname:
                        gname = "default"
                    if fm_name:
                        a_name, m_name = fm_name.split(".")
                        ForeignModel = RestModel.getModel(a_name, m_name)

                if not field or field == "self":
                    # this means it is referencing self
                    foreign_graph = cls.buildGraph(gname)
                    for part in foreign_graph:
                        if part not in graph:
                            graph[part] = foreign_graph[part]
                        else:
                            for f in foreign_graph[part]:
                                if f not in graph[part]:
                                    graph[part].append(f)
                    continue

                if not ForeignModel:
                    ForeignModel = cls.get_fk_model(field)
                if not ForeignModel:
                    rh.log_print("no foreignkey: {0}".format(field))
                    continue

                if field not in graph["recurse_into"]:
                    graph["recurse_into"].append(field)

                if not hasattr(ForeignModel, "getGraph"):
                    # print "NO getGraph"
                    continue
                foreign_graph = ForeignModel.getGraph(gname)

                for part in ["fields", "recurse_into", "extra", "exclude"]:
                    if part not in foreign_graph:
                        continue
                    graph_part = foreign_graph[part]
                    if part not in graph:
                        graph[part] = []
                    root_part = graph[part]
                    for f in graph_part:
                        if type(f) is tuple:
                            f1, f2 = f
                            nfname = ("{0}.{1}".format(field, f1), f2)
                        elif graph["no_uscore"] and '_' in f:
                            f1, f2 = f, f.replace('_', '').split('.')[-1]
                            nfname = ("{0}.{1}".format(field, f1), f2)
                        else:
                            nfname = "{0}.{1}".format(field, f)
                        if nfname not in root_part:
                            root_part.append(nfname)
            del graph["graphs"]
        elif "graphs" in graph:
            del graph["graphs"]

        if "fields" not in graph:
            if graph["no_uscore"]:
                graph["fields"] = []
                for f in field_names:
                    if "_" in f:
                        f1, f2 = f, f.lower().replace('_', '')
                        graph["fields"].append((f1, f2))
                    else:
                        graph["fields"].append(f)
            else:
                graph["fields"] = field_names

        if "no_uscore" in graph:
            del graph["no_uscore"]
        return graph

    @classmethod
    def ro_objects(cls):
        using = getattr(cls.RestMeta, "RO_DATABASE", None)
        if using is None:
            using = getattr(cls.RestMeta, "DATABASE", None)
        # if using is None:
        #   if settings.DATABASES.get("readonly", None) != None:
        #       using = "readonly"
        if using:
            using = cls.get_db_mapping(using)
            return cls.objects.using(using)
        return cls.objects

    @classmethod
    def rw_objects(cls):
        using = getattr(cls.RestMeta, "DATABASE", None)
        if using:
            using = cls.get_db_mapping(using)
            return cls.objects.using(using)
        return cls.objects

    @atomic
    def saveNow(self, **kwargs):
        return self.save(**kwargs)

    def safeSave(self, **kwargs):
        using = getattr(self.RestMeta, "DATABASE", None)
        if using:
            using = self.get_db_mapping(using)
            return self.save(using=using, **kwargs)
        return self.save(**kwargs)

    @classmethod
    def getGraph(cls, name):
        if name is None:
            name = "default"
        graph_key = f"_graph_{name}__"
        if hasattr(cls._meta, graph_key):
            return getattr(cls._meta, graph_key)
        graph = cls.buildGraph(name)
        setattr(cls._meta, graph_key, graph)
        return graph

    def toGraph(self, request=None, graph="basic"):
        RestModel._setupGraphHelpers()
        if not request:
            request = GRAPH_HELPERS.get_request()
        return GRAPH_HELPERS.restGet(request, self, return_httpresponse=False, **self.getGraph(graph))

    def getFieldValue(self, name, default=None):
        fields = name.split('.')
        obj = self
        for f in fields:
            if not hasattr(obj, f):
                return default
            obj = getattr(obj, f, None)
            if obj is None:
                return obj
        return obj

    @classmethod
    def getActiveLogger(cls):
        return rh.getLogger(cls.getActiveRequest())

    @classmethod
    def getActiveMember(cls):
        request = cls.getActiveRequest()
        if request:
            return request.member
        return None

    @classmethod
    def getActiveRequest(cls):
        return rh.getActiveRequest()

    @classmethod
    def getFromRequest(cls, request):
        key = cls.get_class_name().lower()
        key_p = "{0}_id".format(key)
        lookup_fields = [key, key_p]
        using = getattr(cls.RestMeta, "DATABASE", None)
        for field in lookup_fields:
            value = request.DATA.get(field)
            if value:
                if not using:
                    obj = cls.objects.filter(pk=value).first()
                else:
                    obj = cls.objects.using(using).filter(pk=value).first()
                if obj:
                    return obj
        lookup_fields = getattr(cls.RestMeta, "UNIQUE_LOOKUP", [])
        for field in lookup_fields:
            value = request.DATA.get([field, "{}_{}".format(key, field)])
            if value:
                q = {}
                q[field] = value
                if not using:
                    obj = cls.objects.filter(**q).first()
                else:
                    obj = cls.objects.using(using).filter(**q).first()
                if obj:
                    return obj
        return None

    @classmethod
    def getFromPK(cls, pk):
        if isinstance(pk, dict):
            fields = pk
            if "id" in fields:
                pk = fields.get("id")
            elif "pk" in fields:
                pk = fields.get("pk")
            else:
                lookup_fields = getattr(cls.RestMeta, "UNIQUE_LOOKUP", [])
                for field in lookup_fields:
                    if field in fields:
                        pk = fields.get(field)
                        q = {}
                        q[field] = pk
                        return cls.objects.filter(**q).first()
            pk = None
        if pk in (None, ""):
            return None
        using = getattr(cls.RestMeta, "DATABASE", None)
        if using:
            return cls.objects.using(using).filter(pk=pk).first()
        if isinstance(pk, str) and pk.isdigit():
            pk = int(pk)

        if isinstance(pk, int):
            return cls.objects.filter(pk=pk).first()
        # concerns with this being misused
        lookup_fields = getattr(cls.RestMeta, "UNIQUE_LOOKUP", [])
        for field in lookup_fields:
            q = {}
            q[field] = pk
            obj = cls.objects.filter(**q).first()
            if obj is not None:
                return obj
        return None

    @classmethod
    def restEncrypt(cls, data):
        if ENCRYPTER:
            return ENCRYPTER.encrypt(data)
        return data

    @staticmethod
    def restGetModel(app_name, model_name):
        return apps.get_model(app_name, model_name)

    @staticmethod
    def getModel(app_name, model_name):
        return apps.get_model(app_name, model_name)

    @staticmethod
    def getModelInstance(app_name, model_name, **kwargs):
        Model = apps.get_model(app_name, model_name)
        return Model.objects.filter(**kwargs).last()

    @staticmethod
    def createModelInstance(app_name, model_name, **kwargs):
        Model = apps.get_model(app_name, model_name)
        return Model(**kwargs)

    def restGetGenericModel(self, field):
        # called by the rest module to magically parse
        # a component that is marked genericr elation in a graph
        if not hasattr(self, field):
            rh.log_print("model has no field: {0}".format(field))
            return None

        name = getattr(self, field)
        if not name or "." not in name:
            return None
        a_name, m_name = name.split(".")
        model = RestModel.getModel(a_name, m_name)
        if not model:
            rh.log_print("GENERIC MODEL DOES NOT EXIST: {0}".format(name))
        return model

    def restGetGenericRelation(self, field):
        # called by the rest module to magically parse
        # a component that is marked genericrelation in a graph
        GenericModel = self.restGetGenericModel(field)
        if not GenericModel:
            return None
        # verify user has permission to access this model
        key = getattr(self, "{0}_id".format(field))
        obj = GenericModel.rw_objects().filter(pk=key).first()
        if obj is None:
            return None
        if hasattr(obj, "on_rest_can_get"):
            if not obj.on_rest_can_get(self.getActiveRequest()):
                return None
        return obj

    @classmethod
    def get_db_mapping(cls, name):
        if name in DB_ROUTING_MAPS:
            return DB_ROUTING_MAPS[name]
        return name

    @classmethod
    def restGetModelDB(cls, default=None):
        if hasattr(cls, "RestMeta"):
            return cls.get_db_mapping(getattr(cls.RestMeta, "DATABASE", default))
        return default

    @property
    def has_model_changed(self):
        if hasattr(self, "_changed__"):
            return len(self._changed__) > 0
        return False

    def saveFields(self, allow_null=True, **kwargs):
        """
        Helper method to save a list of fields
        """
        self._changed__ = objict()
        for key, value in list(kwargs.items()):
            if value is None and not allow_null:
                continue
            self.restSaveField(key, value)
        if len(self._changed__):
            self.save()

    def restSaveField(self, fieldname, value, has_fields=False, has_no_fields=False, using=None):
        if not hasattr(self, "_changed__"):
            self._changed__ = objict()

        if fieldname.startswith("_"):
            return
        if not hasattr(self, "_field_names__"):
            self._field_names__ = [f.name for f in self._meta.get_fields()]
        # if not hasattr(self, "_related_field_names__"):
        #     self._related_field_names__ = self.get_related_name_fields()
        # print "saving field: {0} = {1}".format(fieldname, value)
        if fieldname in RestModel.__RestMeta__.NO_SAVE_FIELDS:
            return
        if has_no_fields and fieldname in self.RestMeta.NO_SAVE_FIELDS:
            return
        if has_fields and fieldname not in self.RestMeta.SAVE_FIELDS:
            return
        if fieldname.endswith("_id") and not self.get_field_type(fieldname):
            # django will have ForeignKeys with _id, we don't want that, on_delete=dm.CASCADE
            fieldname = fieldname[:-3]
        setter = F"set_{fieldname}"
        if hasattr(self, setter):
            getattr(self, setter)(value)
            return

        if fieldname in self._field_names__:
            # TODO check if it is a function
            if isinstance(value, dm.Model):
                setattr(self, fieldname, value)
                self._changed__[fieldname] = True
                return
            ForeignModel = self.get_fk_model(fieldname)
            if ForeignModel:
                if isinstance(value, dict):
                    obj = getattr(self, fieldname, None)
                    if obj is None:
                        if hasattr(ForeignModel, "getFromPK"):
                            obj = ForeignModel.getFromPK(value)
                        if obj is None:
                            obj = ForeignModel()
                    else:
                        if hasattr(ForeignModel, "getFromPK"):
                            new_obj = ForeignModel.getFromPK(value)
                        if new_obj is None:
                            lookup_fields = getattr(ForeignModel.RestMeta, "UNIQUE_LOOKUP", [])
                            if "id" in value or any(name in value for name in lookup_fields):
                                obj = ForeignModel()
                        elif new_obj.pk != obj.pk:
                            obj = new_obj
                    if using is None:
                        using = self.restGetModelDB()
                    obj.checkPermsAndSave(None, value, using=using)
                    # rh.log_print("{} vs {}".format(self._state.db, obj._state.db))
                    # rh.log_print("saving FK to {} ({}.{}) - {}".format(fieldname, using, obj.pk, type(obj)), value)
                    setattr(self, fieldname, obj)
                    self._changed__[fieldname] = True
                    return
                elif hasattr(ForeignModel, "getFromPK"):
                    value = ForeignModel.getFromPK(value)
                elif isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
                    value = ForeignModel.objects.filter(pk=int(value)).first()
                elif "MediaItem" in ForeignModel.__name__:
                    if value:
                        self.saveMediaFile(value, fieldname, None, True)
                    return
                elif not bool(value):
                    value = None
            else:
                # field_model, model, direct, mm = self._meta.get_field_by_name(fieldname)
                field_model = self._meta.get_field(fieldname)
                # hack to handle save datetime fields correctly from floats
                try:
                    if field_model and value != None:
                        field_model_name = field_model.__class__.__name__
                        if field_model_name == "DateTimeField":
                            value = rh.parseDateTime(value)
                            # value = datetime.fromtimestamp(float(value))
                        elif field_model_name == "DateField":
                            value = rh.parseDate(value, as_date=True)
                        elif field_model_name == "IntegerField":
                            value = int(value)
                        elif field_model_name == "FloatField":
                            value = float(value)
                        elif field_model_name == "CurrencyField":
                            value = Decimal(value).quantize(TWO_DECIMAL_PLACES)
                        elif field_model_name == "BooleanField":
                            if value in [True, 1, 'True', 'true', '1', 't', 'y', 'yes']:
                                value = True
                            else:
                                value = False
                except Exception:
                    return
            if hasattr(self, fieldname) and getattr(self, fieldname) != value:
                self._changed__[fieldname] = getattr(self, fieldname)
            setattr(self, fieldname, value)

    def saveFromRequest(self, request, **kwargs):
        if "files" not in kwargs:
            kwargs["files"] = request.FILES
        return self.checkPermsAndSave(request, request.DATA, **kwargs)

    def hasFieldChanged(self, fieldname):
        if not hasattr(self, "_changed__"):
            return False
        return fieldname in self._changed__

    def _recordRestChange(self, fieldname, old_value):
        if not hasattr(self, "_changed__"):
            self._changed__ = objict()
        if "." in fieldname:
            fields = fieldname.split('.')
            root = self._changed__
            for f in fields[:-1]:
                if f not in root:
                    root[f] = objict()
                root = root[f]
            root[fields[-1]] = old_value
        else:
            self._changed__[fieldname] = old_value

    def checkPermsAndSave(self, request, data, files=None, **kwargs):
        can_save = getattr(self.RestMeta, "CAN_SAVE", True)
        if not can_save:
            raise re.PermissionDeniedException("saving not allowed via rest for this model.")
        # check check for save permissions
        if request is None:
            request = RestModel.getActiveRequest()
            if request is None:
                request = objict(member=None, FILES=[], DATA=objict(), is_authenticated=False, is_local=True)
        self.onRestCanSave(request, data, kwargs)
        return self.saveFromDict(request, data, files=None, **kwargs)

    def saveFromDict(self, request, data, files=None, **kwargs):
        save_media_files = getattr(self.RestMeta, "SAVE_MEDIA_FILES", False) or getattr(self.RestMeta, "SAVE_MEDIA_FILES_BY_NAME", False)
        is_new = self.id is None
        has_fields = hasattr(self.RestMeta, "SAVE_FIELDS") and len(self.RestMeta.SAVE_FIELDS)
        has_no_fields = hasattr(self.RestMeta, "NO_SAVE_FIELDS") and len(self.RestMeta.NO_SAVE_FIELDS)
        self._field_names__ = [f.name for f in self._meta.get_fields()]
        # fix for multidatabase support and using readonly db for get
        self._state.db = kwargs.get("using", self.restGetModelDB("default"))
        auto_save_fields = getattr(self.RestMeta, "AUTO_SAVE", None)
        if auto_save_fields:
            # rh.log_print(auto_save_fields)
            for field in auto_save_fields:
                # rh.log_print(field)
                if isinstance(field, tuple):
                    m_field, req_field = field
                else:
                    m_field = field
                    req_field = field
                if request is not None:
                    req_value = getattr(request, req_field, None)
                    if req_value is not None:
                        data[m_field] = req_value
            # rh.log_print(data)
        self._changed__ = objict()
        if hasattr(self.RestMeta, "POST_SAVE_FIELDS"):
            post_save_fields = self.RestMeta.POST_SAVE_FIELDS
        else:
            post_save_fields = []
        using = kwargs.get("using", self.restGetModelDB())
        deferred = {}
        group_fields = {}
        for fieldname in data:
            # we allow override via kwargs
            value = data.get(fieldname)
            if "." in fieldname:
                gname = fieldname[:fieldname.find('.')]
                fname = fieldname[fieldname.find('.')+1:]
                setter = "set_{0}".format(gname)
                if hasattr(self, setter):
                    if gname not in group_fields:
                        group_fields[gname] = {}
                    group_fields[gname][fname] = value
                    continue
            if fieldname in post_save_fields or fieldname.startswith("metadata"):
                deferred[fieldname] = value
                continue
            if fieldname not in kwargs:
                self.restSaveField(fieldname, value, has_fields, has_no_fields, using=using)
        for key, value in list(kwargs.items()):
            if key in post_save_fields:
                deferred[fieldname] = value
                continue
            self.restSaveField(key, value, has_fields, has_no_fields, using=using)

        rfiles = self.restSaveFiles(request, files)
        if getattr(self.RestMeta, "ALWAYS_SAVE", True) or self.has_model_changed:
            self.on_rest_pre_save(request)
            self.save(using=using)
        for key, value in list(deferred.items()):
            self.restSaveField(key, value, has_fields, has_no_fields, using=using)

        if len(deferred):
            self.save(using=using)

        if rfiles is not None and len(rfiles) and save_media_files:
            self.restSaveMediaFiles(rfiles)

        # these setters are responsible for saving themselves
        for gname in group_fields:
            setter = "set_{0}".format(gname)
            getattr(self, setter)(request, group_fields[gname])

        self.on_rest_saved(request, is_new=is_new)
        if is_new:
            self.on_rest_created(request)
        return self

    def restSaveFiles(self, request, files=None):
        if files is None and request is not None:
            files = request.FILES
        if not files:
            return files
        remaining_files = {}
        for name in files:
            key = f"upload__{name}"
            if hasattr(self, key):
                getattr(self, key)(files[name], name)
            else:
                ForeignModel = self.get_fk_model(name)
                if ForeignModel and ForeignModel.__name__ == "MediaItem":
                    # rh.log_print("saving media file: {}".format(name))
                    self.saveMediaFile(files[name], name, files[name].name)
                else:
                    remaining_files[name] = files[name]
        return remaining_files

    def restSaveMediaFiles(self, files=None):
        MediaItemRef = RestModel.getModel("medialib", "MediaItemRef")
        component = self.get_class_name(True)
        # rh.log_print("saving media files refs: {}".format(component))
        for name in files:
            mi = self.saveMediaFile(files[name], name, is_local=False)
            mr = None
            if getattr(self.RestMeta, "SAVE_MEDIA_FILES_BY_NAME", False):
                # use existing reference
                mr = MediaItemRef.objects.filter(component=component, component_id=self.id, media__name=name).last()
                if mr:
                    rh.log_print(F"existing media files refs: {name}.{component}.{self.id}")
                    mr.media = mi
                    mr.save()
            if mr is None:
                mr = MediaItemRef(media=mi, component=component, component_id=self.id)
                mr.save()

    def getMediaFiles(self):
        MediaItemRef = RestModel.getModel("medialib", "MediaItemRef")
        component = self.get_class_name(True)
        return MediaItemRef.objects.filter(component=component, component_id=self.id)

    def media_files(self, graph="simple"):
        MediaItemRef = RestModel.getModel("medialib", "MediaItemRef")
        component = self.get_class_name(True)
        qset = MediaItemRef.objects.filter(component=component, component_id=self.id)
        if not getattr(self.RestMeta, "SAVE_MEDIA_FILES_BY_NAME", False):
            return MediaItemRef.restList(self.getActiveRequest(), qset, graph, None, False)

        out = {}
        for mr in qset:
            out[mr.media.name] = mr.media.toDict("basic")
        return out

    def changesFromDict(self, data):
        deltas = []
        field_names = [f.name for f in self._meta.get_fields()]
        for key in data:
            if key not in field_names:
                continue
            # we allow override via kwargs
            value = data.get(key)

            # field_model, model, direct, mm = self._meta.get_field_by_name(key)
            field_model = self._meta.get_field(key)
            # hack to handle save datetime fields correctly from floats
            try:
                if field_model and value != None:
                    field_model_name = field_model.__class__.__name__
                    if field_model_name == "DateTimeField":
                        value = datetime.fromtimestamp(float(value))
                    elif field_model_name == "DateField":
                        value = rh.parseDate(value)
                    elif field_model_name == "IntegerField":
                        value = int(value)
                    elif field_model_name == "FloatField":
                        value = float(value)
                    elif field_model_name == "CurrencyField":
                        value = Decimal(value).quantize(TWO_DECIMAL_PLACES)
                if hasattr(self, key) and getattr(self, key) != value:
                    deltas.append(key)
            except:
                pass
        return deltas

    def copyFieldsFrom(self, obj, fields):
        for f in fields:
            if hasattr(self, f):
                setattr(self, f, getattr(obj, f))

    def saveMediaFile(self, file, name, file_name=None, is_base64=False, group=None, is_local=True):
        """
        Generic method to save a media file
        """
        if file_name is None:
            file_name = name
        MediaItem = RestModel.getModel("medialib", "MediaItem")
        # make sure we set the name base64_data
        if is_base64:
            mi = MediaItem(name=file_name, base64_data=file, group=group)
        elif isinstance(file, str):
            if file.startswith("https:") or file.startswith("http:"):
                mi = MediaItem(name=file_name, downloadurl=file, group=group)
            else:
                file = StringIO(file)
                file.size = len(file)
                file.name = file_name
                mi = MediaItem(name=file_name, group=group, newfile=file)
        else:
            mi = MediaItem(name=file_name, newfile=file, group=group)
        # rh.log_print(F"saving media file: {name}")
        mi.save()
        if is_local:
            setattr(self, name, mi)
        return mi

    def updateLogModel(self, request, model):
        if not request:
            request = self.getActiveRequest()
        if not request or not hasattr(request, "setLogModel"):
            rh.log_print("request does not support setLogModel")
            return
        if not self.id:
            self.save()
        request.setLogModel(model, self.id)

    def checkIsOwner(self, member):
        owner_field = getattr(self.RestMeta, "OWNER_FIELD", None)
        if owner_field is None:
            owner_field = getattr(self.RestMeta, "VIEW_PERMS_MEMBER_FIELD", None)
        if owner_field is not None:
            owner = getattr(self, owner_field, None)
            return member == owner
        return False

    def on_rest_pre_get(self, request):
        pass

    def on_rest_can_get(self, request):
        if request is None:
            return True
        perms = getattr(self.RestMeta, "VIEW_PERMS", None)
        if perms:
            if "owner" in perms and self.checkIsOwner(request.member):
                return True
            # we need to check if this user has permission
            group_field = getattr(self.RestMeta, "GROUP_FIELD", "group")
            status, error, code = rh.requestHasPerms(request, perms, getattr(self, group_field, None))
            if not status:
                raise re.PermissionDeniedException(error + " getting", code)
        return True

    def on_rest_get(self, request):
        # check view permissions
        if not self.on_rest_can_get(request):
            return self.restStatus(request, False, error="permission denied", error_code=402)
        self.on_rest_pre_get(request)
        return self.restGet(request)

    def onRestCanDelete(self, request=None, data=None, extended=None):
        self.onRestCheckSavePerms(request, data, extended)

    def onRestCanSave(self, request=None, data=None, extended=None):
        self.onRestCheckSavePerms(request, data, extended)

    def onRestCheckSavePerms(self, request=None, data=None, extended=None):
        if request is None:
            request = self.getActiveRequest()
            if request is None:
                return True
        if getattr(request, "is_local", False):
            return True
        perms = getattr(self.RestMeta, "SAVE_PERMS", getattr(self.RestMeta, "VIEW_PERMS", None))
        if self.id is None:
            perms = getattr(self.RestMeta, "CREATE_PERMS", perms)
        if perms:
            if "owner" in perms and self.checkIsOwner(request.member):
                return True
            # we need to check if this user has permission
            group_field = getattr(self.RestMeta, "GROUP_FIELD", "group")
            # rh.log_error(F"group field={group_field}")
            if group_field == "self" and self.pk:
                group = self
            elif self.id is None:
                group = None
                if extended is not None:
                    group = extended.get(group_field, None)
                if group is None:
                    if data is not None:
                        group = data.get(group_field, None)
                if group is None:
                    if request is not None:
                        group = request.DATA.get(group_field, None)
            elif "__" in group_field and hasattr(self, "group"):
                group = self.group
            elif "__" in group_field:
                fields = group_field.split("__")
                group = self
                for field in fields:
                    group = getattr(group, field, None)
                    if group is None:
                        break
            else:
                group = getattr(self, group_field, None)
            status, error, code = rh.requestHasPerms(request, perms, group)
            if not status:
                if self.id is None and code == 402:
                    code = 435
                    rh.log_error(F"permission denied onRestCheckSavePerms: {self.__class__.__name__}\ngroup: {group}\nstatus={status}, error={error}, code={code}\nperms:", perms)
                raise re.PermissionDeniedException(error + " saving", code)

    def on_rest_post(self, request):
        self.checkPermsAndSave(request, request.DATA)
        status_only = request.DATA.get("status_only", False, field_type=bool)
        if status_only:
            return self.restStatus(request, True)
        graph = request.DATA.get("graph", "default")
        return self.restGet(request, graph)

    def on_rest_pre_save(self, request, **kwargs):
        pass

    def on_rest_created(self, request):
        pass

    def on_rest_saved(self, request, is_new=False):
        pass

    def on_rest_delete(self, request, force=False):
        can_delete = getattr(self.RestMeta, "CAN_DELETE", False)
        if not can_delete:
            raise re.PermissionDeniedException(f"deletion not allowed for {self.get_class_name()}", 438)
        if not force:
            self.onRestCanDelete(request)
        self.on_rest_deleted(request)
        self.delete()
        RestModel._setupGraphHelpers()
        return self.restStatus(request, True)

    def on_rest_deleted(self, request):
        self.auditLog(F"deleted {self.pk}", "deleted", level=8)
        if request and request.member:
            request.member.auditLog(F"deleted {self.get_class_name(True)}:{self.pk}", "deleted", level=8)

    def auditLog(self, message, action="log", path=None, level=0, group=None, method=None):
        if group is None and hasattr(self, "group"):
            group = self.group
        PLOG = self.getModel("auditlog", "PersistentLog")
        component = self.get_class_name(True)
        PLOG.log(message=message, action=action, path=path, level=level, method=method, component=component, pkey=self.id, group=group)

    @classmethod
    def restList(cls, request, qset, graph=None, totals=None, return_httpresponse=True):
        RestModel._setupGraphHelpers()
        sort = request.DATA.get("sort", getattr(cls.RestMeta, "DEFAULT_SORT", "-id"))
        if sort:
            # make sure we have the sort field
            tsort = sort
            if tsort.startswith("-"):
                tsort = sort[1:]
            if "__" not in tsort and not cls.hasField(tsort):
                sort = "-id"

        if totals:
            fields = totals
            totals = {}
            for tf in fields:
                cls_method = "qset_totals_{}".format(tf)
                if hasattr(cls, cls_method):
                    totals[tf] = getattr(cls, cls_method)(qset, request)
        if not graph and request is not None:
            graph = request.DATA.get("graph", "default")
        return GRAPH_HELPERS.restList(
            request, qset, sort=sort, totals=totals,
            return_httpresponse=return_httpresponse,
            response_params=dict(graph=graph),
            **cls.getGraph(graph))

    @classmethod
    def restListSort(cls, request, qset):
        from rest.serializers.collection import sort_list
        sort = request.DATA.get("sort", getattr(cls.RestMeta, "DEFAULT_SORT", "-id"))
        sort = request.DATA.get("sort")
        if sort:
            qset, sort_args = sort_list(qset, sort)
        return qset

    @classmethod
    def toList(cls, qset, graph=None, totals=None, request=None):
        if request is None:
            request = cls.getActiveRequest()
        return cls.restList(request, qset, graph, totals, False)

    @classmethod
    def restListEstimatedCount(cls, request, qset):
        # TODO attempt to make this work with the qset,
        # right now it gets an estimated count of the entire table
        if getattr(cls.RestMeta, "ESTIMATE_COUNTS", False):
            if connection.vendor == 'postgresql':
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT reltuples::bigint FROM pg_class WHERE relname = '{cls._meta.db_table}'")
                    return cursor.fetchone()[0]
        return qset.count()

    def restStatus(self, request, status, **kwargs):
        RestModel._setupGraphHelpers()
        return GRAPH_HELPERS.restStatus(request, status, **kwargs)

    def restGet(self, request, graph=None, as_dict=False):
        RestModel._setupGraphHelpers()
        if not request:
            request = self.getActiveRequest()
        if not graph and request:
            graph = request.DATA.get("graph", "default")
        elif not graph:
            graph = "default"
        return_response = not as_dict
        return GRAPH_HELPERS.restGet(request, self, return_httpresponse=return_response, **self.getGraph(graph))

    def toDict(self, graph=None, schema=None):
        RestModel._setupGraphHelpers()
        if schema is None:
            return self.restGet(None, graph=graph, as_dict=True)
        return GRAPH_HELPERS.restGet(None, self, return_httpresponse=False, **schema)

    def __str__(self):
        return f"<{self.get_class_name(True)}>"

    @classmethod
    def on_rest_list_filter(cls, request, qset=None):
        # override on do any pre filters
        return cls.on_rest_list_perms(request, qset)

    @classmethod
    def on_rest_filter_member_field(cls, request, qset):
        member_field = getattr(cls.RestMeta, "VIEW_PERMS_MEMBER_FIELD", None)
        if member_field is None:
            # this would be permission denied
            member_field = getattr(cls.RestMeta, "OWNER_FIELD", None)
        if member_field is None:
            if EXCEPTION_ON_LIST_PERM_DENIED:
                raise re.PermissionDeniedException(f"user does not have permission to access {cls.get_class_name()}")
            return cls.objects.none()
        # rh.log_error(dict(**{member_field: request.member}))
        return qset.filter(**{member_field: request.member})

    @classmethod
    def on_rest_list_has_perms(cls, request, perms, qset=None):
        if request.auth_model is not None:
            if request.auth_model.hasPerm(perms):
                return True
        if request.member is None:
            return False
        if request.member.hasPerm(perms):
            return True
        if request.group and request.member.hasGroupPerm(request.group, perms):
            return True
        return False

    @classmethod
    def on_rest_list_perms(cls, request, qset=None):
        perms = getattr(cls.RestMeta, "LIST_PERMS_GROUP", None)
        if perms is None:
            perms = getattr(cls.RestMeta, "VIEW_PERMS", None)
        has_perms = True
        if perms is not None:
            has_perms = cls.on_rest_list_has_perms(request, perms, qset)

        if request.group:
            qset = cls.on_rest_filter_children(request, qset)
        if not has_perms:
            return cls.on_rest_filter_member_field(request, qset)
        return qset

    @classmethod
    def on_rest_filter_children(cls, request, qset=None):
        # rh.log_error("filter by group?")
        group_field = getattr(cls.RestMeta, "GROUP_FIELD", "group")
        if group_field is None or ("__" not in group_field and not cls.has_model_field_name(group_field)):
            return qset
        parent_kinds = getattr(cls.RestMeta, "LIST_PARENT_KINDS", ["org"])
        if request.DATA.get("child_groups") or request.group.kind in parent_kinds:
            list_depth = getattr(cls.RestMeta, "LIST_CHILD_DEPTH", 0)
            ids = request.group.getAllChildrenIds(depth=list_depth)
            ids.append(request.group.id)
            # to avoid future filtering issues remove group
            request.group = None
            request.DATA.remove(group_field)
            if group_field != "group":
                # rh.debug("removing group field!!")
                request.DATA.remove("group")
            q = {}
            q["{}_id__in".format(group_field)] = ids
            return qset.filter(**q)
        elif "__" in group_field:
            q = {}
            q[group_field] = request.group.id
            qset = qset.filter(**q)
            # rh.log_error(q, qset.count())
        return qset

    @classmethod
    def on_rest_list_ready(cls, request, qset=None):
        # override on do any post filters
        # rh.log_error("RAW SQL")
        # rh.log_error(qset.query)
        return qset

    @classmethod
    def on_rest_date_filter(cls, request, qset=None):
        dr_start = request.DATA.get("dr_start", field_type=datetime)
        dr_end = request.DATA.get("dr_end", field_type=datetime)
        dr_end_str = request.DATA.get("dr_end")
        tr_start = request.DATA.get("tr_start")
        tr_end = request.DATA.get("tr_end")
        dr_offset = request.DATA.get("dr_offset", 0, field_type=int)
        dr_tz = request.DATA.get("dr_timezone")

        # if we only specify timerange lets set the start to today
        if dr_start is None:
            if tr_start is not None:
                dr_start = datetime.now()

        if dr_start is None:
            return qset

        if dr_end is None:
            dr_end = datetime.now() + timedelta(hours=5)
        elif dr_end == dr_start and not tr_end:
            dr_end = dr_start + timedelta(days=1)
        elif "-" in dr_end_str or "/" in dr_end_str:
            dr_end = dr_end + timedelta(days=1)

        if tr_start is not None:
            dr_start = rh.updateTimeFromString(dr_start, tr_start)
        if tr_end is not None:
            dr_end = request.DATA.get("dr_end", field_type=datetime)
            dr_end = rh.updateTimeFromString(dr_end, tr_end)

        if dr_tz is not None:
            dr_start = request.DATA.get("dr_start", field_type=datetime)
            dr_end = request.DATA.get("dr_end", field_type=datetime)
            dr_eod = request.DATA.get("dr_eod", 0, field_type=int)
            dr_granularity = request.DATA.get("granularity", "day")
            dr_start, dr_end = rh.getDateRange(dr_start, dr_end, dr_granularity, dr_tz, hour=dr_eod)
        elif dr_offset > 0:
            dr_start = dr_start + timedelta(minutes=dr_offset)
            dr_end = dr_end + timedelta(minutes=dr_offset)

        rh.debug("tr_end changing", str(dr_start), str(dr_end))
        dr_field = request.DATA.get("dr_field", getattr(cls.RestMeta, "DATE_RANGE_FIELD", "created"))
        q = dict()
        q["{}__gte".format(dr_field)] = dr_start
        q["{}__lte".format(dr_field)] = dr_end
        qset = qset.filter(**q)
        return qset

    @classmethod
    def on_rest_list(cls, request, qset=None):
        qset = cls.on_rest_list_query(request, qset)
        graph = request.DATA.get("graph", "list")
        format = request.DATA.get("format")
        if format:
            return cls.on_rest_list_format(request, format, qset)
        totals = request.DATA.getlist("totals", None)
        return cls.restList(request, qset, graph, totals)

    @classmethod
    def on_rest_list_query(cls, request, qset=None):
        cls._boundRest()
        cls.on_rest_set_query_defaults(request)
        request.rest_class = cls
        if qset is None:
            qset = cls.ro_objects().all()
        qset = cls.on_rest_list_filter(request, qset)
        qset = cls.filterFromRequest(request, qset)
        qset = cls.queryFromRequest(request, qset)
        qset = cls.searchFromRequest(request, qset)
        qset = cls.on_rest_date_filter(request, qset)
        qset = cls.on_rest_list_ready(request, qset)
        if request.default_rest_filters:
            qset = qset.filter(**request.default_rest_filters)
        return qset

    @classmethod
    def getSortArgs(cls, sort):
        if not bool(sort):
            return []

        elif sort.endswith("_display"):
            # fix for django _display kinds being sorted
            sort = sort[:sort.find("_display")]
        sort_args = []
        for s in sort.split(","):
            if "metadata" in s:
                continue
            if s.endswith("_display"):
                # s = s[:s.find("_display")]
                continue
            s = s.replace('.', '__')
            sort_args.append(s)
        return sort_args

    @classmethod
    def getRestFormatFields(cls, format, graph=None):
        fields = []
        if hasattr(cls.RestMeta, "FORMATS"):
            fields = cls.RestMeta.FORMATS.get(format, fields)
        if len(fields) == 0:
            if format == "json":
                g = cls.getGraph("default")
                if "fields" in g:
                    return g["fields"]
            no_show_fields = RestModel.__RestMeta__.NO_SHOW_FIELDS
            if hasattr(cls.RestMeta, "NO_SHOW_FIELDS"):
                no_show_fields = cls.RestMeta.NO_SHOW_FIELDS
            for f in cls._meta.fields:
                if not f.name.endswith("_ptr"):
                    if f.name not in no_show_fields:
                        fields.append(f.name)
        return fields

    @classmethod
    def on_rest_list_format(cls, request, format, qset):
        if format in ["summary", "summary_only"]:
            return cls.on_rest_list_summary(request, qset)
        fields = None
        if format == "json":
            g = cls.getGraph(request.DATA.get("graph", "download"))
            if g and "fields" in g:
                fields = g["fields"]
        if fields is None:
            fields = cls.getRestFormatFields(format)
        if fields or format == "json":
            name = request.DATA.get("format_filename", None)
            format_size = request.DATA.get("format_size", 10000)
            localize = request.DATA.get("localize", None, field_type=dict)
            if name is None:
                ext = format
                if "_" in ext:
                    ext = ext[:ext.find("_")]
                name = "{}.{}".format(cls.get_class_name(), ext)
            # print "csv size: {}".format(qset.count())
            sort = request.DATA.get("sort", getattr(cls.RestMeta, "DEFAULT_SORT", "-id"))
            sort_args = cls.getSortArgs(sort)
            if sort_args:
                try:
                    qset = qset.order_by(*sort_args)
                except Exception:
                    pass
            cls._boundRest()
            if format.startswith("json"):
                return GRAPH_HELPERS.views.restJSON(
                    request, qset, fields,
                    name, format_size, localize=localize)
            elif format.startswith("csv"):
                return GRAPH_HELPERS.views.restCSV(
                    request, qset, fields,
                    name, format_size, localize=localize)
            elif format == "xlsx":
                return GRAPH_HELPERS.views.restExcel(
                    request, qset, fields,
                    name, format_size, localize=localize)
            elif format == "flat":
                return GRAPH_HELPERS.views.restFlat(
                    request, qset, fields,
                    name, format_size, localize=localize)

    @classmethod
    def on_rest_list_summary(cls, request, qset):
        cls._boundRest()
        summary_info = getattr(cls.RestMeta, "SUMMARY_FIELDS", {})
        output = objict()
        output.count = qset.count()
        for key, value in summary_info.items():
            if key == "sum":
                res = rh.getSum(qset, *value)
                if isinstance(res, dict):
                    output.update(res)
                else:
                    output[value[0]] = res
            elif key == "avg":
                for f in value:
                    output["avg_{}".format(f)] = rh.getAverage(qset, f)
            elif key == "max":
                for f in value:
                    output["max_{}".format(f)] = rh.getMax(qset, f)
            elif isinstance(value, dict):
                if "|" in key:
                    fields = key.split("|")
                    if len(fields) > 1:
                        lbl = fields[0]
                        action = fields[1]
                        field = None
                    if len(fields) > 2:
                        field = fields[2]
                else:
                    action = "count"
                    lbl = key
                    field = None
                act_qset = qset.filter(**value)
                if action == "count":
                    output[lbl] = act_qset.count()
                elif action == "sum":
                    output[lbl] = rh.getSum(act_qset, field)
                elif action == "avg":
                    output[lbl] = rh.getAverage(act_qset, field)
                elif action == "max":
                    output[lbl] = rh.getMax(act_qset, field)
        return GRAPH_HELPERS.restGet(request, output)

    @classmethod
    def getRestBatchCreateFilter(cls, item, exclude=["id", "pk", "created", "modified"], include=None):
        if isinstance(include, list):
            return {key: item[key] for key in include if key in item}
        # ignore related fields
        rfs = cls.get_related_name_fields()
        return {key: item[key] for key in item if key not in exclude and cls.hasField(key) and key not in rfs}

    @classmethod
    def on_rest_batch(cls, request, action):
        # this method is called when rest_batch='somme action'
        if not ALLOW_BATCHING or not getattr(cls.RestMeta, "CAN_BATCH", False):
            raise re.PermissionDeniedException(f"{cls.__name__} model does not allow batch actions", 439)
        cls._boundRest()
        # if not request.member.hasPerm("can_batch_update"):
        #     raise re.PermissionDeniedException(f"batch updated not allowed by user")
        if action == "create":
            return cls.on_rest_batch_create(request)
        batch_ids = request.DATA.getlist("batch_ids", [])
        batch_id_field = request.DATA.get("batch_id_field", "pk")
        if batch_ids:
            q = {}
            q["{}__in".format(batch_id_field)] = batch_ids
            qset = cls.on_rest_list_query(request, cls.rw_objects().filter(**q))
        else:
            qset = cls.on_rest_list_query(request, cls.rw_objects().all())
        if action == "delete":
            can_delete = getattr(cls.RestMeta, "CAN_DELETE", False)
            if not can_delete:
                raise re.PermissionDeniedException(f"deletion not allowed for {cls.get_class_name()}", 438)
            count = qset.delete()[0]
            return GRAPH_HELPERS.restStatus(request, True, error="deleted {} items".format(count))
        elif action == "update":
            update_fields = request.DATA.get(["batch_data", "batch_update"])
            if not isinstance(update_fields, dict):
                return GRAPH_HELPERS.restStatus(request, False, error="batch_update should be key/values")
            if {"id", "pk", "created", "password"} & update_fields.keys():
                return GRAPH_HELPERS.restStatus(request, False, error="field/s not allowed")
            has_meta = False
            for key in update_fields:
                if key.startswith("metadata"):
                    has_meta = True
                    break
            if has_meta or not request.member.is_superuser:
                count = 0
                for obj in qset:
                    obj.checkPermsAndSave(request, update_fields)
                    count += 1
            else:
                # only super users can do this
                count = qset.update(**update_fields)
            return GRAPH_HELPERS.restStatus(request, True, error="updated {} items".format(count))
        return GRAPH_HELPERS.restStatus(request, False, error="not implemented")

    @classmethod
    def on_rest_batch_create(cls, request):
        batch_data = request.DATA.get("batch_data")
        if isinstance(batch_data, str):
            batch_data = objict.fromJSON(batch_data)
        if isinstance(batch_data, dict):
            if "data" in batch_data:
                batch_data = batch_data["data"]
            if isinstance(batch_data, dict):
                batch_data = [batch_data]
        items = []
        for item in batch_data:
            obj = cls.createFromBatch(item)
            if obj:
                items.append(obj)
        return GRAPH_HELPERS.restList(request, items)

    @classmethod
    def createFromBatch(cls, item, request=None):
        obj = None
        item_filter = cls.getRestBatchCreateFilter(item)
        if not item_filter:
            raise Exception("requires item filter")
        rh.debug("createFromBatch", item_filter)
        obj = cls.ro_objects().filter(**item_filter).last()
        if obj is None:
            obj = cls()
            obj.checkPermsAndSave(request, item)
        return obj

    @classmethod
    def on_rest_create(cls, request, pk=None):
        # permissions are checked in the save routine
        can_create = getattr(cls.RestMeta, "CAN_CREATE", True)
        if not can_create:
            return GRAPH_HELPERS.restStatus(request, False, error="creation not allowed via rest for this model.")

        if hasattr(cls.RestMeta, "KEY_TO_FIELD_MAP"):
            kv = {}
            for k, v in list(cls.RestMeta.KEY_TO_FIELD_MAP.items()):
                if hasattr(request, k):
                    value = getattr(request, k)
                    if value is not None:
                        kv[v] = value
            obj = cls.createFromRequest(request, **kv)
        else:
            obj = cls.createFromRequest(request)
        graph = request.DATA.get("graph", "default")
        return obj.restGet(request, graph)

    @classmethod
    def _boundRest(cls):
        RestModel._setupGraphHelpers()

    @staticmethod
    def _setupGraphHelpers():
        if not GRAPH_HELPERS.views:
            views = importlib.import_module("rest.views")
            GRAPH_HELPERS.views = views
            GRAPH_HELPERS.restNotFound = views.restNotFound
            GRAPH_HELPERS.restStatus = views.restStatus
            GRAPH_HELPERS.restList = views.restList
            GRAPH_HELPERS.restGet = views.restGet
        if not GRAPH_HELPERS.get_request:
            mw = importlib.import_module("rest.middleware")
            GRAPH_HELPERS.get_request = mw.get_request

    @classmethod
    def get_rest_help(cls):
        output = objict()
        if cls.__doc__:
            output.doc = cls.__doc__.rstrip()
        else:
            output.doc = ""
        output.model_name = cls.get_class_name()
        output.fields = cls.rest_getQueryFields(True)
        output.graphs = {}
        if hasattr(cls, "RestMeta"):
            output.graph_names = list(getattr(cls.RestMeta, "GRAPHS", {}).keys())
            for key in output.graph_names:
                output.graphs[key] = cls.getGraph(key)
            output.no_show_fields = getattr(cls.RestMeta, "NO_SHOW_FIELDS", [])
            output.no_save_fields = getattr(cls.RestMeta, "NO_SAVE_FIELDS", [])
            output.search_fields = getattr(cls.RestMeta, "SEARCH_FIELDS", [])
        return output

    @classmethod
    def on_rest_request(cls, request, pk=None):
        # check if model id is in post
        request.rest_class = cls
        cls._boundRest()
        if pk is None and getattr(cls.RestMeta, "PK_FROM_FILTER", False):
            pk_fields = []
            key = cls.get_class_name().lower()
            key_p = f"{key}_id"
            pk_fields.append(key_p)
            # check if the cls has a field with the class name, (causes conflict)
            if not cls.get_field_type(key):
                pk_fields.append(key)
            pk = request.DATA.get(pk_fields, None, field_type=int)
        # generic rest request handler
        if pk is not None:
            using = getattr(cls.RestMeta, "RO_DATABASE", None)
            if using is None:
                using = getattr(cls.RestMeta, "DATABASE", None)
            if using:
                obj = cls.objects.using(using).filter(pk=pk).last()
            else:
                obj = cls.objects.filter(pk=pk).last()
            if obj is None:
                return GRAPH_HELPERS.views.restNotFound(request)
            if request.method == "GET":
                return obj.on_rest_get(request)
            elif request.method == "POST":
                return obj.on_rest_post(request)
            elif request.method == "DELETE":
                return obj.on_rest_delete(request)
            return GRAPH_HELPERS.views.restNotFound(request)

        if request.method == "GET":
            return cls.on_rest_list(request)
        elif request.method == "POST":
            if request.DATA.get("rest_batch"):
                return cls.on_rest_batch(request, request.DATA.get("rest_batch"))
            return cls.on_rest_create(request)
        return GRAPH_HELPERS.views.restNotFound(request)

    @classmethod
    def searchFromRequest(cls, request, qset):
        '''returns None if not foreignkey, otherswise the relevant model'''
        search_fields = getattr(cls.RestMeta, "SEARCH_FIELDS", None)
        search_terms = getattr(cls.RestMeta, "SEARCH_TERMS", None)
        search_join = getattr(cls.RestMeta, "SEARCH_JOIN", "and")
        q = request.DATA.get(["search", "q"])
        if q:
            qset = search.filter(qset, q, search_fields, search_terms, search_join)
        return qset

    @classmethod
    def rest_getWHITELISTED(cls):
        if hasattr(cls.RestMeta, "WHITELISTED"):
            return cls.RestMeta.WHITELISTED
        return cls.__RestMeta__.WHITELISTED

    @classmethod
    def rest_getQueryFields(cls, detailed=False):
        field_names = []
        all_fields = True
        if hasattr(cls.RestMeta, "QUERY_FIELDS"):
            field_names = cls.RestMeta.QUERY_FIELDS
            all_fields = "all_fields" in field_names

        if all_fields:
            for f in cls._meta.fields:
                if not f.name.endswith("_ptr") or f in cls.rest_getWHITELISTED():
                    field_names.append(f.name)
            if issubclass(cls, MetaDataModel):
                if detailed:
                    field_names.append("metadata")
                else:
                    field_names.append("properties__key")
                    field_names.append("properties__value")
        if detailed:
            output = []
            for f in field_names:
                if f == "metadata":
                    t = "MetaData"
                    fm = None
                else:
                    t = cls.get_field_type(f)
                    fm = cls.get_fk_model(f)
                info = {}
                info["name"] = f
                info["type"] = t
                if fm:
                    info["model"] = "{}.{}".format(fm._meta.app_label, fm.__name__)
                try:
                    fd = cls._meta.get_field(f)
                    if fd.choices:
                        info["choices"] = fd.choices
                    if fd.help_text:
                        info["help"] = fd.help_text()
                except Exception:
                    pass
                output.append(info)
            return output
        return field_names

    @classmethod
    def on_rest_set_query_defaults(cls, request):
        if not hasattr(request, "default_rest_filters"):
            request.default_rest_filters = None
            default_filters = getattr(cls.RestMeta, "LIST_DEFAULT_FILTERS", None)
            if default_filters:
                # make a copy so we can remove filters until the end
                request.default_rest_filters = objict.fromdict(default_filters)

    @classmethod
    def filterFromRequest(cls, request, qset):
        '''returns None if not foreignkey, otherswise the relevant model'''
        filter = request.DATA.pop("filter")
        # rh.debug("filterFromRequest")
        cls.on_rest_set_query_defaults(request)
        if not filter:
            return qset

        field_names = cls.rest_getQueryFields()
        q = {}

        """
        we can do customer filters but the name must be a allowed field
        and can only be one level deep ie no double "__" "group__member__owner"
        html select:
            name: "user_filter"
            field: "filter"
            options: [
                {
                    label: "Staff Only",
                    value: "is_staff:1"
                },
                {
                    label: "Online",
                    value: "is_online:1"
                },
                {
                    label: "Online",
                    value: "is_online:1"
                },
            ]
        """
        if not isinstance(filter, dict):
            filters = filter.split(';')
            filter = {}
            for f in filters:
                if ":" in f:
                    k, v = f.split(':')
                    if v in ["true", "True"]:
                        v = True
                    elif v in ["false", "False"]:
                        v = False
                    elif v == "null":
                        k = f"{k}__isnull"
                        v = True
                    filter[k] = v
        if filter:
            qset = cls.on_rest_handle_filter(qset, filter, request)
        now = datetime.now()
        for key in filter:
            if request.default_rest_filters:
                j = request.default_rest_filters.pop(key, None)
            name = key.split('__')[0]
            value = filter[key]
            if name in field_names and value != '__':
                if isinstance(value, str) and ':' in value and value.startswith('__'):
                    k, v = value.split(':')
                    key = key + k.strip()
                    value = v.strip()
                if key.endswith("__in") and ',' in value:
                    if value.startswith("["):
                        value = value[1:-1]
                    value = value.split(',')
                elif value in ["true", "True", "1"]:
                    value = 1
                elif value in ["false", "False", "0"]:
                    value = 0
                if isinstance(value, str) and "(" in value and ")" in value:
                    # this is a special function call
                    # rh.log_print(value)
                    if value.startswith("days("):
                        spos = value.find("(")+1
                        epos = value.find(")")
                        # rh.log_print(int(value[spos:epos]))
                        value = now + timedelta(days=int(value[spos:epos]))
                        # rh.log_print(now)
                        # rh.log_print(value)
                    elif value.startswith("hours("):
                        spos = value.find("(")+1
                        epos = value.find(")")
                        value = now + timedelta(hours=int(value[spos:epos]))
                    elif value.startswith("minutes("):
                        spos = value.find("(")+1
                        epos = value.find(")")
                        value = now + timedelta(minutes=int(value[spos:epos]))
                    elif value.startswith("seconds("):
                        spos = value.find("(")+1
                        epos = value.find(")")
                        value = now + timedelta(seconds=int(value[spos:epos]))
                    else:
                        continue
                if key.count('__') <= 4:
                    q[key] = value
            else:
                rh.log_print("filterFromRequest: invalid field: {} or {}".format(name, key))
        if q:
            # rh.debug("filtering...", q)
            qset = qset.filter(**q)
        return qset

    @classmethod
    def on_rest_handle_filter(cls, qset, filters, request=None):
        return qset

    @classmethod
    def filterRequestFields(cls, request, qset):
        """
        REQUEST_FIELDS which are fields attached to a request by middleware
        these fields can be used to auto filter requests
        """
        rfields = getattr(cls.RestMeta, "REQUEST_FIELDS", None)
        if rfields is not None:
            q = {}
            for fn in rfields:
                value = getattr(request, fn, None)
                if value is not None:
                    q[rfields[fn]] = value
            if bool(q):
                qset = qset.filter(**q)
        return qset

    ALLOWED_QUERY_OPERATORS = ["isnull", "gt", "gte", "lt", "lte", "contains", "icontains", "in", "startswith", "endswith"]

    @classmethod
    def queryFromRequest(cls, request, qset):
        """
        This will look at the query request and allow for basic filtering.

        QUERY_FIELDS_SPECIAL can be used to allow mappings of certain queries:
            ?group=iso
            {
                "group": "group__kind"
            }

        QUERY_FIELDS can be used to restrict what fields can be queried
        and add special fields:

        ?group__kind=iso
        # this will allow "group__kind" but also support all other fields
        ["group__kind", "all_fields"]

        <field_name>=value
        or
        <field_name>__<operator>=value

        You cannot do <field_name>__<sub_field>__<operator> unless
         <field_name>__<sub_field> is

        allowed <operator>s
            __gt
            __gte
            __lt
            __lte
            __icontains
            __in

        values can also be prefixed with special operators
            <field_name>=<operator>:value
        """
        q = {}
        exq = {}
        field_names = cls.rest_getQueryFields()
        query_keys = request.DATA.keys()
        special_keys = getattr(cls.RestMeta, "QUERY_FIELDS_SPECIAL", {})
        cls.on_rest_set_query_defaults(request)
        # rh.debug("queryFromRequest.key", query_keys, special_keys, field_names)
        for key in query_keys:
            # remove the key from defaults
            if request.default_rest_filters:
                j = request.default_rest_filters.pop(key, None)
                for drk in request.default_rest_filters:
                    if drk.startswith(f"{key}__"):
                        j = request.default_rest_filters.pop(drk, None)
                        break
            fn = key
            oper = None
            value = request.DATA.get(key)
            if value == "":
                continue
            if key in ["start", "size", "sort", "dr_start", "dr_end", "dr_eod", "dr_tz"]:
                continue
            if key.startswith("metadata__"):
                keys = key.split("__")
                meta_key = keys[1]
                meta_op = None
                meta_cat = None
                if len(keys) > 2:
                    if keys[2] in RestModel.ALLOWED_QUERY_OPERATORS:
                        meta_op = keys[2]
                    else:
                        meta_key = keys[2]
                        meta_cat = keys[1]
                if len(keys) > 3:
                    meta_op = keys[3]
                q["properties__key"] = meta_key
                if meta_cat:
                    q["properties__category"] = meta_cat
                if meta_op:
                    if RestModel.ALLOWED_QUERY_OPERATORS.index(meta_op) < 4:
                        q[f"properties__int_value__{meta_op}"] = value
                    else:
                        q[f"properties__value__{meta_op}"] = value
                elif value in [1, "1"]:
                    q[f"properties__int_value"] = value
                elif value in [0, "0"]:
                    q[f"properties__int_value"] = value
                else:
                    q["properties__value"] = value
                continue
            if key not in field_names:
                # check if special key
                if key in special_keys:
                    key = special_keys.get(key)
                    q[key] = value
                    continue
                # check if maybe this has a operator at end
                if "__" not in key:
                    continue
                fn = key[:key.rfind("__")]
                if fn not in field_names:
                    continue
                oper = key[key.rfind("__") + 2:]
                if oper not in RestModel.ALLOWED_QUERY_OPERATORS:
                    continue
                # this means we will allow it
                # fn = key[:key.rfind("__")]

            if value and isinstance(value, str) and value.startswith("__") and ":" in value:
                # this is another special way to filter via field=__
                oper, value = value[2:].split(':')
                if oper not in RestModel.ALLOWED_QUERY_OPERATORS:
                    continue
                key = "{}__{}".format(key, oper)
            if oper == "in":
                if isinstance(value, str) and ',' in value:
                    value = [a.strip() for a in value.split(',')]
            elif oper == "isnull":
                value = value in [True, "true", 1, "1"]
            elif oper is None and value in ["null", "None"]:
                key = "{}__isnull".format(key)
                value = True
            ft = cls.get_field_type(fn)
            if ft == "DateTimeField":
                value = rh.parseDateTime(value)
            elif ft == "IntegerField":
                value = rh.toInteger(value)
            q[key] = value
        if bool(q):
            rh.debug(q)
            exq = {key[:-4]: q[key] for key in q if key.endswith("__ne")}
            q = {key: q[key] for key in q if not key.endswith("__ne")}
            if bool(exq):
                qset = qset.exclude(**exq)
            if bool(q):
                qset = qset.filter(**q)
        return qset

    @classmethod
    def createFromRequest(cls, request, **kwargs):
        obj = cls()
        return obj.saveFromRequest(request, files=request.FILES, __is_new=True, **kwargs)

    @classmethod
    def createFromDict(cls, request=None, data=None, **kwargs):
        obj = cls()
        return obj.saveFromDict(request, data, __is_new=True, **kwargs)

    @classmethod
    def hasField(cls, fieldname):
        '''returns True if the fieldname exists in this model'''
        is_id = fieldname.endswith("_id")
        if is_id:
            fn = fieldname[:fieldname.rfind("_id")]
        for field in cls._meta.fields:
            if fieldname == field.name:
                return True
            if is_id and fn == field.name:
                return True
        return False

    @classmethod
    def get_class_name(cls, include_app=False):
        cname = cls.__name__
        if cls._meta.proxy:
            cname = cls.__bases__[0].__name__
        if include_app:
            return f"{cls._meta.app_label}.{cname}"
        return cname

    @classmethod
    def get_model_fields(cls):
        return cls._meta.fields

    @classmethod
    def get_model_field_names(cls):
        return [f.name for f in cls._meta.fields]

    @classmethod
    def has_model_field_name(cls, name):
        for f in cls._meta.fields:
            if f.name == name:
                return True
        return False

    @classmethod
    def get_field_type(cls, fieldname):
        '''returns the internal field type'''
        for field in cls._meta.fields:
            if fieldname == field.name:
                return field.get_internal_type()
        return None

    @classmethod
    def get_foreign_fields(cls):
        '''returns the internal field type'''
        return [field.name for field in cls._meta.fields if field.get_internal_type() == "ForeignKey"]

    @classmethod
    def get_related_name_fields(cls):
        return [f.related_name for f in cls._meta.related_objects]

    @classmethod
    def get_model_field_names(cls):
        return [f.name for f in cls._meta.get_fields()]

    @classmethod
    def get_fk_model(cls, fieldname):
        '''returns None if not foreignkey, otherswise the relevant model'''
        try:
            field = cls._meta.get_field(fieldname)
            return field.related_model
        except Exception:
            return None
