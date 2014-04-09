from django.contrib import admin
from prooftree.models import *

# Register your models here.
admin.site.register(Node)
admin.site.register(Proof)
admin.site.register(Prove)
admin.site.register(DAG)
admin.site.register(Keyword)
admin.site.register(KWMap)

