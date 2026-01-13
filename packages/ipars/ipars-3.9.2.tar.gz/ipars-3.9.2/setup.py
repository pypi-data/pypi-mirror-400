from setuptools import setup, find_packages

setup(
    name='ipars',
    version='3.9.2',
    description='Библиотека для работы с файлами во время парсинга',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author_email='statute-wasp-frisk@duck.com',
    packages=find_packages(),
    author='Ilia Miheev',
    license='MIT',
    url='https://iliamiheev.github.io/ipars-doc/#/./home',
    install_requires=[
        'requests',
        'selenium',
        'lxml',
        'bs4',
        'progress',
        'random_user_agent',
        'cerberus'
    ],
    keywords=[
        'ipars', 
        'ипарс',
        'парсинг', 
        'скрапинг', 
        'parsing', 
        'scraping',
        'bs4',
        'beautifulsoup4'
    ],
    project_urls={
        'Bug Reports': 'https://github.com/IliaMiheev/ipars/issues',
        'Source': 'https://github.com/IliaMiheev/ipars',
    },
)
