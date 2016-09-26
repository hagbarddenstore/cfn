Cfn
===

A Python script to generate and manage AWS CloudFormation stacks based
on YAML inputs.

Define stacks and their templates in YAML and make use of Jinja2 in the
template definition to generate a finished JSON CloudFormation template.

Stacks
------

A stack defines the static values and dynamic parameters that are put
into the template to generate a usable CloudFormation template.

You can define multiple stacks that use the same template by using a
different region or environment.

In the examples below I use a single template to define a CloudFormation
stack for the regions ``eu-west-1`` and ``eu-central-1``. The example
creates one subnet per availability zone, something that differs between
the two regions. So, instead of limiting ourself to just using two
availability zones, we use a bit of Jinja2 templating and simply
generate the subnets from a list.

Templates
---------

A template is a YAML file that is pre-processed by Jinja2 before being
turned into JSON. It gets values from the stack and is then generated to
provide a finished stack that can be used by CloudFormation.

Create your first stack and template
------------------------------------

First, create two directories, ``stacks`` and ``templates``. These
folders will contain your stacks and your templates.

Then, create two stacks, one for region ``eu-west-1`` and one for
``eu-central-1``. You can copy paste the code below.

::

    # stacks/example.eu-west-1.yml
    ---
    name: Example
    values:
      azs:
        - eu-west-1a
        - eu-west-1b
        - eu-west-1c

::

    # stacks/example.eu-central-1.yml
    ---
    name: Example
    values:
      azs:
        - eu-central-1a
        - eu-central-1b

Next, create a template that looks like this:

::

    # templates/example.yml
    ---
    AWSTemplateFormatVersion: "2010-09-09"

    Description: Example stack template

    Resources:
    {% for az in azs %}
      {{ "Subnet%s:" | format(az[-1].upper()) }}
        Type: AWS::EC2::Subnet
        Properties:
          AvailabilityZone: {{ az }}
          # Other properties are not present, because the example
          # would become too long...
    {% endfor %}

That's it! Now it's time to generate the CloudFormation files. Run
``cfn --region eu-west-1 generate example`` and
``cfn --region eu-central-1 generate example``. You should have a new
folder ``output`` which contains two files, ``example.eu-west-1.json``
and ``example.eu-central-1.json``. These are the ready to use
CloudFormation templates.

The generated CloudFormation stack template for
``stacks/example.eu-west-1.yml`` would look something like this:

::

    {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": "Example stack template",
        "Resources": {
            "SubnetA": {
                "Type": "AWS::EC2::Subnet",
                "Properties": {
                    "AvailabilityZone": "eu-west-1a"
                }
            },
            "SubnetB": {
                "Type": "AWS::EC2::Subnet",
                "Properties": {
                    "AvailabilityZone": "eu-west-1b"
                }
            },
            "SubnetC": {
                "Type": "AWS::EC2::Subnet",
                "Properties": {
                    "AvailabilityZone": "eu-west-1c"
                }
            }
        }
    }

You can validate these files with the ``aws-cli`` tool by running
``aws cloudformation validate-template --template-body file://output/example.eu-central-1.json``.

To create the stack using the cfn tool, run
``cfn --region eu-west-1 create example``.

If you've made changes to the stack and wish to update, run
``cfn --region eu-west-1 update example``.

Run ``cfn --region eu-west-1 delete example`` to delete an existing
stack created by the cfn tool.
