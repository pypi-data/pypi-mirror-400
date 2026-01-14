"""Setup configuration for agentmonitor package."""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

setup(
    name='agentmonitor',
    version='0.1.0',
    author='AgentMonitor Team',
    author_email='support@agentmonitor.io',
    description='Production-ready SDK for monitoring AI agents',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/agentmonitor/sdk-python',
    project_urls={
        'Documentation': 'https://docs.agentmonitor.io',
        'Source': 'https://github.com/agentmonitor/sdk-python',
        'Tracker': 'https://github.com/agentmonitor/sdk-python/issues',
    },
    packages=find_packages(exclude=['tests', 'examples']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Monitoring',
    ],
    python_requires='>=3.8',
    install_requires=[
        'requests>=2.28.0',
        'typing-extensions>=4.0.0',
    ],
    extras_require={
        'async': [
            'aiohttp>=3.8.0',
        ],
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.0.0',
            'responses>=0.23.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ],
    },
    keywords='ai agent monitoring observability analytics ml llm',
    include_package_data=True,
    zip_safe=False,
)
