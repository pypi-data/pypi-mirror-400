# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pipen_cli_run']

package_data = \
{'': ['*']}

install_requires = \
['pipen-args>=1.1,<2.0', 'pipen==1.1.*']

entry_points = \
{'pipen_cli': ['cli-run = pipen_cli_run:PipenCliRunPlugin']}

setup_kwargs = {
    'name': 'pipen-cli-run',
    'version': '1.0.2',
    'description': 'A pipen cli plugin to run a process or a pipeline',
    'long_description': '# pipen-cli-run\n\nA pipen cli plugin to run a process or a pipeline\n\n## Install\n\n```shell\npip install -U pipen-cli-run\n```\n\n## Usage\n\n### Register a namespace\n\n`pyproject.toml`\n```toml\n[tool.poetry.plugins.pipen_cli_run]\nns = "yourpackage.ns"\n```\n\n`ns` should be a module where you define you processes/pipelines\n',
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/pwwang/pipen-cli-run',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
