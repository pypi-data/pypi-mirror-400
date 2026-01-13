# Copyright (C) 2025 Tao Yuan
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.

"""PkgBase基类包"""

import os
import stat
from abc import abstractmethod
from typing import List, Optional

from yuantao_fmk import Config, logger
from yuantao_fmk.resource_installer import InstallerBase


class RunPackageInstallerBase(InstallerBase):
    def __init__(
        self,
        version: str,
        production_name: str,
        os_: str = Config.OS,
        arch: str = Config.ARCH,
        download_path: Optional[str] = None,
    ):
        super().__init__(version, f"run/{production_name}", download_path)
        self.os = os_
        self.arch = arch

    def pre_install(self, resource_tag, target_path):
        package_path = self.get_resource_local_url(resource_tag)
        if not os.access(package_path, os.X_OK) and package_path.endswith(".run"):
            current_stat = os.stat(package_path)
            os.chmod(package_path, current_stat.st_mode | stat.S_IEXEC)

    @abstractmethod
    def get_activation_commands(self, target_path: str) -> List[str]:
        pass

    def post_install_all(self, target_path):
        assert target_path is not None
        activation_commands = self.get_activation_commands(target_path)

        with open(
            os.path.join(target_path, "set_env.sh"), mode="w+", encoding="utf-8"
        ) as activation_file:
            activation_file.write("\n".join(activation_commands))
        logger.info(
            f"Install success! Run `source {target_path}/set_env.sh` to activate run package."
        )
