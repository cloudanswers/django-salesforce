# django-salesforce
#
# by Phil Christensen
# (c) 2012-2013 Freelancers Union (http://www.freelancersunion.org)
# See LICENSE.md for details
#

"""
Adds support for Salesforce primary keys.
"""

import warnings
from django.core import exceptions
from django.utils.translation import ugettext_lazy as _
from django.db.models import fields
from django.db import models
try:
	from django.utils.encoding import smart_text
	from django.utils.six import string_types
except ImportError:  # Django 1.3
	from django.utils.encoding import smart_unicode as smart_text
	string_types = basestring,
try:
	## in south >= 0.6, we have to explicitly tell south about this
	## custom field.  Even though it will be on an unmanaged model, 
	## south parses everything first and will crap out even though
	## later it'd ignore this model anyway.
	from south.modelsinspector import add_introspection_rules
	add_introspection_rules([], ["^salesforce\.fields\.SalesforceAutoField"])
except ImportError:
	pass

# None of field types defined in this module need a "deconstruct" method,
# in Django 1.7+, because their parameters only describe fixed nature of SF
# standard objects that can not be modified no ways by no API or spell.

FULL_WRITABLE  = 0
NOT_UPDATEABLE = 1
NOT_CREATEABLE = 2
READ_ONLY   = 3  # (NOT_UPDATEABLE & NOT_CREATEABLE)


class SalesforceAutoField(fields.Field):
	"""
	An AutoField that works with Salesforce primary keys.
	"""
	description = _("Text")
	
	empty_strings_allowed = True
	default_error_messages = {
		'invalid': _('This value must be a valid Salesforce ID.'),
	}
	def __init__(self, *args, **kwargs):
		assert kwargs.get('primary_key', False) is True, "%ss must have primary_key=True." % self.__class__.__name__
		kwargs['blank'] = False
		kwargs['null'] = False
		kwargs['default'] = None
		fields.Field.__init__(self, *args, **kwargs)
	
	def get_internal_type(self):
		return "AutoField"
	
	def to_python(self, value):
		if isinstance(value, string_types) or value is None:
			return value
		return smart_text(value)
	
	def validate(self, value, model_instance):
		pass
	
	def get_prep_value(self, value):
		return self.to_python(value)
	
	def contribute_to_class(self, cls, name):
		if cls._meta.has_auto_field:
			if name == cls._meta.auto_field.name and type(self) == type(cls._meta.auto_field):
				print("INFO: The model %s has exactly the same AutoField still: %s: %s"
					% (cls, name, self))
			else:
				print("WARNING: A model can't have more than one AutoField: %s: (%s=%s, %s=%s)"
					% (cls, cls._meta.auto_field.name, cls._meta.auto_field, name, self))
			return
		#assert not cls._meta.has_auto_field, "A model can't have more than one AutoField."
		if hasattr(cls, 'sf_pk'):
			if not cls.sf_pk in ('id', 'Id'):
				raise ImproperlyConfigured("The Meta option 'sf_pk' must be 'id' or 'Id'.")
			name = cls.sf_pk
		super(SalesforceAutoField, self).contribute_to_class(cls, name)
		cls._meta.has_auto_field = True
		cls._meta.auto_field = self
	
	def formfield(self, **kwargs):
		return None

class SfField(models.Field):
	"""
	Add support of 'sf_read_only' and 'custom' parameters to Salesforce fields.

		sf_read_only=3 (READ_ONLY):  The field can not be specified neither on insert or update.
			e.g. LastModifiedDate (the most frequent type of read only)
		sf_read_only=1 (NOT_UPDATEABLE):  The field can be specified on insert but can not be later never modified.
			e.g. ContactId in User object (relative frequent)
		sf_read_only=2 (NOT_CREATEABLE):  The field can not be specified on insert but can be later modified.
			e.g. RecordType.IsActive or Lead.EmailBouncedReason
		sf_read_only=0:  normal writable (default)

		custom=True : Add '__c' to the column name if no db_column is defined.
	"""
	def __init__(self, *args, **kwargs):
		self.sf_read_only = kwargs.pop('sf_read_only', 0)
		self.sf_custom = kwargs.pop('custom', None)
		self.sf_namespace = ''
		super(SfField, self).__init__(*args, **kwargs)

	def get_attname_column(self):
		"""
		Get the database column name automatically in most cases.
		"""
		# See "A guide to Field parameters": django/db/models/fields/__init__.py
		#   * attname:   The attribute to use on the model object. This is the same as
		#                "name", except in the case of ForeignKeys, where "_id" is
		#                appended.
		#   * column:    The database column for this field. This is the same as
		#                "attname", except if db_column is specified.
		attname = self.get_attname()
		if self.db_column is not None:
			# explicit name
			column = self.db_column
		else:
			if not self.name.islower():
				# a Salesforce style name e.g. 'LastName' or 'MyCustomField'
				column = self.name
			else:
				# a Django style name like 'last_name' or 'my_custom_field'
				column = self.name.title().replace('_', '')
			# Fix custom fields
			if self.sf_custom:
				column = self.sf_namespace + column + '__c'
		return attname, column

	def contribute_to_class(self, cls, name, **kwargs):
		super(SfField, self).contribute_to_class(cls, name, **kwargs)
		if self.sf_custom is None and hasattr(cls._meta, 'sf_custom'):
			# Only custom fields in models explicitly marked by
			# Meta custom=True are recognized automatically - for
			# backward compatibility reasons.
			self.sf_custom = cls._meta.sf_custom
		if self.sf_custom and '__' in cls._meta.db_table[:-3]:
			self.sf_namespace = cls._meta.db_table.split('__')[0] + '__'
		self.set_attributes_from_name(name)


class CharField(SfField, models.CharField):
	"""CharField with sf_read_only attribute for Salesforce."""
	pass
class EmailField(SfField, models.EmailField):
	"""EmailField with sf_read_only attribute for Salesforce."""
	pass
class URLField(SfField, models.URLField):
	"""URLField with sf_read_only attribute for Salesforce."""
	pass
class TextField(SfField, models.TextField):
	"""TextField with sf_read_only attribute for Salesforce."""
	pass


class IntegerField(SfField, models.IntegerField):
	"""IntegerField with sf_read_only attribute for Salesforce."""
	pass
class SmallIntegerField(SfField, models.SmallIntegerField):
	"""SmallIntegerField with sf_read_only attribute for Salesforce."""
	pass
class BooleanField(SfField, models.BooleanField):
	"""BooleanField with sf_read_only attribute for Salesforce."""
	def __init__(self, default=False, **kwargs):
		super(BooleanField, self).__init__(default=default, **kwargs)
class DecimalField(SfField, models.DecimalField):
	"""DecimalField with sf_read_only attribute for Salesforce."""
	pass


class DateTimeField(SfField, models.DateTimeField):
	"""DateTimeField with sf_read_only attribute for Salesforce."""
	pass
class DateField(SfField, models.DateField):
	"""DateField with sf_read_only attribute for Salesforce."""
	pass
class TimeField(SfField, models.TimeField):
	"""TimeField with sf_read_only attribute for Salesforce."""
	pass


class ForeignKey(SfField, models.ForeignKey):
	"""ForeignKey with sf_read_only attribute for Salesforce."""
	def __init__(self, *args, **kwargs):
		# Checks parameters before call to ancestor.
		on_delete = kwargs.get('on_delete', models.CASCADE).__name__
		if not on_delete in ('PROTECT', 'DO_NOTHING'):
			# The option CASCADE (currently fails) would be unsafe after a fix
			# of on_delete because Cascade delete is not usually enabled in SF
			# for safety reasons for most fields objects, namely for Owner,
			# CreatedBy etc. Some related objects are deleted automatically
			# by SF even with DO_NOTHING in Django, e.g. for
			# Campaign/CampaignMember
			related_object = args[0]
			warnings.warn("Only foreign keys with on_delete = PROTECT or "
					"DO_NOTHING are currently supported, not %s related to %s"
					% (on_delete, related_object))
		super(ForeignKey, self).__init__(*args, **kwargs)

	def get_attname(self):
		if self.name.islower():
			# the same as django.db.models.fields.related.ForeignKey.get_attname
			return '%s_id' % self.name
		else:
			return '%sId' % self.name

	def get_attname_column(self):
		attname, column = super(ForeignKey, self).get_attname_column()
		if self.db_column is None and not self.sf_custom:
			column += 'Id'
		return attname, column


AutoField = SalesforceAutoField
