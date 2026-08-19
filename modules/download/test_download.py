"""Non-network tests for the download layer."""

import unittest

from .config import ASSEMBLY_CHOICES, DATABASES
from .download import build_plans


class DownloadPlanTests(unittest.TestCase):
    def test_database_registry(self):
        self.assertEqual(
            DATABASES,
            ("ncbi", "ena", "gtdb", "bvbrc", "ddbj", "img", "sra", "uniprot"),
        )

    def test_assembly_choices(self):
        self.assertEqual(ASSEMBLY_CHOICES["1"], ("complete_genome",))
        self.assertEqual(ASSEMBLY_CHOICES["5"], ("complete_genome", "chromosome"))
        self.assertEqual(
            ASSEMBLY_CHOICES["6"],
            ("complete_genome", "chromosome", "scaffold"),
        )

    def test_build_plans_does_not_download(self):
        plans = build_plans(
            "Example organism",
            "input/genomes",
            sources=["ncbi", "ena", "sra", "uniprot"],
            assembly_choice="6",
        )
        self.assertEqual(len(plans), 4)
        self.assertTrue(all(plan["execute"] is False for plan in plans))
        self.assertEqual(plans[0]["assembly_levels"], list(ASSEMBLY_CHOICES["6"]))
        self.assertEqual(plans[2]["data_type"], "raw_reads")
        self.assertEqual(plans[3]["data_type"], "protein_sequences")


if __name__ == "__main__":
    unittest.main()
