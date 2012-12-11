# -*-coding:utf-8-*-

from django.conf.urls.defaults import patterns, include, url
import os.path

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^site_media/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'site_media')}),
    url(r'^admin/', include(admin.site.urls)),
        # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
)

urlpatterns =urlpatterns + patterns('rapidshare_v2.views',
    url(r'^$', 'home', name='home'),
    url(r'^dodaj$', 'addFile', name='addFile'),
    url(r'^grupy$', 'myGroups', name='myGroups'),
    url(r'^grupy/(?P<groupId>[0-9]+)/$', 'inGroup', name='inGroup'),
    url(r'^deleteGroup/(?P<groupId>[0-9]+)/$', 'deleteMyGroup', name='deleteMyGroup'),
    url(r'^logowanie$', 'loginUser', name='login'),
    url(r'^profil', 'profil', name='profil'),
    url(r'^logout', 'logout', name='logout'),
    url(r'^more/(?P<fileCode>[-_A-Za-z0-9]+)/$', 'more', name='more'),
    url(r'^pliki', 'userFiles', name='userFiles'),
    url(r'^delete/(?P<fileCode>[-_A-Za-z0-9]+)/$', 'delete', name='error'),
    url(r'^error', 'error', name='error'),
    url(r'^pakiety', 'packages', name='packages'),
)
