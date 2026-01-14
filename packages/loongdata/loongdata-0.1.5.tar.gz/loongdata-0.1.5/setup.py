from setuptools import setup, find_packages

setup(
    name="loongdata",
    version="0.1.5",
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        "tqdm",
        "requests>=2.20.0",
        "argparse>=1.1",
        "httpx",
        "rich"
    ],
    entry_points={
        'console_scripts': [
            'loongdata=loongdata.cli:main',
        ],
    },
    # 其他元数据...
)