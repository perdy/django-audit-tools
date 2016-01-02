from __future__ import unicode_literals

from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

from demo.views import HomeView, AccessView, LastAccessView, LastModelActionView, CreateModelActionView, \
    UpdateModelActionView, DeleteModelActionView, access_function_based_view, AccessExceptionView, access_decorated_view
from demo.settings import DEBUG, STATIC_URL, STATIC_ROOT
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'demo.views.home', name='home'),
    # url(r'^demo/', include('demo.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', HomeView.as_view(), name='home'),
    # Access
    url(r'^access/class/$', AccessView.as_view(), name='new_access_class'),
    url(r'^access/function/$', access_function_based_view, name='new_access_function'),
    url(r'^access/decorator/$', access_decorated_view, name='new_access_decorator'),
    url(r'^access/exception/$', AccessExceptionView.as_view(), name='new_access_exception'),
    url(r'^access/args/(\d+)/$', AccessView.as_view(), kwargs={'arg1': 1, 'arg2': True, 'arg3': 'test'}, name='new_access_args'),
    url(r'^access/last/', LastAccessView.as_view(), name='last_access'),
    # ModelAction
    url(r'^modelaction/create/$', CreateModelActionView.as_view(), name='create_modelaction'),
    url(r'^modelaction/update/$', UpdateModelActionView.as_view(), name='update_modelaction'),
    url(r'^modelaction/delete/$', DeleteModelActionView.as_view(), name='delete_modelaction'),
    url(r'^modelaction/last/$', LastModelActionView.as_view(), name='last_modelaction'),
    # Audit URLs
    url(r'^audit/', include('audit.urls'))
)

if DEBUG:
    urlpatterns += static(STATIC_URL, document_root=STATIC_ROOT)
