"""Brother label printing plugin for InvenTree.

Supports direct printing of labels to networked label printers, using the brother_ql library.
"""
import math

from django.db import models
from django.utils.translation import gettext_lazy as _

from . import BROTHER_DYNAMIC_TEMPLATE_FUNCTIONS_PLUGIN_VERSION

# InvenTree plugin libs
from report.models import LabelTemplate
from plugin import InvenTreePlugin
from plugin.mixins import AppMixin

# Image library
# from PIL import ImageOps

# Label printerkit stuff
import re
from typing import Sequence
from hyphen import Hyphenator

hyphenator = Hyphenator("de_DE")


def mm2pt(length):
    # 180 DPI
    # 1 in = 25.4mm

    return int(length * (180/25.4))



class DynamicTemplateFunctionsPlugin(AppMixin, InvenTreePlugin):
    """Brother label printer driver plugin for InvenTree."""

    AUTHOR = "Martin Schaflitzl"
    DESCRIPTION = "A collection of label templating functions"
    VERSION = BROTHER_DYNAMIC_TEMPLATE_FUNCTIONS_PLUGIN_VERSION

    # Machine registry was added in InvenTree 0.14.0, use inventree-brother-plugin 0.9.0 for older versions
    # Machine driver interface was fixed with 0.16.0 to work inside of inventree workers
    MIN_VERSION = "0.16.0"

    NAME = "Dynamic Template Functions"
    SLUG = "dynamic-template-functions"
    TITLE = "Dynamic Template Functions"



