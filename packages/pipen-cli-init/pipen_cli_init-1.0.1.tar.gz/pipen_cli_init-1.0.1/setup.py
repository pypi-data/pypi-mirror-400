# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pipen_cli_init', 'pipen_cli_init.template.{{pipeline_name}}']

package_data = \
{'': ['*'],
 'pipen_cli_init': ['template/*'],
 'pipen_cli_init.template.{{pipeline_name}}': ['scripts/*',
                                               '{% if report %}reports{% endif '
                                               '%}/*']}

install_requires = \
['copier>=9,<10', 'pipen==1.1.*']

entry_points = \
{'pipen_cli': ['cli-init = pipen_cli_init:PipenCliInit']}

setup_kwargs = {
    'name': 'pipen-cli-init',
    'version': '1.0.1',
    'description': 'A pipen cli plugin to create a pipen project (pipeline)',
    'long_description': 'None',
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
