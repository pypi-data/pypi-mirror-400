from setuptools import setup, find_packages

setup(
    name='hero-core',
    packages=find_packages(),
    author='Baidu',
    author_email='wangdejiang@baidu.com',
    description='Agentic framework for LLM',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/baidu/hero-core',
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache License 2.0",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3.12",
        "Typing :: Typed",
    ],
    python_requires='>=3.12',
    package_data={
        'hero': ['build_in_tool/prompt/*.md', 'util/*.txt', 'util/tokenizer/*/*.json'],
    },
)
