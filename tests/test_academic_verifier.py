from __future__ import annotations

import unittest

from scripts.verify_academic_batch import identifiers, is_malformed_url, select_candidates


class AcademicVerifierTests(unittest.TestCase):
    def test_extracts_compact_elsevier_pii_ending_in_x(self) -> None:
        url = "https://www.sciencedirect.com/science/article/abs/pii/S016643281830322X?via=ihub"
        self.assertEqual(identifiers(url)["pii"], "S016643281830322X")

    def test_derives_doi_from_nature_slug(self) -> None:
        url = "https://www.nature.com/articles/s41598-020-63980-y"
        self.assertEqual(identifiers(url)["doi"], "10.1038/s41598-020-63980-y")

    def test_flags_truncated_cell_url(self) -> None:
        self.assertTrue(is_malformed_url("https://www.cell.com/cell-reports-medicine/fulltext/S2666-3791(22"))

    def test_candidate_selection_skips_unresolvable_rows_without_consuming_limit(self) -> None:
        rows = [
            {"url": "https://pubmed.ncbi.nlm.nih.gov/?term=example"},
            {"url": "https://www.cell.com/cell-reports-medicine/fulltext/S2666-3791(22"},
            {"url": "https://pubmed.ncbi.nlm.nih.gov/12438211/"},
            {"url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC3060589/"},
        ]
        candidates, scanned, malformed, no_identifier, skipped_provider = select_candidates(rows, limit=2)
        self.assertEqual([item[0]["url"] for item in candidates], [rows[2]["url"], rows[3]["url"]])
        self.assertEqual(scanned, 4)
        self.assertEqual(malformed, 1)
        self.assertEqual(no_identifier, 1)
        self.assertEqual(skipped_provider, 0)

    def test_candidate_selection_can_exclude_rate_limited_provider(self) -> None:
        rows = [
            {"url": "https://www.cell.com/neuron/fulltext/S0896-6273(09)00742-9"},
            {"url": "https://pubmed.ncbi.nlm.nih.gov/12438211/"},
        ]
        candidates, scanned, _, _, skipped_provider = select_candidates(
            rows, limit=1, allowed_providers={"europe-pmc", "crossref"}
        )
        self.assertEqual(candidates[0][0]["url"], rows[1]["url"])
        self.assertEqual(scanned, 2)
        self.assertEqual(skipped_provider, 1)


if __name__ == "__main__":
    unittest.main()
