from django.contrib import admin

# Register your models here.
from .models import MainQuest, ConceptNode

admin.site.register(MainQuest) 
admin.site.register(ConceptNode)
