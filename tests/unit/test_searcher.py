import munch
import pytest
import yaml

import k8v


class TestSearcher:
    """Validate Searcher functionality that can be tested in isolation."""

    def setup(self):
        """Load some Kubernetes manifests as test fixtures."""
        self.resources = []
        for o in yaml.load_all(
            open("tests/manifests/deploy-nginx.yaml", "r"), Loader=yaml.FullLoader
        ):
            obj = munch.munchify(o)  # convert dict() to an object
            obj.type = k8v.resource_types.ResourceType.from_value(obj.kind.lower())
            self.resources.append(obj)

    def test_query_filters(self):
        """Validate filtering by name capability of the Searcher."""
        config: k8v.config.Config = k8v.config.Config()
        config.includes.append("nginx")

        viewer: Viewer = k8v.viewer.Viewer(config)
        searcher: k8v.searcher.Searcher = viewer.searcher

        assert ["nginx-cm", "nginx-sec", "nginx-pvc", "nginx-deployment"] == [
            r.metadata.name for r in searcher.filter_resources(self.resources)
        ]
