import typing as t
import warnings


def _assert_key(key: t.Any) -> str:
    assert isinstance(key, str)
    assert key.isidentifier()
    return key


def _quote(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def to_jaml(data: t.Any, level: int = 0, embed_in: str = "") -> str:
    """Filter for Jinja 2 templates to render human readable YAML."""
    # Don't even believe this is complete!
    # Yes, I have checked pyyaml and ruamel.

    nl = False
    if isinstance(data, str):
        result = _quote(data)
    elif data is True:
        result = "true"
    elif data is False:
        result = "false"
    elif isinstance(data, int):
        result = f"{data}"
    elif isinstance(data, list):
        if len(data):
            nl = embed_in == "dict"
            result = ("\n" + "  " * level).join(
                ("-" + to_jaml(item, level + 1, "list") for item in data)
            )
        else:
            result = "[]"
    elif isinstance(data, dict):
        if len(data):
            nl = embed_in == "dict"
            result = ("\n" + "  " * level).join(
                (
                    f"{_assert_key(key)}:" + to_jaml(value, level + 1, "dict")
                    for key, value in sorted(data.items())
                )
            )
        else:
            result = "{}"
    else:
        raise NotImplementedError("This object is not serializable.")
    if nl:
        result = "\n" + "  " * level + result
    elif embed_in in ("dict", "list"):
        result = " " + result
    elif embed_in == "document":
        if level != 0:
            warnings.warn("jaml: Level should be 0 when embedding in 'document'.")
        return result
    else:
        if level != 0:
            warnings.warn("jaml: Level should be 0 when serializing a docoment.")
        result = "---\n" + result + "\n...\n"
    return result
