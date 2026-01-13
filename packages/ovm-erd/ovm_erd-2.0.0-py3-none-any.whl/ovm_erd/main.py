import argparse
import sys

from ovm_erd.repository_reader import read_repository, build_metadata_dict
from ovm_erd.erd_graphviz import ERDGraphviz

# NIEUW: Mermaid pipeline (ongewijzigd geïmporteerd)
from ovm_erd.erd_mermaid import main as mermaid_main


OUTPUT_DIR = "ovm_erd/output"


def main():
    parser = argparse.ArgumentParser(
        description="OVM-ERD – Data Vault ERD tooling"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # -------------------------------------------------
    # GRAPHVIZ
    # -------------------------------------------------
    graphviz = subparsers.add_parser(
        "graphviz",
        help="Generate Graphviz ERD"
    )

    graphviz.add_argument(
        "--path",
        required=True,
        help="Path to dbt / AutomateDV repository"
    )

    graphviz.add_argument(
        "--ensemble",
        default=None,
        help="Optional ensemble/tag filter or 'distinct'"
    )

    # -------------------------------------------------
    # MERMAID (NIEUW)
    # -------------------------------------------------
    mermaid = subparsers.add_parser(
        "mermaid",
        help="Generate Mermaid ERD (new pipeline)"
    )

    mermaid.add_argument(
        "--path",
        required=True,
        help="Path to dbt / AutomateDV repository"
    )

    mermaid.add_argument(
        "--out",
        default="erd_mermaid.md",
        help="Output Mermaid Markdown file"
    )

    mermaid.add_argument(
        "--ensemble",
        default=None,
        help="Optional ensemble filter or 'distinct'"
    )

    args, unknown = parser.parse_known_args()

    # -------------------------------------------------
    # DISPATCH
    # -------------------------------------------------
    if args.command == "graphviz":
        files = read_repository(args.path)
        metadata = build_metadata_dict(files)

        ERDGraphviz(metadata).generate(
            f"{OUTPUT_DIR}/erd_all"
        )

    elif args.command == "mermaid":
        # ⚠️ CRUCIAAL:
        # we roepen de bestaande erd_mermaid CLI aan
        # zonder deze te wijzigen
        sys.argv = [
            "erd_mermaid",
            "--path", args.path,
            "--out", args.out
        ]

        if args.ensemble:
            sys.argv.extend(["--ensemble", args.ensemble])

        mermaid_main()
