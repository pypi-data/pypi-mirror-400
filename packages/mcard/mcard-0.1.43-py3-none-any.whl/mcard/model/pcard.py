"""PCard Model (Control Plane) - Implementation of LENS/CHART values.

This module defines the PCard, which represents the execution unit in the DOTS framework.
PCards are MCards that contain a valid CLM (Cubical Logic Model) specification.

Categorical Foundation:
    PCard is a Strong Profunctor: P: A^op × B → Set
    
    This means PCard is:
    - Contravariant in its input (A^op): Can accept MORE general inputs
    - Covariant in its output (B): Can produce MORE specific outputs
    
    The "Strong" property means PCard supports:
    - first: P(A, B) → P(C × A, C × B)  (threading context through)
    - second: P(A, B) → P(A × C, B × C) (preserving additional structure)

Composition via Coend:
    Two PCards P and Q compose via the Coend (∫ᴮ):
    
    (P ⨾ Q)(A, C) = ∫ᴮ P(A, B) × Q(B, C)
    
    The Coend "integrates out" the intermediate type B by:
    1. Finding all compatible B-typed interfaces
    2. Identifying outputs of P with inputs of Q
    3. Producing a new PCard that chains the transformations
    
    This is implemented by the `then()` method (sequential composition).
"""

from typing import Optional, Dict, List, Any, Union
import yaml
from mcard.model.card import MCard
from mcard.model.dots import create_pcard_dots_metadata, DOTSMetadata

class PCard(MCard):
    """PCard - The Control Plane unit (Lens + Chart).
    
    A PCard is an MCard whose content is a valid CLM specification.
    
    =============================================================================
    CATEGORICAL FOUNDATIONS (Strong Profunctor)
    =============================================================================
    
    PCard implements the Strong Profunctor pattern from category theory:
    
    **Profunctor Definition**:
        P: A^op × B → Set
        
    Where:
        - A^op denotes contravariance in input types (accepts MORE general)
        - B denotes covariance in output types (produces MORE specific)
        - Set is the category of sets (our value space)
    
    **Strong Profunctor Operations**:
        - `dimap(f, g)`: Transform both input (contravariant) and output (covariant)
        - `first()`: Thread additional context through: P(A,B) → P(C×A, C×B)
        - `second()`: Preserve additional structure: P(A,B) → P(A×C, B×C)
    
    **Intuition**:
        PCard defines a transformation that can:
        - Accept inputs of type A (or any supertype, due to contravariance)
        - Produce outputs of type B (or any subtype, due to covariance)
        - Carry additional context through the transformation (Strong property)
    
    =============================================================================
    COMPOSITION VIA COEND
    =============================================================================
    
    Two PCards compose via the Coend (categorical integral):
    
        (P ⨾ Q)(A, C) = ∫ᴮ P(A, B) × Q(B, C)
    
    Where:
        - ∫ᴮ is the Coend over the intermediate type B
        - P(A, B) is the first PCard (input A, output B)
        - Q(B, C) is the second PCard (input B, output C)
        - The result is a new PCard from A to C
    
    **Coend Interpretation**:
        The Coend "glues together" all compatible B-typed interfaces:
        1. For each possible B, find P's outputs and Q's inputs
        2. Identify P's output with Q's input (via hash matching)
        3. The quotient identifies equivalent compositions
    
    **Implementation**:
        `then()` implements Coend composition:
        - Creates a new CLM that chains the two PCards
        - The intermediate B is represented by content hashes
        - Type compatibility is verified at execution time by PTR
    
    =============================================================================
    SMC STRUCTURE (Symmetric Monoidal Category)
    =============================================================================
    
    PCard composition forms a Symmetric Monoidal Category:
    
        - **Objects**: Content types (MCard content hashes as type witnesses)
        - **Morphisms**: PCards (transformations between types)
        - **Identity**: The "pass-through" PCard (`id_A: A → A`)
        - **Composition**: Sequential chaining via `then()` (;)
        - **Tensor Product**: Parallel composition via `and_also()` (⊗)
        - **Symmetry**: Port swapping via `swap()` (σ)
    
    **Coherence Laws** (satisfied by implementation):
        - Associativity: (f ; g) ; h = f ; (g ; h)
        - Identity: id ; f = f = f ; id
        - Tensor associativity: (A ⊗ B) ⊗ C ≅ A ⊗ (B ⊗ C)
        - Symmetry: σ ∘ σ = id, and σ is natural
    
    =============================================================================
    OTHER ROLES
    =============================================================================
    
    Petri Net (UPTV):
        - Role: Transition (Process)
        - Consumes VCards (input tokens), produces VCards (output tokens)
        - Fire condition: All input places have required tokens
    
    DOTS Vocabulary:
        - LENS: Tight morphism (Abstract ↔ Concrete coherence)
        - CHART: Loose morphism (Interaction pattern wiring)
        
    CLM Triad Structure:
        - Abstract (A): Specification (Thesis) - WHAT
        - Concrete (C): Implementation (Antithesis) - HOW
        - Balanced (B): Evidence/Tests (Synthesis) - PROOF
    """
    
    def __init__(self, content: Union[str, bytes], hash_function: Union[str, Any] = "sha256"):
        """Initialize a PCard.
        
        Args:
            content: The CLM YAML string.
            hash_function: Hash function to use.
            
        Raises:
            ValueError: If content is not valid YAML or valid CLM structure.
        """
        super().__init__(content, hash_function)
        self._parsed_clm = self._validate_and_parse()
        
    def _validate_and_parse(self) -> Dict[str, Any]:
        """Validate content is valid YAML CLM and return parsed dict."""
        try:
            content_str = self.get_content(as_text=True)
            clm = yaml.safe_load(content_str)
            
            if not isinstance(clm, dict):
                raise ValueError("PCard content must be a YAML dictionary")
                
            return clm
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML content for PCard: {e}")
            
    def get_dots_metadata(self) -> DOTSMetadata:
        """Get DOTS metadata for this PCard."""
        tight_refs = []
        loose_refs = []
        
        # Extract dependencies if they exist in standard CLM fields
        for key in ['tight_deps', 'dependencies']:
            if key in self._parsed_clm and isinstance(self._parsed_clm[key], list):
                tight_refs.extend(self._parsed_clm[key])
                
        for key in ['loose_deps', 'alternatives']:
            if key in self._parsed_clm and isinstance(self._parsed_clm[key], list):
                loose_refs.extend(self._parsed_clm[key])
        
        return create_pcard_dots_metadata(
            spec_hash=self.hash,
            tight_refs=tight_refs if tight_refs else None,
            loose_refs=loose_refs if loose_refs else None
        )
    
    @property
    def clm(self) -> Dict[str, Any]:
        """Get the parsed CLM dictionary."""
        return self._parsed_clm
    
    # -------------------------------------------------------------------------
    # UPTV CLM Triad Accessors (A x C x B)
    # -------------------------------------------------------------------------

    def _get_section(self, section_name: str, aliases: List[str]) -> Optional[Dict[str, Any]]:
        """Helper to retrieve section from root or nested 'clm' or aliases."""
        # 1. Check root
        val = self._parsed_clm.get(section_name)
        if val: return val
        
        # 2. Check aliases at root
        for alias in aliases:
            val = self._parsed_clm.get(alias)
            if val: return val
            
        # 3. Check inside 'clm' dict (nested structure)
        clm_inner = self._parsed_clm.get('clm')
        if isinstance(clm_inner, dict):
            val = clm_inner.get(section_name)
            if val: return val
            for alias in aliases:
                val = clm_inner.get(alias)
                if val: return val
        
        return None

    @property
    def abstract(self) -> Optional[Dict[str, Any]]:
        """Get the Abstract (A) section."""
        return self._get_section('abstract', ['abstract_spec'])
        
    @property
    def concrete(self) -> Optional[Dict[str, Any]]:
        """Get the Concrete (C) section."""
        return self._get_section('concrete', ['concrete_impl', 'impl'])

    @property
    def balanced(self) -> Optional[Dict[str, Any]]:
        """Get the Balanced (B) section."""
        return self._get_section('balanced', ['balanced_expectations', 'expectations'])

    # -------------------------------------------------------------------------
    # Legacy Aliases (Strict Backward Compatibility)
    # -------------------------------------------------------------------------

    @property
    def abstract_spec(self) -> Optional[Dict[str, Any]]:
        """Legacy alias for abstract."""
        return self.abstract

    @property
    def concrete_impl(self) -> Optional[Dict[str, Any]]:
        """Legacy alias for concrete."""
        return self.concrete

    @property
    def balanced_expectations(self) -> Optional[Dict[str, Any]]:
        """Legacy alias for balanced."""
        return self.balanced

    # =========================================================================
    # SMC ALGEBRAIC COMBINATORS (Profunctor Composition)
    # =========================================================================
    #
    # These methods implement the Symmetric Monoidal Category structure,
    # enabling algebraic composition of PCards as profunctors.
    #
    # Composition Laws (Categorical Coherence):
    #   - Associativity: (f.then(g)).then(h) ≡ f.then(g.then(h))
    #   - Identity: id.then(f) ≡ f ≡ f.then(id)
    #   - Tensor Associativity: (A ⊗ B) ⊗ C ≅ A ⊗ (B ⊗ C)
    #   - Symmetry Involution: swap().swap() ≡ id
    # =========================================================================


    def then(self, other_pcard: 'PCard') -> 'PCard':
        """Sequential Composition via Coend ($P ⨾ Q$).
        
        Implements profunctor composition using the Coend formula:
        
            (P ⨾ Q)(A, C) = ∫ᴮ P(A, B) × Q(B, C)
        
        Where:
            - self is P: A → B
            - other_pcard is Q: B → C
            - Result is P ⨾ Q: A → C
        
        The Coend (∫ᴮ) "integrates out" the intermediate type B by:
        1. Matching P's output type with Q's input type
        2. Creating a chain where P's result feeds into Q
        3. The composition is associative: (P ⨾ Q) ⨾ R = P ⨾ (Q ⨾ R)
        
        In PTR execution:
            - P is executed first (prep → exec → post)
            - P's output VCard becomes Q's input VCard
            - Q is executed second
            - Final result is Q's output VCard
        
        Args:
            other_pcard: The PCard to execute after this one (Q in P ⨾ Q).
            
        Returns:
            A new PCard representing the composed profunctor (P ⨾ Q).
        """
        # Create a new CLM that composes the two
        new_clm = {
            "chapter": {
                "id": f"composed_{self.hash[:8]}_{other_pcard.hash[:8]}",
                "title": "Sequentially Composed Function",
                "goal": f"Compose {self.hash} then {other_pcard.hash}"
            },
            "clm": {
                "abstract": {
                    "type": "sequential_composition",
                    "coend_formula": "∫ᴮ P(A,B) × Q(B,C)",
                    "steps": [self.hash, other_pcard.hash]
                },
                "concrete": {
                    "runtime": "ptr",
                    "operation": "compose_sequential",
                    "steps": [self.hash, other_pcard.hash]
                }
            }
        }
        return PCard(yaml.dump(new_clm), self.hash_function)


    def and_also(self, other_pcard: 'PCard') -> 'PCard':
        r"""Tensor Product ($A \otimes B$).
        
        Runs this PCard and other_pcard in parallel.
        
        Args:
            other_pcard: The PCard to execute in parallel.
            
        Returns:
            A new PCard representing the parallel execution.
        """
        new_clm = {
            "chapter": {
                "id": f"parallel_{self.hash[:8]}_{other_pcard.hash[:8]}",
                "title": "Parallel Function",
                "goal": f"Run {self.hash} and {other_pcard.hash} in parallel"
            },
            "clm": {
                "abstract": {
                    "type": "tensor_product",
                    "left": self.hash,
                    "right": other_pcard.hash
                },
                "concrete": {
                    "runtime": "ptr",
                    "operation": "compose_parallel",
                    "components": [self.hash, other_pcard.hash]
                }
            }
        }
        return PCard(yaml.dump(new_clm), self.hash_function)

    def swap(self) -> 'PCard':
        r"""Symmetry ($\sigma$).
        
        Swaps the input/output ports of a tensor product.
        
        Returns:
            A new PCard with swapped inputs/outputs.
        """
        new_clm = {
            "chapter": {
                "id": f"swapped_{self.hash[:8]}",
                "title": "Swapped Function",
                "goal": f"Swap inputs/outputs of {self.hash}"
            },
            "clm": {
                "abstract": {
                    "type": "symmetry_swap",
                    "target": self.hash
                },
                "concrete": {
                    "runtime": "ptr",
                    "operation": "apply_symmetry",
                    "target": self.hash
                }
            }
        }
        return PCard(yaml.dump(new_clm), self.hash_function)


    # =========================================================================
    # Universal Tooling Interface
    # =========================================================================

    def verify(self) -> Dict[str, Any]:
        """Run the Balanced Expectations (Proof).
        
        Returns:
            Dict containing verification results.
        """
        # In a real implementation, this would trigger the Verifier component
        # For now, return the balanced spec as a "proof plan"
        return {
            "status": "pending_verification",
            "proof_plan": self.balanced,
            "target": self.hash
        }

    def profile(self) -> Dict[str, Any]:
        """Run with instrumentation (eBPF/Tracing).
        
        Returns:
            Dict containing performance metrics.
        """
        return {
            "status": "profiling_ready",
            "target": self.hash,
            "instrumentation": "standard"
        }

    def debug(self) -> Dict[str, Any]:
        """Run in Operative mode (Step-by-step).
        
        Returns:
            Dict containing debug session info.
        """
        return {
            "status": "debug_session_created",
            "mode": "operative",
            "target": self.hash
        }

    def explain(self) -> Dict[str, Any]:
        """Return documentation/explanation.
        
        Returns:
            Dict containing abstract spec and narrative.
        """
        return {
            "abstract": self.abstract,
            "narrative": self._parsed_clm.get("chapter", {}),
            "dots_metadata": self.get_dots_metadata().__dict__
        }


    def get_input_vcard_refs(self) -> List[Dict[str, Any]]:
        """Get input VCard references (Pre-set: •t).

        These represent the preconditions that must be satisfied before
        this PCard (Transition) can fire.

        Returns:
            List of input VCard references from CLM specification
        """
        refs = []
        clm = self._parsed_clm

        # Check for explicit input_vcards in CLM
        input_vcards = (clm.get('input_vcards') or
                        clm.get('preconditions') or
                        clm.get('requires'))

        if isinstance(input_vcards, list):
            for ref in input_vcards:
                if isinstance(ref, str):
                    refs.append({'handle': ref})
                elif isinstance(ref, dict) and 'handle' in ref:
                    refs.append({
                        'handle': ref['handle'],
                        'expected_hash': ref.get('hash') or ref.get('expected_hash'),
                        'purpose': ref.get('purpose')
                    })

        # Also check verification.pcard_refs for authentication requirements
        verification = clm.get('clm', {}).get('verification') or clm.get('verification')
        if verification:
            pcard_refs = verification.get('pcard_refs', [])
            for ref in pcard_refs:
                if isinstance(ref, str):
                    refs.append({
                        'handle': f"auth://{ref}",
                        'purpose': 'authenticate'
                    })
                elif isinstance(ref, dict) and 'hash' in ref:
                    refs.append({
                        'handle': f"auth://{ref['hash']}",
                        'expected_hash': ref['hash'],
                        'purpose': ref.get('purpose', 'authenticate')
                    })
        
        return refs

    def get_output_vcard_specs(self) -> List[Dict[str, Any]]:
        """Get output VCard specifications (Post-set: t•).

        These define what VCards (Tokens) this PCard produces when fired.

        Returns:
            List of output VCard specifications
        """
        specs = []
        clm = self._parsed_clm

        # Check for explicit output_vcards in CLM
        output_vcards = (clm.get('output_vcards') or
                         clm.get('postconditions') or
                         clm.get('produces'))

        if isinstance(output_vcards, list):
            for spec in output_vcards:
                if isinstance(spec, str):
                    specs.append({'handle': spec, 'type': 'result'})
                elif isinstance(spec, dict) and 'handle' in spec:
                    specs.append({
                        'handle': spec['handle'],
                        'type': spec.get('type', 'result'),
                        'metadata': spec.get('metadata')
                    })

        # Default: produce a verification VCard at balanced handle
        if not specs:
            chapter = clm.get('chapter')
            if chapter and isinstance(chapter, dict) and chapter.get('title'):
                import re
                safe_name = re.sub(r'[^a-z0-9]', '_', chapter['title'].lower())
                specs.append({
                    'handle': f"clm://{safe_name}/balanced",
                    'type': 'verification'
                })

        return specs

    def get_transition_handle(self) -> str:
        """Get the canonical handle for this PCard (Transition).

        Returns:
            Handle string in form `clm://{module}/{function}/spec`
        """
        chapter = self._parsed_clm.get('chapter')
        if chapter and isinstance(chapter, dict) and 'id' in chapter:
            title = chapter.get('title')
            if title:
                import re
                safe_name = re.sub(r'[^a-z0-9]', '_', title.lower())
            else:
                safe_name = f"chapter_{chapter['id']}"
            return f"clm://{safe_name}/spec"
        
        # Fallback to hash-based handle
        return f"clm://hash/{self.hash[:16]}/spec"

    def get_balanced_handle(self) -> str:
        """Get the balanced expectations handle for this PCard.

        This is where verification history is tracked in handle_history.

        Returns:
            Handle string for balanced expectations
        """
        spec_handle = self.get_transition_handle()
        return spec_handle.replace('/spec', '/balanced')

    def can_fire(self, available_vcards: Dict[str, str]) -> Dict[str, Any]:
        """Check if this PCard (Transition) can fire given the available VCards.

        A transition can fire when all input VCards (preconditions) are present.

        Args:
            available_vcards: Dict of handle -> VCard hash

        Returns:
            Dict containing 'can_fire' (bool) and 'missing' (list of handles)
        """
        input_refs = self.get_input_vcard_refs()
        missing = []

        for ref in input_refs:
            handle = ref['handle']
            expected_hash = ref.get('expected_hash')
            
            vcard_hash = available_vcards.get(handle)
            if not vcard_hash:
                missing.append(handle)
            elif expected_hash and vcard_hash != expected_hash:
                missing.append(f"{handle} (hash mismatch)")

        return {
            'can_fire': len(missing) == 0,
            'missing': missing
        }

    def get_runtime(self) -> str:
        """Get the runtime required for this PCard.

        Returns:
            Runtime name (e.g., 'javascript', 'python', 'lean')
        """
        clm_config = self._parsed_clm.get('clm', {}).get('concrete')
        concrete = self._parsed_clm.get('concrete')
        
        if clm_config and 'runtime' in clm_config:
            return clm_config['runtime']
        if concrete and 'runtime' in concrete:
            return concrete['runtime']
        
        # Default or try logic_source detection?
        return 'javascript' # Default in JS implementation too

    def is_multi_runtime(self) -> bool:
        """Check if this is a multi-runtime PCard.

        Returns:
            True if this PCard supports multiple runtimes
        """
        clm_config = self._parsed_clm.get('clm', {}).get('concrete')
        concrete = self._parsed_clm.get('concrete')
        
        config = clm_config or concrete
        return config and isinstance(config.get('runtimes_config'), list) and len(config['runtimes_config']) > 1
