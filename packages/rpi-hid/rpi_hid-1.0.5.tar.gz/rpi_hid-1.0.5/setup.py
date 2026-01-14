from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_desc = f.read()

setup(
    name="rpi-hid",
    version="1.0.5",
    author="Abhirup Rudra",
    author_email="abhiruprudra@gmail.com",
    description="Raspberry Pi USB HID Keyboard + RubberDucky Interpreter",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/AbhirupRudra/RPI-HID/",
    packages=find_packages(),
    python_requires=">=3.7",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: MIT License",
        "Topic :: System :: Hardware",
    ],
)
