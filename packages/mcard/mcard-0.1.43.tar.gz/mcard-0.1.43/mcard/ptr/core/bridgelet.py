"""
Bridgelet Universal Vehicle - Cross-Language Execution Abstraction

The Bridgelet provides a universal interface for executing CLM logic across
different language runtimes, enabling polyglot composition of PCards.

Conceptual Foundation:
    Bridgelet = Universal Vehicle for Cross-Language Execution
    
    Just as a physical bridge connects two lands, a Bridgelet connects two
    language runtimes, enabling data and control flow across the boundary.

Architecture:
    ┌─────────────────────────────────────────────────────────────────────┐
    │                        Bridgelet Interface                          │
    │  invoke(pcard_hash, input_vcard) → output_vcard                    │
    └───────────────────────────┬─────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
    ┌────────┐             ┌────────┐             ┌────────┐
    │ Python │             │  JS    │             │ WASM   │
    │Runtime │             │Runtime │             │Runtime │
    └────────┘             └────────┘             └────────┘

Protocol:
    1. Serialize input VCard to content-addressable format (MCard)
    2. Invoke target runtime with PCard hash and input MCard hash
    3. Receive output MCard hash
    4. Deserialize output MCard to VCard
    
    All data crosses the bridge as immutable MCards (content-addressed),
    ensuring EOS (Experimental-Operational Symmetry).

See Also:
    - CLM_MCard_REPL_Implementation.md §10: Bridgelet Universal Vehicle
    - PTR_MCard_CLM_Recent_Developments_Jan2026.md §5.3: Polyglot Execution
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, List
import logging


class RuntimeType(Enum):
    """Supported runtime types for Bridgelet execution."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    WASM = "wasm"
    LEAN = "lean"
    UNKNOWN = "unknown"


@dataclass
class BridgeletInvocation:
    """
    Represents a cross-runtime invocation request.
    
    All data is represented by content hashes (MCard references),
    ensuring immutability and EOS compliance.
    """
    # PCard to execute (content hash)
    pcard_hash: str
    
    # Input VCard (content hash)
    input_vcard_hash: str
    
    # Target runtime
    target_runtime: RuntimeType
    
    # Execution context (serializable parameters)
    context: Dict[str, Any]
    
    # Trace ID for observability
    trace_id: str


@dataclass
class BridgeletResult:
    """
    Result of a Bridgelet invocation.
    
    Contains the output VCard hash and execution metadata.
    """
    # Success status
    success: bool
    
    # Output VCard (content hash)
    output_vcard_hash: Optional[str]
    
    # Error message if failed
    error: Optional[str]
    
    # Execution time in milliseconds
    execution_time_ms: int
    
    # Runtime that executed the PCard
    executed_by: RuntimeType
    
    # Additional metadata
    metadata: Dict[str, Any]


class BridgeletAdapter(ABC):
    """
    Abstract base class for runtime-specific Bridgelet adapters.
    
    Each adapter implements the protocol for a specific runtime,
    handling serialization, invocation, and deserialization.
    """
    
    @abstractmethod
    def get_runtime_type(self) -> RuntimeType:
        """Get the runtime type this adapter supports."""
        pass
    
    @abstractmethod
    async def invoke(self, invocation: BridgeletInvocation) -> BridgeletResult:
        """
        Invoke a PCard in this runtime.
        
        Args:
            invocation: The invocation request with PCard hash and input.
            
        Returns:
            BridgeletResult with output VCard hash or error.
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this runtime is available for execution."""
        pass


class PythonBridgeletAdapter(BridgeletAdapter):
    """
    Bridgelet adapter for Python runtime.
    
    Executes PCards using the local Python PTR engine.
    """
    
    def __init__(self, collection=None):
        """
        Initialize the Python adapter.
        
        Args:
            collection: MCard collection for content-addressable storage.
        """
        self.logger = logging.getLogger(__name__)
        self._collection = collection
        
    def get_runtime_type(self) -> RuntimeType:
        return RuntimeType.PYTHON
    
    def is_available(self) -> bool:
        return True  # Python is always available in Python runtime
    
    async def invoke(self, invocation: BridgeletInvocation) -> BridgeletResult:
        """
        Execute PCard using local Python PTR engine.
        """
        import time
        start_time = time.time()
        
        try:
            # Lazy import to avoid circular dependencies
            from mcard.ptr.core.engine import PTREngine
            
            # Get or create collection
            if self._collection is None:
                from mcard import default_collection
                self._collection = default_collection
            
            # Create engine and execute
            engine = PTREngine(storage_collection=self._collection)
            result = engine.execute_pcard(
                pcard_hash=invocation.pcard_hash,
                target_hash=invocation.input_vcard_hash,
                context=invocation.context
            )
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            if result.success:
                # Extract output VCard hash
                output_hash = None
                if result.verification_vcard:
                    output_hash = result.verification_vcard.hash if hasattr(result.verification_vcard, 'hash') else str(result.verification_vcard)
                
                return BridgeletResult(
                    success=True,
                    output_vcard_hash=output_hash,
                    error=None,
                    execution_time_ms=execution_time_ms,
                    executed_by=RuntimeType.PYTHON,
                    metadata={
                        "alignment_score": result.alignment_score,
                        "invariants_preserved": result.invariants_preserved
                    }
                )
            else:
                return BridgeletResult(
                    success=False,
                    output_vcard_hash=None,
                    error=result.error_message,
                    execution_time_ms=execution_time_ms,
                    executed_by=RuntimeType.PYTHON,
                    metadata={}
                )
                
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            self.logger.error(f"Python Bridgelet invocation failed: {e}")
            return BridgeletResult(
                success=False,
                output_vcard_hash=None,
                error=str(e),
                execution_time_ms=execution_time_ms,
                executed_by=RuntimeType.PYTHON,
                metadata={}
            )


class Bridgelet:
    """
    Universal Vehicle for Cross-Language Execution.
    
    The Bridgelet manages a registry of runtime adapters and routes
    PCard execution requests to the appropriate runtime based on
    the PCard's declared runtime requirement.
    
    Usage:
        bridgelet = Bridgelet()
        bridgelet.register_adapter(PythonBridgeletAdapter())
        bridgelet.register_adapter(JavaScriptBridgeletAdapter())
        
        result = await bridgelet.invoke(
            pcard_hash="abc123",
            input_vcard_hash="def456",
            context={"param": "value"}
        )
    
    Cross-Language Composition:
        The Bridgelet enables polyglot PCard composition:
        
        python_pcard.then(js_pcard).then(wasm_pcard)
        
        Each transition crosses a runtime bridge, with data flowing
        as content-addressed MCards.
    """
    
    def __init__(self, collection=None):
        """
        Initialize the Bridgelet.
        
        Args:
            collection: MCard collection for content-addressable storage.
        """
        self.logger = logging.getLogger(__name__)
        self._collection = collection
        self._adapters: Dict[RuntimeType, BridgeletAdapter] = {}
        self._trace_counter = 0
        
        # Auto-register Python adapter
        self.register_adapter(PythonBridgeletAdapter(collection))
    
    def register_adapter(self, adapter: BridgeletAdapter) -> None:
        """
        Register a runtime adapter.
        
        Args:
            adapter: The BridgeletAdapter to register.
        """
        runtime_type = adapter.get_runtime_type()
        self._adapters[runtime_type] = adapter
        self.logger.info(f"Registered Bridgelet adapter for {runtime_type.value}")
    
    def get_available_runtimes(self) -> List[RuntimeType]:
        """
        Get list of available runtimes.
        
        Returns:
            List of RuntimeType values for available adapters.
        """
        return [
            rt for rt, adapter in self._adapters.items()
            if adapter.is_available()
        ]
    
    def _generate_trace_id(self) -> str:
        """Generate a unique trace ID for observability."""
        import time
        self._trace_counter += 1
        return f"bridgelet-{int(time.time() * 1000)}-{self._trace_counter}"
    
    def _detect_runtime(self, pcard_hash: str) -> RuntimeType:
        """
        Detect the required runtime for a PCard.
        
        Args:
            pcard_hash: The hash of the PCard.
            
        Returns:
            The detected RuntimeType.
        """
        if self._collection is None:
            return RuntimeType.PYTHON  # Default
        
        try:
            pcard = self._collection.get(pcard_hash)
            if pcard is None:
                return RuntimeType.PYTHON
            
            # Parse CLM content
            import yaml
            content = pcard.content if isinstance(pcard.content, str) else pcard.content.decode('utf-8')
            clm = yaml.safe_load(content)
            
            # Extract runtime from CLM
            runtime_str = (
                clm.get('clm', {}).get('concrete', {}).get('runtime') or
                clm.get('concrete', {}).get('runtime') or
                'python'
            )
            
            # Map string to RuntimeType
            runtime_map = {
                'python': RuntimeType.PYTHON,
                'javascript': RuntimeType.JAVASCRIPT,
                'typescript': RuntimeType.TYPESCRIPT,
                'js': RuntimeType.JAVASCRIPT,
                'ts': RuntimeType.TYPESCRIPT,
                'wasm': RuntimeType.WASM,
                'lean': RuntimeType.LEAN
            }
            
            return runtime_map.get(runtime_str.lower(), RuntimeType.PYTHON)
            
        except Exception as e:
            self.logger.warning(f"Failed to detect runtime for {pcard_hash}: {e}")
            return RuntimeType.PYTHON
    
    async def invoke(
        self,
        pcard_hash: str,
        input_vcard_hash: str,
        context: Optional[Dict[str, Any]] = None,
        target_runtime: Optional[RuntimeType] = None
    ) -> BridgeletResult:
        """
        Invoke a PCard across the appropriate runtime bridge.
        
        Args:
            pcard_hash: Hash of the PCard to execute.
            input_vcard_hash: Hash of the input VCard.
            context: Execution context parameters.
            target_runtime: Override runtime detection (optional).
            
        Returns:
            BridgeletResult with output VCard hash or error.
        """
        context = context or {}
        trace_id = self._generate_trace_id()
        
        # Detect or use specified runtime
        runtime = target_runtime or self._detect_runtime(pcard_hash)
        
        # Check if adapter is available
        if runtime not in self._adapters:
            return BridgeletResult(
                success=False,
                output_vcard_hash=None,
                error=f"No adapter registered for runtime: {runtime.value}",
                execution_time_ms=0,
                executed_by=RuntimeType.UNKNOWN,
                metadata={}
            )
        
        adapter = self._adapters[runtime]
        if not adapter.is_available():
            return BridgeletResult(
                success=False,
                output_vcard_hash=None,
                error=f"Runtime not available: {runtime.value}",
                execution_time_ms=0,
                executed_by=RuntimeType.UNKNOWN,
                metadata={}
            )
        
        # Create invocation
        invocation = BridgeletInvocation(
            pcard_hash=pcard_hash,
            input_vcard_hash=input_vcard_hash,
            target_runtime=runtime,
            context=context,
            trace_id=trace_id
        )
        
        self.logger.info(
            f"Bridgelet invoking {pcard_hash[:8]}... via {runtime.value} "
            f"(trace: {trace_id})"
        )
        
        # Invoke through adapter
        result = await adapter.invoke(invocation)
        
        self.logger.info(
            f"Bridgelet invocation complete: {'success' if result.success else 'failed'} "
            f"({result.execution_time_ms}ms)"
        )
        
        return result
