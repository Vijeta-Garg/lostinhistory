"""
purp

riya gives  list of names extracted from the PDF
builds graph, finds missing women,
calculates gender ratio, ranks omissions by importance

"""

import json
import networkx as nx
from collections import deque


class GraphEngine:
    def __init__(self, knowledge_graph_path: str):
        
        with open(knowledge_graph_path, "r") as f:
            self.data = json.load(f)

        #entry for quick lookup
        self.people = {entry["name"]: entry for entry in self.data}

        # build a lookup by last name and common short name
        self.name_index = {}
        for entry in self.data:
            full = entry["name"].lower()
            last = full.split()[-1]
            self.name_index[full] = entry["name"]
            self.name_index[last] = entry["name"]  # "Franklin" → "Rosalind Franklin"

    #graph buil
        self.graph = nx.Graph()
        self._build_graph()

        # centrality scores (slow on huge graphs, fine for 150 nodes)
        self.betweenness = nx.betweenness_centrality(self.graph, weight=None)
        self.pagerank = nx.pagerank(self.graph)

    def _build_graph(self):
        """Add all people as nodes, then connect them via connected_people."""
        #node
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

        # edge
        for entry in self.data:
            for connected_name in entry.get("connected_people", []):
                # resolve short names like "Watson" → "James Watson"
                resolved = self._resolve_name(connected_name)
                if resolved and resolved in self.graph:
                    self.graph.add_edge(entry["name"], resolved, relationship="connected_to")

    def _resolve_name(self, name: str) -> str | None:
        """Try to find a full name from a partial name."""
        lower = name.lower()
        if lower in self.name_index:
            return self.name_index[lower]
        # Try last name only
        for key, val in self.name_index.items():
            if lower in key:
                return val
        return None

    def _resolve_extracted_names(self, extracted_names: list[str]) -> list[str]:
        """
        Take riyas and resolve to full names in  graph
        Returns list 
        """
        resolved = []
        for name in extracted_names:
            r = self._resolve_name(name)
            if r:
                resolved.append(r)
        return list(set(resolved))

    def bfs_find_missing_women(self, mentioned_names: list[str], depth: int = 2) -> list[dict]:
        """
        BFS from each mentioned node in the reference graph
        Returns list of missing women with their info.
        """
        mentioned_set = set(mentioned_names)
        missing_women = {}

        for start_node in mentioned_names:
            if start_node not in self.graph:
                continue

            # Standard BFS
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

                    # Flag if female AND not in document
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
                                # Graph scores for ranking
                                "betweenness_centrality": round(self.betweenness.get(neighbor, 0), 4),
                                "pagerank": round(self.pagerank.get(neighbor, 0), 4),
                                "importance_weight": self.graph.nodes[neighbor].get("importance_weight", 0.5),
                                "hops_from_mentioned": current_depth + 1,
                            }

                    queue.append((neighbor, current_depth + 1))

        return list(missing_women.values())

    def rank_omissions(self, missing_women: list[dict]) -> list[dict]:
        """
        Sort missing women by composite importance score.
        Higher score = bigger omission = show first / bigger node in graph.
        """
        if not missing_women:
            return []

        # Normalize pagerank and betweenness to 0-1
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
        """
        Given the names extracted from a PDF section,
        return gender breakdown and representation ratio.
        """
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
            "female_ratio": ratio,  # 0.0 = no women, 1.0 = all women
            "representation_percent": round(ratio * 100, 1),
        }

    def analyze(self, extracted_names: list[str], bfs_depth: int = 2) -> dict:
        """
        MAIN FUNCTION — call this with the list of names from llm
        
        Returns everything needed for the frontend
        """
        # Resolve names 
        resolved = self._resolve_extracted_names(extracted_names)

        # Find missing women via BFS
        missing_raw = self.bfs_find_missing_women(resolved, depth=bfs_depth)
        missing_ranked = self.rank_omissions(missing_raw)

        # Gender ratio
        gender_stats = self.calculate_gender_ratio(resolved)

        # Build graph  for frontend
        graph_data = self._build_frontend_graph(resolved, missing_ranked)

        return {
            "mentioned_figures": resolved,
            "missing_women": missing_ranked,
            "gender_ratio": gender_stats,
            "graph": graph_data,
            "completeness_score": self._completeness_score(resolved, missing_ranked),
        }

    def _completeness_score(self, mentioned: list[str], missing: list[dict]) -> float:
        """
        How complete is the document's representation?
        0.0 = no women mentioned, 1.0 = no women missing
        """
        mentioned_women = sum(
            1 for n in mentioned
            if n in self.graph and self.graph.nodes[n].get("gender") == "female"
        )
        total = mentioned_women + len(missing)
        if total == 0:
            return 1.0
        return round(mentioned_women / total, 3)

    def _build_frontend_graph(self, mentioned: list[str], missing: list[dict]) -> dict:
        """
        Format for react-force-graph 
        
        Node colors:
        - blue: mentioned male
        - green: mentioned female  
        - pink/glow: missing female 
        """
        nodes = []
        links = []
        added_nodes = set()

        # Add mentioned nodes
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
                "size": 8 + self.pagerank.get(name, 0) * 200,  # size by importance
                "fields": node_data.get("fields", []),
                "era": node_data.get("era", ""),
            })
            added_nodes.add(name)

        # Add missing women nodes 
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

        # Add edges between all nodes now in the graph
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


# TESTNG
if __name__ == "__main__":
    engine = GraphEngine("knowledge_graph.json")


    extracted = ["Rosalind Franklin", "Marie Curie", "Watson", "Crick", "Otto Hahn", "Joshua Lederberg"]

    results = engine.analyze(extracted)

    print("=== MENTIONED FIGURES ===")
    print(results["mentioned_figures"])

    print("\n=== GENDER RATIO ===")
    print(results["gender_ratio"])

    print("\n=== TOP 5 MISSING WOMEN ===")
    for w in results["missing_women"][:5]:
        print(f"  {w['name']} (score: {w['omission_score']})")
        print(f"    Connected to: {w['connected_to_mentioned']}")
        print(f"    Why she matters: {w['erasure_pattern']}")

    print("\n=== COMPLETENESS SCORE ===")
    print(results["completeness_score"])

    print("\n=== GRAPH (first 3 nodes) ===")
    for node in results["graph"]["nodes"][:3]:
        print(node)
