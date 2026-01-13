#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  untitled.py
#
#  Copyright 2024 cswaim <cswaim@tpginc.net>

import src.config as cfg

class ConfigUtils():
    """ a class of utilities for the config module """

    @staticmethod
    def print_config_vars( heading=None, comments=True, fileobj=None ):
        print("", file=fileobj)
        if heading is not None:
            print(f"--- {heading} ---", file=fileobj)

        print(f"    wkdir: {cfg.wkdir}", file=fileobj)
        print(f"  wk path: {cfg.wkdir_path}", file=fileobj)
        print(f"  src dir: {cfg.srcdir}", file=fileobj)
        print(f" data dir: {cfg.datadir}", file=fileobj)
        print(f"file name: {cfg.cfg_flnm}", file=fileobj)
        print("", file=fileobj)

        print(f"sections: {cfg.config.sections()}", file=fileobj)

        # print config variables
        for sec, vars in cfg.config.items():
            if comments:
                ConfigUtils.print_cfg_var_comments(sec, sec=True, fileobj=fileobj)
            print(cfg.config[sec], file=fileobj)
            for var, val in vars.items():
                if comments:
                    ConfigUtils.print_cfg_var_comments(var, fileobj=fileobj)
                print(f"   {var}: {val}", file=fileobj)

    @staticmethod
    def print_cfg_var_comments( var, sec=False, fileobj=None):
        """look for comments for the var (sec or var)"""
        if var in cfg.cfg_comments.keys():
                for c in cfg.cfg_comments[var]:
                    if sec:
                        print(f"# {c}", file=fileobj)
                    else:
                        print(f"   # {c}", file=fileobj)
