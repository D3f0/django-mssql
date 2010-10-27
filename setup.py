from setuptools import setup, find_packages

version = __import__('sqlserver_ado').get_version()

setup(
    name='django-mssql',
    version=version.replace(' ', '-'),
    maintainer='Michael Manfre',
    maintainer_email='mmanfre@gmail.com',
    url='http://django-mssql.googlecode.com/',
    description="Django backend database support for MS SQL 2005 and up.",
    license='Apache License, Version 2.0',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "Environment :: Web Environment",
    ],
)
