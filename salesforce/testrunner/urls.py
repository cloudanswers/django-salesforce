try:
	from django.conf.urls import patterns, include, url
except ImportError:  # Django 1.3
	from django.conf.urls.defaults import patterns, url, include

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('salesforce.testrunner.example.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
