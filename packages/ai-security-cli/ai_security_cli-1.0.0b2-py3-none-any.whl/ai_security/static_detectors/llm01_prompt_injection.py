"""
LLM01: Prompt Injection Detector

Detects unsafe embedding of user input into LLM prompts using:
- Taint analysis (user input → prompt string → LLM call)
- String operation patterns (f-strings, concatenation, .format())
- Confidence scoring based on validation presence
"""

import logging
from typing import Dict, List, Any, Set, Optional
from dataclasses import dataclass

from ai_security.static_detectors.base_detector import BaseDetector
from ai_security.models.finding import Finding, Severity

logger = logging.getLogger(__name__)


@dataclass
class TaintFlow:
    """Track flow of user input to LLM prompt"""
    source_var: str  # Variable name containing user input
    source_line: int
    operations: List[Dict[str, Any]]  # String operations applied
    sink_line: int  # Line where it reaches LLM call
    sink_function: str  # LLM API function called


class PromptInjectionDetector(BaseDetector):
    """
    Detect LLM01: Prompt Injection vulnerabilities

    Detects:
    - Direct f-string injection: f"Prompt: {user_input}"
    - String concatenation: prompt + user_message
    - .format() calls: template.format(user_input)

    Confidence factors:
    - HIGH (0.9): Direct injection with no validation
    - MEDIUM (0.6): Injection with basic validation (length check)
    - LOW (0.3): Injection with sanitization/allowlist
    """

    detector_id = "LLM01"
    name = "Prompt Injection"
    default_confidence_threshold = 0.6

    # User input parameter name patterns
    USER_INPUT_PATTERNS = {
        'user_input', 'user_message', 'user_query', 'query', 'message',
        'input', 'prompt', 'text', 'content', 'request', 'user_text',
        'user_prompt', 'user_data', 'search_query'
    }

    # Validation/sanitization indicators (reduce confidence)
    VALIDATION_PATTERNS = {
        'sanitize', 'clean', 'escape', 'validate', 'filter',
        'allowlist', 'whitelist', 'strip_html', 'remove_',
        'check_', 'verify_', 'PromptTemplate'
    }

    def _gather_potential_findings(self, parsed_data: Dict[str, Any]) -> List[Finding]:
        """
        Find all potential prompt injection points

        Strategy:
        1. Identify user input parameters
        2. Track taint flow through string operations
        3. Check if tainted data reaches LLM calls
        """
        findings = []

        # Get parsed AST data
        functions = parsed_data.get('functions', [])
        string_ops = parsed_data.get('string_operations', [])
        llm_calls = parsed_data.get('llm_api_calls', [])
        assignments = parsed_data.get('assignments', [])

        if not llm_calls:
            # No LLM calls, nothing to check
            return findings

        # For each function with LLM calls
        for func in functions:
            func_name = func['name']
            func_start = func['line']
            func_end = func.get('end_line', func_start + 100)

            # Find LLM calls in this function
            func_llm_calls = [
                call for call in llm_calls
                if func_start <= call['line'] <= func_end
            ]

            if not func_llm_calls:
                continue

            # Check if function has user input parameters
            user_params = self._identify_user_input_params(func['args'])

            if not user_params:
                # No user input parameters, skip
                continue

            # Find string operations in this function
            func_string_ops = [
                op for op in string_ops
                if func_start <= op['line'] <= func_end
            ]

            # Find assignments in this function for taint tracking
            func_assignments = [
                assign for assign in assignments
                if func_start <= assign['line'] <= func_end
            ]

            # Check for taint flow: user_param → string_op → llm_call
            for llm_call in func_llm_calls:
                taint_flows = self._trace_taint_flows(
                    user_params=user_params,
                    string_ops=func_string_ops,
                    assignments=func_assignments,
                    llm_call=llm_call,
                    func_name=func_name
                )

                for flow in taint_flows:
                    finding = self._create_finding(
                        flow=flow,
                        parsed_data=parsed_data,
                        func=func
                    )
                    findings.append(finding)

        return findings

    def _identify_user_input_params(self, param_names: List[str]) -> Set[str]:
        """Identify which parameters likely contain user input"""
        user_params = set()

        for param in param_names:
            param_lower = param.lower()
            if any(pattern in param_lower for pattern in self.USER_INPUT_PATTERNS):
                user_params.add(param)

        return user_params

    def _trace_taint_flows(
        self,
        user_params: Set[str],
        string_ops: List[Dict[str, Any]],
        assignments: List[Dict[str, Any]],
        llm_call: Dict[str, Any],
        func_name: str
    ) -> List[TaintFlow]:
        """
        Trace flow of user input through string operations to LLM call

        Proper taint analysis (no proximity heuristic):
        1. Track user params through variable assignments
        2. Track string operation results through their targets
        3. Check if tainted variables appear in LLM call arguments
        """
        flows = []

        # Build taint tracking from assignments
        tainted_vars = set(user_params)  # Start with user input params

        # First pass: identify all tainted assignments
        # e.g., sanitized = user_input.strip()
        for assign in sorted(assignments, key=lambda a: a['line']):
            assign_value = assign.get('value', '')
            assign_name = assign.get('name', '')

            # Check if assignment references a tainted variable
            for tainted_var in list(tainted_vars):
                if tainted_var in assign_value:
                    tainted_vars.add(assign_name)
                    break

        # Second pass: track string operations with tainted input
        # and mark their targets as tainted
        tainted_string_ops = []

        for string_op in string_ops:
            op_type = string_op['type']
            op_line = string_op['line']

            # Check if this string operation involves tainted input
            involves_tainted_input = False
            source_var = None

            if op_type == 'f-string':
                # Check if f-string contains tainted variable
                values = string_op.get('values', [])
                for value in values:
                    value_str = str(value)
                    for tainted_var in tainted_vars:
                        if tainted_var in value_str:
                            involves_tainted_input = True
                            source_var = tainted_var
                            break

            elif op_type == 'concatenation':
                # Check if concatenation involves tainted variable
                left = string_op.get('left', '')
                right = string_op.get('right', '')
                for tainted_var in tainted_vars:
                    if tainted_var in left or tainted_var in right:
                        involves_tainted_input = True
                        source_var = tainted_var
                        break

            elif op_type == 'format_call':
                # .format() calls are suspicious if they involve tainted input
                if tainted_vars:
                    involves_tainted_input = True
                    source_var = list(tainted_vars)[0]

            if involves_tainted_input and source_var:
                # Mark the target as tainted
                target = string_op.get('target')
                if target:
                    tainted_vars.add(target)

                # Store this tainted operation
                tainted_string_ops.append({
                    'string_op': string_op,
                    'source_var': source_var,
                    'target': target
                })

        # Build a mapping of variable provenance to trace back to string operations
        # For variables that were assigned from other tainted vars
        var_provenance = {}  # var -> source_var it was assigned from
        for assign in sorted(assignments, key=lambda a: a['line']):
            assign_name = assign.get('name', '')
            assign_value = assign.get('value', '')

            # Check if this assignment is from another tainted variable
            for tainted_var in tainted_vars:
                if assign_name in tainted_vars and tainted_var in assign_value and tainted_var != assign_name:
                    var_provenance[assign_name] = tainted_var
                    break

        # Helper function to find the string operation for a tainted variable
        def find_string_operation_for_var(var: str) -> Optional[Dict]:
            """Trace back through assignments to find the originating string operation"""
            current_var = var
            visited = set()

            while current_var and current_var not in visited:
                visited.add(current_var)

                # Check if this variable has a string operation
                for op in tainted_string_ops:
                    if op['target'] == current_var or op['source_var'] == current_var:
                        return op

                # Follow the provenance chain
                current_var = var_provenance.get(current_var)

            return None

        # Third pass: check if any tainted variable reaches the LLM call arguments
        llm_args = llm_call.get('args', [])
        llm_keywords = llm_call.get('keywords', {})

        # Check positional arguments
        for arg in llm_args:
            arg_str = str(arg)
            for tainted_var in tainted_vars:
                if tainted_var in arg_str:
                    # Find the string operation that created this taint (or its provenance)
                    source_op = find_string_operation_for_var(tainted_var)

                    if source_op:
                        flow = TaintFlow(
                            source_var=source_op['source_var'],
                            source_line=source_op['string_op']['line'],
                            operations=[source_op['string_op']],
                            sink_line=llm_call['line'],
                            sink_function=llm_call['function']
                        )
                        flows.append(flow)
                        break

        # Check keyword arguments
        for key, value in llm_keywords.items():
            value_str = str(value)
            for tainted_var in tainted_vars:
                if tainted_var in value_str:
                    # Find the string operation that created this taint (or its provenance)
                    source_op = find_string_operation_for_var(tainted_var)

                    if source_op:
                        flow = TaintFlow(
                            source_var=source_op['source_var'],
                            source_line=source_op['string_op']['line'],
                            operations=[source_op['string_op']],
                            sink_line=llm_call['line'],
                            sink_function=llm_call['function']
                        )
                        flows.append(flow)
                        break

        return flows

    def _create_finding(
        self,
        flow: TaintFlow,
        parsed_data: Dict[str, Any],
        func: Dict[str, Any]
    ) -> Finding:
        """Create Finding from taint flow"""

        file_path = parsed_data.get('file_path', 'unknown')
        source_lines = parsed_data.get('source_lines', [])

        # Get code snippet
        snippet_start = max(0, flow.source_line - 2)
        snippet_end = min(len(source_lines), flow.sink_line + 1)
        code_snippet = '\n'.join(source_lines[snippet_start:snippet_end])

        # Build evidence for confidence calculation
        evidence = {
            'source_var': flow.source_var,
            'operation_type': flow.operations[0]['type'] if flow.operations else 'unknown',
            'llm_function': flow.sink_function,
            'function_name': func['name'],
            'has_validation': self._check_for_validation(func, source_lines),
            'has_sanitization': self._check_for_sanitization(func, source_lines)
        }

        return Finding(
            id=f"{self.detector_id}_{file_path}_{flow.source_line}",
            category=f"{self.detector_id}: {self.name}",
            severity=Severity.CRITICAL,  # Prompt injection is critical
            confidence=0.0,  # Will be calculated in calculate_confidence()
            title=f"User input '{flow.source_var}' directly embedded in LLM prompt",
            description=(
                f"The function '{func['name']}' embeds user input ('{flow.source_var}') "
                f"directly into an LLM prompt using {evidence['operation_type']}. "
                f"This allows attackers to inject malicious instructions that can override "
                f"system prompts, leak sensitive data, or manipulate model behavior."
            ),
            file_path=file_path,
            line_number=flow.source_line,
            code_snippet=code_snippet,
            recommendation=(
                "Mitigations:\n"
                "1. Use structured prompt templates (e.g., LangChain PromptTemplate)\n"
                "2. Implement input sanitization to remove prompt injection patterns\n"
                "3. Use separate 'user' and 'system' message roles (ChatML format)\n"
                "4. Apply input validation and length limits\n"
                "5. Use allowlists for expected input formats\n"
                "6. Consider prompt injection detection libraries"
            ),
            evidence=evidence
        )

    def _check_for_validation(self, func: Dict[str, Any], source_lines: List[str]) -> bool:
        """Check if function has input validation"""
        func_start = func['line']
        func_end = func.get('end_line', func_start + 50)

        # Simple heuristic: look for len() checks or conditionals
        for i in range(func_start - 1, min(func_end, len(source_lines))):
            line = source_lines[i].lower()
            if 'len(' in line and ('>' in line or '<' in line or '==' in line):
                return True
            if any(pattern in line for pattern in ['if ', 'assert ', 'raise ']):
                return True

        return False

    def _check_for_sanitization(self, func: Dict[str, Any], source_lines: List[str]) -> bool:
        """Check if function has input sanitization or uses PromptTemplate"""
        import re

        func_start = func['line']
        func_end = func.get('end_line', func_start + 50)

        for i in range(func_start - 1, min(func_end, len(source_lines))):
            line = source_lines[i].lower()

            # Check for actual sanitization function calls (not just variable names)
            # Match pattern at start of word followed by optional chars and (
            # e.g., sanitize(, sanitize_input(, clean(, clean_data(
            for pattern in self.VALIDATION_PATTERNS:
                # Use regex to match pattern as start of function name
                if re.search(rf'\b{re.escape(pattern)}[a-z_]*\(', line):
                    return True

            # Check for PromptTemplate usage (safe pattern)
            if 'prompttemplate' in line.replace(' ', ''):
                return True

        return False

    def calculate_confidence(self, evidence: Dict[str, Any]) -> float:
        """
        Calculate confidence based on evidence

        Scoring:
        - Start with HIGH confidence (0.9)
        - Reduce by 0.2 if validation present
        - Reduce by 0.4 if sanitization/PromptTemplate present (stronger mitigation)
        """
        confidence = 0.9  # Start high for direct injection

        # Reduce confidence if mitigations are present
        if evidence.get('has_validation', False):
            confidence -= 0.2

        if evidence.get('has_sanitization', False):
            confidence -= 0.4  # Increased from 0.3 - sanitization is more effective

        # Certain operation types are more risky
        op_type = evidence.get('operation_type', '')
        if op_type == 'f-string':
            confidence = min(confidence + 0.05, 1.0)  # f-strings are most direct
        elif op_type == 'format_call':
            confidence = min(confidence + 0.03, 1.0)

        # Ensure confidence stays in valid range
        return max(0.0, min(1.0, confidence))
