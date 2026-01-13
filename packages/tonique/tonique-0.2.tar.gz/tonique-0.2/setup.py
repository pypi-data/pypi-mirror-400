from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    description = f.read()

setup(
    name='tonique',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        'numpy'
    ],
    entry_points={
        "console_scripts": [
            "tonique-hello = tonique:hello",
        ]
    },
    long_description=description,
    long_description_content_type='text/markdown'
)