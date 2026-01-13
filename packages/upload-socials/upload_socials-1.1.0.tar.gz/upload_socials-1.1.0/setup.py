from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="upload-socials",
    version="1.1.0",
    author="AMAMazing",
    author_email="alexmalone489@gmail.com",
    description="A Python library to automate video uploads to YouTube.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AMAMazing/upload-socials",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'pyautogui',
        'pywin32',
        'optimisewait',
        'smartpaste'
    ],
    include_package_data=True,
    package_data={
        'upload_socials': ['uploadyt/*.png'],
    },
)
