import setuptools
import pathlib

here = pathlib.Path(__file__).parent.resolve()

with open(here / "README.md", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="anipy-server",
    version="0.1.7",
    description="A modern, self-hosted anime scrapper and streaming server.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="B14CK-KN1GH7",
    author_email="owner@anipy.stream",
    url="https://anipy.stream",
    project_urls={
        "SERVER": "https://anipy.stream",
    },
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn",
        "bs4",
        "lxml",
        "jinja2",
        "requests",
        "selenium",
        "undetected-chromedriver",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "anipy=anipy_server.main:main",
        ],
    },
    python_requires=">=3.10",
    keywords=["anime", "server", "streaming", "web", "self-hosted", "media","scrapper","animepahe-scrapper"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video :: Display",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
)