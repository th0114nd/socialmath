from django.contrib import admin
from prooftree.models import *
from django.contrib.auth.models import User

# Register your models here.
admin.site.register(Node)
admin.site.register(DAG)
admin.site.register(Keyword)
admin.site.register(KWMap)
admin.site.register(Event)