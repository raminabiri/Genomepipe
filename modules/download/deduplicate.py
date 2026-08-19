from pathlib import Path
import pandas as pd
import re


class GenomeDeduplicator:

    def __init__(self, ncbi_metadata, ena_metadata):
        self.ncbi_metadata = Path(ncbi_metadata)
        self.ena_metadata = Path(ena_metadata)

    @staticmethod
    def normalize_accession(accession):

        if pd.isna(accession):
            return None

        accession = str(accession).strip()

        match = re.match(
            r"^(GC[AF]_\d+)(?:\.\d+)?$",
            accession,
        )

        if not match:
            return accession

        return match.group(1)

    def run(self):

        ncbi = pd.read_csv(self.ncbi_metadata)

        ena = pd.read_csv(
            self.ena_metadata,
            sep="\t",
        )

        # NCBI accession set
        ncbi_ids = set()

        for column in [
            "accession",
            "current_accession",
            "paired_accession",
        ]:

            if column not in ncbi.columns:
                continue

            for value in ncbi[column].dropna():

                normalized = self.normalize_accession(value)

                if normalized:
                    ncbi_ids.add(normalized)

        # Remove duplicates inside ENA
        ena["_normalized_accession"] = (
            ena["accession"]
            .apply(self.normalize_accession)
        )

        ena_internal_duplicates = ena[
            ena["_normalized_accession"].duplicated(
                keep="first"
            )
        ].copy()

        ena_unique_internal = ena[
            ~ena["_normalized_accession"].duplicated(
                keep="first"
            )
        ].copy()

        # Remove ENA records already represented by NCBI
        cross_database_mask = (
            ena_unique_internal["_normalized_accession"]
            .isin(ncbi_ids)
        )

        ena_cross_duplicates = ena_unique_internal[
            cross_database_mask
        ].copy()

        ena_final_unique = ena_unique_internal[
            ~cross_database_mask
        ].copy()

        # Remove helper column
        for df in [
            ena_internal_duplicates,
            ena_cross_duplicates,
            ena_final_unique,
        ]:
            df.drop(
                columns=["_normalized_accession"],
                inplace=True,
            )

        # Output
        output_dir = self.ena_metadata.parent

        ena_internal_duplicates.to_csv(
            output_dir / "ena_internal_duplicates.tsv",
            sep="\t",
            index=False,
        )

        ena_cross_duplicates.to_csv(
            output_dir / "ena_ncbi_duplicates.tsv",
            sep="\t",
            index=False,
        )

        ena_final_unique.to_csv(
            output_dir / "ena_final_nonredundant.tsv",
            sep="\t",
            index=False,
        )

        print("\n========== DEDUPLICATION ==========")
        print(f"NCBI accession IDs       : {len(ncbi_ids)}")
        print(f"ENA original assemblies  : {len(ena)}")
        print(f"ENA internal duplicates  : {len(ena_internal_duplicates)}")
        print(f"ENA-NCBI duplicates      : {len(ena_cross_duplicates)}")
        print(f"ENA final unique         : {len(ena_final_unique)}")
        print("===================================")

        return ena_final_unique
