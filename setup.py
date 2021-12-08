from setuptools import setup, find_packages

setup(
    name='tsm',
    version='0.1.0',
    description='Taiwanese Southern Min text processing',
    author='Chung-Yi Li',
    author_email='leon129506@gmail.com',
    url='https://github.com/Chung-I/tsm',
    packages=find_packages(
        exclude=[
            "*.tests",
            "*.tests.*",
            "tests.*",
            "tests",
            "test_fixtures",
            "test_fixtures.*"
        ]
    ),
    install_requires=[
        'cn2an',
        'regex',
        'zhon',
        'pandas',
        'numpy',
        'scipy',
        'ckiptagger',
        'opencc',
        'tai5-uan5_gian5-gi2_kang1-ku7',
    ],
    include_package_data=True,
)
