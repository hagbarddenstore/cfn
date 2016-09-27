#!/usr/bin/env python2.7

import boto3
import botocore
import json
import os
import getopt
import sys
import yaml
import jinja2

class Stack():
	def __init__(self, name, **kwargs):
		self.name = name
		self.environment = kwargs.get("environment", "")

		# TODO: Retrieve AWS region from a boto3 client.
		# See https://github.com/hagbarddenstore/cfn/issues/1
		self.region = kwargs.get("region", os.getenv("AWS_DEFAULT_REGION"))

		self._loaded = False
		self._stacks_dir = os.path.join(os.getcwd(), "stacks")
		self._templates_dir = os.path.join(os.getcwd(), "templates")
		self._output_dir = os.path.join(os.getcwd(), "output")
		self._debug = bool(kwargs.get("debug", False))
		self._format_json = bool(kwargs.get("format-json", False))

	def exists(self):
		"""Check if the stack exists in the current AWS region"""
		self._load()

		try:
			client = boto3.client("cloudformation")

			response = client.describe_stacks(StackName=self._stack_data.get("name"))

			return len(response.get("Stacks", [])) > 0
		except botocore.exceptions.ClientError:
			# TODO: Raise the exception again if it's not a "Stack not found" exception.
			# See https://github.com/hagbarddenstore/cfn/issues/2
			return False

	def generate(self):
		"""Generate the AWS CloudFormation JSON template"""
		self._load()

		if not os.path.exists(self._output_dir):
			os.makedirs(self._output_dir)

		names = self._generate_names()

		for name in names:
			path = os.path.join(self._templates_dir, name)

			if not os.path.exists(path):
				continue

			template = self._load_template(path)

			self._save_output(template)

	def validate(self):
		"""Validate template"""
		self.generate()

		client = boto3.client("cloudformation")

		stack = self._load_generated()

		response = client.validate_template(TemplateBody=stack[1])

		# TODO: Make use of the output
		print response

	def create(self):
		"""Create stack"""
		self.generate()

		client = boto3.client("cloudformation")

		stack = self._load_generated()

		response = client.create_stack(
			StackName=self._stack_data.get("name"),
			TemplateBody=stack[1],
			Parameters=self._generate_parameters(),
			# TODO: Make this optional
			Capabilities=["CAPABILITY_IAM"])

		# TODO: Make use of the output
		print response

	def update(self):
		"""Update existing stack"""
		self.generate()

		client = boto3.client("cloudformation")

		stack = self._load_generated()

		response = client.update_stack(
			StackName=self._stack_data.get("name"),
			TemplateBody=stack[1],
			UsePreviousTemplate=False,
			Parameters=self._generate_parameters(),
			# TODO: Make this optional
			Capabilities=["CAPABILITY_IAM"])

		# TODO: Make use of the output
		print response

	def delete(self):
		"""Delete existing stack"""
		self._load()

		client = boto3.client("cloudformation")

		response = client.delete_stack(StackName=self._stack_data.get("name"))

		# TODO: Make use of the output
		print response

	def _load(self):
		if self._loaded:
			return

		names = self._generate_names()

		for name in names:
			path = os.path.join(self._stacks_dir, name)

			if not os.path.exists(path):
				continue

			with open(path, "r") as stream:
				self._stack_data = yaml.load(stream)

			self._loaded = True

			return

		raise Exception("no usable stack found")

	def _load_generated(self):
		names = self._generate_names("json")
		for name in names:
			path = os.path.join(self._output_dir, name)

			if not os.path.exists(path):
				continue

			with open(path, "r") as stream:
				return (path, stream.read())

		raise Exception("no usable output found")

	def _generate_names(self, extension="yml"):
		names = []

		if self.environment != "" and self.region != "":
			names.append("%s.%s.%s.%s" % (self.name, self.environment, self.region, extension))

		if self.environment != "":
			names.append("%s.%s.%s" % (self.name, self.environment, extension))

		if self.region != "":
			names.append("%s.%s.%s" % (self.name, self.region, extension))

		names.append("%s.%s" % (self.name, extension))

		return names

	def _load_template(self, path):
		with open(path, "r") as stream:
			values = self._stack_data.get("values", {})

			template = yaml.load(jinja2.Template(stream.read()).render(**values))

			return template

	def _save_output(self, template):
		paths = self._generate_names(extension="json")

		path = paths[0]

		with open(os.path.join(self._output_dir, path), "w") as stream:
			if self._format_json or self._debug:
				json.dump(template, stream, indent=4, sort_keys=True)
			else:
				json.dump(template, stream, sort_keys=True)

	def _generate_parameters(self):
		parameters = []

		for key, value in self._stack_data.get("parameters").iteritems():
			parameters.append({
				"ParameterKey": key,
				"ParameterValue": value,
				"UsePreviousValue": False	
			})

		return parameters

def main():
	options = "h"

	long_options = [
		"environment=",
		"region=",
		"help",
		"no-wait",
		"debug",
		"format-json"
	]

	try:
		options, arguments = getopt.getopt(sys.argv[1:], options, long_options)
	except getopt.GetoptError as error:
		print help()

		sys.exit(2)

	settings = {}

	debug = False

	for option, argument in options:
		if option == "--environment":
			settings["environment"] = argument

		if option == "--region":
			settings["region"] = argument

		if option == "--no-wait":
			settings["no-wait"] = True

		if option == "--format-json":
			settings["format-json"] = True

		if option == "--help" or option == "-h":
			print help()

			sys.exit(2)

		if option == "--debug":
			debug = True
			settings["debug"] = True

	command = arguments[0]
	name = arguments[1]

	if debug:
		print "--environment=%s" % settings.get("environment", "")
		print "--region=%s" % settings.get("region", "")
		print "--debug=%s" % debug
		print "--no-wait=%s" % settings.get("no-wait", False)
		print "command=%s" % command
		print "name=%s" % name

	if command == "exists":
		stack = Stack(name, **settings)

		if stack.exists():
			print "stack exist"
		else:
			print "stack does not exist"

	elif command == "generate":
		stack = Stack(name, **settings)

		stack.generate()

	elif command == "validate":
		stack = Stack(name, **settings)

		stack.validate()

	elif command == "create":
		stack = Stack(name, **settings)

		stack.create()

	elif command == "update":
		stack = Stack(name, **settings)

		stack.update()

	elif command == "delete":
		stack = Stack(name, **settings)

		stack.delete()

def help():
	return """Usage: cfn.py [options...] <command> <stack>
Options:
 -h, --help         This help text
     --environment  Environment, like development, testing, staging, production, etc.
     --region       AWS region name"""

if __name__ == "__main__":
	main()
