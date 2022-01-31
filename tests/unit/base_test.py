import pytest
import pickle


class BaseTest:
    def load_all(self, filename):
        with open(filename, "rb") as f:
            while True:
                try:
                    yield pickle.load(f)
                except EOFError:
                    break

    def load_fixture(self, filename, display=False):
        data = list(self.load_all(filename))
        if display:
            print()
            for num, r in enumerate(data):
                print(
                    f"#{num} {r.kind.lower()}/{r.metadata.namespace}/{r.metadata.name}"
                )
        return data
