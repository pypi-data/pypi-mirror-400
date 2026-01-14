from objict import objict
from django.db import models as dm
import string

from rest import helpers as rh
from rest import errors as re
from rest.encryption import ENCRYPTER, DECRYPTER
from datetime import datetime, date


class MetaDataBase(dm.Model):
    class Meta:
        abstract = True

    category = dm.CharField(db_index=True, max_length=32, default=None, null=True, blank=True)

    key = dm.CharField(db_index=True, max_length=80)

    value_format = dm.CharField(max_length=16)
    value = dm.TextField()

    int_value = dm.IntegerField(default=None, null=True, blank=True)
    float_value = dm.IntegerField(default=None, null=True, blank=True)

    def setValue(self, value):
        self.value = "{}".format(value)
        if type(value) is int or self.value in ["0", "1"]:
            if type(value) is int and value > 2147483647:
                self.value_format = "S"
                return
            self.value_format = "I"
            self.int_value = value
        elif type(value) is float:
            self.value_format = "F"
            self.float_value = value
        elif isinstance(value, list):
            self.value_format = "L"
            # self.value = ",".join(value)
        elif isinstance(value, dict):
            self.value_format = "O"
        elif type(value) in [str, str] and len(value) < 9 and value.isdigit():
            self.value_format = "I"
            self.int_value = value
        elif value in ["True", "true", "False", "false"]:
            self.value_format = "I"
            if value in ["True", "true"]:
                self.int_value = 1
            else:
                self.int_value = 0
        elif isinstance(value, bool):
            self.value_format = "I"
            if value:
                self.int_value = 1
            else:
                self.int_value = 0
        else:
            self.value_format = "S"

    def getStrictType(self, field_type):
        if type(self.value) is field_type:
            return self.value
        if field_type in [int, str, float, str]:
            return field_type(self.value)
        elif field_type is bool:
            if self.value_format == 'I':
                return self.int_value != 0
            return self.value in [True, 1, '1', 'y', 'Y', 'Yes', 'true', 'True']
        elif field_type in [date, datetime]:
            return rh.parseDate(self.value)
        return self.value

    def getValue(self, field_type=None):
        if field_type:
            return self.getStrictType(field_type)
        elif self.value_format == 'I':
            return self.int_value
        elif self.value_format == 'F':
            return self.float_value
        elif self.value_format in ["L", "O"] and self.value:
            try:
                return eval(self.value)
            except Exception:
                pass
        return self.value

    def __unicode__(self):
        if self.category:
            return "{}.{}={}".format(self.category, self.key, self.value)
        return "{}={}".format(self.key, self.value)

    def __str__(self):
        if self.category:
            return "{}.{}={}".format(self.category, self.key, self.value)
        return "{}={}".format(self.key, self.value)


class MetaDataModel(object):
    def set_metadata(self, request, values=None):
        # this may get called before the model is saved
        if not self.id:
            self.save()

        if values is None:
            values = request
            request = None

        if isinstance(values, list):
            # bug fix probably for odd browser handling of certain form data
            output = objict()
            for item in values:
                if isinstance(item, dict):
                    output.update(item)
            values = output

        if not isinstance(values, dict):
            raise Exception("invalid metadata: {}".format(values))

        for key, value in values.items():
            cat = None
            if "." in key:
                cat, key = key.split('.')
            self.setProperty(key, value, cat, request=request)

    def metadata(self):
        return self.getProperties()

    def removeProperties(self, category=None):
        # this will remove all properties
        # if category is not it will remove all properties
        self.properties.filter(category=category).delete()

    def getProperties(self, category=None):
        ret = {}
        for p in self.properties.all():
            if p.category:
                props = self.getFieldProps(p.category)
                if props.hidden:
                    continue
                if p.category not in ret or not isinstance(ret.get(p.category, None), dict):
                    ret[p.category] = {}
                props = self.getFieldProps("{}.{}".format(p.category, p.key))
                if props.hidden:
                    continue
                if p.category == "secrets":
                    if p.int_value:
                        ret[p.category][p.key] = "*" * p.int_value
                    else:
                        ret[p.category][p.key] = "******"
                    continue
                ret[p.category][p.key] = p.getValue()
            else:
                props = self.getFieldProps(p.key)
                if props.hidden:
                    continue
                ret[p.key] = p.getValue()
        if category is not None:
            if category in ret:
                return ret[category]
            return {}
        return ret

    def __initFieldProps(self):
        if not hasattr(self, "__field_props"):
            if hasattr(self.RestMeta, "METADATA_FIELD_PROPERTIES"):
                # this provides extra protection for metadata fields
                self.__field_props = self.RestMeta.METADATA_FIELD_PROPERTIES
            else:
                self.__field_props = None

    def getFieldProps(self, key):
        self.__initFieldProps()
        full_key = key
        category = None
        if "." in key:
            category, key = key.split('.')
        props = objict()
        if self.__field_props:
            if category and self.__field_props.get(category, None):
                cat_props = self.__field_props.get(category, None)
                if cat_props:
                    props.notify = cat_props.get("notify", None)
                    props.requires = cat_props.get("requires", None)
                    props.on_change_name = cat_props.get("on_change", None)
                    props.hidden = cat_props.get("hidden", False)
                    if props.on_change_name:
                        props.on_change = getattr(self, props.on_change_name, None)
            field_props = self.__field_props.get(full_key, None)
            if field_props:
                props.notify = field_props.get("notify", props.notify)
                props.requires = field_props.get("requires", None)
                props.hidden = field_props.get("hidden", False)
                on_change_name = field_props.get("on_change", None)
                if on_change_name:
                    on_change = getattr(self, on_change_name, None)
                    if on_change:
                        props.on_change = on_change
        return props

    def checkFieldPerms(self, full_key, props, request=None):
        if not props.requires:
            return True
        if not request or not request.member:
            return False
        if request.member.hasPermission(props.requires) or request.user.is_superuser:
            return True

        # this a unauthorized attempt to change field, log and throw exception
        if props.notify and request.member:
            subject = "permission denied changing protected '{}' field".format(full_key)
            msg = "permission denied changing protected field '{}'\nby user: {}\nfor: {}".format(
                    full_key,
                    request.user.username,
                    self
                )
            request.member.notifyWithPermission(props.notify, subject, msg, email_only=True)
        raise re.PermissionDeniedException(subject, 481)

    def setProperties(self, data, category=None, request=None, using=None):
        for k, v in data.items():
            self.setProperty(k, v, category, request=request, using=using)

    def setProperty(self, key, value, category=None, request=None, using=None, ascii_only=False, encrypted=False):
        # rh.log_print("{}:{} ({})".format(key, value, type(value)))
        if ascii_only and isinstance(value, str):
            value = "".join([x for x in value if x in string.printable])
        on_change = None
        if not using:
            using = getattr(self.RestMeta, "DATABASE", using)
        if not request:
            request = rh.getActiveRequest()
        self.__initFieldProps()

        if "." in key:
            category, key = key.split('.')
            
        if isinstance(value, dict):
            if category is None:
                return self.setProperties(value, key)
        username = "root"
        if request and request.member:
            username = request.member.username
        prop = None

        if category:
            # delete any keys with this category name
            full_key = "{}.{}".format(category, key)
            # this deletes anything with the key that matches the category
            # this works because the category is stored not in key but category field
            # rh.log_print("deleting key={}".format(category))
            self.properties.filter(key=category).delete()
            if category == "secrets":
                encrypted = True
            elif category == "permissions":
                if value == 0:
                    value = None
        else:
            full_key = key

        value_len = 0
        if encrypted:
            value_len = len(value)
            value = ENCRYPTER.encrypt(value)

        field_props = self.getFieldProps(full_key)
        if not self.checkFieldPerms(full_key, field_props, request):
            return False

        check_value = "{}".format(value)
        has_changed = False
        prop = self.properties.filter(category=category, key=key).last()
        old_value = None
        if prop:
            # existing property we need to make sure we delete
            old_value = prop.getValue()
            if value is None or value == "":
                # we need to delete all, if there was dups for some reason
                self.properties.filter(category=category, key=key).delete()
                has_changed = True
            else:
                has_changed = check_value != prop.value
                if not has_changed:
                    return
                prop.setValue(value)
                if encrypted and value_len:
                    prop.int_value = value_len
                prop.save(using=using)
            if field_props.on_change:
                field_props.on_change(key, value, old_value, category)
        elif value is None or value == "":
            # do not create none or empty property
            return False
        else:
            has_changed = True
            PropClass = self.get_fk_model("properties")
            prop = PropClass(parent=self, key=key, category=category)
            prop.setValue(value)
            # rh.log_print(u"saving {}.{}".format(category, key))
            # rh.log_print(u"saving {} : {}".format(full_key, value))
            prop.save(using=using)

        if hasattr(self, "_recordRestChange"):
            self._recordRestChange("metadata.{}".format(full_key), old_value)

        if field_props.notify and request and request.member:
            notify = field_props.get("notify")
            if value:
                value = str(value)
                if len(value) > 5:
                    value = "***"
            msg = "protected field '{}' changed to '{}'\nby user: {}\nfor: {}".format(
                full_key,
                value,
                username,
                self
            )
            request.member.notifyWithPermission(notify, "protected '{}' field changed".format(full_key), msg, email_only=True)
        return has_changed

    def getProperty(self, key, default=None, category=None, field_type=None, decrypted=False):
        try:
            if "." in key:
                category, key = key.split('.')
            value = self.properties.get(category=category, key=key).getValue(field_type)
            if decrypted and value is not None:
                return DECRYPTER.decrypt(value)
            return value
        except Exception:
            pass
        return default

    def setSecretProperty(self, key, value):
        return self.setProperty(key, value, category="secrets", encrypted=True)

    def getSecretProperty(self, key, default=None):
        return self.getProperty(key, default, "secrets", decrypted=True)
