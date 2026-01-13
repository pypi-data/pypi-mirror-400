#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  configparms.py
#     read the config file and load the
#     variables in the config.py module
#
#  Copyright 2023 cswaim <cswaim@jcrl.net>
#  Licensed under the Apache License, Version 2.0
#  http://www.apache.org/licenses/LICENSE-2.0

import configparser
from pathlib import Path
import os
import sys
import importlib.util
import src.config as cfg

class ConfigParms:
    """ read the config file and set cfg values
        if version changes, the cfg file is read and rewritten with the new changes reflected.
           The data values in the cfg file are perserved
    """

    def __init__(self, cfg_values=cfg.cfg_values, cfg_comments=cfg.cfg_comments, autorun=False):
        """ on init, load the directory paths, if autorun read the cfg file"""
        self.cfg_values = cfg_values
        self.cfg_comments = cfg_comments

        # set the directories
        self.set_directories()

        # custom init routine
        self.custom_init_routine()

        cfg.config = configparser.ConfigParser(allow_no_value=True)

        # check the version,
        # 3.11 changed config parser prefix
        # if sys.version_info >= (3,12):
        #     self.prefixes = cfg.config._prefixes.full
        # else:
        #     self.prefixes = cfg.config._comment_prefixes
        self.prefixes = cfg.sys_comment_prefixes

        if autorun:
            self.run()

    def set_directories(self,) -> None:
        """ set the working directory paths in cfg module
            Add any additional custom cfg values
           """
        if cfg.wkdir is None:
            # Find the path to the config module
            config_spec = importlib.util.find_spec("src.config")
            if config_spec is None and config_spec.origin is None:
                raise FileNotFoundError("config.py not found in the module search path.")

            cfg.wkdir_path = Path(config_spec.origin).resolve()
            cfg.srcdir = str(cfg.wkdir_path.parent) + os.sep
            cfg.wkdir = str(Path(cfg.srcdir).resolve().parent) + os.sep
            cfg.datadir = str(Path(cfg.wkdir).resolve()) + os.sep + 'data' + os.sep

    def custom_init_routine(self,) -> None:
        """ This is where code can be insterted to customize the init of the class and set custom values that are not being defined in the config.py module
        """
        pass

    def run(self,) -> None:
        """ read the config file, if not found, write the default file,
            set the values in the config module
        """
        # the config is a ConfigParser object, and can be
        # updated by read_config_file, so it is returned
        config = self.read_config_file(cfg.config)

        self.set_config_module_variables(config)

        return

    def read_config_file(self, config):
        """read in the config file if exists or create it"""
        if Path(f"{cfg.datadir}{cfg.cfg_flnm}").is_file():
            config.read(f"{cfg.datadir}{cfg.cfg_flnm}")
        else:
            # create the default config file
            config = self.set_default_config(config)
            self.write_cfg(config)

        # if the sys_version is different, write out the new config file
        if not config.has_option('SYSTEM', 'sys_cfg_version') or cfg.sys_cfg_version != config.get('SYSTEM', 'sys_cfg_version'):
            self.set_config_module_variables(config)
            self.set_default_config(config)
            self.write_cfg(config)

        # remove comments from sections to be consistent with data from read
        self.remove_default_comments(config)

        # verify all attributes are present in config
        self.verify_config_attributes(config)

        return config

    def write_cfg(self, config):
        """ write the cfg file from the current cfg settings"""
        with open(f"{cfg.datadir}{cfg.cfg_flnm}", 'w') as configfile:
            config.write(configfile)
        return

    def set_default_config(self, config):
        """define the default config file, adding varibles with default values """
        for sec, vars in self.cfg_values.items():
            # create the section
            if not config.has_section(sec):
                config.add_section(sec)
            config[sec].clear()
            self.check_for_comments(sec)

            next_iter = self.set_custom_default_sects(config, sec, vars)
            if next_iter:
                continue

            for var in vars:
                var_name = var[0]
                # check for comments and add them if they exists
                self.check_for_comments(sec, var_name)

                next_iter = self.set_custom_default_vars(config, sec, vars, var_name)
                if next_iter:
                    continue

                # add the variable
                if var[1] == 'l':
                    # process list - convert to string
                    listitems = getattr(cfg, var_name)
                    list_str = ",".join(x for x in listitems)
                    config.set(sec, var_name, list_str)
                else:
                    config.set(sec, var_name, str(getattr(cfg, var_name)))

        return config

     # set custom default values in the config object before writing the config file

    def set_custom_default_sects(self, config, sec, vars) -> None:
        """ Process any section that needs special handling, such as a dictionary that is converted into variables within a section in the config file
        """
        #  set to True to skip the rest of the loop
        next_iter = False
        return next_iter

    def set_custom_default_vars(self, config, sec, vars, var) -> None:
        """ Process any variable that needs special handling """
        #  set to True to skip the rest of the loop
        next_iter = False
        return next_iter

    # set the values in the cfg module

    def set_config_module_variables(self, config):
        """set the cfg module variables from config for consistant access"""
        for sec, vars in self.cfg_values.items():

            next_iter = self.set_module_sects(config, sec, vars)
            if next_iter:
                continue

            for var in vars:
                var_name = var[0]
                # do not override the module version number
                if var_name == 'sys_cfg_version':
                    continue

                next_iter = self.set_module_vars(config, sec, vars, var_name)
                if next_iter:
                    continue

                # set variable from config value
                match var[1]:
                    case 'b':
                        setattr(cfg, var_name, config.getboolean(sec, var_name, fallback=getattr(cfg, var_name)))
                    case 'f':
                        setattr(cfg, var_name, config.getfloat(sec,var_name, fallback=getattr(cfg, var_name)))
                    case 'i':
                        setattr(cfg, var_name, config.getint(sec, var_name, fallback=getattr(cfg, var_name)))
                    case 'l':
                        # convert string to list
                        listitems = []
                        list_str = config.get(sec, var_name, fallback=getattr(cfg, var_name))
                        if isinstance(list_str, str):
                            listitems = [x.strip() for x in list_str.split(',')]
                        else:
                            # if list_str not str, then it is the fallback list
                            listitems = list_str
                        setattr(cfg, var_name, listitems)
                    case 's':
                        setattr(cfg, var_name, config.get(sec, var_name, fallback=getattr(cfg, var_name)))

        self.set_custom_module_vars(config)

        return config

    def set_module_sects(self, config, sec, vars) -> bool:
        """ special processing for module sections """
        #  set to True to skip the rest of the loop
        next_iter = False
        return next_iter

    def set_module_vars(self, config, sec, vars, var) -> bool:
        """ special processing for module variables"""
        #  set to True to skip the rest of the loop
        next_iter = False
        return next_iter

    def set_custom_module_vars(self, config) -> None:
        """ set any custiom vars that are not being defined in the config.py module
            These generally are values that are derived from values received from the config file
        """
        pass

    def check_for_comments(self, sec, var_name=None):
        """set comments in config, if they exist for a sec or variable,
            comments are set after a section and before a variable
            comments will be written to file, then removed from config later
        """
        if var_name is None:
            if sec in self.cfg_comments.keys():
                for c in self.cfg_comments[sec]:
                    cfg.config.set(sec, f"# {c}")
        else:
            if var_name in self.cfg_comments.keys():
                for c in self.cfg_comments[var_name]:
                    cfg.config.set(sec, f"# {c}")

    def remove_default_comments(self, config):
        """remove the comments set up in the defaults"""
        for s in config.sections():
            # the key is a tuple (key, value)
            for key in config[s].items():
                if key[0][:1] in self.prefixes:
                    config.remove_option(s, key[0])

    def verify_config_attributes(self, config):
        """verify all attributes are present in config"""
        for sec, vars in self.cfg_values.items():
            # create the section
            if not config.has_section(sec):
                config.add_section(sec)

            next_iter = self.verify_config_sects(config, sec, vars)
            if next_iter:
                continue

            for var in vars:
                var_name = var[0]

                next_iter = self.verify_config_vars(config, sec, vars, var_name)
                if next_iter:
                    continue

                # if variable does not exist
                if not config.has_option(sec, var_name):
                    # add the variable
                    if var[1] == 'l':
                        # process list - convert to string
                        listitems = getattr(cfg, var_name)
                        list_str = ",".join(x for x in listitems)
                        config.set(sec, var_name, list_str)
                    else:
                        config.set(sec, var_name, str(getattr(cfg, var_name)))

    def verify_config_sects(self, config, sec, vars) -> bool:
        """ special processing for module groups """
        #  set to True to skip the rest of the loop
        next_iter = False
        return next_iter

    def verify_config_vars(self, config, sec, vars, var) -> bool:
        """ special processing for module variables """
        #  set to True to skip the rest of the loop
        next_iter = False
        return next_iter