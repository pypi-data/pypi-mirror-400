"""
PTR Engine - Core execution engine for Polynomial Type Runtime

The PTREngine serves as the central coordination point for CLM verification
and execution, implementing the REPL pattern with correctness guarantees
through Object-Process Network principles and computable certificates.

REPL PARADIGM (prep → exec → post → await):
- prep:  Load artifacts, validate V_pre, check preconditions
- exec:  Execute CLM Concrete logic in sandbox
- post:  Verify Balanced expectations, generate V_post (VCard)
- await: Record to handle_history, emit events, prepare for next cycle

THEORETICAL FOUNDATION:
- Object-Process Network (OPN): Models objects and processes as interacting components
- Correctness Theory: Safety/liveness properties, temporal flow guarantees
- MVP+CLM Integration: Three-dimensional verification with mathematical measures
- Arithmetic of Identity: MCard as Prime Number (Atomic Identity)
- Algebra of Composition: PCard as Polynomial Operator (Structure)

ARCHITECTURAL PRINCIPLES:
1. Separates trust (simple verifier) from complexity (generator)
2. Provides directional alignment measurement (cosine similarity)
3. Ensures invariant preservation (Jacobian determinant check)
4. Implements experimental-operational symmetry (content-addressing)
5. Realizes Efficiency Theorem: Compactness, Computability, Composability
"""

import logging
from datetime import datetime, timezone
from typing import Any, Optional, Dict, List, Tuple

from mcard import default_collection

from .lens_protocol import LensProtocol
from .verifier import CLMVerifier
from .common_types import ExecutionResult, VerificationStatus
from .sandbox import SandboxExecutor
from .correctness import CorrectnessTracker
from .certifier import CertificateGenerator
from .monads import IO, Either, Left, Right
from .observability import OpenTelemetrySidecar, REPLPhase, instrument_phase


class PTREngine:
    """
    Core PTR Engine implementing the REPL paradigm with correctness guarantees.
    
    REPL PHASES (aligns with CLM dimensions):
    - prep (Read):   Load Abstract (A), validate V_pre, check preconditions
    - exec (Eval):   Execute Concrete (C) logic in sandboxed environment
    - post (Print):  Verify Balanced (B) expectations, generate V_post witness
    - await (Loop):  Record history, emit events, await next input
    
    CORRECTNESS GUARANTEES:
    1. Safety Properties: Never enters invalid states (enforced by CLM verification)
    2. Liveness Properties: Always makes forward progress (timeout + caching)
    3. Computable Certificates: Verifiable audit trail (VCard generation)
    4. Directional Alignment: Measured alignment with specification (cosine similarity)
    5. Invariant Preservation: Transformations are reversible (|J| != 0)
    
    OBJECT-PROCESS NETWORK DESIGN:
    - Objects: PCards, Target MCards, VCards (entities with state)
    - Processes: Verification, Execution, Certificate Generation (behaviors/actions)
    - Channels: Collection storage, Cache communication
    - Concurrency: Multiple PCard executions can be verified in parallel
    """

    def __init__(self, storage_collection=None, enable_alignment_scoring=False):
        """Initialize PTREngine with correctness tracking.
        
        Args:
            storage_collection: MCard collection for content-addressable storage
            enable_alignment_scoring: Enable directional alignment measurement (requires embeddings)
        """
        self.logger = logging.getLogger(__name__)
        self.collection = storage_collection or default_collection
        
        # Components
        self.verifier = CLMVerifier(self)
        self.lens_protocol = LensProtocol(self)
        self.sandbox = SandboxExecutor(self.collection)
        self.correctness_tracker = CorrectnessTracker(enable_alignment_scoring)
        self.certifier = CertificateGenerator(self.collection)
        
        # Observability Sidecar
        self.observability = OpenTelemetrySidecar.get_instance()
        
        # Execution Cache (implements Liveness through memoization)
        self.execution_cache: Dict[str, ExecutionResult] = {}

    def execute_pcard(
        self, 
        pcard_hash: str, 
        target_hash: str, 
        context: dict[str, Any] = None,
        specification_embedding: Optional[List[float]] = None
    ) -> ExecutionResult:
        """
        Execute a PCard through the complete REPL cycle.
        
        REPL Cycle:
        1. prep:  Load PCard and Target, validate preconditions
        2. exec:  Execute CLM Concrete in sandbox
        3. post:  Verify Balanced expectations, generate VCard witness
        4. await: Record to history, prepare for next input
        
        Args:
            pcard_hash: Hash of the PCard to execute
            target_hash: Hash of the target MCard/VCard
            context: Execution context parameters
            specification_embedding: Optional embedding vector for alignment scoring
            
        Returns:
            ExecutionResult with verification evidence and correctness measures
        """
        start_time = datetime.now(timezone.utc)
        context = context or {}
        
        # Execute the REPL cycle
        result_either = self._execute_repl_cycle(
            pcard_hash, target_hash, context, specification_embedding, start_time
        )
        
        if result_either.is_left():
            # Construct failure result
            end_time = datetime.now(timezone.utc)
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return ExecutionResult(
                success=False,
                output=None,
                verification_vcard=None,
                execution_time_ms=execution_time_ms,
                alignment_score=None,
                invariants_preserved=False,
                safety_violations=self.correctness_tracker.safety_violations.copy(),
                liveness_metrics=self.correctness_tracker.liveness_metrics.copy(),
                error_message=result_either.value
            )
            
        return result_either.value

    def _execute_repl_cycle(
        self, 
        pcard_hash: str, 
        target_hash: str, 
        context: dict[str, Any],
        specification_embedding: Optional[List[float]],
        start_time: datetime
    ) -> Either[str, ExecutionResult]:
        """
        Execute the full REPL cycle: prep → exec → post → await
        
        Each phase is instrumented with OpenTelemetry for observability.
        """
        try:
            # ============================================================
            # PHASE 1: PREP (Read) - Load and validate
            # ============================================================
            with self.observability.trace_phase(
                REPLPhase.PREP, 
                pcard_hash=pcard_hash, 
                target_hash=target_hash
            ):
                prep_result = self._prep(pcard_hash, target_hash, context)
                if prep_result.is_left():
                    return prep_result
                
                pcard, target, verification_result = prep_result.value
                self.observability.log_event(
                    REPLPhase.PREP, 
                    "prep_complete",
                    {"pcard_hash": pcard_hash, "verification_status": "passed"}
                )
            
            # ============================================================
            # PHASE 2: EXEC (Evaluate) - Execute CLM Concrete
            # ============================================================
            with self.observability.trace_phase(
                REPLPhase.EXEC, 
                pcard_hash=pcard_hash, 
                target_hash=target_hash
            ):
                # Check cache first (Liveness guarantee)
                cache_key = f"{pcard_hash}:{target_hash}:{hash(frozenset(context.items()))}"
                if cache_key in self.execution_cache:
                    self.logger.info(f"Using cached execution result for {cache_key}")
                    self.correctness_tracker.record_liveness_metric("cached_execution", 1.0)
                    self.observability.log_event(
                        REPLPhase.EXEC, "cache_hit", {"cache_key": cache_key}
                    )
                    return Right(self.execution_cache[cache_key])
                
                exec_result = self._exec(pcard, target, context)
                if exec_result.is_left():
                    return exec_result
                
                execution_output = exec_result.value
                self.correctness_tracker.record_liveness_metric("execution_completed", 1.0)
                self.observability.log_event(
                    REPLPhase.EXEC, 
                    "exec_complete",
                    {"output_type": type(execution_output).__name__}
                )
            
            # ============================================================
            # PHASE 3: POST (Print) - Verify and generate VCard
            # ============================================================
            with self.observability.trace_phase(
                REPLPhase.POST, 
                pcard_hash=pcard_hash, 
                target_hash=target_hash
            ):
                post_result = self._post(
                    pcard, target, pcard_hash, target_hash,
                    verification_result, execution_output, specification_embedding
                )
                if post_result.is_left():
                    return post_result
                
                verification_vcard, alignment_score, invariants_preserved = post_result.value
                self.observability.log_event(
                    REPLPhase.POST, 
                    "post_complete",
                    {"alignment_score": alignment_score, "invariants_preserved": invariants_preserved}
                )
            
            # ============================================================
            # PHASE 4: AWAIT (Loop) - Record history, prepare next
            # ============================================================
            with self.observability.trace_phase(
                REPLPhase.AWAIT, 
                pcard_hash=pcard_hash, 
                target_hash=target_hash
            ):
                end_time = datetime.now(timezone.utc)
                execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
                
                result = self._await(
                    pcard_hash, target_hash, execution_output, 
                    verification_vcard, execution_time_ms,
                    alignment_score, invariants_preserved, cache_key
                )
                
                self.observability.log_event(
                    REPLPhase.AWAIT, 
                    "await_complete",
                    {"execution_time_ms": execution_time_ms, "cached": True}
                )
                
                return Right(result)
            
        except Exception as e:
            self.logger.error(f"REPL cycle failed: {str(e)}")
            return Left(str(e))

    def _prep(
        self, 
        pcard_hash: str, 
        target_hash: str, 
        context: Dict[str, Any]
    ) -> Either[str, Tuple[Any, Any, Any]]:
        """
        PREP Phase (Read): Load artifacts and validate preconditions.
        
        CLM Dimension: Abstract (A) - Specification check
        Petri Net: Check input places have required tokens
        
        Returns:
            Either[error, (pcard, target, verification_result)]
        """
        # Load PCard
        pcard = self.collection.get(pcard_hash)
        if not pcard:
            self.correctness_tracker.record_safety_violation(
                "pcard_existence", "missing_artifact", f"PCard not found: {pcard_hash}"
            )
            return Left(f"PCard not found: {pcard_hash}")
        
        # Load Target
        target = self.collection.get(target_hash)
        if not target:
            self.correctness_tracker.record_safety_violation(
                "target_existence", "missing_artifact", f"Target not found: {target_hash}"
            )
            return Left(f"Target not found: {target_hash}")
        
        self.logger.info(f"[PREP] Loaded PCard {pcard_hash} and target {target_hash}")
        
        # CLM Verification (Abstract dimension check)
        verification_result = self.verifier.verify_clm_consistency(pcard, target, context)
        if not verification_result.is_valid:
            self.correctness_tracker.record_safety_violation(
                "clm_consistency", "verification_failure", 
                f"CLM verification failed: {verification_result.errors}"
            )
            return Left(f"CLM verification failed: {verification_result.errors}")
        
        self.logger.info(f"[PREP] CLM verification passed for {pcard_hash}")
        return Right((pcard, target, verification_result))

    def _exec(
        self, 
        pcard: Any, 
        target: Any, 
        context: Dict[str, Any]
    ) -> Either[str, Any]:
        """
        EXEC Phase (Evaluate): Execute CLM Concrete logic in sandbox.
        
        CLM Dimension: Concrete (C) - Implementation execution
        Petri Net: Fire transition
        
        Returns:
            Either[error, execution_output]
        """
        try:
            # Use SandboxExecutor's monadic interface
            exec_res = self.sandbox.execute_monad(pcard, target, context).unsafe_run()
            if exec_res.is_left():
                return exec_res
            
            self.logger.info(f"[EXEC] Execution completed successfully")
            return Right(exec_res.value)
            
        except Exception as e:
            self.logger.error(f"[EXEC] Execution failed: {str(e)}")
            return Left(str(e))

    def _post(
        self, 
        pcard: Any,
        target: Any,
        pcard_hash: str, 
        target_hash: str,
        verification_result: Any,
        execution_output: Any,
        specification_embedding: Optional[List[float]]
    ) -> Either[str, Tuple[Any, Optional[float], bool]]:
        """
        POST Phase (Print): Verify Balanced expectations and generate VCard.
        
        CLM Dimension: Balanced (B) - Expectations verification
        Petri Net: Deposit output token, generate witness
        
        Returns:
            Either[error, (verification_vcard, alignment_score, invariants_preserved)]
        """
        try:
            # Alignment measurement
            alignment_score = self.correctness_tracker.calculate_alignment(
                execution_output, specification_embedding
            )
            
            # Invariant preservation check
            invariants_preserved = self.correctness_tracker.verify_invariant_preservation(
                pcard, target, execution_output
            )
            
            if not invariants_preserved:
                self.correctness_tracker.record_safety_violation(
                    "invariant_preservation", "jacobian_zero", 
                    "Transformation is not reversible (|J| = 0)"
                )
            
            # Generate VCard witness (V_post)
            verification_vcard = self.certifier.generate_verification_vcard(
                pcard_hash, 
                target_hash, 
                verification_result, 
                execution_output,
                alignment_score,
                invariants_preserved
            )
            
            self.logger.info(
                f"[POST] VCard generated (alignment: {alignment_score}, "
                f"invariants: {invariants_preserved})"
            )
            return Right((verification_vcard, alignment_score, invariants_preserved))
            
        except Exception as e:
            self.logger.error(f"[POST] Post-verification failed: {str(e)}")
            return Left(str(e))

    def _await(
        self, 
        pcard_hash: str,
        target_hash: str,
        execution_output: Any,
        verification_vcard: Any,
        execution_time_ms: int,
        alignment_score: Optional[float],
        invariants_preserved: bool,
        cache_key: str
    ) -> ExecutionResult:
        """
        AWAIT Phase (Loop): Record history and prepare for next input.
        
        CLM Dimension: Balanced (B) feedback - History recording
        Petri Net: Update marking, emit event
        
        Returns:
            ExecutionResult (ready for next REPL cycle)
        """
        # Assemble final result
        result = ExecutionResult(
            success=True,
            output=execution_output,
            verification_vcard=verification_vcard,
            execution_time_ms=execution_time_ms,
            alignment_score=alignment_score,
            invariants_preserved=invariants_preserved,
            safety_violations=[],
            liveness_metrics=self.correctness_tracker.liveness_metrics.copy()
        )
        
        # Cache result (Liveness guarantee: memoization)
        self.execution_cache[cache_key] = result
        
        self.logger.info(
            f"[AWAIT] PCard {pcard_hash} completed in {execution_time_ms}ms "
            f"(alignment: {alignment_score}, invariants: {invariants_preserved})"
        )
        
        # TODO: Record to handle_history for provenance tracking
        # self._record_to_handle_history(pcard_hash, target_hash, verification_vcard)
        
        return result

    def evaluate_polynomial(
        self, 
        polynomial_hash: str, 
        target_hash: str, 
        context: dict[str, Any] = None,
        specification_embedding: Optional[List[float]] = None
    ) -> ExecutionResult:
        """
        Evaluate a PCard as a Polynomial Operator: F(X) = Sum(A_i * X^{B_i})
        
        This method is an alias for `execute_pcard` but emphasizes the theoretical
        view of the PCard as a mathematical operator acting on a target (X).
        
        The evaluation process:
        1. Resolves the Polynomial Structure (PCard) from `polynomial_hash`
        2. Applies the Operator to the Target (X) from `target_hash`
        3. Verifies the result against the Modular Constraints (VCard/Context)
        
        Args:
            polynomial_hash: Hash of the PCard (Polynomial Operator)
            target_hash: Hash of the Target (Prime Value)
            context: Modular Constraints (Ring Context)
            specification_embedding: Optional embedding for alignment
            
        Returns:
            ExecutionResult: The computed value with attached proof (VCard)
        """
        return self.execute_pcard(polynomial_hash, target_hash, context, specification_embedding)

    def get_verification_status(self, pcard_hash: str, target_hash: str) -> dict[str, Any]:
        """Get verification status for a PCard-target pair"""
        cache_key = f"{pcard_hash}:{target_hash}"

        if cache_key in self.execution_cache:
            result = self.execution_cache[cache_key]
            return {
                "verified": result.success,
                "verification_vcard": result.verification_vcard,
                "execution_time_ms": result.execution_time_ms,
                "alignment_score": result.alignment_score,
                "invariants_preserved": result.invariants_preserved,
                "error": result.error_message
            }
        else:
            return {"verified": False, "error": "Not yet verified"}

    def get_safety_violations(self) -> List[Dict[str, Any]]:
        """Get all recorded safety violations"""
        return self.correctness_tracker.get_safety_violations()

    def get_liveness_metrics(self) -> List[Dict[str, Any]]:
        """Get all recorded liveness metrics"""
        return self.correctness_tracker.get_liveness_metrics()

    def get_available_runtimes(self) -> Dict[str, bool]:
        """
        Get list of available language runtimes on this system.
        
        Returns:
            Dict mapping runtime name to availability status
        """
        return self.sandbox.list_available_runtimes()

    def run_balanced_tests(self, pcard_hash: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run all test cases defined in the PCard's balanced dimension.
        
        Args:
            pcard_hash: Hash of the PCard to test
            context: Optional base context (e.g. for infrastructure params)
            
        Returns:
            Dict containing test results
        """
        pcard = self.collection.get(pcard_hash)
        if not pcard:
            raise ValueError(f"PCard not found: {pcard_hash}")
            
        import yaml
        pcard_content = pcard.get_content().decode('utf-8')
        pcard_data = yaml.safe_load(pcard_content)
        
        balanced = pcard_data.get('balanced', {})
        test_cases = balanced.get('test_cases', [])
        
        results = {
            'total': len(test_cases),
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        for i, test_case in enumerate(test_cases):
            description = test_case.get('description', f"Test Case #{i+1}")
            given = test_case.get('given', {})
            expected = test_case.get('then', {})
            
            # Extract input from 'given'
            # Handle different input formats (string, dict, etc.)
            input_val = given
            if isinstance(given, dict) and 'input' in given:
                input_val = given['input']
            elif isinstance(given, dict) and len(given) == 1:
                # If single key dict, assume value is input
                input_val = list(given.values())[0]
                
            # Extract context params from 'when'
            when = test_case.get('when', {})
            test_context = when.get('params', {})
            
            # Merge with base context
            # Base context (infrastructure) + Test context (logic overrides)
            full_context = (context or {}).copy()
            full_context.update(test_context)
                
            # Create target MCard from input
            if isinstance(input_val, str):
                target_content = input_val.encode('utf-8')
            else:
                import json
                target_content = json.dumps(input_val).encode('utf-8')
                
            from mcard import MCard
            target = MCard(target_content)
            self.collection.add(target)
            
            # Execute
            try:
                result = self.execute_pcard(pcard_hash, target.hash, context=full_context)
                
                # Verify output matches expectation
                # This is a simplified check - ideally we'd use a proper matcher
                passed = True
                failure_reason = ""
                
                actual = result.output
                
                # Check each expected output field
                for key, expected_val in expected.items():
                    if key == 'epsilon': continue # Skip epsilon parameter
                    
                    # Handle nested keys if actual is dict
                    actual_val = actual
                    if isinstance(actual, dict) and key in actual:
                        actual_val = actual[key]
                    elif isinstance(actual, (int, float, str)) and key in ['result', 'sine_value', 'value']:
                        # If actual is scalar, compare directly against expected value
                        actual_val = actual
                    
                    # Numeric comparison with epsilon
                    if isinstance(expected_val, (int, float)) and isinstance(actual_val, (int, float)):
                        epsilon = float(expected.get('epsilon', 0))
                        if abs(actual_val - expected_val) > epsilon:
                            passed = False
                            failure_reason = f"Expected {key}={expected_val} (epsilon={epsilon}), got {actual_val}"
                            break
                    elif isinstance(expected_val, dict) and isinstance(actual_val, dict):
                        # Partial dict match (subset check)
                        # Check if all keys/values in expected_val are present in actual_val
                        def check_subset(exp, act, path=""):
                            for k, v in exp.items():
                                if k not in act:
                                    return False, f"Missing key '{path}{k}'"
                                
                                if isinstance(v, dict) and isinstance(act[k], dict):
                                    sub_ok, sub_reason = check_subset(v, act[k], f"{path}{k}.")
                                    if not sub_ok:
                                        return False, sub_reason
                                elif v != act[k]:
                                    return False, f"Value mismatch at '{path}{k}': expected {v}, got {act[k]}"
                            return True, ""

                        subset_ok, subset_reason = check_subset(expected_val, actual_val)
                        if not subset_ok:
                            passed = False
                            failure_reason = f"Dict mismatch for {key}: {subset_reason}"
                            break
                    elif actual_val != expected_val:
                        passed = False
                        failure_reason = f"Expected {key}={expected_val}, got {actual_val}"
                        break
                
                if passed:
                    results['passed'] += 1
                    status = "PASSED"
                else:
                    results['failed'] += 1
                    status = "FAILED"
                    
                results['details'].append({
                    'id': i + 1,
                    'description': description,
                    'status': status,
                    'input': input_val,
                    'expected': expected,
                    'actual': actual,
                    'reason': failure_reason
                })
                
            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'id': i + 1,
                    'description': description,
                    'status': "ERROR",
                    'input': input_val,
                    'error': str(e)
                })
                
        return results
