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
        self.viewer: Viewer = k8v.viewer.Viewer(k8v.config.Config())
        self.searcher: k8v.searcher.Searcher = self.viewer.searcher

    def test_include_filter(self):
        """Validate sub-string include filtering."""
        self.viewer.config.includes.append("nginx-deploy")
        assert ["nginx-deployment"] == [
            r.metadata.name for r in self.searcher.filter_resources(self.resources)
        ]

    def test_exclude_filter(self):
        """Validate sub-string resource exclusion filtering."""
        self.viewer.config.excludes.append("nginx-sec")
        assert ["nginx-cm", "nginx-pvc", "nginx-deployment"] == [
            r.metadata.name for r in self.searcher.filter_resources(self.resources)
        ]

    def test_include_and_exclude_filters(self):
        """Validate that combination of include and exclude filters work as expected."""
        self.viewer.config.includes.append("nginx-")
        self.viewer.config.excludes.append("nginx-pvc")
        assert ["nginx-cm", "nginx-sec", "nginx-deployment"] == [
            r.metadata.name for r in self.searcher.filter_resources(self.resources)
        ]
