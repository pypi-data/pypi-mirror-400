# yuantao_fmk

这是陶源自己开发的软件的一些基础框架部分，由于想在任何场景复用，所以抽取成框架。

## 接口示例

```python
from yuantao_fmk import InstallerBase

class MyInstaller(InstallerBase):
    ...

if __name__ == "__main__":
    my_installer = MyInstaller()
    

## TODO

- [ ] 下载进度条显示文件大小