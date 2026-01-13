from setuptools import setup, find_packages

setup(
    name="nyxai-cli",
    version="4.0.1",
    description="Nyx AI Tools CLI",
    author="Nyx AI Tools",
    packages=find_packages(include=["nyx_kaggle_manager", "nyx_kaggle_manager.*"]),
    include_package_data=True,
    install_requires=[
        "kaggle>=1.6.0",
        "pyyaml>=6.0",
        "psutil>=6.0.0",
        "requests>=2.31.0",
        "aiohttp>=3.9.0"
    ],
    entry_points={
        "console_scripts": [
            "nyxcli=nyx_kaggle_manager.nyxcli:main_entry_point",
        ],
    },
    python_requires=">=3.7",
)
