## 维护
- 打包时依赖
```bash
pip install setuptools twine wheel
```
- 构建和推送
```bash
 python setup.py sdist bdist_wheel 
```
```bash
 twine upload  dist/*  -r ctcdn-pypi  --config-file .\custom.pypirc
```
推送到pypi
```bash
 twine upload  dist/* 
```

- 安装包
```bash
pip install -i  https://pypi-readonly:VelYkURflvbDOkE7lNRu@devops.ctcdn.cn/nexus/repository/group-pypi/simple  biaoshu_hpc==0.1.26
```
- 查看当前系统架构
```
python -c "import platform;print(platform.platform())"
```

## 使用
### LCS算法
```python
from biaoshu_hpc.lcs import LCS
LCS.calculate_general("a", "aa")
LCS.calculate_dp("acccgggc", "aagggc")
```
