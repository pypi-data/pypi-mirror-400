#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  gen_config.py
#     run to create the config.py file in current directory
#
#     this should only be run to initialize the config.py file
#
#  Copyright 2024 cswaim <cswaim@jcrl.net>
#  Licensed under the Apache License, Version 2.0
#  http://www.apache.org/licenses/LICENSE-2.0

import os
import app_config as ac

def run():
    """ copy the cofig file to the current dir"""

    """
    Generates a skeleton config.py file in the specified directory.

    Args:
        output_dir (str): The directory to generate the config file in.
    """
    # Get the directory of the package
    package_dir = os.path.dirname(ac.__file__)

    mod_list = ['config.py', 'configparms_ext.py']

    for m in mod_list:
        # Full path to the template file
        src = os.path.join(package_dir, m)
        dst_dir = os.getcwd()

        # Destination path in the current directory
        dst = os.path.join(dst_dir, m)

        if os.path.exists(dst):
            print("")
            print(f"    ** {m} already exists in {dst_dir} **")
            print("        Skipping generation.")
            continue

        # Check the operating system and use the respective command
        if os.name == 'nt':  # Windows
            cmd = f'copy "{src}" "{dst}"'
        else:  # Unix/Linux
            cmd = f'cp "{src}" "{dst}"'

        print("")
        print(f"    {m} generated successfully in {dst_dir}")
        # Copy File
        os.system(cmd)

    print("")