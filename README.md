# 格雷科技6(GregTech6)核反应堆模拟器
(由于我懒得弄英文版所以介绍也用中文写了)

鉴于网上没有好用的GT6的核反应堆模拟器，我就自己写了一个

目前适用版本6.14.00(该版本有钍盐反应堆不输出的bug，模拟器里还是照样输出)

# 预览
![preview](/preview.png)
软件引导应该还可以所以就懒得写怎么用了（

# 下载
直接在[Releases](https://github.com/CHanzyLazer/GT6_nuclear_simulator/releases)下载

# 代码
## 运行
需要前置包
```shell
pip install pillow
pip install mouse==0.7.0
pip install pyyaml
pip install ruamel.yaml
```
运行 `main.py` 即可

## 打包
使用 pyinstaller 打包：
```shell
pip install pyinstaller
```
运行
```shell
pyinstaller -F -w -i textures\nuclearsim.ico main.py
```