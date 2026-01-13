from setuptools import setup, find_packages

def readme():
    with open('README.md', 'r') as file:
        return file.read()

setup(
    name = 'artconsole',
    version = '1.0.8',
    author = 'Dima M. Shirokov',
    author_email = 'D.Shirokov05@yandex.ru',
    description = '🚀 This is a library 📖 for outputting beautiful ASCII images 🏞️ to the console written in Python 🐍!',
    long_description = readme(),
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/dimamshirokov/artconsole',
    packages = find_packages(),
    classifiers = [
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    project_urls = {
        'GitHub': 'https://github.com/dimamshirokov'
    },
    python_requires = '>=3.6'
)