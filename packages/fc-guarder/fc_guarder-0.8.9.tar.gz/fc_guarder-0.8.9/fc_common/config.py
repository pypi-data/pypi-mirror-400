# -*- coding: utf-8 -*-
#
# Copyright 2023, 2025 NXP
#
# SPDX-License-Identifier: MIT


import os

import yaml


class Config:
    @staticmethod
    def save_cfg(cfg):
        cfg_path = os.path.expanduser(
            os.environ.get("FC_CLIENT_CFG_PATH", "~/.fc/client_cfg")
        )
        cfg_yaml = os.path.join(cfg_path, "fc.yaml")
        os.makedirs(cfg_path, exist_ok=True)

        with open(cfg_yaml, "w", encoding="utf-8") as f_cfg:
            yaml.dump(cfg, f_cfg)

    @staticmethod
    def load_cfg():
        system_cfg_path = "/opt/.fc/client_cfg"
        system_cfg_yaml = os.path.join(system_cfg_path, "fc.yaml")
        if os.path.exists(system_cfg_yaml):
            cfg_yaml = system_cfg_yaml
        else:
            cfg_path = os.path.expanduser(
                os.environ.get("FC_CLIENT_CFG_PATH", "~/.fc/client_cfg")
            )
            cfg_yaml = os.path.join(cfg_path, "fc.yaml")

        try:
            with open(cfg_yaml, encoding="utf-8") as f_cfg:
                data = yaml.load(f_cfg.read(), yaml.SafeLoader)
                return data
        except Exception:  # pylint: disable=broad-except
            return {}

    @staticmethod
    def load_user_config():
        user_config = os.path.expanduser("~/.fc/config.yaml")
        system_user_config = "/opt/.fc/config.yaml"

        verbose = int(os.environ.get("verbose", 0))

        # Load system config first (base configuration)
        system_data = {}
        if os.path.exists(system_user_config):
            try:
                with open(system_user_config, encoding="utf-8") as f_cfg:
                    system_data = yaml.load(f_cfg.read(), yaml.SafeLoader) or {}
                    if verbose >= 10:
                        print(f"System config loaded: {system_user_config}")
            except Exception as exc:  # pylint: disable=broad-except
                if verbose >= 10:
                    print(f"Error loading system config: {exc}")
                system_data = {}

        # Load user config (override configuration)
        user_data = {}
        if os.path.exists(user_config):
            try:
                with open(user_config, encoding="utf-8") as f_cfg:
                    user_data = yaml.load(f_cfg.read(), yaml.SafeLoader) or {}
                    if verbose >= 10:
                        print(f"User config loaded: {user_config}")
            except Exception as exc:  # pylint: disable=broad-except
                if verbose >= 10:
                    print(f"Error loading user config: {exc}")
                user_data = {}

        # Merge configurations: system config as base, user config overrides
        merged_config = system_data.copy()
        merged_config.update(user_data)

        return merged_config
