"""The setup script."""
import re
from pathlib import Path

from setuptools import setup, find_packages

# 安装时依赖包
with open(file='dependence/requirements.txt', mode='r', encoding='utf-8') as f:
    requirements = f.read().splitlines()
    # 过滤本地包和空行
    requirements = list(filter(lambda x: x and re.search(r'local', x) is None and not x.startswith('#'), requirements))
    # print(requirements)

setup(
    name='geocoding-cli',
    version='1.0.3',
    author="zzhoo8",
    author_email='zzhoo8@gmail.com',
    description="将 Excel 中的地址列批量转换为经纬度（百度地图 API）",
    long_description=(Path(__file__).parent / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    license="LicenseRef-Proprietary",
    license_files=["LICENSE"],
    python_requires='>=3.10',
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "geocoding-cli=geocoding.main:main",
        ],
    },
    extras_require={
    },
    include_package_data=True,
    keywords='geocoding',
    url='https://github.com/zzhoo8/geocoding-cli',
    zip_safe=False
)
