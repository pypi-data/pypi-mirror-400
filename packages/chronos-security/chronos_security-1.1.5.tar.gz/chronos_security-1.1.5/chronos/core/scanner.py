"""
CHRONOS File Scanner
====================

Real file scanning and analysis service.
Scans files for security patterns, cryptographic usage, and threats.
"""

import ast
import hashlib
import re
import os
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Set, Any, Generator
import mimetypes

from chronos.utils.logging import get_logger

logger = get_logger(__name__)


class SeverityLevel(str, Enum):
    """Severity levels for findings."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingType(str, Enum):
    """Types of security findings."""
    WEAK_CRYPTO = "weak_crypto"
    HARDCODED_SECRET = "hardcoded_secret"
    INSECURE_RANDOM = "insecure_random"
    SQL_INJECTION = "sql_injection"
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    DEPRECATED_FUNCTION = "deprecated_function"
    QUANTUM_VULNERABLE = "quantum_vulnerable"
    UNSAFE_DESERIALIZATION = "unsafe_deserialization"
    SENSITIVE_DATA_EXPOSURE = "sensitive_data_exposure"
    DEBUG_CODE = "debug_code"


@dataclass
class ScanFinding:
    """Represents a security finding from a scan."""
    finding_type: FindingType
    severity: SeverityLevel
    file_path: str
    line_number: int
    column: int
    message: str
    code_snippet: str
    recommendation: str
    cwe_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.finding_type.value,
            "severity": self.severity.value,
            "file": self.file_path,
            "line": self.line_number,
            "column": self.column,
            "message": self.message,
            "code": self.code_snippet,
            "recommendation": self.recommendation,
            "cwe": self.cwe_id,
        }


@dataclass
class ScanResult:
    """Complete scan result."""
    target: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    files_scanned: int = 0
    files_skipped: int = 0
    findings: List[ScanFinding] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    @property
    def duration_seconds(self) -> float:
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return 0.0
    
    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == SeverityLevel.CRITICAL)
    
    @property
    def high_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == SeverityLevel.HIGH)
    
    @property
    def medium_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == SeverityLevel.MEDIUM)
    
    @property
    def low_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == SeverityLevel.LOW)


# Security patterns to detect
CRYPTO_PATTERNS = {
    # Weak hash algorithms
    r'\bmd5\b': {
        "type": FindingType.WEAK_CRYPTO,
        "severity": SeverityLevel.HIGH,
        "message": "MD5 hash detected - cryptographically broken",
        "recommendation": "Use SHA-256 or SHA-3 instead",
        "cwe": "CWE-328",
    },
    r'\bsha1\b': {
        "type": FindingType.WEAK_CRYPTO,
        "severity": SeverityLevel.HIGH,
        "message": "SHA-1 hash detected - vulnerable to collision attacks",
        "recommendation": "Use SHA-256 or SHA-3 instead",
        "cwe": "CWE-328",
    },
    # Weak encryption
    r'\bdes\b': {
        "type": FindingType.WEAK_CRYPTO,
        "severity": SeverityLevel.CRITICAL,
        "message": "DES encryption detected - easily breakable",
        "recommendation": "Use AES-256 or ChaCha20 instead",
        "cwe": "CWE-327",
    },
    r'\brc4\b': {
        "type": FindingType.WEAK_CRYPTO,
        "severity": SeverityLevel.CRITICAL,
        "message": "RC4 encryption detected - known vulnerabilities",
        "recommendation": "Use AES-256 or ChaCha20 instead",
        "cwe": "CWE-327",
    },
    r'\bblowfish\b': {
        "type": FindingType.WEAK_CRYPTO,
        "severity": SeverityLevel.MEDIUM,
        "message": "Blowfish encryption detected - limited block size",
        "recommendation": "Consider using AES-256 for better security",
        "cwe": "CWE-327",
    },
    # Quantum vulnerable algorithms
    r'\brsa\b': {
        "type": FindingType.QUANTUM_VULNERABLE,
        "severity": SeverityLevel.MEDIUM,
        "message": "RSA detected - vulnerable to quantum attacks (Shor's algorithm)",
        "recommendation": "Plan migration to post-quantum cryptography (CRYSTALS-Kyber, CRYSTALS-Dilithium)",
        "cwe": "CWE-327",
    },
    r'\becdsa\b|\becc\b|\belliptic[\s_]?curve\b': {
        "type": FindingType.QUANTUM_VULNERABLE,
        "severity": SeverityLevel.MEDIUM,
        "message": "Elliptic curve cryptography detected - vulnerable to quantum attacks",
        "recommendation": "Plan migration to post-quantum cryptography",
        "cwe": "CWE-327",
    },
    r'\bdiffie[\s_-]?hellman\b|\bdh[\s_]?key\b': {
        "type": FindingType.QUANTUM_VULNERABLE,
        "severity": SeverityLevel.MEDIUM,
        "message": "Diffie-Hellman key exchange detected - vulnerable to quantum attacks",
        "recommendation": "Consider hybrid key exchange with post-quantum algorithms",
        "cwe": "CWE-327",
    },
}

SECRET_PATTERNS = {
    # API Keys
    r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']([a-zA-Z0-9_\-]{20,})["\']': {
        "type": FindingType.HARDCODED_SECRET,
        "severity": SeverityLevel.CRITICAL,
        "message": "Hardcoded API key detected",
        "recommendation": "Use environment variables or a secret manager",
        "cwe": "CWE-798",
    },
    # Passwords
    r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']([^"\']{4,})["\']': {
        "type": FindingType.HARDCODED_SECRET,
        "severity": SeverityLevel.CRITICAL,
        "message": "Hardcoded password detected",
        "recommendation": "Use environment variables or a secret manager",
        "cwe": "CWE-798",
    },
    # AWS Keys
    r'(?i)AKIA[0-9A-Z]{16}': {
        "type": FindingType.HARDCODED_SECRET,
        "severity": SeverityLevel.CRITICAL,
        "message": "AWS Access Key ID detected",
        "recommendation": "Rotate the key immediately and use IAM roles",
        "cwe": "CWE-798",
    },
    # Private Keys
    r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----': {
        "type": FindingType.HARDCODED_SECRET,
        "severity": SeverityLevel.CRITICAL,
        "message": "Private key embedded in code",
        "recommendation": "Store private keys securely outside of code",
        "cwe": "CWE-321",
    },
    # JWT Secrets
    r'(?i)(jwt[_-]?secret|secret[_-]?key)\s*[=:]\s*["\']([a-zA-Z0-9_\-]{16,})["\']': {
        "type": FindingType.HARDCODED_SECRET,
        "severity": SeverityLevel.HIGH,
        "message": "Hardcoded JWT secret detected",
        "recommendation": "Use environment variables or a secret manager",
        "cwe": "CWE-798",
    },
}

VULNERABILITY_PATTERNS = {
    # SQL Injection
    r'(?i)(execute|cursor\.execute)\s*\([^)]*["\'].*%s.*["\']\s*%': {
        "type": FindingType.SQL_INJECTION,
        "severity": SeverityLevel.HIGH,
        "message": "Potential SQL injection via string formatting",
        "recommendation": "Use parameterized queries",
        "cwe": "CWE-89",
    },
    r'(?i)f["\'].*SELECT.*{.*}': {
        "type": FindingType.SQL_INJECTION,
        "severity": SeverityLevel.HIGH,
        "message": "Potential SQL injection via f-string",
        "recommendation": "Use parameterized queries",
        "cwe": "CWE-89",
    },
    # Command Injection
    r'(?i)(os\.system|subprocess\.call|subprocess\.run|subprocess\.Popen)\s*\([^)]*\+': {
        "type": FindingType.COMMAND_INJECTION,
        "severity": SeverityLevel.CRITICAL,
        "message": "Potential command injection via string concatenation",
        "recommendation": "Use subprocess with shell=False and pass arguments as list",
        "cwe": "CWE-78",
    },
    r'(?i)eval\s*\(': {
        "type": FindingType.COMMAND_INJECTION,
        "severity": SeverityLevel.HIGH,
        "message": "Use of eval() detected - potential code injection",
        "recommendation": "Avoid eval() - use safer alternatives like ast.literal_eval()",
        "cwe": "CWE-94",
    },
    r'(?i)exec\s*\(': {
        "type": FindingType.COMMAND_INJECTION,
        "severity": SeverityLevel.HIGH,
        "message": "Use of exec() detected - potential code injection",
        "recommendation": "Avoid exec() with user input",
        "cwe": "CWE-94",
    },
    # Path Traversal
    r'(?i)open\s*\([^)]*\+[^)]*\)': {
        "type": FindingType.PATH_TRAVERSAL,
        "severity": SeverityLevel.MEDIUM,
        "message": "Potential path traversal via string concatenation in file open",
        "recommendation": "Validate and sanitize file paths before use",
        "cwe": "CWE-22",
    },
    # Insecure Random
    r'(?i)\brandom\.(random|randint|choice|shuffle)\b': {
        "type": FindingType.INSECURE_RANDOM,
        "severity": SeverityLevel.MEDIUM,
        "message": "Non-cryptographic random number generator used",
        "recommendation": "Use secrets module for security-sensitive operations",
        "cwe": "CWE-330",
    },
    # Unsafe Deserialization
    r'(?i)(pickle\.loads?|yaml\.load|yaml\.unsafe_load)\s*\(': {
        "type": FindingType.UNSAFE_DESERIALIZATION,
        "severity": SeverityLevel.HIGH,
        "message": "Unsafe deserialization detected",
        "recommendation": "Use safe loaders (yaml.safe_load) or avoid deserializing untrusted data",
        "cwe": "CWE-502",
    },
    # Debug code
    r'(?i)(print\s*\(.*password|print\s*\(.*secret|print\s*\(.*key)': {
        "type": FindingType.DEBUG_CODE,
        "severity": SeverityLevel.MEDIUM,
        "message": "Potential sensitive data in debug output",
        "recommendation": "Remove debug statements that may leak sensitive data",
        "cwe": "CWE-200",
    },
}


class FileScanner:
    """
    Scans files for security issues, cryptographic patterns, and vulnerabilities.
    
    This is a real working scanner that:
    - Parses Python files using AST for accurate analysis
    - Uses regex patterns for text-based detection
    - Identifies cryptographic usage and weaknesses
    - Detects hardcoded secrets
    - Finds common vulnerability patterns
    """
    
    # File extensions to scan
    SCANNABLE_EXTENSIONS = {
        ".py", ".pyw",  # Python
        ".js", ".jsx", ".ts", ".tsx",  # JavaScript/TypeScript
        ".java",  # Java
        ".c", ".cpp", ".h", ".hpp",  # C/C++
        ".cs",  # C#
        ".go",  # Go
        ".rb",  # Ruby
        ".php",  # PHP
        ".sh", ".bash",  # Shell
        ".yml", ".yaml",  # YAML configs
        ".json",  # JSON configs
        ".xml",  # XML configs
        ".env",  # Environment files
        ".ini", ".cfg", ".conf",  # Config files
    }
    
    # Directories to skip
    SKIP_DIRS = {
        "__pycache__",
        ".git",
        ".svn",
        ".hg",
        "node_modules",
        "venv",
        ".venv",
        "env",
        ".env",
        "build",
        "dist",
        ".tox",
        ".pytest_cache",
        ".mypy_cache",
        "eggs",
        ".eggs",
    }
    
    def __init__(
        self,
        include_patterns: Optional[Set[str]] = None,
        exclude_patterns: Optional[Set[str]] = None,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB default
    ):
        """
        Initialize the file scanner.
        
        Args:
            include_patterns: Glob patterns to include
            exclude_patterns: Glob patterns to exclude
            max_file_size: Maximum file size to scan in bytes
        """
        self.include_patterns = include_patterns or set()
        self.exclude_patterns = exclude_patterns or set()
        self.max_file_size = max_file_size
        
        # Compile regex patterns
        self._crypto_patterns = {
            re.compile(pattern, re.IGNORECASE): info
            for pattern, info in CRYPTO_PATTERNS.items()
        }
        self._secret_patterns = {
            re.compile(pattern): info
            for pattern, info in SECRET_PATTERNS.items()
        }
        self._vuln_patterns = {
            re.compile(pattern): info
            for pattern, info in VULNERABILITY_PATTERNS.items()
        }
    
    def scan(
        self,
        target: Path,
        recursive: bool = True,
        quantum_check: bool = True,
    ) -> ScanResult:
        """
        Scan a file or directory for security issues.
        
        Args:
            target: Path to file or directory
            recursive: Scan directories recursively
            quantum_check: Include quantum vulnerability checks
        
        Returns:
            ScanResult with all findings
        """
        result = ScanResult(
            target=str(target.absolute()),
            started_at=datetime.now(),
        )
        
        try:
            if target.is_file():
                self._scan_file(target, result, quantum_check)
            elif target.is_dir():
                for file_path in self._iter_files(target, recursive):
                    self._scan_file(file_path, result, quantum_check)
            else:
                result.errors.append(f"Target not found: {target}")
        except Exception as e:
            logger.error(f"Scan error: {e}")
            result.errors.append(str(e))
        
        result.completed_at = datetime.now()
        return result
    
    def _iter_files(
        self,
        directory: Path,
        recursive: bool,
    ) -> Generator[Path, None, None]:
        """Iterate over scannable files in a directory."""
        try:
            for entry in directory.iterdir():
                if entry.is_dir():
                    if entry.name in self.SKIP_DIRS:
                        continue
                    if recursive:
                        yield from self._iter_files(entry, recursive)
                elif entry.is_file():
                    if self._should_scan_file(entry):
                        yield entry
        except PermissionError:
            logger.warning(f"Permission denied: {directory}")
    
    def _should_scan_file(self, file_path: Path) -> bool:
        """Check if a file should be scanned."""
        # Check extension
        if file_path.suffix.lower() not in self.SCANNABLE_EXTENSIONS:
            # Also check files without extension that might be scripts
            if file_path.suffix:
                return False
        
        # Check file size
        try:
            if file_path.stat().st_size > self.max_file_size:
                return False
        except OSError:
            return False
        
        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if file_path.match(pattern):
                return False
        
        return True
    
    def _scan_file(
        self,
        file_path: Path,
        result: ScanResult,
        quantum_check: bool,
    ) -> None:
        """Scan a single file for security issues."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")
            result.files_scanned += 1
            
            # Run pattern-based scanning
            self._scan_patterns(file_path, content, lines, result, quantum_check)
            
            # For Python files, also do AST analysis
            if file_path.suffix in (".py", ".pyw"):
                self._scan_python_ast(file_path, content, result)
                
        except Exception as e:
            logger.debug(f"Error scanning {file_path}: {e}")
            result.files_skipped += 1
    
    def _scan_patterns(
        self,
        file_path: Path,
        content: str,
        lines: List[str],
        result: ScanResult,
        quantum_check: bool,
    ) -> None:
        """Scan content using regex patterns."""
        file_str = str(file_path)
        
        # Scan for secrets
        for pattern, info in self._secret_patterns.items():
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count("\n") + 1
                col = match.start() - content.rfind("\n", 0, match.start())
                code_line = lines[line_num - 1] if line_num <= len(lines) else ""
                
                result.findings.append(ScanFinding(
                    finding_type=info["type"],
                    severity=info["severity"],
                    file_path=file_str,
                    line_number=line_num,
                    column=col,
                    message=info["message"],
                    code_snippet=code_line.strip()[:100],
                    recommendation=info["recommendation"],
                    cwe_id=info.get("cwe"),
                ))
        
        # Scan for crypto issues
        for pattern, info in self._crypto_patterns.items():
            # Skip quantum checks if not enabled
            if not quantum_check and info["type"] == FindingType.QUANTUM_VULNERABLE:
                continue
                
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count("\n") + 1
                col = match.start() - content.rfind("\n", 0, match.start())
                code_line = lines[line_num - 1] if line_num <= len(lines) else ""
                
                result.findings.append(ScanFinding(
                    finding_type=info["type"],
                    severity=info["severity"],
                    file_path=file_str,
                    line_number=line_num,
                    column=col,
                    message=info["message"],
                    code_snippet=code_line.strip()[:100],
                    recommendation=info["recommendation"],
                    cwe_id=info.get("cwe"),
                ))
        
        # Scan for vulnerabilities
        for pattern, info in self._vuln_patterns.items():
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count("\n") + 1
                col = match.start() - content.rfind("\n", 0, match.start())
                code_line = lines[line_num - 1] if line_num <= len(lines) else ""
                
                result.findings.append(ScanFinding(
                    finding_type=info["type"],
                    severity=info["severity"],
                    file_path=file_str,
                    line_number=line_num,
                    column=col,
                    message=info["message"],
                    code_snippet=code_line.strip()[:100],
                    recommendation=info["recommendation"],
                    cwe_id=info.get("cwe"),
                ))
    
    def _scan_python_ast(
        self,
        file_path: Path,
        content: str,
        result: ScanResult,
    ) -> None:
        """Perform AST-based analysis for Python files."""
        try:
            tree = ast.parse(content, filename=str(file_path))
            visitor = SecurityASTVisitor(str(file_path), result)
            visitor.visit(tree)
        except SyntaxError:
            # File has syntax errors, skip AST analysis
            pass


class SecurityASTVisitor(ast.NodeVisitor):
    """AST visitor for security analysis of Python code."""
    
    DANGEROUS_FUNCTIONS = {
        "eval": ("eval() can execute arbitrary code", SeverityLevel.HIGH),
        "exec": ("exec() can execute arbitrary code", SeverityLevel.HIGH),
        "compile": ("compile() with untrusted input is dangerous", SeverityLevel.MEDIUM),
        "__import__": ("Dynamic imports can be dangerous", SeverityLevel.LOW),
    }
    
    DANGEROUS_MODULES = {
        "pickle": ("pickle can execute arbitrary code during deserialization", SeverityLevel.HIGH),
        "marshal": ("marshal can execute arbitrary code", SeverityLevel.HIGH),
        "shelve": ("shelve uses pickle internally", SeverityLevel.HIGH),
    }
    
    def __init__(self, file_path: str, result: ScanResult):
        self.file_path = file_path
        self.result = result
    
    def visit_Call(self, node: ast.Call) -> None:
        """Check for dangerous function calls."""
        func_name = self._get_call_name(node)
        
        if func_name in self.DANGEROUS_FUNCTIONS:
            msg, severity = self.DANGEROUS_FUNCTIONS[func_name]
            self.result.findings.append(ScanFinding(
                finding_type=FindingType.COMMAND_INJECTION,
                severity=severity,
                file_path=self.file_path,
                line_number=node.lineno,
                column=node.col_offset,
                message=msg,
                code_snippet=f"{func_name}(...)",
                recommendation=f"Avoid using {func_name}() with untrusted input",
                cwe_id="CWE-94",
            ))
        
        self.generic_visit(node)
    
    def visit_Import(self, node: ast.Import) -> None:
        """Check for dangerous imports."""
        for alias in node.names:
            if alias.name in self.DANGEROUS_MODULES:
                msg, severity = self.DANGEROUS_MODULES[alias.name]
                self.result.findings.append(ScanFinding(
                    finding_type=FindingType.UNSAFE_DESERIALIZATION,
                    severity=severity,
                    file_path=self.file_path,
                    line_number=node.lineno,
                    column=node.col_offset,
                    message=f"Import of {alias.name}: {msg}",
                    code_snippet=f"import {alias.name}",
                    recommendation=f"Use safe alternatives to {alias.name}",
                    cwe_id="CWE-502",
                ))
        
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check for dangerous from imports."""
        if node.module in self.DANGEROUS_MODULES:
            msg, severity = self.DANGEROUS_MODULES[node.module]
            self.result.findings.append(ScanFinding(
                finding_type=FindingType.UNSAFE_DESERIALIZATION,
                severity=severity,
                file_path=self.file_path,
                line_number=node.lineno,
                column=node.col_offset,
                message=f"Import from {node.module}: {msg}",
                code_snippet=f"from {node.module} import ...",
                recommendation=f"Use safe alternatives to {node.module}",
                cwe_id="CWE-502",
            ))
        
        self.generic_visit(node)
    
    def _get_call_name(self, node: ast.Call) -> str:
        """Extract function name from a Call node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        return ""


def compute_file_hash(file_path: Path, algorithm: str = "sha256") -> str:
    """Compute hash of a file."""
    hasher = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()
