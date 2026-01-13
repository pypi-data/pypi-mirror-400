from jinja2 import Environment
from jinja2.ext import Extension

from .jamldump import to_jaml


class Jaml(Extension):
    def __init__(self, environment: Environment):
        super().__init__(environment)
        environment.filters["jaml"] = to_jaml


__all__ = ["Jaml"]
