#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: bb(bobby.miao)
# Description: APP Launch Test

from setuptools import setup, find_packages

setup(
    name='bblt',
    version='26.1.5.1',
    keywords='launchtest',
    description='APP Launch Test',
    license='MIT License',
    url='https://github.com/xiaoyaoamiao/lt.git',
    author='bob',
    author_email='miao2005xu@163.com',
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    install_requires=[
                'ImageHash == 4.2.1',
                'facebook-wda  == 1.0.11',
                'Pillow == 9.2.0',
                'opencv-python == 4.10.0.84',
                'paddleocr >= 2.9.1',
                'paddlepaddle >= 2.6.1',
                'pandas == 2.2.3',
                'matplotlib == 3.5.0',
                'Appium-Python-Client==4.4.0',
        ],
)