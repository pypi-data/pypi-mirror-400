from setuptools import setup, find_packages

setup(
    name="hoper_ramanjaneyulu",
    version="0.1.1",
    author="ram",
    author_email="ram@gmail.com",
    description="A simple calculator package",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [     # ✅ FIXED
            "hoper_ramanjaneyulu=hoper_ramanjaneyulu.calculator:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",   # case-sensitive fix
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
