# JAMLDUMP

This library provides a `to_jaml` function that serializes JSON-serializable data in an arguably more readable YAML compatible fashion.
The format chosen is supposed to be reproducible while avoiding the Norway-problem and it's cousins.
We believe, this makes it useful for repeatedly templating the same (YAML) configuration files with the least expected surprise.

Notable features:
* Dictionary keys need to be strings.
* String values are _always_ quoted (see Norway problem or versions decoded as numbers).
* Indentation is always 2 spaces.
* With `level` and `embed_in`, you can template a branch of a larger Yaml document.
* When `jinja2` is installed, a jinja2 filter is available.

For example usage, please take a look at the tests.

## Versioning

This library follows SemVer.
Its test suite specifies what is covered.
