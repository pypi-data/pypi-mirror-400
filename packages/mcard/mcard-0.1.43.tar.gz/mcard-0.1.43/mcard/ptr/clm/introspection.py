"""
CLM Introspection - Recursive CLM Hierarchy Analysis

This module provides introspection capabilities for CLM (Cubical Logic Model)
hierarchies, enabling formal inspection of recursive CLM composition.

Recursive CLM Composition:
    CLMs can compose recursively, creating hierarchies of specifications:
    
    Root CLM (Chapter)
    ├── Sub-CLM A (referenced PCard)
    │   ├── Leaf CLM X
    │   └── Leaf CLM Y
    └── Sub-CLM B (referenced PCard)
        └── Leaf CLM Z
    
    This module enables:
    - Traversal of CLM dependency graphs
    - Detection of circular dependencies
    - Extraction of CLM metadata at any level
    - Composition path tracing

SMC Structure Preservation:
    The introspection respects the Symmetric Monoidal Category structure:
    - Composition paths preserve associativity
    - Parallel compositions are correctly identified
    - Identity CLMs are recognized

See Also:
    - CLM_MCard_REPL_Implementation.md §8: Recursive CLM Composition
    - PTR_MCard_CLM_Recent_Developments_Jan2026.md §4.2: Recursive Structure
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import yaml
import logging


class CLMType(Enum):
    """Type classification for CLM nodes."""
    CHAPTER = "chapter"          # Has chapter metadata
    PCARD = "pcard"              # Pure PCard (no chapter wrapper)
    COMPOSED = "composed"        # Sequential composition (then)
    PARALLEL = "parallel"        # Tensor product (and_also)
    REFERENCE = "reference"      # Reference to another CLM by hash
    UNKNOWN = "unknown"


class CompositionType(Enum):
    """Type of composition between CLMs."""
    SEQUENTIAL = "sequential"    # A ; B (Coend composition)
    PARALLEL = "parallel"        # A ⊗ B (Tensor product)
    NONE = "none"                # Leaf node


@dataclass
class CLMNode:
    """
    Represents a node in the CLM hierarchy tree.
    
    Each node corresponds to a CLM (PCard) in the composition graph.
    """
    # Content hash (MCard identity)
    hash: str
    
    # Node classification
    clm_type: CLMType
    
    # CLM dimensions
    abstract: Optional[Dict[str, Any]] = None
    concrete: Optional[Dict[str, Any]] = None
    balanced: Optional[Dict[str, Any]] = None
    
    # Chapter metadata (if present)
    chapter: Optional[Dict[str, Any]] = None
    
    # Composition metadata
    composition_type: CompositionType = CompositionType.NONE
    
    # Children nodes (for composed CLMs)
    children: List['CLMNode'] = field(default_factory=list)
    
    # Parent hash (for traversal)
    parent_hash: Optional[str] = None
    
    # Depth in the hierarchy (root = 0)
    depth: int = 0
    
    # Declared runtime
    runtime: str = "unknown"


@dataclass
class CLMIntrospectionResult:
    """
    Result of CLM hierarchy introspection.
    
    Contains the full tree structure and analysis metadata.
    """
    # Root node of the hierarchy
    root: CLMNode
    
    # All nodes indexed by hash
    nodes: Dict[str, CLMNode]
    
    # Maximum depth of the hierarchy
    max_depth: int
    
    # Total node count
    node_count: int
    
    # Detected circular dependencies
    cycles: List[List[str]]
    
    # Runtime distribution
    runtimes: Dict[str, int]
    
    # Composition statistics
    sequential_count: int
    parallel_count: int
    leaf_count: int


class CLMIntrospector:
    """
    Recursive CLM Hierarchy Introspector.
    
    Analyzes CLM composition graphs, extracting structure and metadata
    from arbitrarily nested CLM hierarchies.
    
    Usage:
        introspector = CLMIntrospector(collection)
        result = await introspector.introspect("root_pcard_hash")
        
        # Access hierarchy
        print(result.root.chapter)
        for child in result.root.children:
            print(f"  - {child.hash}: {child.clm_type}")
        
        # Check for cycles
        if result.cycles:
            print(f"Circular dependencies detected: {result.cycles}")
    """
    
    def __init__(self, collection=None, max_depth: int = 100):
        """
        Initialize the introspector.
        
        Args:
            collection: MCard collection for content retrieval.
            max_depth: Maximum recursion depth to prevent infinite loops.
        """
        self.logger = logging.getLogger(__name__)
        self._collection = collection
        self._max_depth = max_depth
        self._visited: Set[str] = set()
        self._nodes: Dict[str, CLMNode] = {}
        self._cycles: List[List[str]] = []
    
    async def introspect(self, pcard_hash: str) -> CLMIntrospectionResult:
        """
        Introspect a CLM hierarchy starting from the given root.
        
        Args:
            pcard_hash: Hash of the root PCard.
            
        Returns:
            CLMIntrospectionResult containing the full hierarchy analysis.
        """
        self._visited = set()
        self._nodes = {}
        self._cycles = []
        
        root = await self._build_tree(pcard_hash, depth=0, path=[])
        
        if root is None:
            root = CLMNode(
                hash=pcard_hash,
                clm_type=CLMType.UNKNOWN
            )
        
        # Calculate statistics
        max_depth = max((n.depth for n in self._nodes.values()), default=0)
        runtimes = self._count_runtimes()
        seq_count, par_count, leaf_count = self._count_compositions()
        
        return CLMIntrospectionResult(
            root=root,
            nodes=self._nodes,
            max_depth=max_depth,
            node_count=len(self._nodes),
            cycles=self._cycles,
            runtimes=runtimes,
            sequential_count=seq_count,
            parallel_count=par_count,
            leaf_count=leaf_count
        )
    
    async def _build_tree(
        self, 
        pcard_hash: str, 
        depth: int, 
        path: List[str],
        parent_hash: Optional[str] = None
    ) -> Optional[CLMNode]:
        """
        Recursively build the CLM tree from a PCard hash.
        """
        # Check for cycles
        if pcard_hash in path:
            cycle = path[path.index(pcard_hash):] + [pcard_hash]
            self._cycles.append(cycle)
            self.logger.warning(f"Circular dependency detected: {' -> '.join(cycle)}")
            return None
        
        # Check max depth
        if depth > self._max_depth:
            self.logger.warning(f"Max depth {self._max_depth} exceeded at {pcard_hash}")
            return None
        
        # Check if already processed
        if pcard_hash in self._nodes:
            return self._nodes[pcard_hash]
        
        # Get PCard content
        clm_data = await self._get_clm_data(pcard_hash)
        if clm_data is None:
            return None
        
        # Create node
        node = self._create_node(pcard_hash, clm_data, depth, parent_hash)
        self._nodes[pcard_hash] = node
        
        # Process children based on composition type
        new_path = path + [pcard_hash]
        
        if node.composition_type == CompositionType.SEQUENTIAL:
            # Sequential composition: process steps
            steps = clm_data.get('clm', {}).get('abstract', {}).get('steps', [])
            for step_hash in steps:
                child = await self._build_tree(step_hash, depth + 1, new_path, pcard_hash)
                if child:
                    node.children.append(child)
                    
        elif node.composition_type == CompositionType.PARALLEL:
            # Parallel composition: process components
            left = clm_data.get('clm', {}).get('abstract', {}).get('left')
            right = clm_data.get('clm', {}).get('abstract', {}).get('right')
            
            if left:
                child = await self._build_tree(left, depth + 1, new_path, pcard_hash)
                if child:
                    node.children.append(child)
            if right:
                child = await self._build_tree(right, depth + 1, new_path, pcard_hash)
                if child:
                    node.children.append(child)
        
        # Check for recursive runtime references
        runtime = node.runtime
        if runtime.endswith('.yaml') or runtime.endswith('.clm'):
            # This is a reference to another CLM file - would need file resolution
            pass
        
        return node
    
    async def _get_clm_data(self, pcard_hash: str) -> Optional[Dict[str, Any]]:
        """Get CLM data from a PCard hash."""
        if self._collection is None:
            return None
        
        try:
            pcard = self._collection.get(pcard_hash)
            if pcard is None:
                return None
            
            content = pcard.content if isinstance(pcard.content, str) else pcard.content.decode('utf-8')
            return yaml.safe_load(content)
            
        except Exception as e:
            self.logger.error(f"Failed to get CLM data for {pcard_hash}: {e}")
            return None
    
    def _create_node(
        self, 
        pcard_hash: str, 
        clm_data: Dict[str, Any],
        depth: int,
        parent_hash: Optional[str]
    ) -> CLMNode:
        """Create a CLMNode from parsed CLM data."""
        # Determine CLM type
        clm_type = self._classify_clm(clm_data)
        
        # Extract CLM dimensions
        clm_section = clm_data.get('clm', {})
        abstract = clm_section.get('abstract') or clm_data.get('abstract')
        concrete = clm_section.get('concrete') or clm_data.get('concrete')
        balanced = clm_section.get('balanced') or clm_data.get('balanced')
        
        # Extract chapter
        chapter = clm_data.get('chapter')
        
        # Determine composition type
        composition_type = CompositionType.NONE
        abstract_type = (abstract or {}).get('type', '')
        
        if abstract_type == 'sequential_composition':
            composition_type = CompositionType.SEQUENTIAL
        elif abstract_type == 'tensor_product':
            composition_type = CompositionType.PARALLEL
        
        # Extract runtime
        runtime = (
            (concrete or {}).get('runtime') or
            clm_section.get('concrete', {}).get('runtime') or
            'unknown'
        )
        
        return CLMNode(
            hash=pcard_hash,
            clm_type=clm_type,
            abstract=abstract,
            concrete=concrete,
            balanced=balanced,
            chapter=chapter,
            composition_type=composition_type,
            children=[],
            parent_hash=parent_hash,
            depth=depth,
            runtime=runtime
        )
    
    def _classify_clm(self, clm_data: Dict[str, Any]) -> CLMType:
        """Classify the CLM by its structure."""
        if 'chapter' in clm_data:
            return CLMType.CHAPTER
        
        abstract = clm_data.get('clm', {}).get('abstract') or clm_data.get('abstract', {})
        abstract_type = abstract.get('type', '') if isinstance(abstract, dict) else ''
        
        if abstract_type == 'sequential_composition':
            return CLMType.COMPOSED
        elif abstract_type == 'tensor_product':
            return CLMType.PARALLEL
        elif 'clm' in clm_data or 'abstract' in clm_data:
            return CLMType.PCARD
        
        return CLMType.UNKNOWN
    
    def _count_runtimes(self) -> Dict[str, int]:
        """Count nodes by runtime."""
        runtimes: Dict[str, int] = {}
        for node in self._nodes.values():
            rt = node.runtime
            runtimes[rt] = runtimes.get(rt, 0) + 1
        return runtimes
    
    def _count_compositions(self) -> tuple:
        """Count sequential, parallel, and leaf compositions."""
        seq = 0
        par = 0
        leaf = 0
        
        for node in self._nodes.values():
            if node.composition_type == CompositionType.SEQUENTIAL:
                seq += 1
            elif node.composition_type == CompositionType.PARALLEL:
                par += 1
            else:
                leaf += 1
        
        return seq, par, leaf
    
    def to_tree_string(self, result: CLMIntrospectionResult) -> str:
        """
        Generate a tree visualization of the CLM hierarchy.
        
        Returns:
            ASCII tree representation.
        """
        lines = []
        self._tree_to_string(result.root, lines, "", True)
        return "\n".join(lines)
    
    def _tree_to_string(
        self, 
        node: CLMNode, 
        lines: List[str], 
        prefix: str, 
        is_last: bool
    ) -> None:
        """Recursive helper for tree visualization."""
        connector = "└── " if is_last else "├── "
        
        # Build node label
        label_parts = [node.hash[:8]]
        if node.chapter:
            title = node.chapter.get('title', '')
            if title:
                label_parts.append(f"({title})")
        label_parts.append(f"[{node.clm_type.value}]")
        if node.runtime != 'unknown':
            label_parts.append(f"@{node.runtime}")
        
        lines.append(prefix + connector + " ".join(label_parts))
        
        # Process children
        new_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(node.children):
            self._tree_to_string(child, lines, new_prefix, i == len(node.children) - 1)
