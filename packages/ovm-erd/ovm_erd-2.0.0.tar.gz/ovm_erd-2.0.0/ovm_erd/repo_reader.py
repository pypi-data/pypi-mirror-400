import os
import re


# ---------------------------------------------------------
# REGEX
# ---------------------------------------------------------

AUTOMATE_DV_PATTERN = re.compile(
    r"\{\{\s*automate_dv\.([a-zA-Z_]+)\s*\(",
    re.IGNORECASE
)

SRC_PK_PATTERN = re.compile(
    r"set\s+src_pk\s*=\s*(\[[^\]]+\]|\"[^\"]+\")",
    re.IGNORECASE
)

SRC_FK_PATTERN = re.compile(
    r"set\s+src_fk\s*=\s*(\[[^\]]+\]|\"[^\"]+\")",
    re.IGNORECASE
)

SRC_CDK_PATTERN = re.compile(
    r"set\s+src_cdk\s*=\s*(\[[^\]]+\]|\"[^\"]+\")",
    re.IGNORECASE
)

TAGS_PATTERN = re.compile(
    r"tags\s*=\s*\[([^\]]*)\]",
    re.IGNORECASE
)


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def _extract_list(pattern, content):
    match = pattern.search(content)
    if not match:
        return []

    raw = match.group(1)

    if raw.startswith("["):
        return [
            v.strip().strip('"').strip("'")
            for v in raw.strip("[]").split(",")
            if v.strip()
        ]

    return [raw.strip('"')]


def _extract_ensembles(content):
    match = TAGS_PATTERN.search(content)
    if not match:
        return []

    return [
        v.strip().strip('"').strip("'")
        for v in match.group(1).split(",")
        if v.strip()
    ]


# ---------------------------------------------------------
# GRAPH BUILDER
# ---------------------------------------------------------

def build_graph(path: str) -> dict:
    """
    Build AutomateDV graph in memory.
    """
    entities = {}

    for root, _, files in os.walk(path):
        for file in files:
            if not file.endswith(".sql"):
                continue

            full_path = os.path.join(root, file)

            try:
                with open(full_path, encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                continue

            macro = AUTOMATE_DV_PATTERN.search(content)
            if not macro:
                continue

            entity = file[:-4]

            entities[entity] = {
                "entity": entity,
                "filename": file,
                "pattern": macro.group(1),
                "pk": _extract_list(SRC_PK_PATTERN, content),
                "fk": _extract_list(SRC_FK_PATTERN, content),
                "cdk": _extract_list(SRC_CDK_PATTERN, content),
                "ensemble": _extract_ensembles(content),
                "relationships": []
            }

    _derive_relationships(entities)

    return {"entities": entities}


# ---------------------------------------------------------
# RELATIONSHIPS
# ---------------------------------------------------------

def _derive_relationships(entities: dict) -> None:
    hubs = {k: v for k, v in entities.items() if v["pattern"] == "hub"}
    links = {k: v for k, v in entities.items() if v["pattern"] == "link"}
    sats = {
        k: v for k, v in entities.items()
        if v["pattern"] in ["sat", "ma_sat", "msat"]
    }

    # hub → sat
    for hub in hubs.values():
        for sat in sats.values():
            if hub["pk"] and hub["pk"] == sat["pk"]:
                hub["relationships"].append({
                    "type": "hub-sat",
                    "target": sat["entity"],
                    "key": hub["pk"]
                })

    # hub → link
    for hub in hubs.values():
        for link in links.values():
            for fk in link["fk"]:
                if fk in hub["pk"]:
                    hub["relationships"].append({
                        "type": "hub-link",
                        "target": link["entity"],
                        "key": [fk]
                    })

    # link → ma_sat / msat
    for link in links.values():
        for sat in sats.values():
            if sat["pattern"] in ["ma_sat", "msat"]:
                if link["pk"] and link["pk"] == sat["pk"]:
                    link["relationships"].append({
                        "type": "link-sat",
                        "target": sat["entity"],
                        "key": sat["pk"]
                    })
