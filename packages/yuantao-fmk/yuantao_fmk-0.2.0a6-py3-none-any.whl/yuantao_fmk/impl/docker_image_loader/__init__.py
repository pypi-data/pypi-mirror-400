# Copyright (C) 2025 Tao Yuan
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.

from yuantao_fmk.executor import execute_command
from yuantao_fmk.resource_installer import InstallerBase


class DockerImageLoader(InstallerBase):
    def install_resource(self, resource_tag, target_path=None):
        execute_command(
            ["docker", "load", "-i", self.get_resource_local_url(resource_tag)]
        )
