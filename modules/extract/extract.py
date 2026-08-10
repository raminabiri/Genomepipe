from pathlib import Path
import zipfile


def run(project_path):

    download_dir = (
        project_path /
        "input" /
        "download" /
        "genomes"
    )

    output_dir = (
        project_path /
        "input" /
        "genomes"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    zip_files = list(
        download_dir.glob("*.zip")
    )

    print(f"\nExtracting {len(zip_files)} genomes ...")

    for z in zip_files:

        try:

            with zipfile.ZipFile(z, "r") as archive:

                archive.extractall(output_dir)

            print(f"Extracted: {z.name}")

        except Exception as e:

            print(f"Failed: {z.name}")
            print(e)

    print("\nExtraction finished.")