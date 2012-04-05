#!/usr/bin/python
# -*- coding: utf-8 -*-

# pylint: disable=C0111

# Copyright (c) 2012 Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.

import os

from UserList import UserList
from unittest import TestCase

from mock import Mock

from lizard_area.models import Area
from lizard_portal.configurations_retriever import ConfigurationFactory
from lizard_portal.configurations_retriever import ConfigurationsRetriever
from lizard_portal.configurations_retriever import DescriptionParser
from lizard_portal.configurations_retriever import ZipFileNameRetriever
from lizard_portal.models import ConfigurationToValidate

class MockQuerySet(UserList):

    def __init__(*args, **kwargs):
        UserList.__init__(*args, **kwargs)

    def all(self):
        return self.data

    def filter(self, *args, **kwargs):
        result = MockQuerySet()
        for o in self.data:
            print o.action
            is_searched_object = True
            for keyword, value in kwargs.items():
                print keyword, value
                is_searched_object = getattr(o, keyword) == value
                if not is_searched_object:
                    break
            if is_searched_object:
                result.append(o)
        return result

    def get(self, *args, **kwargs):
        result = None
        for o in self.data:
            is_searched_object = True
            for keyword, value in kwargs.items():
                is_searched_object = getattr(o, keyword) == value
                if not is_searched_object:
                    break
            if is_searched_object:
                result = o
                break
        if result is None:
            assert False
        return result

    def count(self):
        return len(self.data)


class MockDatabase(object):

    def __init__(self):
        self.areas = MockQuerySet()
        self.configurations = MockQuerySet()

    def ConfigurationToValidate(self):
        config = Mock(ConfigurationToValidate)
        config.save = lambda c=config: self.configurations.append(c)
        return config

    def Area(self):
        area = Mock(Area)
        area.save = lambda a=area: self.areas.append(a)
        return area

class ConfigurationsRetrieverTestSuite(TestCase):

    def setUp(self):
        self.db = MockDatabase()

    def test_a(self):
        """Test no configurations are retrieved.

        There are no configurations to validate.

        """
        retriever = ConfigurationsRetriever(self.db)
        self.assertEqual([], retriever.retrieve_configurations())

    def test_b(self):
        """Test a single configuration is retrieved."""
        config = self.db.ConfigurationToValidate()
        config.save()
        retriever = ConfigurationsRetriever(self.db)
        self.assertEqual([config], retriever.retrieve_configurations())

    # def test_a(self):
    #     """Test the right configurations are retrieved."""
    #     retriever = ConfigurationsRetriever(None, None)
    #     configuration_list = ['config A', 'config B']
    #     retriever.retrieve_configurations = \
    #         (lambda : [MockConfig(config) for config in configuration_list])
    #     self.assertEqual(configuration_list, retriever.retrieve_configurations_as_dict())

    # def test_b(self):
    #     """Test no configurations are retrieved when there are no zip files."""
    #     file_name_retriever = Mock()
    #     file_name_retriever.retrieve = Mock(return_value=[])
    #     retriever = ConfigurationsRetriever(file_name_retriever, None)
    #     self.assertEqual([], retriever.retrieve_configurations_as_dict())

    # def test_c(self):
    #     """Test a single configurations is retrieved when there is a single zip file."""
    #     file_name_retriever = Mock()
    #     file_name_retriever.retrieve = Mock(return_value=['hello world.zip'])
    #     configuration_factory = StubConfigurationFactory()
    #     retriever = ConfigurationsRetriever(file_name_retriever, configuration_factory)
    #     configurations = retriever.retrieve_configurations()
    #     self.assertEqual(1, len(configurations))
    #     self.assertEqual('hello world.zip', configurations[0].zip_file)


class StubConfigurationFactory(object):

    def create(self, zip_file_name):
        configuration = Mock()
        configuration.zip_file = zip_file_name
        return configuration


class ZipFileNameRetrieverTestSuite(TestCase):

    def test_a(self):
        """Test no files are returned when there are no files present."""
        retriever = ZipFileNameRetriever()
        retriever.retrieve_file_names = (lambda : [])
        file_names = retriever.retrieve()
        self.assertEqual([], file_names)

    def test_b(self):
        """Test no files are returned when there are no zip files present."""
        retriever = ZipFileNameRetriever()
        retriever.retrieve_file_names = (lambda : ['hello.txt'])
        file_names = retriever.retrieve()
        self.assertEqual([], file_names)

    def test_c(self):
        """Test the single zip file is returned."""
        retriever = ZipFileNameRetriever()
        retriever.retrieve_file_names = (lambda : ['hello.zip'])
        file_names = retriever.retrieve()
        self.assertEqual(['hello.zip'], file_names)


class StubParser(object):

    def __init__(self, attributes_dict):
        self.as_dict = Mock(return_value=attributes_dict)


class ConfigurationFactoryTestSuite(TestCase):

    def create_factory(self, attributes_dict):
        return ConfigurationFactory(StubParser(attributes_dict))

    def test_a(self):
        factory = self.create_factory({'gebruiker': 'Pieter Swinkels'})
        zip_file, description_file = Mock(), Mock()
        factory.get_description_file = (lambda s: (zip_file, description_file))
        configuration = factory.create('mnt/vss-share/waterbalans_Waternet_20120228_141234.zip')
        self.assertEqual(configuration.zip_file_path, 'mnt/vss-share/waterbalans_Waternet_20120228_141234.zip')
        self.assertEqual(configuration.gebruiker, 'Pieter Swinkels')

    def test_b(self):
        """Test the type of the water balance configuration is set."""
        factory = self.create_factory({})
        zip_file, description_file = Mock(), Mock()
        factory.get_description_file = (lambda s: (zip_file, description_file))
        configuration = factory.create('mnt/vss-share/waterbalans_Waternet_20120228_141234.zip')
        self.assertEqual(configuration.type, 'waterbalans')

    def test_c(self):
        """Test the type of the ESF_1 configuration is set."""
        factory = self.create_factory({})
        zip_file, description_file = Mock(), Mock()
        factory.get_description_file = (lambda s: (zip_file, description_file))
        configuration = factory.create('mnt/vss-share/ESF_1_Waternet_20120228_141234.zip')
        self.assertEqual(configuration.type, 'ESF_1')

    def test_d(self):
        """Test the open description file is also closed."""
        factory = self.create_factory({})
        zip_file, description_file = Mock(), Mock()
        factory.get_description_file = (lambda s: (zip_file, description_file))
        factory.create('hello.zip')
        method, args, kwargs = zip_file.method_calls[0]
        self.assertTrue('close' == method and () == args and {} == kwargs)

    def test_e(self):
        """Test the contents of the description file make up the meta info."""
        factory = self.create_factory({
            'naam':      'nieuwe oppervlakte',
            'gebruiker': 'Pieter Swinkels'})
        zip_file, description_file = Mock(), Mock()
        factory.get_description_file = (lambda s: (zip_file, description_file))
        configuration = factory.create('mnt/vss-share/ESF_1_Waternet_20120228_141234.zip')
        self.assertEqual(configuration.meta_info,
            'naam: nieuwe oppervlakte; gebruiker: Pieter Swinkels')


class DescriptionParserTestSuite(TestCase):

    def setup(self, *lines):
        self.parser = DescriptionParser()
        self.open_file = Mock()
        self.open_file.readlines = Mock(return_value=lines)

    def test_a(self):
        """Test that an option value that contains a space is parsed."""
        self.setup('naam = nieuwe oppervlakte')
        description_dict = self.parser.as_dict(self.open_file)
        self.assertEqual({'naam': 'nieuwe oppervlakte'}, description_dict)

    def test_b(self):
        """Test that multiple options are parsed."""
        lines = 'naam = nieuwe oppervlakte', 'gebruiker = Pieter Swinkels'
        self.setup(*lines)
        description_dict = self.parser.as_dict(self.open_file)
        self.assertEqual(2, len(description_dict))
        self.assertEqual('nieuwe oppervlakte', description_dict['naam'])
        self.assertEqual('Pieter Swinkels', description_dict['gebruiker'])

    def test_c(self):
        """Test that trailing spaces of a value are removed."""
        self.setup('naam = nieuwe oppervlakte  ')
        description_dict = self.parser.as_dict(self.open_file)
        self.assertEqual('nieuwe oppervlakte', description_dict['naam'])

    def test_d(self):
        """Test that an invalid option is not parsed."""
        self.setup('naam nieuwe oppervlakte')
        description_dict = self.parser.as_dict(self.open_file)
        self.assertEqual({}, description_dict)

    def test_e(self):
        """Test that an attribute name is lowercased."""
        self.setup('Naam = nieuwe oppervlakte')
        description_dict = self.parser.as_dict(self.open_file)
        self.assertEqual('nieuwe oppervlakte', description_dict['naam'])

    def test_f(self):
        """Test that attribute values can contain non-alphanumeric characters.
        """
        self.setup('datum = 08-03-2012 20:13:00')
        description_dict = self.parser.as_dict(self.open_file)
        self.assertEqual('08-03-2012 20:13:00', description_dict['datum'])


class NoSelf(object):

    pass


class Self(object):

    def get_self(self):
        return self


class OverrideSelf(object):

    def get_self(self):
        return self


class OverrideSelfTestSuite(TestCase):

    def test_a(self):
        """Test replace a method by a method changes self."""
        s = Self()
        self.assertEqual(s, s.get_self())
        o = OverrideSelf()
        s.get_self = o.get_self
        self.assertEqual(o, s.get_self())

    def test_b(self):
        """Test replace a method by a function with a self argument fails."""
        s = Self()
        self.assertEqual(s, s.get_self())
        s.get_self = get_self
        try:
            self.assertEqual(s, s.get_self())
            self.assertTrue(False)
        except TypeError:
            pass

    def test_c(self):
        """Test replace a method by a function with a self argument."""
        NoSelf.get_self = get_self
        s = NoSelf()
        self.assertEqual(s, s.get_self())
        print "type(s.get_self)", type(s.get_self)
        print "s.get_self", s.get_self
        print "s.__dict__", s.__dict__
        self.assertEqual(s, s.get_self())

    def test_d(self):
        """Test replace a method by a function without a self argument."""
        s = Self()
        self.assertEqual(s, s.get_self())
        global global_s
        global_s = s
        s.get_self = get_self_c
        self.assertEqual(s, s.get_self())


def get_self(self):
    return self

global_s = None

def get_self_c():
    return global_s


class ConfigurationStore(object):

    def __init__(self, database):
        self.db = database
        self.extract = ConfigurationExtractor().extract

    def supply(self):
        config = self.db.ConfigurationToValidate()
        for zip_name in self.retrieve_zip_names():
            dir_name, config_type = self.extract(zip_name)
            for config_spec in self.retrieve_config_specs(dir_name, config_type):
                for key, value in config_spec.items():
                    if key == 'area_code':
                        config.area = self.db.areas.get(code=value)
                    else:
                        setattr(config, key, value)
                config.file_path = dir_name
                config.action = ConfigurationToValidate.KEEP
                config.save()


class ConfigurationStoreTestSuite(TestCase):

    def setUp(self):
        self.db = MockDatabase()
        area = self.db.Area()
        area.code = '3201'
        area.save()
        self.store = ConfigurationStore(self.db)
        self.store.retrieve_zip_names = lambda : ['waterbalans_Waternet_04042012_081400.zip']
        self.store.retrieve_config_specs = lambda dir_name, config_type: [{'area_code': '3201'}]

    def test_a(self):
        """Test the supply of a single ConfigurationToValidate."""
        self.store.supply()
        self.assertEqual(1, self.db.configurations.count())

    def test_b(self):
        """Test the zip file name specifies the directory of a single ConfigurationToValidate."""
        self.store.supply()
        config = self.db.configurations.all()[0]
        self.assertEqual('/tmp/waterbalans_Waternet_04042012_081400', config.file_path)

    def test_c(self):
        """Test the new ConfigurationToValidate points to the correct Area."""
        self.store.supply()
        config = self.db.configurations.all()[0]
        self.assertEqual(self.db.areas.all()[0], config.area)

    def test_d(self):
        """Test the new ConfigurationToValidate should be kept."""
        self.store.supply()
        config = self.db.configurations.all()[0]
        self.assertEqual(ConfigurationToValidate.KEEP, config.action)

    def test_e(self):
        """Test retrieve_config_specs is called correctly."""
        self.store.retrieve_config_specs = Mock(return_value=self.store.retrieve_config_specs("don't care", "don't care"))
        self.store.supply()
        args, kwargs = self.store.retrieve_config_specs.call_args
        self.assertEqual('/tmp/waterbalans_Waternet_04042012_081400', args[0])
        self.assertEqual('waterbalans', args[1])


class ConfigurationExtractor(object):

    def extract(self, zip_name):
        directory = os.path.join(self.dbf_directory, zip_name[:-4])
        return directory, 'waterbalans'

    @property
    def dbf_directory(self):
        return '/tmp'


class ConfigurationSpecRetriever(object):

    def retrieve(self, dir_name, config_type):
        config_specs = []
        for area_code in self.retrieve_area_codes(dir_name, config_type):
            config_spec = {'area_code': area_code}
            config_specs.append(config_spec)
        return config_specs


class ConfigurationSpecRetrieverTestSuite(TestCase):

    def setUp(self):
        self.retriever = ConfigurationSpecRetriever()
        self.retriever.retrieve_area_codes = lambda dir_name, config_type: ['3201']

    def test_a(self):
        """Test the construction of a single ConfigurationSpec."""
        dir_name = '/tmp/waterbalans_Waternet_04042012_081400'
        config_type = 'waterbalans'
        config_specs = self.retriever.retrieve(dir_name, config_type)
        self.assertEqual(1, len(config_specs))
        self.assertEqual('3201', config_specs[0]['area_code'])
