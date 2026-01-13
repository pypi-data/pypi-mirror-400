# Copyright (C) 2025 Tao Yuan
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.

import os
import shutil
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Iterable, List, Optional

from yuantao_fmk import Config, logger
from yuantao_fmk.downloader import Downloader, RequestsDownloader
from yuantao_fmk.utils.decorator import dryrun


class InstallerMode(Enum):
    """资源安装器运行模式枚举类。

    DDII: 全部下载后安装
    DIDI: 逐个资源下载后安装
    DO:   只下载，不安装
    """

    DDII = auto()
    DIDI = auto()
    DO = auto()


class InstallerBase(ABC):
    """资源安装器基类。

    提供通用的资源下载、预安装、安装和后处理方法，具体的资源管理逻辑由子类实现。
    """

    def __init__(
        self,
        resource_type: Optional[str],
        version: Optional[str] = None,
        necessary_resource_tag_list: Iterable[str] = (),
        download_path: Optional[str] = None,
        **kwargs,
    ):
        """初始化资源安装器。

        Args:
            resource_type: 资源类型
            version: 资源版本号，如果为None则自动获取最新版本
            necessary_resource_tag_list: 必需资源标签列表
            download_path: 资源包下载保存路径
        """
        super().__init__()
        self.resource_type = resource_type
        if version is not None:
            self.version = self.get_version(version)
        else:
            self.version = self.get_latest_version()
        self.necessary_resource_tag_list = necessary_resource_tag_list
        self.download_path = download_path

    def get_version(self, original_version: str) -> str:
        """
        在某些场景下，传入版本可能并非实际版本.
        默认返回原始版本，可重载实现逻辑.
        Args:
            original_version: 原始版本号

        Returns: 实际版本号

        """
        return original_version

    def get_filename_version(self, version: str) -> str:
        """
        获取某个版本中资源文件名中体现的版本号.
        Args:
            version: 实际版本号

        Returns: 文件名中的版本号

        """
        return version

    def check_version(self, version: str) -> bool:
        """检查版本号是否合法。

        Args:
            version: 实际版本号

        Returns:
            bool: 版本号是否合法，默认返回True
        """
        return True

    def get_latest_version(self) -> str:
        """获取最新版本号。

        Returns:
            str: 最新版本号

        Raises:
            ValueError: 如果没有可用版本
        """
        versions = self.get_version_list(True, True)
        versions_list = list(versions) if not isinstance(versions, list) else versions
        if not versions_list:
            raise ValueError("No versions found")
        return versions_list[0]

    def get_best_version(self, necessary_resource_tag_list: Iterable[str] = ()) -> str:
        """获取最佳版本号。

        从可用版本列表中选择第一个包含所有必需资源的版本。

        Args:
            necessary_resource_tag_list: 所需资源的列表，如果为空则使用默认资源列表

        Returns:
            str: 最佳版本号

        Raises:
            ValueError: 如果找不到满足条件的版本
        """
        if not necessary_resource_tag_list:
            necessary_resource_tag_list = self.get_default_resource_tag_list()
        original_version = self.version
        try:
            for version in self.get_version_list(True, True):
                # 临时设置版本上下文以检查该版本的资源
                self.version = version
                all_exist = True
                for resource_tag in necessary_resource_tag_list:
                    if not self.check_remote_resource_exists(resource_tag):
                        all_exist = False
                        break
                if all_exist:
                    return version
            raise ValueError("No version found that contains all required resources")
        finally:
            # 恢复原始版本
            self.version = original_version

    @abstractmethod
    def get_default_resource_tag_list(self) -> List[str]:
        """
        获取默认资源列表
        Returns: 默认资源列表

        """
        pass

    @abstractmethod
    def get_available_resource_tag_list(self) -> List[str]:
        """
        获取可用资源列表
        Returns: 可用资源列表

        """
        pass

    @abstractmethod
    def get_resource_filename(self, resource_tag: str) -> str:
        """
        获取指定资源标签所对应的文件名

        Args:
            resource_tag: 资源标签

        Returns: 文件名
        """
        pass

    def get_resource_remote_location(self, resource_tag: str) -> str:
        """获取指定资源标签远程存储目录的路径。

        如果子类重写了 `get_resource_remote_url`，可以不需要实现此方法。
        但如果需要使用 `check_remote_resource_exists` 或 `get_best_version`，
        则必须实现此方法。

        Args:
            resource_tag: 资源标签

        Returns:
            str: 远程目录路径

        Raises:
            NotImplementedError: 如果子类未实现此方法且未重写 `get_resource_remote_url`
        """
        raise NotImplementedError(
            "Subclass must implement get_resource_remote_location() "
            "or override get_resource_remote_url()"
        )

    def get_resource_remote_filename(self, resource_tag: str) -> str:
        """获取资源标签远程文件名（默认直接与本地文件名一致）。

        Args:
            resource_tag: 资源标签

        Returns: 文件名
        """
        return self.get_resource_filename(resource_tag)

    def get_resource_local_location(self, resource_tag: str) -> str:
        """获取指定资源标签本地存储目录的路径。

        Args:
            resource_tag: 资源标签

        Returns:
            str: 本地存储路径

        Raises:
            ValueError: 如果download_path为None且无法自动生成
        """
        if self.download_path:
            return self.download_path
        raise ValueError(
            "download_path is None. Please provide download_path in constructor "
            "or ensure version and resource_type are set for auto-generation."
        )

    def get_resource_local_filename(self, resource_tag: str) -> str:
        """获取本地文件名（默认直接与资源文件名一致）。

        Args:
            resource_tag: 资源标签

        Returns: 文件名
        """
        return self.get_resource_filename(resource_tag)

    def get_resource_remote_url(self, resource_tag: str) -> str:
        """获取资源标签的完整远程URL。

        Args:
            resource_tag: 资源标签

        Returns: 远程完整URL
        """
        return (
            self.get_resource_remote_location(resource_tag).rstrip("/")
            + "/"
            + self.get_resource_remote_filename(resource_tag)
        )

    def get_resource_local_url(self, resource_tag: str) -> str:
        """获取资源标签的本地完整文件路径。

        Args:
            resource_tag: 资源标签

        Returns:
            str: 本地完整路径
        """
        return os.path.join(
            self.get_resource_local_location(resource_tag),
            self.get_resource_local_filename(resource_tag),
        )

    @abstractmethod
    def get_version_list(
        self, reverse: bool = True, stable: bool = Config.FORCE_STABLE
    ) -> Iterable[str]:
        """获取可用版本列表。

        Args:
            reverse: 是否逆序返回结果，默认True（最新版本在前）
            stable: 是否只显示稳定版本，排除带有`alpha`/`beta`字样的版本

        Returns:
            Iterable[str]: 版本号的可迭代对象
        """
        pass

    def get_version_remote_location_list(self) -> List[str]:
        """
        获取某个版本中，资源远程存储目录的路径列表。

        Returns: 所有资源的路径列表

        """
        remote_location_list = []
        for resource_tag in self.get_available_resource_tag_list():
            remote_location_list.append(self.get_resource_remote_location(resource_tag))
        return remote_location_list

    def get_remote_location_list(self, remote_location: str) -> List[str]:
        """获取远程存储目录中的文件路径列表。

        如果子类重写了 `get_resource_remote_url` 或 `check_remote_resource_exists`，
        可以不需要实现此方法。

        Args:
            remote_location: 远程存储目录路径

        Returns:
            List[str]: 远程存储目录中的文件路径列表

        Raises:
            NotImplementedError: 如果子类未实现此方法且需要使用 `check_remote_resource_exists`
        """
        raise NotImplementedError(
            "Subclass must implement get_remote_location_list() "
            "or override check_remote_resource_exists()"
        )

    def check_remote_resource_exists(self, resource_tag: str) -> bool:
        """检查指定资源标签的远程资源是否存在。

        Args:
            resource_tag: 资源标签

        Returns:
            bool: 是否存在
        """
        remote_locations = self.get_version_remote_location_list()
        resource_url = self.get_resource_remote_url(resource_tag)
        return any(
            resource_url in self.get_remote_location_list(remote_location)
            for remote_location in remote_locations
        )

    def get_downloader(self) -> Downloader:
        """获取用于下载资源的 Downloader 对象。

        Returns: 资源下载器
        """
        logger.debug("Using default downloader: RequestsDownloader()")
        return RequestsDownloader()

    @dryrun
    def download_resource(
        self, resource_tag: str, download_path: Optional[str] = None
    ) -> str:
        """下载指定资源（如本地已存在，则跳过）。

        Args:
            resource_tag: 资源标签
            download_path: 指定下载目标路径（如不指定则用默认路径）

        Returns: 资源包本地路径
        """
        if self.download_path is None:
            assert self.resource_type is not None and self.version is not None
            self.download_path = os.path.join(
                Config.WORKSPACE_PATH, self.resource_type, self.version
            )
        package_storage_filename = self.get_resource_local_url(resource_tag)
        if os.path.exists(package_storage_filename):
            logger.info(f"{resource_tag} package file already exists.")
            return package_storage_filename
        if download_path is None:
            download_path = self.get_resource_local_location(resource_tag)
        logger.info(f"Start to download {resource_tag} package to {download_path}")
        logger.info(f"Downloading {self.get_resource_filename(resource_tag)}...")
        self.get_downloader().download_file(
            self.get_resource_remote_url(resource_tag), package_storage_filename
        )
        logger.info(f"Downloaded {resource_tag} package to {package_storage_filename}")
        return package_storage_filename

    def clean(self):
        """清空当前版本的包的下载路径。

        删除下载目录并重建空目录。

        Raises:
            ValueError: 如果download_path为None
            OSError: 如果删除或创建目录失败
        """
        if self.download_path is None:
            raise ValueError("download_path is None, cannot clean")
        if os.path.exists(self.download_path):
            shutil.rmtree(self.download_path)
        os.makedirs(self.download_path, exist_ok=True)

    def __builtin_pre_install_all(self, target_path: str):
        if target_path and not os.path.exists(target_path):
            os.makedirs(target_path, exist_ok=True)
        self.pre_install_all(target_path)

    def __builtin_post_install_all(self, target_path: str):
        self.post_install_all(target_path)

    def pre_install_all(self, target_path: str):
        """所有资源安装之前的操作。

        Args:
            target_path: 目标安装路径
        """
        pass

    def pre_install(self, resource_tag: str, target_path: str):
        """单个资源安装前的操作。

        Args:
            resource_tag: 资源标签
            target_path: 目标安装路径
        """
        pass

    def post_install(self, resource_tag: str, target_path: str):
        """单个资源安装后的操作。

        Args:
            resource_tag: 资源标签
            target_path: 目标安装路径
        """
        pass

    def post_install_all(self, target_path: str):
        """所有资源安装之后的操作。

        Args:
            target_path: 目标安装路径
        """
        pass

    @abstractmethod
    def install_resource(self, resource_tag: str, target_path: str):
        """
        将资源安装到目标路径
        Args:
            resource_tag: 资源标签
            target_path: 目标路径
        """
        pass

    def download_and_install_resource(
        self,
        target_path: str,
        necessary_resource_tag_list: Iterable[str] = (),
        mode: InstallerMode = InstallerMode.DDII,
    ):
        """批量下载并依据资源列表安装资源。

        Args:
            target_path: 目标安装路径
            necessary_resource_tag_list: 资源标签列表，如果为空则使用默认资源列表
            mode: 安装模式（DDII: 全部下载后安装, DIDI: 逐个下载安装, DO: 只下载不安装）

        Raises:
            ValueError: 如果资源标签不可用或找不到合适的版本
        """
        if not necessary_resource_tag_list:
            logger.warning(
                "No necessary resource tags provided, using default resource tags"
            )
            necessary_resource_tag_list = self.get_default_resource_tag_list()
        else:
            for resource_tag in necessary_resource_tag_list:
                if resource_tag not in self.get_available_resource_tag_list():
                    raise ValueError(f"Resource tag {resource_tag} is not available")
        if self.version is None:
            logger.warning("No version provided, trying to find the best version")
            self.version = self.get_best_version(necessary_resource_tag_list)
            if self.version is None:
                raise ValueError("No version found")
        logger.info(f"Using version {self.version}")
        if mode == InstallerMode.DDII or mode == InstallerMode.DO:
            for resource_tag in necessary_resource_tag_list:
                self.download_resource(resource_tag, self.download_path)
            if mode == InstallerMode.DO:
                return
            self.__builtin_pre_install_all(target_path)
            for resource_tag in necessary_resource_tag_list:
                self.pre_install(resource_tag, target_path)
                self.install_resource(resource_tag, target_path)
                self.post_install(resource_tag, target_path)
            self.__builtin_post_install_all(target_path)
        elif mode == InstallerMode.DIDI:
            self.__builtin_pre_install_all(target_path)
            for resource_tag in necessary_resource_tag_list:
                self.download_resource(resource_tag, self.download_path)
                self.pre_install(resource_tag, target_path)
                self.install_resource(resource_tag, target_path)
                self.post_install(resource_tag, target_path)
            self.__builtin_post_install_all(target_path)
