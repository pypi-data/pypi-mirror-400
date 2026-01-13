import os
import re


def read_repository(repository_path: str) -> dict:
    """
    Recursively read .sql files containing AutomateDV logic.
    """
    files = {}

    for root, _, filenames in os.walk(repository_path):
        for filename in filenames:
            if not filename.endswith(".sql"):
                continue

            full_path = os.path.join(root, filename)

            try:
                with open(full_path, encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                continue

            if "{{ automate_dv." not in content:
                continue

            files[filename] = {
                "content": content
            }

    return files


def build_metadata_dict(file_dict: dict) -> dict:
    """
    Extracts Data Vault metadata from AutomateDV SQL files.
    """
    metadata = {}

    for filename, info in file_dict.items():
        content = info["content"]
        table_name = filename[:-4]

        tags_match = re.search(r"tags\s*=\s*\[([^\]]*)\]", content)
        tags = (
            [t.strip().strip('"').strip("'") for t in tags_match.group(1).split(",")]
            if tags_match else []
        )

        pk_match = re.search(r"set\s+src_pk\s*=\s*\"([^\"]+)\"", content)
        pk = pk_match.group(1) if pk_match else ""

        fk_match = re.search(r"set\s+src_fk\s*=\s*\[([^\]]+)\]", content)
        fk = (
            [f.strip().strip('"').strip("'") for f in fk_match.group(1).split(",")]
            if fk_match else []
        )

        hashdiff_match = re.search(r"set\s+src_hashdiff\s*=\s*\"([^\"]+)\"", content)
        hashdiff = hashdiff_match.group(1) if hashdiff_match else ""

        nk_match = re.search(r"set\s+src_nk\s*=\s*\"([^\"]+)\"", content)
        nk = nk_match.group(1) if nk_match else ""

        if nk:
            pattern = "hub"
        elif fk:
            pattern = "link"
        elif hashdiff:
            pattern = "sat"
        else:
            pattern = ""

        metadata[filename] = {
            "table_name": table_name,
            "tags": tags,
            "pk": pk,
            "fk": fk,
            "pattern": pattern
        }

    return metadata
