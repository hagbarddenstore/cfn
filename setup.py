from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open("README.rst", encoding="utf-8") as f:
  long_description = f.read()

setup(
	name="cfn",
	version="0.0.11",
	description="Small script to manipulate AWS CloudFormation stacks",
	long_description=long_description,
	url="https://github.com/hagbarddenstore/cfn",
	author="Kim Johansson",
	author_email="hagbarddenstore@gmail.com",
	license="MIT",
	classifiers=[
		"Development Status :: 3 - Alpha",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Programming Language :: Python :: 2.7"
	],
	keywords="aws cfn cloudformation",
	packages=find_packages(exclude=["contrib", "docs", "tests"]),
	install_requires=["boto3", "PyYAML", "jinja2"],
	extras_require={},
	package_data={
		"": [ "*.md", "*.txt", "*.rst" ]
	},
	data_files=[],
	entry_points={
		"console_scripts": [
			"cfn=cfn:main"
		]
	}
)
