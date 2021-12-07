# -*- coding: utf-8 -*-
from setuptools import setup
import os


# Setup!
setup(
    name="BigPl",
    description="VPLANET Data Analysis Tools",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/VirtualPlanetaryLaboratory/BigPlanet",
    author="Caitlyn Wilhelm",
    author_email="cwilhelm@uw.edu",
    license="MIT",
    packages=["BigPlanet"],
    include_package_data=True,
    use_scm_version={
        "write_to": os.path.join("bigplanet", "bigplanet_version.py"),
        "write_to_template": '__version__ = "{version}"\n',
    },
    install_requires=["numpy", "h5py", "argparse",
                      "scipy", "pandas"],
    entry_points={
        "console_scripts": [
            "BigPlanet = BigPlanet.BigPlanet:Arguments",
            "bpstatus = BigPlanet.bpstatus:main",
        ],
    },
    setup_requires=["setuptools_scm"],
    zip_safe=False,
)
