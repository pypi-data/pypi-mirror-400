from setuptools import setup, find_packages
import os

# 读取README文件
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# 获取版本信息
with open('upx_installer/__init__.py', 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip("'\"")
            break
    else:
        version = '1.0.0'

setup(
    name='upx-installer',
    version=version,

    description='自动安装UPX可执行文件到Windows系统',
    long_description=long_description,
    long_description_content_type='text/markdown',
    
    packages=find_packages(),
    package_data={
        'upx_installer': ['data/*.exe'],
    },
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'upx-installer=upx_installer.installer:main',
        ],
    },
    install_requires=[
        'setuptools>=45.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'twine>=3.0',
            'wheel>=0.36',
        ],
    },
    keywords='upx, installer, executable, compression, windows',

)
