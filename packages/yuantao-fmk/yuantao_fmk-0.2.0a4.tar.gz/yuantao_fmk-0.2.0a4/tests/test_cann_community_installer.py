from yuantao_fmk.impl.run_package_installer.cann_community_installer import CANNCommunityInstaller
from yuantao_fmk import Config
import unittest

class TestCANNCommunityInstaller(unittest.TestCase):
    def test_list_version(self):
        installer = CANNCommunityInstaller(None, "910b")
        Config.FORCE_STABLE = False
        print(installer.list_version(reverse=True))


    def test_get_latest_version(self):
        installer = CANNCommunityInstaller(None, "910b")
        print(installer.get_latest_version())

    def test_get_default_resource_tags(self):
        installer = CANNCommunityInstaller(None, "910b")
        print(installer.get_default_resource_tags())
    
    def test_install_resource(self):
        installer = CANNCommunityInstaller(None, "910b")
        installer.download_and_install_resource("/home/yuantao/Ascend/"+installer.version, ["toolkit"])

if __name__ == "__main__":
    unittest.main()