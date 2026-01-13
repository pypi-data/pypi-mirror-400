import os
import sys
import platform
import glob
import shutil
import platform

from setuptools import setup, Extension
from setuptools import find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

scripts = []
for f in glob.glob("ailia_voice/*.py"):
    scripts.append(f)

def find_libraries():
    dll_names = []
    platforms = ["win32", "darwin", "linux_armv7l", "linux_aarch64", "linux_x86_64"]

    for platform in platforms:
        if platform == "win32":
            dll_platform = "windows/x64"
            dll_type = ".dll"
        elif platform == "darwin":
            dll_platform = "mac"
            dll_type = ".dylib"
        else:
            if platform == "linux_armv7l":
                dll_platform = "linux/armeabi-v7a"
            elif platform == "linux_aarch64":
                dll_platform = "linux/arm64-v8a"
            else:
                dll_platform = "linux/x64"
            dll_type = ".so"
    
        dll_path = "./ailia_voice/" + dll_platform + "/"

        for f in glob.glob(dll_path+"*"+dll_type):
            f = f.replace("\\", "/")
            f = f.replace("./ailia_voice/", "./")
            dll_names.append(f)

    dll_names.append("./LICENSE_AILIA_EN.pdf")
    dll_names.append("./LICENSE_AILIA_JA.pdf")
    dll_names.append("./oss/LICENSE_CMUDICT.txt")
    dll_names.append("./oss/LICENSE_G2P_EN.txt")
    dll_names.append("./oss/LICENSE_GPT_SOVITS.txt")
    dll_names.append("./oss/LICENSE_MECAB.txt")
    dll_names.append("./oss/LICENSE_NLTK.txt")
    dll_names.append("./oss/LICENSE_OPENJTALK.txt")
    dll_names.append("./oss/LICENSE_UNIDIC.txt")

    return dll_names
    
if __name__ == "__main__":
    setup(
        name="ailia_voice",
        scripts=scripts,
        version="1.4.0.0",
        install_requires=[
            "ailia",
        ],
        description="ailia AI Voice",
        long_description=long_description,
        long_description_content_type="text/markdown",
        author="ailia Inc.",
        author_email="contact@ailia.ai",
        url="https://ailia.ai/en/",
        license="https://ailia.ai/en/license/",
        packages=find_packages(),
        package_data={"ailia_voice":find_libraries()},
        include_package_data=True,
        python_requires=">3.6",
    )