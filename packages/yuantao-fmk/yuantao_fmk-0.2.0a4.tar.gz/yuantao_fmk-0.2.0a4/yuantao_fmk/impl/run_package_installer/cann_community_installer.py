from functools import lru_cache
from typing import Dict, Optional

import requests

from yuantao_fmk import Config
from yuantao_fmk.downloader import RequestsDownloader
from yuantao_fmk.executor import execute_command
from yuantao_fmk.impl.run_package_installer import RunPackageInstallerBase


class CANNCommunityInstaller(RunPackageInstallerBase):
    """昇腾CANN社区版安装器(这个框架的初衷)"""

    def __init__(
        self,
        version: Optional[str] = None,
        ascend_platform: Optional[str] = None,
        os_: str = Config.OS,
        arch: str = Config.ARCH,
        download_path: Optional[str] = None,
    ):
        super().__init__(version, "cann_community", os_, arch, download_path)
        self.ascend_platform = ascend_platform

    def get_downloader(self):
        return RequestsDownloader(
            headers={
                "Referer": "https://www.hiascend.com/",
            }
        )

    def list_version(self, reverse=True, stable=Config.FORCE_STABLE):
        response = requests.get(
            "https://www.hiascend.com/ascendgateway/ascendservice/resourceDownload/mappingList?category=0&offeringType&model&offeringList=CANN",
            headers={
                "Referer": "https://www.hiascend.com/developer/download/community/result?module=cann"
            },
        )
        response_json = response.json()
        ori_versions = (
            response_json.get("data", {}).get("dropDownMap", {}).get("CANN", [])
        )
        if not ori_versions:
            raise ValueError("No versions found")
        version_list = [ori_version["versionName"] for ori_version in ori_versions]
        if stable:
            version_list = filter(
                lambda v: "alpha" not in v and "beta" not in v, version_list
            )
        return sorted(version_list, reverse=reverse)

    def get_default_resource_tags(self):
        return ["toolkit"]
    def get_available_resource_tags(self):
        return ["toolkit"]

    @lru_cache
    def get_version_info(self, version: str) -> Dict:
        response = requests.get(
            "https://www.hiascend.com/ascendgateway/ascendservice/cann/info/zh/0",
            params={
                "versionName": version,
            },
            headers={
                "Accept": "application/json",
                "Referer": "https://www.hiascend.com/",
            },
        )
        pkgs = response.json()["data"]["packageList"]
        mapper = {}
        for pkg in pkgs:
            mapper[pkg["softwareName"]] = pkg["downloadUrl"]
        return mapper

    @property
    def _package_postfix(self):
        """获取包的统一后缀
        like version_os-arch.run
        :return: _description_
        """
        return f"{self.version}_{self.os}-{self.arch}.run"

    def get_resource_filename(self, resource_tag):
        if resource_tag == "opp_kernel":
            if self.ascend_platform == "a3":
                package_name = f"Atlas-A3-cann-kernels_{self._package_postfix}"
            else:
                package_name = f"Ascend-cann-kernels-{self.ascend_platform}_{self._package_postfix}"
        elif resource_tag == "ops":
            package_name = (
                f"Ascend-cann-{self.ascend_platform}-ops_{self._package_postfix}"
            )
        else:
            package_name = f"Ascend-cann-{resource_tag}_{self._package_postfix}"
        return package_name

    def get_resource_remote_url(self, resource_tag):
        pkg_name = self.get_resource_filename(resource_tag)
        return self.get_version_info(self.version)[pkg_name]

    def get_activation_commands(self, target_path):
        return [f"source {target_path}/ascend-toolkit/set_env.sh"]

    def install_resource(self, resource_tag, target_path):
        execute_command(
            [
                self.get_resource_local_url(resource_tag),
                "--install",
                "--quiet",
                f"--install-path={target_path}",
            ]
        )
