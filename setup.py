from distutils.core import setup

from setuptools import find_packages

import about_time


def get_readme():
    with open('README.md', encoding='utf-8') as readme_file:
        return readme_file.read()


setup(
    name='about-time',
    version=about_time.__version__,
    description='Easily measure timing and throughput of code blocks, '
                'with beautiful human friendly representations.',
    long_description=get_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/rsalmei/about-time',
    author=about_time.__author__,
    author_email=about_time.__email__,
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Environment :: Console',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # 'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.2',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: 3.5',
        # 'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords='python track tracker time code blocks monitor statistics analytics'.split(),
    packages=find_packages(),
    data_files=[('', ['LICENSE'])],
    python_requires='>=3.7, <4',
    install_requires=[],
)
