import os

from setuptools import setup

bundle_7zip = os.environ.get("BUNDLE_7ZIP", "") == "1"

if bundle_7zip:
    package_data = {
        "stygian_compressor": ["7zip_32bit/*", "7zip_64bit/*"],
    }
else:
    package_data = {}

setup(
    package_data=package_data,
)
