from setuptools import find_packages, setup

VERSION = "1.26"
DESCRIPTION = "CLI for downloading all repositories from a specified user."
with open("README.md", "r") as file:
    LONG_DESCRIPTION = file.read()
AUTHOR = "NecRaul"
AUTHOR_EMAIL = "necraul@kuroneko.dev"

setup(
    name="git_neko",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=find_packages(),
    keywords=[
        "python",
        "repository downloader",
        "downloader",
        "repository",
        "git-neko",
        "kuroneko",
    ],
    url="https://github.com/NecRaul/git-neko",
    project_urls={
        "Documentation": "https://github.com/NecRaul/git-neko#readme",
        "Source": "https://github.com/NecRaul/git-neko",
        "Issues": "https://github.com/NecRaul/git-neko/issues",
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
            "git-neko = git_neko:main",
        ],
    },
)
