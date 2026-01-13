from setuptools import setup,find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cobweb_launcher",
    version="3.2.21",
    packages=find_packages(),
    url="https://github.com/Juannie-PP/cobweb",
    license="MIT",
    author="Juannie-PP",
    author_email="2604868278@qq.com",
    description="spider_hole",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "requests>=2.19.1",
        "redis>=4.4.4",
        "aliyun-log-python-sdk"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="cobweb-launcher, cobweb, spider",
    python_requires=">=3.7",
)
