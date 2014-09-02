from __future__ import absolute_import
from django.test import TestCase
from tests.test_mixin.models import Contact

class MixinTest(TestCase):
	def test_mixin(self):
		contacts = Contact.objects.all()
		self.assertGreater(len(contacts[:2]), 0)
