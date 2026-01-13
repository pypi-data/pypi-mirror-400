import inspect
import json
import re
from pathlib import Path
from typing import Callable, Iterable, Optional

import black


class TemplateException(Exception):
    pass


def _get_body(func):

    source_lines = inspect.getsource(func).splitlines()
    first_line = source_lines[0]
    if not re.match(r"def \w+\((\w+(, \w+)*)?\):", first_line.strip()):
        # Parsing to AST and unparsing is a more robust option,
        # but more complicated.
        raise TemplateException(
            f"def and parameters should fit on one line: {first_line}"
        )

    # The "def" should not be in the output,
    # and cleandoc handles the first line differently.
    source_lines[0] = ""
    body = inspect.cleandoc("\n".join(source_lines))
    comments_to_strip = [
        r"\s+#\s+type:\s+ignore\s*",
        r"\s+#\s+noqa:.+\s*",
        r"\s+#\s+pragma:\s+no cover\s*",
    ]
    for comment_re in comments_to_strip:
        body = re.sub(
            comment_re,
            "\n",
            body,
        )

    return body


def _check_repr(value):
    """
    Confirms that the string returned by repr()
    can be evaluated to recreate the original value.
    Takes a conservative approach by checking
    if the value can be serialized to JSON.
    """
    try:
        json.dumps(value)
    except TypeError as e:
        raise TemplateException(e)
    return repr(value)


_slot_re = r"\b[A-Z][A-Z_]{2,}\b"


def _check_kwargs(func):
    def wrapper(*args, **kwargs):
        WHEN = "when"
        errors = []
        for k in kwargs.keys():
            if k in args[0]._ignore:
                errors.append(f'kwarg "{k}" is an ignored slot name')
            if not (re.fullmatch(_slot_re, k) or k == WHEN):
                errors.append(f'kwarg "{k}" is not a valid slot name')
        if errors:
            raise TemplateException(
                "; ".join(errors)
                + f'. Slots should match "{_slot_re}". '
                + "Some slots are ignored, and should not be filled: "
                + ",".join(f'"{v}"' for v in args[0]._ignore)
            )
        if not kwargs.get(WHEN, True):
            # return self:
            return args[0]
        kwargs.pop(WHEN, None)
        return func(*args, **kwargs)

    return wrapper


class Template:

    def __init__(
        self,
        template: str | Callable,
        root: Optional[Path] = None,
        ignore: Iterable[str] = ("TODO",),
    ):
        if root is None:
            if callable(template):
                self._source = "function template"
                self._template = _get_body(template)
            else:
                self._source = "string template"
                self._template = template
        else:
            if callable(template):
                raise TemplateException(
                    "If template is function, root kwarg not allowed"
                )
            else:
                template_name = f"_{template}.py"
                template_path = root / template_name
                self._source = f"'{template_name}'"
                self._template = template_path.read_text()
        # We want a list of the initial slots, because substitutions
        # can produce sequences of upper case letters that could be mistaken for slots.
        self._initial_slots = self._find_slots()
        self._ignore = ignore

    def _find_slots(self) -> set[str]:
        # Slots:
        # - are all caps or underscores
        # - have word boundary on either side
        # - are at least three characters
        return set(re.findall(_slot_re, self._template))

    def _make_message(self, errors: list[str]) -> str:
        return (
            f"In {self._source}, " + ", ".join(sorted(errors)) + f":\n{self._template}"
        )

    def _loop_kwargs(
        self,
        function: Callable[[str, str, list[str]], None],
        **kwargs,
    ) -> None:
        errors = []
        for k, v in kwargs.items():
            function(k, v, errors)
        if errors:
            raise TemplateException(self._make_message(errors))

    def _fill_inline_slots(
        self,
        stringifier: Callable[[str], str],
        **kwargs,
    ) -> None:
        def function(k, v, errors):
            k_re = re.escape(k)
            self._template, count = re.subn(
                rf"\b{k_re}\b", stringifier(v), self._template
            )
            if count == 0:
                errors.append(f"no '{k}' slot to fill with '{v}'")

        self._loop_kwargs(function, **kwargs)

    def _fill_attribute_slots(self, **kwargs) -> None:
        def function(k, v, errors):
            k_re = re.escape(k)
            attr_re = rf"\.\b{k_re}\b"
            self._template, count = re.subn(
                attr_re, f".{v}" if v else "", self._template
            )
            if count == 0:
                errors.append(
                    f"no '.{k}' slot to fill with '{v}'"
                    if v
                    else f"no '.{k}' slot to delete (because replacement is false-y)"
                )

        self._loop_kwargs(function, **kwargs)

    def _fill_argument_slots(
        self,
        stringifier: Callable[[str], str],
        **kwargs,
    ) -> None:
        def function(k, v, errors):
            k_re = re.escape(k)
            arg_re = rf"\s*\b{k_re}\b,\s*"
            self._template, count = re.subn(
                arg_re, f"{stringifier(v)}," if v else "", self._template
            )
            if count == 0:
                errors.append(
                    f"no '{k},' slot to fill with '{v}'"
                    if v
                    else f"no '{k},' slot to delete (because replacement is false-y)"
                )

        self._loop_kwargs(function, **kwargs)

    def _fill_block_slots(
        self,
        prefix_re: str,
        splitter: Callable[[str], list[str]],
        **kwargs,
    ) -> None:
        def function(k, v, errors):
            if not isinstance(v, str):
                errors.append(f"for '{k}' slot, expected string, not '{v}'")
                return

            def match_indent(match):
                # This does what we want, but binding is confusing.
                return "\n".join(
                    match.group(1) + line for line in splitter(v)  # noqa: B023
                )

            k_re = re.escape(k)
            self._template, count = re.subn(
                rf"^([ \t]*{prefix_re}){k_re}$",
                match_indent,
                self._template,
                flags=re.MULTILINE,
            )
            if count == 0:
                base_message = f"no '{k}' slot to fill with '{v}'"
                if k in self._template:
                    note = (
                        "comment slots must be prefixed with '#'"
                        if prefix_re
                        else "block slots must be alone on line"
                    )
                    errors.append(f"{base_message} ({note})")
                else:
                    errors.append(base_message)

        self._loop_kwargs(function, **kwargs)

    @_check_kwargs
    def fill_expressions(self, **kwargs) -> "Template":
        """
        Fill in variable names, or dicts or lists represented as strings.
        """
        self._fill_inline_slots(stringifier=str, **kwargs)
        return self

    @_check_kwargs
    def fill_attributes(self, **kwargs) -> "Template":
        """
        Fill in attributes with expressions, or remove leading "." if false-y.
        """
        self._fill_attribute_slots(**kwargs)
        return self

    @_check_kwargs
    def fill_argument_expressions(self, **kwargs) -> "Template":
        """
        Fill in argument expressions, or removing trailing "," if false-y.
        """
        self._fill_argument_slots(stringifier=str, **kwargs)
        return self

    @_check_kwargs
    def fill_argument_values(self, **kwargs) -> "Template":
        """
        Fill in argument values, or removing trailing "," if false-y.
        """
        self._fill_argument_slots(stringifier=_check_repr, **kwargs)
        return self

    @_check_kwargs
    def fill_values(self, **kwargs) -> "Template":
        """
        Fill in string or numeric values. `repr` is called before filling.
        """
        self._fill_inline_slots(stringifier=_check_repr, **kwargs)
        return self

    @_check_kwargs
    def fill_code_blocks(self, **kwargs) -> "Template":
        """
        Fill in code blocks. Slot must be alone on line.
        """

        def splitter(s):
            return s.split("\n")

        self._fill_block_slots(prefix_re=r"", splitter=splitter, **kwargs)
        return self

    @_check_kwargs
    def fill_comment_blocks(self, **kwargs) -> "Template":
        """
        Fill in comment blocks. Slot must be commented.
        """

        def splitter(s):
            stripped = [line.strip() for line in s.split("\n")]
            return [line for line in stripped if line]

        self._fill_block_slots(prefix_re=r"#\s+", splitter=splitter, **kwargs)
        return self

    def finish(self, reformat: bool = False) -> str:
        # The reformat default is False here,
        # because it is true downstream for notebook generation,
        # and we don't need to be redundant.
        unfilled_slots = (self._initial_slots & self._find_slots()) - set(self._ignore)
        if unfilled_slots:
            errors = [f"'{slot}' slot not filled" for slot in unfilled_slots]
            raise TemplateException(self._make_message(errors))

        if reformat:
            self._template = black.format_str(self._template, mode=black.Mode())

        return self._template
