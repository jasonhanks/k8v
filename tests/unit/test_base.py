import pytest
import pickle


class TestBase:
    def load_all(self, filename):
        """Load all resources from the specified filename from test data files."""
        with open(filename, "rb") as f:
            while True:
                try:
                    yield pickle.load(f)
                except EOFError:
                    break

    def load_fixture(self, filename, display=False):
        """Load all objects from the specified filename and display them for debugging if needed."""
        data = list(self.load_all(filename))
        if display:
            print()
            for num, r in enumerate(data):
                print(
                    f"#{num} {r.kind.lower()}/{r.metadata.namespace}/{r.metadata.name}"
                )
        return data
