import argparse
import os
from repo_reader import build_graph


# ---------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------

OUTPUT_DIR = "ovm_erd/output"


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def sanitize(name: str) -> str:
    return name.replace("-", "_").replace(" ", "_")


def ensure_output_path(out: str) -> str:
    """
    Ensure output file is written to ovm_erd/output unless
    an explicit path is provided.
    """
    if os.path.dirname(out):
        return out

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    return os.path.join(OUTPUT_DIR, out)


def render_attribute(name: str, key: str | None = None) -> str:
    if key:
        return f"        {sanitize(name)} string {key}"
    return f"        {sanitize(name)} string"


def filter_entities_by_ensemble(entities, ensemble):
    if not ensemble:
        return entities
    return {
        k: v for k, v in entities.items()
        if ensemble in v.get("ensemble", [])
    }


def distinct_ensembles(entities):
    result = set()
    for e in entities.values():
        result.update(e.get("ensemble", []))
    return result


# ---------------------------------------------------------
# MERMAID
# ---------------------------------------------------------

def generate_mermaid_erd(graph, ensemble=None):
    entities = filter_entities_by_ensemble(graph["entities"], ensemble)

    lines = ["```mermaid", "erDiagram"]

    for name, data in entities.items():
        lines.append(f"    {sanitize(name)} {{")

        for pk in data.get("pk", []):
            lines.append(render_attribute(pk, "PK"))

        for fk in data.get("fk", []):
            lines.append(render_attribute(fk, "FK"))

        for cdk in data.get("cdk", []):
            lines.append(render_attribute(cdk))

        lines.append("    }")

    for src, data in entities.items():
        for rel in data.get("relationships", []):
            tgt = rel["target"]
            if tgt in entities:
                lines.append(
                    f"    {sanitize(src)} ||--o{{ {sanitize(tgt)} : {rel['type']}"
                )

    lines.append("```")
    return "\n".join(lines)


# ---------------------------------------------------------
# CLI
# ---------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate Mermaid ERDs from AutomateDV repository"
    )
    parser.add_argument("--path", required=True)
    parser.add_argument("--out", default="erd_mermaid.md")
    parser.add_argument("--ensemble", default=None)

    args = parser.parse_args()

    graph = build_graph(args.path)
    entities = graph["entities"]

    # ---------------------------------------------
    # DISTINCT
    # ---------------------------------------------
    if args.ensemble == "distinct":
        base_name = os.path.splitext(args.out)[0]
        base_name = os.path.basename(base_name)

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        for ens in sorted(distinct_ensembles(entities)):
            mermaid = generate_mermaid_erd(graph, ens)
            out_file = os.path.join(
                OUTPUT_DIR,
                f"{base_name}_{ens}.md"
            )

            with open(out_file, "w", encoding="utf-8") as f:
                f.write(mermaid)

            print(f"✅ {out_file}")
        return

    # ---------------------------------------------
    # SINGLE / ALL
    # ---------------------------------------------
    out_file = ensure_output_path(args.out)
    mermaid = generate_mermaid_erd(graph, args.ensemble)

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(mermaid)

    print(f"✅ {out_file}")


if __name__ == "__main__":
    main()
