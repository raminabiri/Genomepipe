import pandas as pd


class GenomeFilter:

    def __init__(self, metadata_file):
        self.metadata_file = metadata_file

    def load(self):

        return pd.read_json(
            self.metadata_file,
            lines=True,
        )

    def refseq(self, df):

        return df[
            df["accession"].str.startswith("GCF_")
        ]

    def complete(self, df):

        return df[
            df["assembly_info"].apply(
                lambda x: x.get("assembly_level") == "Complete Genome"
            )
        ]

    def high_quality(self, df):

        return df[
            df["checkm_info"].apply(
                lambda x: x.get("completeness", 0) >= 95
            )
        ]