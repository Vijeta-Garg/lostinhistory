import json
import networkx as nx
from collections import deque


class GraphEngine:
    def __init__(self, knowledge_graph_path: str):
        with open(knowledge_graph_path, "r") as f:
            self.data = json.load(f)

        self.people = {entry["name"]: entry for entry in self.data}

        self.name_index = {}
        for entry in self.data:
            full = entry["name"].lower()
            last = full.split()[-1]
            self.name_index[full] = entry["name"]
            self.name_index[last] = entry["name"]

        self.graph = nx.Graph()
        self._build_graph()

        self.betweenness = nx.betweenness_centrality(self.graph, weight=None)
        self.pagerank = nx.pagerank(self.graph)

    def _build_graph(self):
        for entry in self.data:
            self.graph.add_node(
                entry["name"],
                gender=entry["gender"],
                fields=entry["fields"],
                era=entry["era"],
                importance_weight=entry["importance_weight"],
                erasure_pattern=entry.get("common_erasure_pattern", ""),
                contribution_type=entry["contribution_type"],
                connected_concepts=entry.get("connected_concepts", []),
            )

        for entry in self.data:
            for connected_name in entry.get("connected_people", []):
                if connected_name not in self.graph:
                    self.graph.add_node(
                        connected_name,
                        gender="unknown",
                        fields=[],
                        era="",
                        importance_weight=0.5,
                        erasure_pattern="",
                        contribution_type="unknown",
                        connected_concepts=[],
                    )
                    self.name_index[connected_name.lower()] = connected_name
                    last = connected_name.lower().split()[-1]
                    self.name_index[last] = connected_name

        for entry in self.data:
            for connected_name in entry.get("connected_people", []):
                resolved = self._resolve_name(connected_name)
                if resolved and resolved in self.graph:
                    self.graph.add_edge(entry["name"], resolved, relationship="connected_to")

    def _resolve_name(self, name: str) -> str | None:
        lower = name.lower()
        if lower in self.name_index:
            return self.name_index[lower]
        for key, val in self.name_index.items():
            if lower in key:
                return val
        return None

    def _resolve_extracted_names(self, extracted_names):
        resolved = []
        i = 0
        joined_names = []
        while i < len(extracted_names):
            if i + 1 < len(extracted_names):
                combined = extracted_names[i] + " " + extracted_names[i + 1]
                if combined.lower() in self.name_index:
                    joined_names.append(combined)
                    i += 2
                    continue
            joined_names.append(extracted_names[i])
            i += 1
        for name in joined_names:
            r = self._resolve_name(name)
            if r:
                resolved.append(r)
        resolved = list(set(resolved))
        final = []
        for name in resolved:
            is_subset = any(
                name != other and name.lower() in other.lower()
                for other in resolved
            )
            if not is_subset:
                final.append(name)
        return final

    def bfs_find_missing_women(self, mentioned_names: list[str], depth: int = 2) -> list[dict]:
        mentioned_set = set(mentioned_names)
        missing_women = {}

        for start_node in mentioned_names:
            if start_node not in self.graph:
                continue

            visited = {start_node}
            queue = deque([(start_node, 0)])

            while queue:
                current, current_depth = queue.popleft()

                if current_depth >= depth:
                    continue

                for neighbor in self.graph.neighbors(current):
                    if neighbor in visited:
                        continue
                    visited.add(neighbor)

                    node_data = self.graph.nodes[neighbor]

                    if node_data.get("gender") == "female" and neighbor not in mentioned_set:
                        if neighbor not in missing_women:
                            missing_women[neighbor] = {
                                "name": neighbor,
                                "gender": "female",
                                "fields": node_data.get("fields", []),
                                "era": node_data.get("era", ""),
                                "erasure_pattern": node_data.get("erasure_pattern", ""),
                                "contribution_type": node_data.get("contribution_type", ""),
                                "connected_concepts": node_data.get("connected_concepts", []),
                                "connected_to_mentioned": [
                                    n for n in self.graph.neighbors(neighbor)
                                    if n in mentioned_set
                                ],
                                "betweenness_centrality": round(self.betweenness.get(neighbor, 0), 4),
                                "pagerank": round(self.pagerank.get(neighbor, 0), 4),
                                "importance_weight": self.graph.nodes[neighbor].get("importance_weight", 0.5),
                                "hops_from_mentioned": current_depth + 1,
                            }

                    queue.append((neighbor, current_depth + 1))

        return list(missing_women.values())

    def rank_omissions(self, missing_women: list[dict]) -> list[dict]:
        if not missing_women:
            return []

        max_pr = max((w["pagerank"] for w in missing_women), default=1) or 1
        max_bc = max((w["betweenness_centrality"] for w in missing_women), default=1) or 1

        for w in missing_women:
            pr_norm = w["pagerank"] / max_pr
            bc_norm = w["betweenness_centrality"] / max_bc
            w["omission_score"] = round(
                0.40 * w["importance_weight"]
                + 0.35 * pr_norm
                + 0.25 * bc_norm,
                4
            )

        return sorted(missing_women, key=lambda x: x["omission_score"], reverse=True)

    def calculate_gender_ratio(self, mentioned_names: list[str]) -> dict:
        counts = {"female": 0, "male": 0, "unknown": 0}

        for name in mentioned_names:
            if name in self.graph:
                gender = self.graph.nodes[name].get("gender", "unknown")
                counts[gender] = counts.get(gender, 0) + 1
            else:
                counts["unknown"] += 1

        total_known = counts["female"] + counts["male"]
        ratio = round(counts["female"] / total_known, 3) if total_known > 0 else 0.0

        return {
            "female_count": counts["female"],
            "male_count": counts["male"],
            "unknown_count": counts["unknown"],
            "female_ratio": ratio,
            "representation_percent": round(ratio * 100, 1),
        }

    def analyze(self, extracted_names: list[str], bfs_depth: int = 2) -> dict:
        resolved = self._resolve_extracted_names(extracted_names)
        missing_raw = self.bfs_find_missing_women(resolved, depth=bfs_depth)
        missing_ranked = self.rank_omissions(missing_raw)
        gender_stats = self.calculate_gender_ratio(resolved)
        graph_data = self._build_frontend_graph(resolved, missing_ranked)

        return {
            "mentioned_figures": resolved,
            "missing_women": missing_ranked,
            "gender_ratio": gender_stats,
            "graph": graph_data,
            "completeness_score": self._completeness_score(resolved, missing_ranked),
        }

    def _completeness_score(self, mentioned: list[str], missing: list[dict]) -> float:
        mentioned_women = sum(
            1 for n in mentioned
            if n in self.graph and self.graph.nodes[n].get("gender") == "female"
        )
        total = mentioned_women + len(missing)
        if total == 0:
            return 1.0
        return round(mentioned_women / total, 3)

    def _build_frontend_graph(self, mentioned: list[str], missing: list[dict]) -> dict:
        nodes = []
        links = []
        added_nodes = set()

        for name in mentioned:
            if name not in self.graph:
                continue
            node_data = self.graph.nodes[name]
            gender = node_data.get("gender", "unknown")
            nodes.append({
                "id": name,
                "label": name,
                "gender": gender,
                "status": "mentioned",
                "color": "#4a90d9" if gender == "male" else "#2ecc71",
                "size": 8 + self.pagerank.get(name, 0) * 200,
                "fields": node_data.get("fields", []),
                "era": node_data.get("era", ""),
            })
            added_nodes.add(name)

        for woman in missing:
            name = woman["name"]
            if name in added_nodes:
                continue
            nodes.append({
                "id": name,
                "label": name,
                "gender": "female",
                "status": "missing",
                "color": "#ff69b4",
                "glow": True,
                "size": 6 + woman["omission_score"] * 20,
                "omission_score": woman["omission_score"],
                "erasure_pattern": woman["erasure_pattern"],
                "fields": woman["fields"],
                "era": woman["era"],
                "connected_concepts": woman["connected_concepts"],
            })
            added_nodes.add(name)

        seen_edges = set()
        for u, v, data in self.graph.edges(data=True):
            if u in added_nodes and v in added_nodes:
                edge_key = tuple(sorted([u, v]))
                if edge_key not in seen_edges:
                    links.append({
                        "source": u,
                        "target": v,
                        "relationship": data.get("relationship", "connected_to"),
                    })
                    seen_edges.add(edge_key)

        return {"nodes": nodes, "links": links}


if __name__ == "__main__":
    engine = GraphEngine("knowledge_graph.json")

    extracted = ["Henry Norris Russell", "Watson", "Crick", "Otto Hahn", "Hubble"]
    results = engine.analyze(extracted)

    line = "-" * 40
    print(line)
    print("ANNOTATEHER - ANALYSIS RESULTS")
    print(line)

    print("Names found:")
    for name in results["mentioned_figures"]:
        print(f"  {name}")

    print("\nMissing women (ranked by importance):")
    for w in results["missing_women"][:5]:
        print(f"  {w['name']} (importance: {w['omission_score']})")
        print(f"    Connected to: {', '.join(w['connected_to_mentioned'])}")
        print(f"    Why she matters: {w['erasure_pattern']}")

    print("\nGender ratio:")
    print(f"  {results['gender_ratio']['representation_percent']}% women mentioned")
    print(f"  {results['gender_ratio']['female_count']} women / {results['gender_ratio']['male_count']} men")

    print("\nCompleteness score:")
    print(f"  {results['completeness_score']} out of 1.0")

    print(line)
