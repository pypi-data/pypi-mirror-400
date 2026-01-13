"""
MotionOS SDK - Timeline Walker

Utilities for walking and analyzing timeline graphs.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class TimelineAnalysis:
    """Result of analyzing a timeline walk."""
    total_nodes: int
    max_depth_reached: int
    root_nodes: List[Dict[str, Any]]
    leaf_nodes: List[Dict[str, Any]]
    superseding_nodes: List[Dict[str, Any]]
    obsolete_nodes: List[Dict[str, Any]]
    nodes_by_depth: Dict[int, List[Dict[str, Any]]] = field(default_factory=dict)


def analyze_timeline_walk(result: Dict[str, Any]) -> TimelineAnalysis:
    """Analyze a timeline walk result."""
    nodes = result.get("nodes", [])
    edges = result.get("edges", [])
    
    # Group nodes by depth
    nodes_by_depth: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
    max_depth_reached = 0
    
    for node in nodes:
        depth = node.get("depth", 0)
        nodes_by_depth[depth].append(node)
        max_depth_reached = max(max_depth_reached, depth)
    
    # Find root and leaf nodes
    incoming_edges: Set[str] = {e.get("to_version_id") for e in edges}
    outgoing_edges: Set[str] = {e.get("from_version_id") for e in edges}
    
    root_nodes = [
        n for n in nodes
        if n.get("version_id") not in incoming_edges or n.get("depth") == 0
    ]
    
    leaf_nodes = [
        n for n in nodes
        if n.get("version_id") not in outgoing_edges
    ]
    
    # Find superseding and obsolete nodes
    superseding_nodes = [
        n for n in nodes
        if any(
            e.get("from_version_id") == n.get("version_id") and e.get("edge_type") == "supersedes"
            for e in edges
        )
    ]
    
    obsolete_nodes = [
        n for n in nodes
        if n.get("is_obsolete") or n.get("is_superseded")
    ]
    
    return TimelineAnalysis(
        total_nodes=len(nodes),
        max_depth_reached=max_depth_reached,
        root_nodes=root_nodes,
        leaf_nodes=leaf_nodes,
        superseding_nodes=superseding_nodes,
        obsolete_nodes=obsolete_nodes,
        nodes_by_depth=dict(nodes_by_depth),
    )


def find_path(
    result: Dict[str, Any],
    from_version_id: str,
    to_version_id: str,
) -> Optional[List[Dict[str, Any]]]:
    """Find the path between two versions in a timeline."""
    nodes = result.get("nodes", [])
    edges = result.get("edges", [])
    
    # Build adjacency list
    adjacency: Dict[str, List[str]] = defaultdict(list)
    for edge in edges:
        from_id = edge.get("from_version_id")
        to_id = edge.get("to_version_id")
        if from_id and to_id:
            adjacency[from_id].append(to_id)
    
    # Node map for lookup
    node_map = {n.get("version_id"): n for n in nodes}
    
    # BFS to find path
    visited: Set[str] = set()
    queue: List[tuple] = [(from_version_id, [from_version_id])]
    
    while queue:
        current_id, path = queue.pop(0)
        
        if current_id == to_version_id:
            return [node_map.get(vid) for vid in path if node_map.get(vid)]
        
        if current_id in visited:
            continue
        visited.add(current_id)
        
        for neighbor in adjacency.get(current_id, []):
            if neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))
    
    return None


def get_causes(result: Dict[str, Any], version_id: str) -> List[Dict[str, Any]]:
    """Get all causes (nodes that led to this version)."""
    nodes = result.get("nodes", [])
    edges = result.get("edges", [])
    
    node_map = {n.get("version_id"): n for n in nodes}
    causes = []
    
    for edge in edges:
        if edge.get("to_version_id") == version_id and edge.get("edge_type") == "cause":
            node = node_map.get(edge.get("from_version_id"))
            if node:
                causes.append(node)
    
    return causes


def get_effects(result: Dict[str, Any], version_id: str) -> List[Dict[str, Any]]:
    """Get all effects (nodes caused by this version)."""
    nodes = result.get("nodes", [])
    edges = result.get("edges", [])
    
    node_map = {n.get("version_id"): n for n in nodes}
    effects = []
    
    for edge in edges:
        if edge.get("from_version_id") == version_id and edge.get("edge_type") == "cause":
            node = node_map.get(edge.get("to_version_id"))
            if node:
                effects.append(node)
    
    return effects


def lineage_to_chain(lineage: Dict[str, Any]) -> List[str]:
    """Convert lineage to a simple version chain."""
    ancestors = sorted(
        lineage.get("ancestors", []),
        key=lambda v: v.get("version", 0)
    )
    
    descendants = sorted(
        lineage.get("descendants", []),
        key=lambda v: v.get("version", 0)
    )
    
    ancestor_ids = [v.get("version_id") for v in ancestors]
    descendant_ids = [v.get("version_id") for v in descendants]
    
    return ancestor_ids + [lineage.get("version_id")] + descendant_ids


def find_common_ancestor(
    lineage1: Dict[str, Any],
    lineage2: Dict[str, Any],
) -> Optional[str]:
    """Find the common ancestor of two versions."""
    ancestors1 = {lineage1.get("root_version")}
    for v in lineage1.get("ancestors", []):
        ancestors1.add(v.get("version_id"))
    
    ancestors2 = [lineage2.get("root_version")]
    for v in lineage2.get("ancestors", []):
        ancestors2.append(v.get("version_id"))
    
    # Check in reverse order (most recent first)
    for ancestor in reversed(ancestors2):
        if ancestor in ancestors1:
            return ancestor
    
    return None
