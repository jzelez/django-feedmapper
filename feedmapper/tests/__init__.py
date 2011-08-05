import os
from StringIO import StringIO

from django.db import models
from django.test import TestCase

from feedmapper.models import Mapping
from feedmapper.parsers import XMLParser


TEST_DIR = os.path.abspath(os.path.dirname(__file__))


class Thing(models.Model):
    "Dummy model for testing."
    email = models.EmailField()
    name = models.CharField(max_length=255)
    combined = models.TextField()

    def convert_name(self, first_name, last_name):
        return "%s %s" % (first_name, last_name)


class FeedMapperTests(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.mapping = Mapping.objects.get(pk=1)
        self.mapping.source = os.path.join(TEST_DIR, "dummy1.xml")
        self.mapping.parse()
        self.parser = XMLParser(self.mapping)

    def test_model_format_validation_passes(self):
        "Ensure that validation passes if JSON mapping models are formatted properly."
        model_string = 'myapp.MyModel'
        self.assertTrue(self.parser.validate_model_format(model_string))

    def test_model_format_validation_fails(self):
        "Ensure that validation fails if JSON mapping models are formatted improperly."
        model_string = 'myapp.fail.MyModel'
        self.assertFalse(self.parser.validate_model_format(model_string))

    def test_parser_one_to_one(self):
        "Ensure the parser can handle a one-to-one model field to feed node mapping."
        thing = Thing.objects.get(pk=1)
        self.assertEqual(thing.email, "vader@sith.org")

    def test_parser_one_to_attribute(self):
        "Ensure the parser can handle a model field to feed node attribute mapping."
        pass

    def test_parser_one_to_many(self):
        "Ensure the parser can handle a one-to-many model field to feed nodes mapping."
        thing = Thing.objects.get(pk=1)
        self.assertEqual(thing.combined, "vader@sith.org Anakin Skywalker")

    def test_parser_one_to_transformer(self):
        "Ensure the parser can handle a custom transformer for a model field."
        thing = Thing.objects.get(pk=1)
        self.assertEqual(thing.name, "Anakin Skywalker")

    def test_parser_overwrites_items(self):
        "Ensure the parser overwrites items when sync type is set to OVERWRITE."
        num_things_before = Thing.objects.count()
        self.mapping.source = os.path.join(TEST_DIR, "dummy2.xml")
        self.mapping.overwrite = True
        self.mapping.parse()
        num_things_after = Thing.objects.count()
        self.assertEqual(num_things_before, 2)
        self.assertEqual(num_things_after, 1)

    def test_parser_updates_items(self):
        "Ensure the parser updates items when sync type is set to UPDATE."
        num_things_before = Thing.objects.count()
        self.mapping.source = os.path.join(TEST_DIR, "dummy2.xml")
        self.mapping.parse()
        num_things_after = Thing.objects.count()
        self.assertEqual(num_things_before, num_things_after)

    def test_parser_update_impossible(self):
        """
        Ensure that if the identifier isn't specified in a mapping and sync type is
        set to UPDATE the parsing is aborted.
        """
        pass

    def tearDown(self):
        pass
