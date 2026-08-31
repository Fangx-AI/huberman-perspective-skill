from __future__ import annotations

import unittest

from scripts.build_academic_repair_queue import build_rows, classify


class AcademicRepairQueueTests(unittest.TestCase):
    def test_classifies_nonspecific_and_malformed_sources(self) -> None:
        self.assertEqual(
            classify("https://pubmed.ncbi.nlm.nih.gov/?term=example")[0],
            "nonspecific-search-page",
        )
        self.assertEqual(
            classify("https://www.sciencedirect.com/topics/neuroscience/carnosine")[0],
            "nonspecific-publisher-page",
        )
        self.assertEqual(
            classify("https://www.cell.com/cell-reports-medicine/fulltext/S2666-3791(22")[0],
            "malformed-url",
        )

    def test_classifies_resolvable_but_unverified_pii(self) -> None:
        repair_class, provider, identifier, _ = classify(
            "https://www.sciencedirect.com/science/article/pii/S1935861X25000609"
        )
        self.assertEqual(repair_class, "elsevier-unresolved")
        self.assertEqual(provider, "elsevier")
        self.assertEqual(identifier, "pii:S1935861X25000609")

    def test_build_rows_includes_only_pending_records(self) -> None:
        rows = [
            {
                "url": "https://pubmed.ncbi.nlm.nih.gov/?term=example",
                "episode_count": "1",
                "episode_ids": "episode-a",
                "episode_title_sample": "Example",
                "verification_status": "pending",
            },
            {
                "url": "https://pubmed.ncbi.nlm.nih.gov/12438211/",
                "episode_count": "1",
                "episode_ids": "episode-b",
                "episode_title_sample": "Verified",
                "verification_status": "verified-bibliographic",
            },
        ]
        output = build_rows(rows, {})
        self.assertEqual(len(output), 1)
        self.assertEqual(output[0]["repair_class"], "nonspecific-search-page")


if __name__ == "__main__":
    unittest.main()
