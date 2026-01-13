from graphviz import Digraph


class ERDGraphviz:
    def __init__(self, metadata: dict):
        self.metadata = metadata
        self.graph = Digraph(format="png")
        self.graph.attr(rankdir="TB", layout="dot", splines="polyline")
        self.graph.attr("node", shape="box", style="filled", fontname="Helvetica")

        self.hubs = []
        self.links = []
        self.sats = []

    def classify_entities(self):
        for data in self.metadata.values():
            pattern = data.get("pattern")
            name = data["table_name"]

            if pattern == "hub":
                self.hubs.append(name)
            elif pattern == "link":
                self.links.append(name)
            elif pattern == "sat":
                self.sats.append(name)

    def add_entities(self):
        self.classify_entities()

        colors = {
            "hub": "lightblue",
            "link": "lightcoral",
            "sat": "lightyellow"
        }

        # Sats boven
        with self.graph.subgraph() as s:
            s.attr(rank="min")
            for sat in self.sats:
                s.node(sat, fillcolor=colors["sat"])

        # Hubs in het midden
        with self.graph.subgraph() as s:
            s.attr(rank="same")
            for hub in self.hubs:
                s.node(hub, fillcolor=colors["hub"])

        # Links onder
        for link in self.links:
            self.graph.node(link, fillcolor=colors["link"])

    def add_relationships(self):
        for data in self.metadata.values():
            source = data["table_name"]
            pattern = data.get("pattern")
            pk = data.get("pk")
            fk_list = data.get("fk", [])

            if pattern == "sat":
                for target in self.metadata.values():
                    if target.get("pattern") == "hub" and pk == target.get("pk"):
                        self.graph.edge(
                            target["table_name"],
                            source,
                            dir="none"
                        )

            elif pattern == "link":
                for fk in fk_list:
                    for target in self.metadata.values():
                        if target.get("pattern") == "hub" and fk == target.get("pk"):
                            self.graph.edge(
                                target["table_name"],
                                source,
                                dir="none"
                            )

    def generate(self, output_filename: str):
        self.add_entities()
        self.add_relationships()
        self.graph.render(filename=output_filename, cleanup=True)
        print(f"🖼 ERD generated: {output_filename}.png")
