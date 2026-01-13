# Copyright (C) 2025 Tao Yuan
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.

import os
import re
import shutil
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Generator, List, Optional, Union

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
        version: Optional[str],
        resource_type: Optional[str],
        download_path: Optional[str] = None,
    ):
        """初始化资源安装器。

        参数:
            version (str): 资源版本号
            resource_type (str): 资源类型
            download_path (str): 资源包下载保存路径
        """
        super().__init__()
        """
        About version:

        """
        if version is not None:
            self.version = self.get_actual_version(version)
        else:
            self.version = self.get_latest_version()
        self.resource_type = resource_type
        self.download_path = download_path or os.path.join(
            Config.WORKSPACE_PATH, self.resource_type, self.version
        )

    def get_actual_version(self, original_version: str) -> str:
        """
        在某些场景下，传入版本可能并非实际版本.
        默认返回原始版本，可重载实现逻辑.
        Args:
            original_version:

        Returns:

        """
        return original_version

    def get_filename_version(self, resource_tag: Optional[str] = None) -> str:
        """
        提取文件名中的版本号
        Args:
            resource_tag:

        Returns:

        """
        raise NotImplementedError

    def get_actual_version_pattern(self) -> re.Pattern:
        """
        获取实际版本正则表达式
        Returns:

        """

    def get_latest_version(self) -> str:
        """获取最新的实际版本号"""
        return self.list_version(True, True)[0]

    @abstractmethod
    def get_default_resource_tags(self) -> List[str]:
        """获取默认的资源类型"""
        pass

    @abstractmethod
    def get_available_resource_tags(self) -> List[str]:
        pass

    @abstractmethod
    def get_resource_filename(self, resource_tag: Optional[str]) -> str:
        """获取指定资源标签所对应的文件名。

        参数:
            resource_tag (Optional[str]): 资源标签

        返回:
            str: 文件名
        """
        pass

    def get_resource_remote_location(self, resource_tag: Optional[str]) -> str:
        """获取指定资源标签远程存储目录的路径。

        参数:
            resource_tag (Optional[str]): 资源标签

        返回:
            str: 远程目录路径
        """
        raise NotImplementedError

    def get_resource_remote_filename(self, resource_tag: Optional[str]) -> str:
        """获取资源标签远程文件名（默认直接与本地文件名一致）。

        参数:
            resource_tag (Optional[str]): 资源标签

        返回:
            str: 文件名
        """
        return self.get_resource_filename(resource_tag)

    def get_resource_local_location(self, resource_tag: Optional[str]) -> str:
        """获取指定资源标签本地存储目录的路径。

        参数:
            resource_tag (Optional[str]): 资源标签

        返回:
            str: 本地存储路径
        """
        return self.download_path

    def get_resource_local_filename(self, resource_tag: Optional[str]) -> str:
        """获取本地文件名（默认直接与资源文件名一致）。

        参数:
            resource_tag (Optional[str]): 资源标签

        返回:
            str: 文件名
        """
        return self.get_resource_filename(resource_tag)

    def get_resource_remote_url(self, resource_tag: Optional[str]) -> str:
        """获取资源标签的完整远程URL。

        参数:
            resource_tag (Optional[str]): 资源标签

        返回:
            str: 远程完整URL
        """
        return (
            self.get_resource_remote_location(resource_tag).rstrip("/")
            + "/"
            + self.get_resource_remote_filename(resource_tag)
        )

    def get_resource_local_url(self, resource_tag: Optional[str]) -> str:
        """获取资源标签的本地完整文件路径。

        参数:
            resource_tag (Optional[str]): 资源标签

        返回:
            str: 本地完整路径
        """
        return os.path.join(
            self.get_resource_local_location(resource_tag),
            self.get_resource_local_filename(resource_tag),
        )

    def list_version(
        self, reverse: bool = True, stable: bool = Config.FORCE_STABLE
    ) -> Union[List[str], Generator]:
        """
        列出可用版本
        Returns:

        """
        raise NotImplementedError

    def list_remote_location(self, remote_location: str) -> List[str]:
        """获取远程存储目录的路径列表。

        返回:
            List[str]: 远程存储目录的路径列表
        """
        raise NotImplementedError

    def check_remote_resource_exists(self, resource_tag: str) -> bool:
        """检查指定资源标签的远程资源是否存在。

        参数:
            resource_tag (str): 资源标签

        返回:
            bool: 是否存在
        """
        return self.get_resource_remote_url(resource_tag) in self.list_remote_location(
            self.get_resource_remote_location(resource_tag)
        )

    def get_downloader(self) -> Downloader:
        """获取用于下载资源的 Downloader 对象。

        返回:
            Downloader: 用于资源下载的对象
        """
        return RequestsDownloader()

    @dryrun
    def download_resource(
        self, resource_tag: Optional[str], download_path: Optional[str] = None
    ) -> str:
        """下载指定资源（如本地已存在，则跳过）。

        参数:
            resource_tag (Optional[str]): 资源标签
            download_path (Optional[str]): 指定下载目标路径（如不指定则用默认路径）

        返回:
            str: 资源包本地路径
        """
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
        """
        shutil.rmtree(self.download_path)
        os.makedirs(self.download_path, exist_ok=True)

    def __builtin_pre_install_all(self, target_path: Optional[str]):
        if target_path and not os.path.exists(target_path):
            os.makedirs(target_path, exist_ok=True)
        self.pre_install_all(target_path)

    def __builtin_post_install_all(self, target_path: Optional[str]):
        self.post_install_all(target_path)

    def pre_install_all(self, target_path: Optional[str]):
        """所有资源安装之前的操作。

        参数:
            target_path (Optional[str]): 目标安装路径
        """
        pass

    def pre_install(self, resource_tag: Optional[str], target_path: Optional[str]):
        """单个资源安装前的操作。

        参数:
            resource_tag (Optional[str]): 资源标签
            target_path (Optional[str]): 目标安装路径
        """
        pass

    def post_install(self, resource_tag: Optional[str], target_path: Optional[str]):
        """单个资源安装后的操作。

        参数:
            resource_tag (Optional[str]): 资源标签
            target_path (Optional[str]): 目标安装路径
        """
        pass

    def post_install_all(self, target_path: Optional[str]):
        """所有资源安装之后的操作。

        参数:
            target_path (Optional[str]): 目标安装路径
        """
        pass

    @abstractmethod
    def install_resource(self, resource_tag: Optional[str], target_path: Optional[str]):
        """执行单个资源安装的抽象方法，应在子类中实现具体的安装逻辑。

        参数:
            resource_tag (Optional[str]): 资源标签
            target_path (Optional[str]): 目标安装路径
        """
        pass

    def download_and_install_resource(
        self,
        target_path: Optional[str],
        necessary_resource_tags: List[str] = [],
        mode: InstallerMode = InstallerMode.DDII,
    ):
        """批量下载并安装所有资源的主流程。

        参数:
            target_path (Optional[str]): 资源的安装目标目录
            necessary_resource_tags (List[str]): 所需的资源标签列表
            mode (InstallerMode, 可选): 安装模式，可选为DDII、DIDI、DO，默认DDII。

        主要流程如下：
            - DDII/DO: 先下载全部资源；DO模式只下载不安装；否则继续做批量预处理和批量安装
            - DIDI: 先批量做预处理，逐条下载和安装资源，安装后做批量后处理
        """
        if necessary_resource_tags == []:
            necessary_resource_tags = self.get_default_resource_tags()
        if mode == InstallerMode.DDII or mode == InstallerMode.DO:
            for resource_tag in necessary_resource_tags:
                self.download_resource(resource_tag, self.download_path)
            if mode == InstallerMode.DO:
                return
            self.__builtin_pre_install_all(target_path)
            for resource_tag in necessary_resource_tags:
                self.pre_install(resource_tag, target_path)
                self.install_resource(resource_tag, target_path)
                self.post_install(resource_tag, target_path)
            self.__builtin_post_install_all(target_path)
        elif mode == InstallerMode.DIDI:
            self.__builtin_pre_install_all(target_path)
            for resource_tag in necessary_resource_tags:
                self.download_resource(resource_tag, self.download_path)
                self.pre_install(resource_tag, target_path)
                self.install_resource(resource_tag, target_path)
                self.post_install(resource_tag, target_path)
            self.__builtin_post_install_all(target_path)
