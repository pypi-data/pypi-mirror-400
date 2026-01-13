#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_setup_module.py
#
#  Copyright 2024 cswaim <cswaim@tpginc.net>

import os
import sys
import app_config as ac

def run():
    """ this will set up the src folder within the test folder
        A new copy of the config and configparms_ext are copied to
        test/src.  This assures tests are run with the most recent
        copies of this members.

        The confg module can be modified by subsequent tests, but the
        changes are not kept because this module will refresh the config
        with copies from the package.
        """

    print("===== in the test setup module =====")
    package_dir = os.path.dirname(ac.__file__)

    mod_list = ['config.py', 'configparms_ext.py']

    for m in mod_list:
        # Full path to the template file
        src = os.path.join(package_dir, m)

        # Destination path in the test.src directory
        dst = os.path.dirname(__file__)

        # Check the operating system and use the respective command
        if os.name == 'nt':  # Windows
            cmd = f'copy "{src}" "{dst}"'
        else:  # Unix/Linux
            cmd = f'cp "{src}" "{dst}"'

        try:
            # Copy File
            os.system(cmd)
            print("")
            print(f"    {m} generated successfully in {dst}")
        except Exception as e:
            print(e)

    print("===== exit the test setup module =====")

def run_ext():
    """ copy the config_ext_mod.py to config.py

        the modified config overrides the configparms
        """

    print("===== in the test ext setup module =====")

    # a list of package files  (src file, dest file)
    mod_list = [ ('config_ext_mod.py', 'config.py'),
                 ('configparms_ext_mod.py', 'configparms_ext.py')]

    for f in mod_list:
        s, d = f

        src = os.path.join(os.path.dirname(__file__), s)
        dst = os.path.join(os.path.dirname(__file__), d)

        """copy the src file to the dst file"""
        # Check the operating system and use the respective command
        if os.name == 'nt':  # Windows
            cmd = f'copy "{src}" "{dst}"'
        else:  # Unix/Linux
            cmd = f'cp "{src}" "{dst}"'

        try:
            # Copy File
            os.system(cmd)
            print("")
            print(f"    {s} copied successfully to {dst}")
        except Exception as e:
            print(e)

    print("===== exit the test ext setup module =====")


if __name__ == '__main__':
    run()