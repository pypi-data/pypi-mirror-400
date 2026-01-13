from setuptools import setup, find_packages
from pathlib import Path

# Baca README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="iewil",
    version="0.0.7",
    author="iewilmaestro",
    author_email="purna.iera@gmail.com",
    description="Modul pribadi iewil: display, captcha, html scraping, cache storage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        'requests',
        'pillow'
    ],
    keywords=['iewil', 'display', 'captcha', 'scraping', 'cache'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ]
)
