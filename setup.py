# -*- coding: utf-8 -*-

"""Youtube-dl-gui setup file.

Examples:
    Windows/Linux::

        python setup.py pyinstaller

    Linux::

        python setup.py install

    Build source distribution::

        python setup.py sdist

    Build platform distribution::

        python setup.py bdist

"""

import os
import sys
from setuptools import setup, Command
from distutils.spawn import spawn
import time


__packagename__ = "youtube_dl_gui"

PYINSTALLER = len(sys.argv) >= 2 and sys.argv[1] == "pyinstaller"

try:
    from PyInstaller import compat as pyi_compat

    if pyi_compat.is_win:
        # noinspection PyUnresolvedReferences
        from PyInstaller.utils.win32.versioninfo import (
            VarStruct, VarFileInfo, StringStruct, StringTable,
            StringFileInfo, FixedFileInfo, VSVersionInfo, SetVersion,
        )
except ImportError:
    pyi_compat = None
    if PYINSTALLER:
        print("Cannot import pyinstaller", file=sys.stderr)
        exit(1)

# Get the info from UI/__init__.py without importing the package
exec(compile(open("UI/__init__.py").read(), "UI/__init__.py", "exec"))

DESCRIPTION = __description__
LONG_DESCRIPTION = __descriptionfull__


def on_windows():
    """Returns True if OS is Windows."""
    return os.name == "nt"


def version2tuple(commit=0):
    version_list = str(__version__).split(".")
    if len(version_list) > 3:
        _commit = int(version_list[3])
        del version_list[3]
    else:
        _commit = commit

    _year, _month, _day = [int(value) for value in version_list]
    return _year, _month, _day, _commit


def version2str(commit=0):
    version_tuple = version2tuple(commit)
    return "%s.%s.%s.%s" % version_tuple


class BuildPyinstallerBin(Command):
    description = "Build the executable"
    user_options = []
    version_file = None
    if pyi_compat and pyi_compat.is_win:
        version_file = VSVersionInfo(
            ffi=FixedFileInfo(
                filevers=version2tuple(),
                prodvers=version2tuple(),
                mask=0x3F,
                flags=0x0,
                OS=0x4,
                fileType=0x1,
                subtype=0x0,
                date=(0, 0),
            ),
            kids=[
                VarFileInfo([VarStruct("Translation", [0, 1200])]),
                StringFileInfo(
                    [
                        StringTable(
                            "000004b0",
                            [
                                StringStruct("CompanyName", __maintainer_contact__),
                                StringStruct("FileDescription", DESCRIPTION),
                                StringStruct("FileVersion", version2str()),
                                StringStruct("InternalName", "youtube-dl-gui.exe"),
                                StringStruct(
                                    "LegalCopyright",
                                    __projecturl__ + "LICENSE",
                                ),
                                StringStruct("OriginalFilename", "youtube-dl-gui.exe"),
                                StringStruct("ProductName", __appname__),
                                StringStruct("ProductVersion", version2str()),
                            ],
                        )
                    ]
                ),
            ],
        )

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self, version=version_file):
        """Run pyinstaller"""
        if on_windows():
            path_sep = ";"
        else:
            path_sep = ":"
        
        spawn(
            [
                "pyinstaller",
                "-w",
                "-F",
                "--icon=UI/images/icon.ico",
                "--add-data=UI/images"+path_sep+"UI/images",
                "--name=youtube-dl-gui",
                "main.py",
            ],
            dry_run=self.dry_run)

        if version:
            time.sleep(3)
            SetVersion("./dist/youtube-dl-gui.exe", version)


def setup_data():
    """Setup params for Windows/Linux"""
    # Add pixmaps icons (*.ico,*.png)
    package_data = {"UI": [
        "images/*.ico",
        "images/*.png"
    ]}
    setup_params = {
       "package_data": package_data,
    }

    return setup_params

cmdclass = dict()
params = dict()

if PYINSTALLER:
    cmdclass.update({"pyinstaller": BuildPyinstallerBin})
else:
    params = setup_data()
    params["entry_points"] = {
        "console_scripts": ["youtube-dl-gui = main:main"]
    }


setup(
    name=__packagename__,
    version=__version__,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url=__projecturl__,
    author=__author__,
    author_email=__contact__,
    maintainer=__maintainer__,
    maintainer_email=__maintainer_contact__,
    license=__license__,
    py_modules=["main"],
    packages=["GUI", "Threads", "UI", "youtube_dl", "youtube_dl.downloader", "youtube_dl.extractor", "youtube_dl.postprocessor"],
    include_package_data=True,
    python_requires=">=3.6.0",
    install_requires=["PyQt5>=5.15.2"],
    classifiers=[
        "Topic :: Multimedia :: Video :: User Interfaces",
        "Development Status :: 5 - Production/Stable",
        "Environment :: MacOS X :: Cocoa",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications :: GTK",
        "License :: Public Domain",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    cmdclass=cmdclass,
    **params
)
