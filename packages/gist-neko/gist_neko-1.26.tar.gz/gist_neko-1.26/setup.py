from setuptools import find_packages, setup

VERSION = "1.26"
DESCRIPTION = "CLI for downloading all gists from a specified user."
with open("README.md", "r") as file:
    LONG_DESCRIPTION = file.read()
AUTHOR = "NecRaul"
AUTHOR_EMAIL = "necraul@kuroneko.dev"

setup(
    name="gist_neko",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=find_packages(),
    keywords=[
        "python",
        "gist downloader",
        "downloader",
        "gist",
        "gist-neko",
        "kuroneko",
    ],
    url="https://github.com/NecRaul/gist-neko",
    project_urls={
        "Documentation": "https://github.com/NecRaul/gist-neko#readme",
        "Source": "https://github.com/NecRaul/gist-neko",
        "Issues": "https://github.com/NecRaul/gist-neko/issues",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP",
    ],
    py_modules=["download", "environment"],
    entry_points={
        "console_scripts": [
            "gist-neko = gist_neko:main",
        ],
    },
)
