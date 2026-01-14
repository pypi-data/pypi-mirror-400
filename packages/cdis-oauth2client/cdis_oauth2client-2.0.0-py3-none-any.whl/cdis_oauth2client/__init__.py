"""
cdis_oauth2client

Library providing an OAuth2 client model for CDIS microservices.
"""

from .blueprint import blueprint
from .client import OAuth2Client
from .exceptions import OAuth2Error
from .oauth2 import get_username
