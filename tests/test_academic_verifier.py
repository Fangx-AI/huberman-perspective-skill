from __future__ import annotations

import tempfile
import unittest
import csv
from pathlib import Path
from unittest.mock import patch

from scripts.verify_academic_batch import (
    identifiers,
    is_malformed_url,
    load_identifier_overrides,
    ncbi_idconv_lookup,
    select_candidates,
    write_csv,
)


class AcademicVerifierTests(unittest.TestCase):
    def test_extracts_compact_elsevier_pii_ending_in_x(self) -> None:
        url = "https://www.sciencedirect.com/science/article/abs/pii/S016643281830322X?via=ihub"
        self.assertEqual(identifiers(url)["pii"], "S016643281830322X")

    def test_derives_doi_from_nature_slug(self) -> None:
        url = "https://www.nature.com/articles/s41598-020-63980-y"
        self.assertEqual(identifiers(url)["doi"], "10.1038/s41598-020-63980-y")

    def test_strips_publisher_session_parameter_from_doi(self) -> None:
        url = (
            "https://www.annualreviews.org/content/journals/"
            "10.1146/annurev-psych-122414-033417;jsessionid=temporary-session"
        )
        self.assertEqual(
            identifiers(url)["doi"],
            "10.1146/annurev-psych-122414-033417",
        )

    def test_derives_doi_from_legacy_nature_and_figure_urls(self) -> None:
        self.assertEqual(
            identifiers("https://www.nature.com/articles/1301376")["doi"],
            "10.1038/1301376",
        )
        self.assertEqual(
            identifiers("https://www.nature.com/articles/srep46173/figures/5")["doi"],
            "10.1038/srep46173",
        )
        self.assertEqual(
            identifiers("https://www.nature.com/articles/nn0799_597")["doi"],
            "10.1038/nn0799_597",
        )
        self.assertEqual(
            identifiers("https://www.nature.com/articles/tp201546")["doi"],
            "10.1038/tp.2015.46",
        )
        self.assertEqual(
            identifiers("https://www.nature.com/articles/mp201451")["doi"],
            "10.1038/mp.2014.51",
        )

    def test_extracts_legacy_sciencedirect_and_eid_pii(self) -> None:
        self.assertEqual(
            identifiers("https://www.sciencedirect.com/science/article/abs/pii/0018506X71900377")["pii"],
            "0018506X71900377",
        )
        self.assertEqual(
            identifiers("https://www.sciencedirect.com/sdfe/pdf/download/eid/1-s2.0-S0268005X23006410/first-page-pdf")["pii"],
            "S0268005X23006410",
        )

    def test_traceable_override_replaces_noncanonical_legacy_guess(self) -> None:
        url = "https://www.nature.com/articles/nn0799_597"
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "overrides.csv"
            path.write_text(
                "url,pmcid,pmid,doi,pii,provenance_url,note\n"
                f"{url},,,10.1038/10154,,{url},official citation metadata\n",
                encoding="utf-8",
            )
            overrides = load_identifier_overrides(path)
        self.assertEqual(identifiers(url, overrides)["doi"], "10.1038/10154")

    def test_queue_writer_collapses_multiline_provider_metadata(self) -> None:
        row = {
            "url": "https://example.org/paper",
            "episode_count": "1",
            "episode_ids": "episode",
            "episode_title_sample": "Example",
            "verification_status": "verified-bibliographic",
            "evidence_notes": "Title with\n             provider indentation",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "queue.csv"
            write_csv(path, [row])
            raw = path.read_text(encoding="utf-8")
            with path.open(encoding="utf-8", newline="") as handle:
                saved = next(csv.DictReader(handle))
        self.assertNotIn("\n             ", raw)
        self.assertEqual(saved["evidence_notes"], "Title with provider indentation")

    @patch("scripts.verify_academic_batch.request_json")
    def test_ncbi_id_converter_accepts_only_non_error_records(self, request_json) -> None:
        request_json.return_value = {
            "records": [{"pmcid": "PMC3060589", "pmid": "21224217", "doi": "10.1113/jphysiol.2010.201194"}]
        }
        record = ncbi_idconv_lookup("PMC3060589", 20, "test-agent")
        self.assertEqual(record["pmid"], "21224217")
        self.assertIn("PMC3060589", request_json.call_args.args[0])

        request_json.return_value = {"records": [{"pmcid": "PMC0", "status": "error"}]}
        self.assertIsNone(ncbi_idconv_lookup("PMC0", 20, "test-agent"))

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
