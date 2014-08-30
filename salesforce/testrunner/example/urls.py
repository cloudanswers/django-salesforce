# django-salesforce
#
# by Phil Christensen
# (c) 2012-2013 Freelancers Union (http://www.freelancersunion.org)
# See LICENSE.md for details
#

try:
	from django.conf.urls import patterns, include, url
except ImportError:  # Django 1.3
	from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('salesforce.testrunner.example.views',
	url(r'^$', 'list_accounts', name='list_accounts'),
	url(r'^search/$', 'search_accounts', name='search_accounts'),
)
