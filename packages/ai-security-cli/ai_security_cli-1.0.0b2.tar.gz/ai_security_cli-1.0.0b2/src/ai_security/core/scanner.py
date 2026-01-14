"""
Static Code Scanner - Orchestrates parsing, detection, and scoring
"""

import os
import re
import time
import shutil
import logging
import tempfile
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse

from ai_security.parsers.python.ast_parser import PythonASTParser
from ai_security.static_detectors import (
    PromptInjectionDetector,
    InsecureOutputDetector,
    TrainingPoisoningDetector,
    ModelDOSDetector,
    SupplyChainDetector,
    SecretsDetector,
    InsecurePluginDetector,
    ExcessiveAgencyDetector,
    OverrelianceDetector,
    ModelTheftDetector,
)
from ai_security.scorers.prompt_security_scorer import PromptSecurityScorer
from ai_security.scorers.model_security_scorer import ModelSecurityScorer
from ai_security.scorers.data_privacy_scorer import DataPrivacyScorer
from ai_security.scorers.hallucination_scorer import HallucinationScorer
from ai_security.scorers.ethical_ai_scorer import EthicalAIScorer
from ai_security.scorers.governance_scorer import GovernanceScorer
from ai_security.scorers.owasp_scorer import OWASPScorer
from ai_security.models.finding import Finding, Severity
from ai_security.models.result import ScanResult, CategoryScore
from ai_security.utils.scoring import calculate_overall_score, get_severity_counts

logger = logging.getLogger(__name__)


# Patterns for detecting remote Git URLs
GIT_URL_PATTERNS = [
    r'^https?://github\.com/[\w\-\.]+/[\w\-\.]+',
    r'^https?://gitlab\.com/[\w\-\.]+/[\w\-\.]+',
    r'^https?://bitbucket\.org/[\w\-\.]+/[\w\-\.]+',
    r'^git@github\.com:[\w\-\.]+/[\w\-\.]+',
    r'^git@gitlab\.com:[\w\-\.]+/[\w\-\.]+',
    r'^git@bitbucket\.org:[\w\-\.]+/[\w\-\.]+',
    r'^https?://.*\.git$',
]


def is_remote_url(path: str) -> bool:
    """Check if a path is a remote Git URL."""
    for pattern in GIT_URL_PATTERNS:
        if re.match(pattern, path, re.IGNORECASE):
            return True
    return False


def normalize_git_url(url: str) -> str:
    """Normalize a Git URL to be clonable."""
    # Remove trailing slashes
    url = url.rstrip('/')

    # Handle GitHub URLs that don't end in .git
    if 'github.com' in url or 'gitlab.com' in url or 'bitbucket.org' in url:
        # Remove /tree/branch or /blob/branch suffixes
        url = re.sub(r'/(tree|blob)/[^/]+.*$', '', url)
        # Add .git if not present
        if not url.endswith('.git'):
            url = url + '.git'

    return url


def clone_repository(url: str, depth: int = 1) -> Tuple[str, bool]:
    """
    Clone a remote Git repository to a temporary directory.

    Args:
        url: Git repository URL
        depth: Clone depth (1 for shallow clone)

    Returns:
        Tuple of (temp_dir_path, success)
    """
    temp_dir = tempfile.mkdtemp(prefix="ai-security-scan-")

    try:
        normalized_url = normalize_git_url(url)
        logger.info(f"Cloning repository: {normalized_url}")

        # Run git clone
        result = subprocess.run(
            ["git", "clone", "--depth", str(depth), normalized_url, temp_dir],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        if result.returncode != 0:
            logger.error(f"Git clone failed: {result.stderr}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return "", False

        logger.info(f"Successfully cloned to: {temp_dir}")
        return temp_dir, True

    except subprocess.TimeoutExpired:
        logger.error("Git clone timed out")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return "", False
    except FileNotFoundError:
        logger.error("Git is not installed or not in PATH")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return "", False
    except Exception as e:
        logger.error(f"Error cloning repository: {e}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return "", False


class StaticScanner:
    """
    Static code scanner for OWASP LLM Top 10 vulnerabilities.

    Architecture:
    1. Parse: Extract code structure from files (AST)
    2. Detect: Find OWASP vulnerabilities (per-file findings)
    3. Score: Calculate framework security posture (aggregated)
    4. Report: Generate results matching schema
    """

    def __init__(
        self,
        verbose: bool = False,
        confidence_threshold: float = 0.7,
        categories: Optional[List[str]] = None,
    ):
        """
        Initialize scanner.

        Args:
            verbose: Enable verbose logging
            confidence_threshold: Minimum confidence for findings (0.0-1.0)
            categories: Filter to specific OWASP categories (e.g., ["LLM01", "LLM02"])
        """
        self.verbose = verbose
        self.confidence_threshold = confidence_threshold
        self.filter_categories = categories

        # Initialize detectors (10 OWASP LLM detectors)
        self.detectors = [
            PromptInjectionDetector(verbose=verbose, confidence_threshold=confidence_threshold),
            InsecureOutputDetector(verbose=verbose, confidence_threshold=confidence_threshold),
            TrainingPoisoningDetector(verbose=verbose, confidence_threshold=confidence_threshold),
            ModelDOSDetector(verbose=verbose, confidence_threshold=confidence_threshold),
            SupplyChainDetector(verbose=verbose, confidence_threshold=confidence_threshold),
            SecretsDetector(verbose=verbose, confidence_threshold=confidence_threshold),
            InsecurePluginDetector(verbose=verbose, confidence_threshold=confidence_threshold),
            ExcessiveAgencyDetector(verbose=verbose, confidence_threshold=confidence_threshold),
            OverrelianceDetector(verbose=verbose, confidence_threshold=confidence_threshold),
            ModelTheftDetector(verbose=verbose, confidence_threshold=confidence_threshold),
        ]

        # Filter detectors by category if specified
        if self.filter_categories:
            self.detectors = [
                d for d in self.detectors
                if d.detector_id in self.filter_categories
            ]

        # Initialize scorers (6 framework categories)
        self.scorers = [
            PromptSecurityScorer(verbose=verbose),
            ModelSecurityScorer(verbose=verbose),
            DataPrivacyScorer(verbose=verbose),
            HallucinationScorer(verbose=verbose),
            EthicalAIScorer(verbose=verbose),
            GovernanceScorer(verbose=verbose),
        ]

        # OWASP scorer (needs findings)
        self.owasp_scorer = OWASPScorer(verbose=verbose)

    def scan(self, path: str) -> ScanResult:
        """
        Scan a file, directory, or remote Git URL for security issues.

        Args:
            path: Path to file/directory or Git URL (GitHub/GitLab/Bitbucket)

        Returns:
            ScanResult with all findings and scores
        """
        # Check if path is a remote Git URL
        if is_remote_url(path):
            return self._scan_remote(path)

        target_path = Path(path).resolve()

        if target_path.is_file():
            return self._scan_file(target_path)
        elif target_path.is_dir():
            return self._scan_directory(target_path)
        else:
            raise FileNotFoundError(f"Path not found: {path}")

    def _scan_remote(self, url: str) -> ScanResult:
        """
        Scan a remote Git repository.

        Args:
            url: Git repository URL

        Returns:
            ScanResult with findings
        """
        logger.info(f"Scanning remote repository: {url}")

        # Clone the repository
        temp_dir, success = clone_repository(url)

        if not success:
            raise RuntimeError(f"Failed to clone repository: {url}")

        try:
            # Scan the cloned repository
            result = self._scan_directory(Path(temp_dir))

            # Update the target path to show the original URL
            result.target_path = url
            result.metadata = result.metadata or {}
            result.metadata["source"] = "remote"
            result.metadata["cloned_to"] = temp_dir

            return result
        finally:
            # Clean up the temporary directory
            logger.info(f"Cleaning up temporary directory: {temp_dir}")
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _scan_file(self, file_path: Path) -> ScanResult:
        """Scan a single file."""
        start_time = time.time()

        if file_path.suffix != ".py":
            logger.warning(f"Skipping non-Python file: {file_path}")
            return ScanResult(
                target_path=str(file_path),
                files_scanned=0,
                duration_seconds=time.time() - start_time,
            )

        # Parse file
        parser = PythonASTParser(str(file_path))
        parsed_data = parser.parse()

        if not parsed_data.get("parsable", False):
            logger.warning(f"Could not parse file: {file_path}")
            return ScanResult(
                target_path=str(file_path),
                files_scanned=1,
                duration_seconds=time.time() - start_time,
                metadata={"parse_error": True},
            )

        # Run detectors
        all_findings = []
        for detector in self.detectors:
            findings = detector.detect(parsed_data)
            all_findings.extend(findings)

        # Run scorers
        category_scores = self._run_scorers(parsed_data, all_findings)

        # Calculate overall score
        overall_score = calculate_overall_score(
            findings=all_findings,
            category_scores=list(category_scores.values()),
        )

        duration = time.time() - start_time

        return ScanResult(
            target_path=str(file_path),
            findings=all_findings,
            category_scores=category_scores,
            overall_score=overall_score,
            confidence=self._calculate_scan_confidence(all_findings, category_scores),
            files_scanned=1,
            duration_seconds=duration,
        )

    def _scan_directory(self, directory: Path) -> ScanResult:
        """Scan all Python files in a directory."""
        start_time = time.time()

        # Find all Python files
        python_files = list(directory.rglob("*.py"))

        if not python_files:
            logger.warning(f"No Python files found in {directory}")
            return ScanResult(
                target_path=str(directory),
                files_scanned=0,
                duration_seconds=time.time() - start_time,
            )

        # Parse all files
        all_parsed_data = []
        all_findings = []

        for file_path in python_files:
            # Skip test files and __pycache__
            if "__pycache__" in str(file_path) or "test_" in file_path.name:
                continue

            try:
                parser = PythonASTParser(str(file_path))
                parsed_data = parser.parse()

                if parsed_data.get("parsable", False):
                    all_parsed_data.append(parsed_data)

                    # Run detectors on each file
                    for detector in self.detectors:
                        findings = detector.detect(parsed_data)
                        all_findings.extend(findings)

            except Exception as e:
                logger.warning(f"Error scanning {file_path}: {e}")

        # Aggregate parsed data for scoring
        aggregated_data = self._aggregate_parsed_data(all_parsed_data)

        # Run scorers on aggregated data
        category_scores = self._run_scorers(aggregated_data, all_findings)

        # Calculate overall score
        overall_score = calculate_overall_score(
            findings=all_findings,
            category_scores=list(category_scores.values()),
        )

        duration = time.time() - start_time

        return ScanResult(
            target_path=str(directory),
            findings=all_findings,
            category_scores=category_scores,
            overall_score=overall_score,
            confidence=self._calculate_scan_confidence(all_findings, category_scores),
            files_scanned=len(all_parsed_data),
            duration_seconds=duration,
        )

    def _aggregate_parsed_data(self, parsed_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate parsed data from multiple files."""
        if not parsed_data_list:
            return {}

        aggregated = {
            "file_path": "project",
            "parsable": True,
            "imports": [],
            "functions": [],
            "classes": [],
            "assignments": [],
            "string_operations": [],
            "llm_api_calls": [],
            "source_lines": [],
        }

        for parsed_data in parsed_data_list:
            aggregated["imports"].extend(parsed_data.get("imports", []))
            aggregated["functions"].extend(parsed_data.get("functions", []))
            aggregated["classes"].extend(parsed_data.get("classes", []))
            aggregated["assignments"].extend(parsed_data.get("assignments", []))
            aggregated["string_operations"].extend(parsed_data.get("string_operations", []))
            aggregated["llm_api_calls"].extend(parsed_data.get("llm_api_calls", []))
            aggregated["source_lines"].extend(parsed_data.get("source_lines", []))

        return aggregated

    def _run_scorers(
        self, parsed_data: Dict[str, Any], findings: List[Finding]
    ) -> Dict[str, CategoryScore]:
        """Run all scorers and return category scores."""
        category_scores = {}

        # Run framework scorers
        for scorer in self.scorers:
            try:
                score = scorer.calculate_score(parsed_data)
                category_scores[score.category_id] = score
            except Exception as e:
                logger.warning(f"Scorer {scorer.__class__.__name__} failed: {e}")

        # Run OWASP scorer
        try:
            self.owasp_scorer.set_findings(findings)
            owasp_score = self.owasp_scorer.calculate_score(parsed_data)
            category_scores[owasp_score.category_id] = owasp_score
        except Exception as e:
            logger.warning(f"OWASP scorer failed: {e}")

        return category_scores

    def _calculate_scan_confidence(
        self, findings: List[Finding], category_scores: Dict[str, CategoryScore]
    ) -> float:
        """Calculate overall scan confidence."""
        # Average confidence from findings
        if findings:
            finding_confidence = sum(f.confidence for f in findings) / len(findings)
        else:
            finding_confidence = 0.8  # Default when no findings

        # Average confidence from scorers
        if category_scores:
            scorer_confidence = sum(
                s.confidence for s in category_scores.values()
            ) / len(category_scores)
        else:
            scorer_confidence = 0.5

        # Combined confidence
        return (finding_confidence * 0.4 + scorer_confidence * 0.6)
