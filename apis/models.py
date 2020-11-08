
import datetime
import os

import django
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models
import uuid
# Create your models here.
from django.db import models
from django.utils.timezone import make_aware




def get_file_name(path="other"):
    def wrapper(instance, filename):
        filename, extension = os.path.splitext(filename)
        if path in ["media", "thumbnail"]:
            return os.path.join("uiflo", path, str(instance.uuid), filename + extension)
        return os.path.join("uiflo", path, "%s" % instance.uuid + "_" + filename + extension)
    # return wrapper




class User(models.Model):

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True, blank=True, db_index=True)
    social_id = models.CharField(max_length=60, blank=True, db_index=True)
    password = models.CharField(max_length=64, blank=True)
    first_name = models.CharField(max_length=60, blank=True)
    last_name = models.CharField(max_length=60, blank=True)
    profile_pic = models.FileField(null=True, blank=True, upload_to=get_file_name("profile_pic"))
    email = models.EmailField(blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    remark = JSONField(default=dict, null=True, blank=True)

    created_at = models.DateTimeField(default=django.utils.timezone.now)

    class Meta:
        db_table = 'user'
        verbose_name = "User"
        verbose_name_plural = "Users"



