"""
Setup file for flask_music_search
"""
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flask_music_search",
    packages=setuptools.find_packages(),
    author="Adam Bukolt",
    author_email="abukolt@gmx.com",
    description="Package that creates a Web interface to search a music DB.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={
        'console_scripts': [
            'music_search=music-search.sh',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
