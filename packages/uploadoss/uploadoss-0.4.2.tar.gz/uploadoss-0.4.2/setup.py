from setuptools import setup, find_packages
import codecs

# with open('README.md') as f:
#     long_description = f.read()

setup(
    name='uploadoss',
    version='0.4.2',
    author='Binghe',
    description='Uploadoss is the general module of uploading database data and local files to the Alibaba Cloud OSS',
    packages=find_packages(),
    install_requires=[
        'oss2',
        'pandas',
        'pymysql',
        'configparser',
        'oracledb',
        'csv',
        'gzip'
    ],
    project_urls={  
        'Source': 'https://github.com/binghexmo/uploadoss/',   
    },
    long_description=(codecs.open("README.md", encoding='utf-8').read()),
    long_description_content_type="text/markdown"
)

