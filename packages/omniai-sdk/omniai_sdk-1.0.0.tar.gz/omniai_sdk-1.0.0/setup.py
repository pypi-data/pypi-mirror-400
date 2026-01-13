from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='omniai-sdk',
    version='1.0.0',
    author='OmniAI Team',
    author_email='dev@omniaiassist.com',
    description='Official Python SDK for OmniAI API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/omniaiassist/omniai-python-sdk',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.7',
    install_requires=[
        'requests>=2.25.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.10',
            'black>=21.0',
            'flake8>=3.8',
        ],
    },
    keywords='omniai api sdk whatsapp messaging ai automation',
    project_urls={
        'Documentation': 'https://docs.omniaiassist.com',
        'Source': 'https://github.com/omniaiassist/omniai-python-sdk',
        'Bug Reports': 'https://github.com/omniaiassist/omniai-python-sdk/issues',
    },
)
