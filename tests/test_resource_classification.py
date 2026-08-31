from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


CLASSIFIER = load_module("resource_classification", ROOT / "scripts" / "resource_classification.py")
CATALOG = load_module("build_resource_catalog", ROOT / "scripts" / "build_resource_catalog.py")
GRAPH = load_module("build_knowledge_graph_classification", ROOT / "scripts" / "build_knowledge_graph.py")


class ResourceClassificationTests(unittest.TestCase):
    def test_major_publishers_and_registries_are_academic(self) -> None:
        urls = [
            "https://www.annualreviews.org/doi/abs/10.1146/annurev-psych-122414-033417",
            "https://onlinelibrary.wiley.com/doi/10.1002/ejsp.674",
            "https://academic.oup.com/sleep/article/1/2/1/",
            "https://link.springer.com/article/10.1007/example",
            "https://www.science.org/doi/10.1126/example",
            "https://jamanetwork.com/journals/jama/fullarticle/example",
            "https://www.frontiersin.org/journals/psychology/articles/example/full",
            "https://www.mdpi.com/2227-9032/12/23/2488",
            "https://clinicaltrials.gov/study/NCT00000000",
            "https://bmcmedicine.biomedcentral.com/articles/10.1186/example",
            "https://bmjopen.bmj.com/content/1/1/example",
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(CLASSIFIER.classify_resource(url), "academic-or-medical")
                self.assertEqual(CATALOG.kind(url), "academic-or-medical")
                self.assertEqual(GRAPH.resource_kind(url), "academic-or-medical")

    def test_nonacademic_and_official_sources_remain_distinct(self) -> None:
        self.assertEqual(CLASSIFIER.classify_resource("https://www.amazon.com/example"), "other-resource")
        self.assertEqual(
            CLASSIFIER.classify_resource("https://www.hubermanlab.com/episode/example"),
            "official-or-institutional",
        )
        self.assertEqual(CLASSIFIER.classify_resource("https://www.youtube.com/watch?v=abc"), "video")


if __name__ == "__main__":
    unittest.main()
