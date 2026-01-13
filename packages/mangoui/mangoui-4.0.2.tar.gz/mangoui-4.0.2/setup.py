from setuptools import setup, find_packages

__version__ = '4.0.2'

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='mangoui',
    version=__version__,
    description='UI组件库',
    long_description=long_description,
    long_description_content_type="text/markdown",  # 添加这一行
    author='毛鹏',
    author_email='729164035@qq.com',
    url='https://gitee.com/mao-peng/MangoUi',
    packages=find_packages(),
    install_requires=[
        'pydantic>=2.9.2',
        'pyside6>=6.8.1',
        'matplotlib>=3.9.2',
        'numpy>=2.2.0',
        'pyqtgraph>=0.13.7'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    license_expression="MIT",  # 使用 SPDX 许可证表达式
    python_requires='>=3.10',
)

r"""
pyside6-rcc D:\GitCode\MangoUi\mango_ui\resources\resources.qrc -o D:\GitCode\MangoUi\mango_ui\resources\app_rc.py

python -m pip install --upgrade setuptools wheel
python -m pip install --upgrade twine

python setup.py check
python setup.py sdist bdist_wheel
twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
"""