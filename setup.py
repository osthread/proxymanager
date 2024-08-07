# setup.py
from setuptools import setup, find_packages

setup(
    name='proxymanager',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'aiosqlite'
    ],
    author='osthread',
    author_email='support@trinixbot.xyz',
    description='A simple asynchronous proxy manager using SQLite3.',
    keywords='proxy manager asynchronous sqlite',
    url='',  # Optional project URL
)
