"""IMG/JGI data-source adapter.

IMG access can require JGI authentication/permissions. Therefore this module
creates an explicit retrieval plan and never assumes public bulk genome access.
"""

from pathlib import Path


class IMG:
    source = "img"

    def __init__(self, organism, output_dir, assembly_levels=()):
        self.organism = str(organism)
        self.output_dir = Path(output_dir)
        self.assembly_levels = tuple(assembly_levels)

    def plan(self):
        return {
            "source": self.source,
            "organism": self.organism,
            "assembly_levels": list(self.assembly_levels),
            "output_dir": str(self.output_dir),
            "execute": False,
            "requires_authentication": True,
            "note": "IMG/JGI access must be validated for the user's account before execution.",
        }

    def download(self, execute=False):
        if not execute:
            return self.plan()
        raise NotImplementedError("IMG execution requires an authenticated JGI/IMG workflow.")
