# -*- coding: utf-8 -*-

import importlib
import importlib.util
import os
import setuptools

"""Read the plugin version from the source code."""
module_path = os.path.join(
    os.path.dirname(__file__), "inventree_dynamic_template_functions", "__init__.py"
)
spec = importlib.util.spec_from_file_location("inventree_dynamic_template_functions", module_path)
inventree_dynamic_template_functions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventree_dynamic_template_functions)

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()


setuptools.setup(
    name="inventree-dynamic-template-functions-plugin",
    version=inventree_dynamic_template_functions.BROTHER_DYNAMIC_TEMPLATE_FUNCTIONS_PLUGIN_VERSION,
    author="Martin Schaflitzl",
    author_email="dev@martin-sc.de",
    description="Some functions for dynamically formatting text",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="inventree label template format text inventory dynamic width",
    url="https://github.com/mschaf/inventree-dynamic-template-functions-plugin",
    license="MIT",
    packages=setuptools.find_packages(),
    install_requires=[
        "pyhyphen",
    ],
    setup_requires=[
        "wheel",
        "twine",
    ],
    python_requires=">=3.9",
    entry_points={
        "inventree_plugins": [
            "DynamicTemplateFunctionsPlugin = inventree_dynamic_template_functions.dynamic_template_functions_plugin:DynamicTemplateFunctionsPlugin"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Framework :: InvenTree",
    ],
)
