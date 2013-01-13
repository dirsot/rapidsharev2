# -*-coding:utf-8-*-

from django.contrib import admin
from rapidshare_v2.models import *

class DownloadsAdmin(admin.ModelAdmin):
    list_display = ('ip', 'user', 'file', 'date')

class GroupsAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'owner')

class GroupsAssignationAdmin(admin.ModelAdmin):
    list_display = ('owner', 'group')

class FileAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'despription', 'file', 'date_uploaded', 'owner', 'ip', 'visibility')

admin.site.register(UserGroup, GroupsAdmin)  
admin.site.register(Downloads, DownloadsAdmin)  
admin.site.register(UserGroupAssignation, GroupsAssignationAdmin) 
admin.site.register(File, FileAdmin) 
