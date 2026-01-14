"""
LLM05: Supply Chain Vulnerabilities Detector

Detects risks in the AI/ML supply chain:
- Unpinned model dependencies
- Untrusted model sources
- Missing model verification
- Vulnerable ML libraries
- Unsigned model downloads
"""

import logging
import re
from typing import Dict, List, Any

from ai_security.static_detectors.base_detector import BaseDetector
from ai_security.models.finding import Finding, Severity

logger = logging.getLogger(__name__)


class SupplyChainDetector(BaseDetector):
    """
    Detect LLM05: Supply Chain Vulnerabilities

    Detects:
    - Unpinned model versions (model="gpt-4" without version)
    - Untrusted model sources (arbitrary URLs, local paths)
    - Missing model verification (no checksums, signatures)
    - Vulnerable ML library versions
    - Direct model downloads without validation
    """

    detector_id = "LLM05"
    name = "Supply Chain Vulnerabilities"
    default_confidence_threshold = 0.6

    # Model loading patterns
    MODEL_LOADING_PATTERNS = {
        'huggingface': ['from_pretrained', 'AutoModel', 'AutoTokenizer', 'pipeline'],
        'openai': ['openai.', 'ChatOpenAI', 'OpenAI('],
        'anthropic': ['anthropic.', 'ChatAnthropic', 'Anthropic('],
        'langchain': ['ChatOpenAI', 'ChatAnthropic', 'HuggingFacePipeline'],
        'tensorflow': ['tf.keras.models.load_model', 'load_model'],
        'pytorch': ['torch.load', 'torch.hub.load'],
        'custom': ['load(', 'download(', 'fetch_model']
    }

    # Trusted model repositories
    TRUSTED_SOURCES = {
        'huggingface.co', 'huggingface-models', 'openai.com', 'anthropic.com',
        'tensorflow.org', 'pytorch.org', 'registry.hub.docker.com'
    }

    # Verification patterns (positive indicators)
    VERIFICATION_PATTERNS = {
        'checksum': ['sha256', 'md5sum', 'hashlib', 'verify_checksum', 'check_hash'],
        'signature': ['gpg', 'signature', 'verify_signature', 'signed'],
        'pinning': ['==', 'model_version', 'version=', '@', 'revision='],
        'sbom': ['sbom', 'bill_of_materials', 'dependencies.json']
    }

    # Risky patterns
    RISKY_PATTERNS = {
        'arbitrary_url': [r'https?://(?!(?:' + '|'.join(TRUSTED_SOURCES) + r'))'],
        'local_path': [r'[\'"](?:/|\.\.?/|~/).*?\.(?:bin|pt|h5|ckpt|safetensors)[\'"]'],
        'dynamic_model': ['model_name = request.', 'model_id = os.getenv', 'model = user_input']
    }

    def _gather_potential_findings(self, parsed_data: Dict[str, Any]) -> List[Finding]:
        """Find supply chain vulnerabilities"""
        findings = []

        imports = parsed_data.get('imports', [])
        llm_calls = parsed_data.get('llm_api_calls', [])
        assignments = parsed_data.get('assignments', [])
        source_lines = parsed_data.get('source_lines', [])
        file_path = parsed_data.get('file_path', 'unknown')

        # Check 1: Unpinned model versions
        findings.extend(
            self._check_unpinned_models(llm_calls, assignments, source_lines, file_path)
        )

        # Check 2: Untrusted model sources
        findings.extend(
            self._check_untrusted_sources(source_lines, file_path)
        )

        # Check 3: Missing verification
        findings.extend(
            self._check_missing_verification(llm_calls, source_lines, file_path)
        )

        # Check 4: Vulnerable libraries
        findings.extend(
            self._check_vulnerable_libraries(imports, file_path)
        )

        return findings

    def _check_unpinned_models(
        self,
        llm_calls: List[Dict[str, Any]],
        assignments: List[Dict[str, Any]],
        source_lines: List[str],
        file_path: str
    ) -> List[Finding]:
        """Check for unpinned model versions"""
        findings = []

        for llm_call in llm_calls:
            func_name = llm_call.get('function', '')
            line_num = llm_call.get('line', 0)
            keywords = llm_call.get('keywords', {})

            # Check if model is specified
            model_arg = keywords.get('model') or keywords.get('model_name')

            if model_arg and line_num > 0:
                # Check if version is pinned
                has_pinning = any(
                    pattern in model_arg
                    for pattern in self.VERIFICATION_PATTERNS['pinning']
                )

                if not has_pinning and self._is_model_identifier(model_arg):
                    evidence = {
                        'function': func_name,
                        'model_arg': model_arg,
                        'has_pinning': False,
                        'line': line_num
                    }

                    findings.append(Finding(
                        id=f"{self.detector_id}_{file_path}_{line_num}_unpinned",
                        category=f"{self.detector_id}: Supply Chain Vulnerabilities",
                        severity=Severity.MEDIUM,
                        confidence=self.calculate_confidence(evidence),
                        title="Unpinned model version in API call",
                        description=(
                            f"Model '{model_arg}' is used without version pinning on line {line_num}. "
                            f"Unpinned models can change unexpectedly, introducing breaking changes, "
                            f"security vulnerabilities, or behavioral shifts. Always pin to specific "
                            f"versions (e.g., 'gpt-4-0613' instead of 'gpt-4')."
                        ),
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=self._get_code_snippet(source_lines, line_num, 3),
                        recommendation=(
                            "Supply Chain Security Best Practices:\n"
                            "1. Pin model versions explicitly (model='gpt-4-0613')\n"
                            "2. Use model registries with version control\n"
                            "3. Document model versions in requirements.txt or similar\n"
                            "4. Implement model versioning in CI/CD pipelines\n"
                            "5. Test thoroughly before upgrading model versions\n"
                            "6. Monitor for model deprecation notices"
                        ),
                        evidence=evidence
                    ))

        return findings

    def _check_untrusted_sources(
        self,
        source_lines: List[str],
        file_path: str
    ) -> List[Finding]:
        """Check for untrusted model sources"""
        findings = []
        source_code = '\n'.join(source_lines)

        # Check for arbitrary URLs
        for pattern_name, patterns in self.RISKY_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, source_code, re.IGNORECASE)
                for match in matches:
                    line_num = source_code[:match.start()].count('\n') + 1
                    matched_text = match.group(0)

                    evidence = {
                        'pattern_type': pattern_name,
                        'matched_text': matched_text,
                        'line': line_num
                    }

                    if pattern_name == 'arbitrary_url':
                        severity = Severity.HIGH
                        description = (
                            f"Untrusted URL '{matched_text}' found on line {line_num}. "
                            f"Loading models from arbitrary URLs poses significant security risks "
                            f"including malicious model injection, backdoors, and data exfiltration."
                        )
                    elif pattern_name == 'local_path':
                        severity = Severity.MEDIUM
                        description = (
                            f"Local file path '{matched_text}' found on line {line_num}. "
                            f"Loading models from local paths without verification can introduce "
                            f"compromised models if the filesystem is not properly secured."
                        )
                    else:  # dynamic_model
                        severity = Severity.HIGH
                        description = (
                            f"Dynamic model selection from user input on line {line_num}. "
                            f"Allowing users to specify model names/paths enables attackers to "
                            f"load malicious models or bypass security controls."
                        )

                    findings.append(Finding(
                        id=f"{self.detector_id}_{file_path}_{line_num}_{pattern_name}",
                        category=f"{self.detector_id}: Supply Chain Vulnerabilities",
                        severity=severity,
                        confidence=self.calculate_confidence(evidence),
                        title=f"Untrusted model source: {pattern_name}",
                        description=description,
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=self._get_code_snippet(source_lines, line_num, 3),
                        recommendation=(
                            "Secure Model Loading:\n"
                            "1. Only load models from trusted registries (HuggingFace, official repos)\n"
                            "2. Verify model checksums/signatures before loading\n"
                            "3. Use allowlists for permitted models\n"
                            "4. Implement content scanning for downloaded models\n"
                            "5. Never allow user-controlled model paths\n"
                            "6. Use isolated environments for model loading\n"
                            "7. Maintain an SBOM (Software Bill of Materials) for AI components"
                        ),
                        evidence=evidence
                    ))

        return findings

    def _check_missing_verification(
        self,
        llm_calls: List[Dict[str, Any]],
        source_lines: List[str],
        file_path: str
    ) -> List[Finding]:
        """Check for model loading without verification"""
        findings = []
        source_code = ' '.join(source_lines).lower()

        # Check if any verification is present
        has_verification = any(
            any(pattern in source_code for pattern in patterns)
            for patterns in self.VERIFICATION_PATTERNS.values()
        )

        # Look for model loading without verification
        for llm_call in llm_calls:
            func_name = llm_call.get('function', '').lower()
            line_num = llm_call.get('line', 0)

            # Check if this is a model loading function
            is_model_loading = any(
                any(pattern.lower() in func_name for pattern in patterns)
                for patterns in self.MODEL_LOADING_PATTERNS.values()
            )

            if is_model_loading and not has_verification and line_num > 0:
                # Check nearby lines for verification (within 10 lines)
                nearby_verification = self._check_verification_nearby(
                    line_num, source_lines, window=10
                )

                if not nearby_verification:
                    evidence = {
                        'function': llm_call.get('function'),
                        'has_verification': False,
                        'line': line_num
                    }

                    findings.append(Finding(
                        id=f"{self.detector_id}_{file_path}_{line_num}_no_verification",
                        category=f"{self.detector_id}: Supply Chain Vulnerabilities",
                        severity=Severity.MEDIUM,
                        confidence=self.calculate_confidence(evidence),
                        title="Model loaded without integrity verification",
                        description=(
                            f"Model loading on line {line_num} lacks integrity verification. "
                            f"Without checksum or signature verification, compromised models "
                            f"could be loaded, leading to backdoors, data leaks, or adversarial behavior."
                        ),
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=self._get_code_snippet(source_lines, line_num, 3),
                        recommendation=(
                            "Model Verification:\n"
                            "1. Verify SHA256 checksums before loading models\n"
                            "2. Check GPG signatures for official models\n"
                            "3. Use model registries with built-in verification\n"
                            "4. Implement hash validation in deployment pipelines\n"
                            "5. Store expected hashes in version control\n"
                            "6. Fail fast if verification fails"
                        ),
                        evidence=evidence
                    ))
                    break  # Only report once per file

        return findings

    def _check_vulnerable_libraries(
        self,
        imports: List[Dict[str, Any]],
        file_path: str
    ) -> List[Finding]:
        """Check for known vulnerable ML libraries (basic check)"""
        findings = []

        # Known vulnerable patterns (this would ideally use CVE database)
        vulnerable_imports = {
            'pickle': 'HIGH',  # Arbitrary code execution risk
            'joblib': 'MEDIUM',  # Can execute arbitrary code
            'dill': 'MEDIUM'  # Extended pickle with same risks
        }

        for imp in imports:
            module = imp.get('module', '')
            line_num = imp.get('line', 0)

            for vuln_module, severity in vulnerable_imports.items():
                if vuln_module in module.lower():
                    evidence = {
                        'module': module,
                        'vulnerability': 'arbitrary_code_execution',
                        'line': line_num
                    }

                    findings.append(Finding(
                        id=f"{self.detector_id}_{file_path}_{line_num}_{vuln_module}",
                        category=f"{self.detector_id}: Supply Chain Vulnerabilities",
                        severity=Severity[severity],
                        confidence=self.calculate_confidence(evidence),
                        title=f"Use of {vuln_module} for model serialization",
                        description=(
                            f"Import of '{module}' on line {line_num} for model serialization. "
                            f"This library can execute arbitrary code during deserialization, "
                            f"making it vulnerable to supply chain attacks if loading untrusted models."
                        ),
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=f"import {module}",
                        recommendation=(
                            "Secure Serialization:\n"
                            "1. Use safer alternatives like safetensors for PyTorch/TensorFlow\n"
                            "2. Never deserialize models from untrusted sources\n"
                            "3. Scan serialized models before loading\n"
                            "4. Use sandboxed environments for model loading\n"
                            "5. Implement allowlists for model formats\n"
                            "6. Consider using ONNX for model exchange"
                        ),
                        evidence=evidence
                    ))

        return findings

    def calculate_confidence(self, evidence: Dict[str, Any]) -> float:
        """
        Calculate confidence based on evidence

        High confidence (0.8-1.0):
        - Direct pattern match (URLs, local paths)
        - Explicit unpinned versions

        Medium confidence (0.6-0.8):
        - Missing verification (could be elsewhere)
        - Vulnerable library usage

        Low confidence (0.4-0.6):
        - Heuristic-based detection
        """
        confidence = 0.7  # Base confidence

        # High confidence for direct matches
        if evidence.get('pattern_type') in ['arbitrary_url', 'dynamic_model']:
            confidence = 0.9

        # Medium-high for unpinned models
        if evidence.get('has_pinning') is False:
            confidence = 0.75

        # Medium for missing verification
        if evidence.get('has_verification') is False:
            confidence = 0.65

        # High for vulnerable libraries
        if evidence.get('vulnerability'):
            confidence = 0.85

        return min(confidence, 1.0)

    def _is_model_identifier(self, model_arg: str) -> bool:
        """Check if argument looks like a model identifier"""
        # Simple heuristic: contains model names or patterns
        model_patterns = ['gpt', 'claude', 'llama', 'bert', 'model']
        return any(pattern in model_arg.lower() for pattern in model_patterns)

    def _check_verification_nearby(
        self,
        line_num: int,
        source_lines: List[str],
        window: int = 10
    ) -> bool:
        """Check if verification patterns exist within a window of lines"""
        start = max(0, line_num - window)
        end = min(len(source_lines), line_num + window)

        nearby_code = ' '.join(source_lines[start:end]).lower()

        return any(
            any(pattern in nearby_code for pattern in patterns)
            for patterns in self.VERIFICATION_PATTERNS.values()
        )

    def _get_code_snippet(
        self,
        source_lines: List[str],
        line_num: int,
        context: int = 3
    ) -> str:
        """Get code snippet with context"""
        start = max(0, line_num - context)
        end = min(len(source_lines), line_num + context)
        return '\n'.join(source_lines[start:end])
