import pytest
import io
import json
import munch

import k8v

from test_base import TestBase


class TestPrinter(TestBase):
    """Validate the Printer properly formats groups of resources."""

    def setup(self):
        self.config = k8v.config.Config(
            colors=None, file=io.StringIO(""), output="brief"
        )
        self.config.load()
        self.printer = k8v.printer.Printer(self.config)

    def test_brief(self):
        """Validate we can view brief output."""
        pass

    def test_default(self):
        pass

    def test_json(self):
        pass
