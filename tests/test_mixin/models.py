import salesforce
from salesforce.models import SalesforceModel

class CascadeMixin(SalesforceModel):
	class Meta(object):
		abstract = True

class Account(CascadeMixin, SalesforceModel):
	pass

class Contact(CascadeMixin, SalesforceModel):
	account = salesforce.fields.ForeignKey(Account, on_delete=salesforce.models.DO_NOTHING)
