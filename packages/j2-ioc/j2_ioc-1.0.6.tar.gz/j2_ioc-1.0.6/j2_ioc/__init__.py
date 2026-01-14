"""Python IoC - A Python IoC (Inversion of Control) container.

This package provides a simple and flexible dependency injection container
for Python applications.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from j2_ioc.container import Container
from j2_ioc.lifetime import Lifetime
from j2_ioc.scope import Scope

__all__ = ["Container", "Lifetime", "Scope"]
