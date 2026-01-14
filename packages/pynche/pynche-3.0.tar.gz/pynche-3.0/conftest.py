from doctest import ELLIPSIS, REPORT_NDIFF, NORMALIZE_WHITESPACE
from sybil import Sybil
from sybil.parsers.codeblock import PythonCodeBlockParser
from sybil.parsers.doctest import DocTestParser
from sybil.parsers.rest import SkipParser


DOCTEST_FLAGS = ELLIPSIS | NORMALIZE_WHITESPACE | REPORT_NDIFF


class DoctestNamespace:
    def setup(self, namespace):
        pass

    def teardown(self, namespace):
        pass


namespace = DoctestNamespace()


pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(optionflags=DOCTEST_FLAGS),
        PythonCodeBlockParser(),
        SkipParser(),
    ],
    pattern='*.rst',
    setup=namespace.setup,
).pytest()
