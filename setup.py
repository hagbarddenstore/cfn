from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

try:
	import pypandoc

	long_description = pypandoc.convert("README.md", "rst")
	long_description = long_description.replace("\r", "")
except (OSError, ImportError):
	print "Pandoc not found. long_description conversion failure."

	with open("README.md", encoding="utf-8") as f:
		long_description = f.read()

setup(
	name="cfn",
	version="0.0.7",
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
	package_data={},
	data_files=[],
	entry_points={
		"console_scripts": [
			"cfn=cfn:main"
		]
	}
)
