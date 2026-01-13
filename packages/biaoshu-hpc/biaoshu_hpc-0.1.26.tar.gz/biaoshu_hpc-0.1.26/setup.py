from setuptools import setup, find_packages
import os

# 获取当前目录
here = os.path.abspath(os.path.dirname(__file__))

# 定义包数据
package_data = {
    'biaoshu_hpc.lcs': ['*.so', '*.pyd'],
    'biaoshu_hpc.difflib_hpc': ['*.so', '*.pyd'],
}


# 设置 setup 参数
setup(
    name='biaoshu_hpc',
    version='0.1.26',
    description='biaoshu_hpc',
    long_description="",
    long_description_content_type='text/markdown',
    author='huangwenbin',
    author_email='huangwb5@chinatelecom.cn ',
    packages=find_packages(),
    package_data=package_data,
    include_package_data=True,
    python_requires='>=3.10',
    install_requires=[
        # 添加依赖项
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
    ],
)
