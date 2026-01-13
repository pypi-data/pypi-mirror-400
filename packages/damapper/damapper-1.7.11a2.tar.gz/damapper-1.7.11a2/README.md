| Example of use | Abstract |
| :--------: | -------- | 
![image](https://gitlab.com/-/project/61464222/uploads/7d95d181921947a009c0a63c6d1771a5/image.png) | [DaMapper](https://gitlab.com/dlr-sy/damapper) is a damage segmentation and mapping tool for NDT data. The damage itself is abstracted as a polygon or idealized as an ellipse and can be exported layerwise as XML or IGES. <br><br>**Keywords**: `ndt` `segmentation` `postprocessing`

[![doc](https://img.shields.io/static/v1?label=Pages&message=User%20Guide&color=blue&style=flat&logo=gitlab)](https://dlr-sy.gitlab.io/damapper)
[![PyPi](https://img.shields.io/pypi/v/damapper?label=PyPi)](https://pypi.org/project/damapper)

# DaMapper
This package is supported by [stmlab](https://gitlab.com/dlr-sy/stmlab) and is best installed by running
```
stmlab install damapper
```
Please refer to [stmlab](https://gitlab.com/dlr-sy/stmlab) for further installation and licensing instructions.

## Downloading
Use GIT to get the latest code base. From the command line, use
```
git clone https://gitlab.dlr.de/dlr-sy/damapper damapper
```
If you check out the repository for the first time, you have to initialize all submodule dependencies first. Execute the following from within the repository. 
```
git submodule update --init --recursive
```
To fetch all required metadata for each submodule, use
```
git submodule foreach --recursive 'git checkout $(git config -f $toplevel/.gitmodules submodule.$name.branch || echo master) || git checkout main'
```
To update all refererenced submodules to the latest production level, use
```
git submodule foreach --recursive 'git pull origin $(git config -f $toplevel/.gitmodules submodule.$name.branch || echo master) || git pull origin main'
```

## Installation
DaMapper can be installed from source using [poetry](https://python-poetry.org). If you don't have [poetry](https://python-poetry.org) installed, run
```
pip install poetry --pre --upgrade
```
to install the latest version of [poetry](https://python-poetry.org) within your python environment. Use
```
poetry update
```
to update all dependencies in the lock file or directly execute
```
poetry install
```
to install all dependencies from the lock file. Last, you should be able to import DaMapper as a python package.
```python
import damapper
```

## Contact
* [Marc Garbade](mailto:marc.garbade@dlr.de)