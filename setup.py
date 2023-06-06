from setuptools import setup

setup(
    name='redcli',
    version='1.0',
    scripts=['redcli.py'],
    entry_points={
        'console_scripts': [
            'redcli = redcli:main'
        ]
    }
)
