from setuptools import setup, find_packages
from os import path

# Read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()
    
setup(
    name='captivate-ai-api',
    version='0.6.2',
    description="An API for Captivate conversation and state management",
    long_description=long_description,
    long_description_content_type="text/markdown",  # or "text/x-rst" if you're using reStructuredText
    author="Lance Del Valle",
    author_email="lance@captivatechat.com",
    url="https://github.com/captivatechat/captivate-ai-api",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pydantic>=2.5.0',
        'httpx>=0.25.2'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    license="MIT",  # License field
)