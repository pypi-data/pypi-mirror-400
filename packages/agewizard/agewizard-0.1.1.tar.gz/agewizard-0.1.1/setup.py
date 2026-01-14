from setuptools import setup, find_packages

setup(
    name="agewizard",          # Package name on PyPI
    version="0.1.1",         # Bump for import name fix
    packages=find_packages(),
    install_requires=[],     # Dependencies (none if pure Python)
    python_requires=">=3.6",
    author="Kamran Hussain",
    author_email="contact.kamrankami@gmail.com",
    description="A powerful age calculator library",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/KamranProjects/agewizard",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
