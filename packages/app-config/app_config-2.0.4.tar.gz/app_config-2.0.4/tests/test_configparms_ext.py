#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_configparms_ext.py
#
#  Copyright 2023 cswaim <cswaim@jcrl.net>
#  Licensed under the Apache License, Version 2.0
#  http://www.apache.org/licenses/LICENSE-2.0

import unittest
import importlib
import os
import sys

from src import setup_module

class TestConfigParmsExt(unittest.TestCase):
    """ tests for the """

    # testfile_path = f"tests{os.sep}data{os.sep}"
    testfile_path = f"testfiles{os.sep}"

    @classmethod
    def setUpClass(cls):
        """class set up"""
        print("\n ------- \nTesting module - test_configparms_ext.py")
        if not os.path.exists(cls.testfile_path):
           os.mkdir(cls.testfile_path)

        # copy ext_mod to ext
        global cfg
        setup_module.run_ext()
        # import the ext to overide imports in cfg
        from src import config as cfg
        sys.modules['src.configparms_ext'] = importlib.reload(sys.modules['src.configparms_ext'])
        importlib.reload(cfg)

        # load the cfg with default paths
        # cp is instantiated in the config module
        cfg.datadir = cls.testfile_path
        cfg.run()

        return

    @classmethod
    def tearDownClass(cls):
        """class tear down"""
        dir_list = [cls.testfile_path,]

        for i in dir_list:
            if os.path.exists(i):
                for pth, dir, files in os.walk(i):
                    for fl in files:
                        os.remove(f"{i}{fl}")
                os.rmdir(i)
        return

    def setUp(self):

        return

    def tearDown(self):

        return

    def test_update(self):

        pass

    def test_set_directories(self,):
        """test set directories """

        # data directory set in ext
        self.assertEqual(cfg.datadir, self.testfile_path)

        # value added in init routine set_directories
        self.assertEqual(cfg.extdir, "added in set_directories")

    def test_custom_init_routine(self,):
        """test custom init routine"""
        self.assertEqual(cfg.init_var, 'loaded from ext')

    # test setting values in config object

    def test_set_custom_default_sects(self,):
        """ test set custom default sects """
        self.assertEqual(cfg.scds, "from set_custom_default_sects")

    def test_set_custom_default_vars(self,):
        """ test set custom default vars """
        self.assertEqual(cfg.scdv, "from set_custom_default_vars")

    # test setting the values in the cfg module

    def test_set_module_sects(self):
        """ test set module sects """
        self.assertEqual(cfg.sms, "from set_module_sects")

    def test_set_module_vars(self):
        """ test set module vars """
        self.assertEqual(cfg.smv, "from set_module_vars")
        self.assertEqual(cfg.seed, .023)

    def test_set_custom_module_vars(self):
        """ test set custiom module vars """
        self.assertEqual(cfg.scmv, "from set_custom_module_vars")

    # test verifying the values in the config parser object

    def test_verify_config_sects(self):
        """ test verify config sects """
        self.assertEqual(cfg.vcs, "from verify_config_sects")

    def test_verify_config_vars(self):
        """ test verify config vars """
        self.assertEqual(cfg.vcv, "from verify_config_vars")

if __name__ == '__main__':

    cf = unittest.TestLoader().loadTestsFromTestCase(TestConfigParmsExt)
    unittest.TextTestRunner(verbosity=2).run(cf)
