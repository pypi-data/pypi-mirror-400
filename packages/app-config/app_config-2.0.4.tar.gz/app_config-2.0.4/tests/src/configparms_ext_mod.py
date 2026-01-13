#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  configparms_ext.py
#     read the config file and load the
#     variables in the config.py module
#
#  Copyright 2023 cswaim <cswaim@jcrl.net>
#  Licensed under the Apache License, Version 2.0
#  http://www.apache.org/licenses/LICENSE-2.0

from pathlib import Path
import os
import importlib.util
import src.config as cfg
from app_config.configparms import ConfigParms

class ConfigParmsExt(ConfigParms):
    """ This class extends the ConfigParms class allowing overrides of
        base class
    """
    def __init__(self, cfg_values=cfg.cfg_values, cfg_comments=cfg.cfg_comments, autorun=False):
        """ on init, load the directory paths, if autorun read the cfg file"""
        super().__init__(cfg_values, cfg_comments, autorun)

    # this method allow for changing the paths
    def set_directories(self,) -> None:
        """ set the working directory paths in cfg """
        if cfg.wkdir is None:
            # Find the path to the config module
            config_spec = importlib.util.find_spec("src.config")
            if config_spec is None and config_spec.origin is None:
                raise FileNotFoundError("config.py not found in the module search path.")

            cfg.wkdir_path = Path(config_spec.origin).resolve()
            cfg.srcdir = str(cfg.wkdir_path.parent) + os.sep
            cfg.wkdir = str(Path(cfg.srcdir).resolve().parent) + os.sep
            cfg.datadir = str(Path(cfg.wkdir).resolve()) + os.sep + 'data' + os.sep
            cfg.datadir = f"testfiles{os.sep}"
            cfg.extdir = "added in set_directories"

    def custom_init_routine(self,) -> None:
        """ Run any custom process need during init of the class.  This is rarely used. """
        cfg.init_var = 'loaded from ext'

    # set custom default values in the config object before writing the config file

    def set_custom_default_sects(self, config, sec, vars) -> bool:
        """ Process any section that needs special handling, such as a dictionary that is converted into variables within a section in the config file """
        #  set to True to skip the rest of the loop
        next_iter = False

        cfg.scds = "from set_custom_default_sects"
        return next_iter

    def set_custom_default_vars(self, config, sec, vars, var) -> bool:
        """ Process any variable that needs special handling """
        #  set to True to skip the rest of the loop
        next_iter = False
        cfg.scdv = "from set_custom_default_vars"
        return next_iter

    # set the values in the cfg module

    def set_module_sects(self, config, sec, vars) -> bool:
        """ special processing for module groups """
        #  set to True to skip the rest of the loop
        next_iter = False
        cfg.sms = "from set_module_sects"
        return next_iter

    def set_module_vars(self, config, sec, vars, var) -> bool:
        """ special processing for module variables """
        #  set to True to skip the rest of the loop
        next_iter = False
        cfg.smv = "from set_module_vars"
        if var == 'seed':
            cfg.seed = .023
            next_iter = True
        return next_iter

    def set_custom_module_vars(self, config) -> None:
        """ set any custiom vars that are not being defined in the config.py module
            These generally are values that are derived from values received from the config file

            Fro example: build a list based on the number of items, as set in a config file varible
        """
        cfg.scmv = "from set_custom_module_vars"

    # verify the values in the config parser object

    def verify_config_sects(self, config, sec, vars) -> bool:
        """ special processing for module groups """
        #  set to True to skip the rest of the loop
        next_iter = False
        cfg.vcs = "from verify_config_sects"
        return next_iter

    def verify_config_vars(self, config, sec, vars, var) -> bool:
        """ special processing for module variables """
        #  set to True to skip the rest of the loop
        next_iter = False
        cfg.vcv = "from verify_config_vars"
        return next_iter