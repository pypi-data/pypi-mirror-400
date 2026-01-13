from setuptools import setup, find_packages

setup(
    name='hnt_nf_caixa_jira_library',
    version='0.0.4',
    license='MIT License',
    author='Pepe',
    maintainer='Pepe',
    keywords='nota_fiscal',
    description=u'Lib to access nf from Jira',
    packages=find_packages(),
    package_data={'nfe': ['integrations/*','model/*','notification/*']},
    include_package_data=True,
    install_requires=[
        'requests',
        'pydantic>=2.5.2'
    ],
)