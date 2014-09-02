from django.db import models
from salesforce.models import SalesforceModel

class CascadeMixin(SalesforceModel):
	class Meta(object):
		abstract = True

class User(CascadeMixin, SalesforceModel):
	pass
