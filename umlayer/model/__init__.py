"""Domain model of the application.

Also includes common abstractions.

This file contains all package-wide definitions
"""

from . import constants, utils

from .base_item import BaseItem
from .folder import Folder
from .diagram import Diagram
from .project import Project
from .project_storage import ProjectStorage
from .data_model import DataModel
