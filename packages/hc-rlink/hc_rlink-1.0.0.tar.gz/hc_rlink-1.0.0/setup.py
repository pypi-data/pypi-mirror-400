from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

setup(
    name="hc-rlink",
    version="1.0.0",
    author="HobbyComponents (Andrew Davies)",
    author_email="support@hobbycomponents.com",
    description="Python library to control Hobby Components rLink RS485 modules",
    long_description=(here / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://hobbycomponents.com/rlink",
    packages=find_packages(include=["rlink", "rlink.*"]),
    python_requires=">=3.6",
    install_requires=["pyserial>=3.4", "RPi.GPIO>=0.7"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    include_package_data=True,
)
