# -*-coding:utf-8-*-

from django.conf.urls.defaults import patterns, include, url
import os.path

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
     
    url(r'^$', 'rapidshare_v2.views.home', name='home'),
    url(r'^dodaj$', 'rapidshare_v2.views.addFile', name='addFile'),
    url(r'^grupy$', 'rapidshare_v2.views.myGroups', name='myGroups'),
    url(r'^grupy/(?P<groupId>[0-9]+)/$', 'rapidshare_v2.views.inGroup', name='inGroup'),
    url(r'^deleteGroup/(?P<groupId>[0-9]+)/$', 'rapidshare_v2.views.deleteMyGroup', name='deleteMyGroup'),
    url(r'^logowanie$', 'rapidshare_v2.views.loginUser', name='login'),
    url(r'^profil', 'rapidshare_v2.views.profil', name='profil'),
    url(r'^logout', 'rapidshare_v2.views.logout', name='logout'),
    url(r'^more/(?P<fileCode>[-_A-Za-z0-9]+)/$', 'rapidshare_v2.views.more', name='more'),
    url(r'^pliki', 'rapidshare_v2.views.userFiles', name='userFiles'),
    url(r'^delete/(?P<fileCode>[-_A-Za-z0-9]+)/$', 'rapidshare_v2.views.delete', name='error'),
    url(r'^error', 'rapidshare_v2.views.error', name='error'),
    url(r'^pakiety', 'rapidshare_v2.views.packages', name='packages'),
    url(r'^site_media/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'site_media')}),
    # url(r'^rapidshare_v2/', include('rapidshare_v2.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
