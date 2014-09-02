from __future__ import absolute_import
from django.test import TestCase
from tests.test_mixin.models import User

class MixinTest(TestCase):
	def test_mixin(self):
		users = User.objects.all()
		self.assertGreater(len(users[:2]), 0)
