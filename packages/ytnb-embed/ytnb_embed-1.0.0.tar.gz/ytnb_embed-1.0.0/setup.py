import setuptools
from pathlib import Path

BASE_DIR = Path(__file__).parent
long_description = (BASE_DIR / "README.md").read_text(encoding="utf-8")

__version__ = "1.0.0"

REPO_NAME = "ytnb-embed"
PACKAGE_NAME = "ytnb_embed"
AUTHOR_USER_NAME = "aatansen"
AUTHOR_EMAIL = "aatansen@gmail.com"

setuptools.setup(
    name=REPO_NAME,
    version=__version__,
    author=AUTHOR_USER_NAME,
    author_email=AUTHOR_EMAIL,
    description="Embed youtube video inside notebook",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}",
    project_urls={
        "Bug Tracker": f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}/issues",
    },
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src")
)