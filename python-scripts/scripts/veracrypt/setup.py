from setuptools import setup

setup (
    name='veracrypt-cli-tools',
    version='1.0',
    py_modules=['vctools'],
    install_requires=[
        'Click'
    ],
    entry_points='''
        [console_scripts]
        hello=vctools:test
    '''
)