from setuptools import setup, find_packages

setup(
    name='tonique',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'numpy'
    ],
    entry_points={
        "console_scripts": [
            "tonique-hello = tonique:hello",
        ]
    }
)