#!/usr/bin/env python3
"""
IMC Prosperity Script Checker (v3 - Configurable)

A static analysis tool to validate trading algorithms before submission.
Supports YAML configuration for customizing allowed imports and severity levels.
"""

import ast
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

# Try to import yaml, fall back to defaults if not available
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    OFF = "off"


@dataclass
class Issue:
    severity: Severity
    code: str
    message: str
    line: Optional[int] = None
    column: Optional[int] = None
    suggestion: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "severity": self.severity.value,
            "code": self.code,
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "suggestion": self.suggestion
        }

    def __str__(self) -> str:
        loc = f":{self.line}" if self.line else ""
        loc += f":{self.column}" if self.column else ""
        sev_symbol = {"error": "❌", "warning": "⚠️", "info": "ℹ️", "off": ""}[self.severity.value]
        s = f"{sev_symbol} [{self.code}]{loc} {self.message}"
        if self.suggestion:
            s += f"\n   💡 {self.suggestion}"
        return s


@dataclass
class CheckResult:
    valid: bool
    issues: List[Issue] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "issues": [i.to_dict() for i in self.issues],
            "error_count": sum(1 for i in self.issues if i.severity == Severity.ERROR),
            "warning_count": sum(1 for i in self.issues if i.severity == Severity.WARNING),
        }


# =============================================================================
# DEFAULT CONFIGURATION
# =============================================================================

DEFAULT_CONFIG = {
    "prosperity_version": 3,
    "imports": {
        # Required
        "datamodel": True,
        # Official allowed (Appendix C)
        "pandas": True, "pd": True,
        "numpy": True, "np": True,
        "statistics": True,
        "math": True,
        "typing": True,
        "jsonpickle": True,
        # Standard library (usually safe)
        "json": True,
        "collections": True,
        "copy": True,
        "functools": True,
        "itertools": True,
        "string": True,
        # Commonly attempted but NOT allowed
        "scipy": False,
        "sklearn": False,
        "random": False,
        "time": False,
        "datetime": False,
        # Definitely forbidden
        "os": False,
        "sys": False,
        "subprocess": False,
        "socket": False,
        "requests": False,
        "urllib": False,
        "http": False,
        "threading": False,
        "multiprocessing": False,
        "asyncio": False,
        "pickle": False,
    },
    "severity": {
        "E001": "error", "E002": "error", "E003": "error", "E004": "error",
        "E010": "error", "E011": "error",
        "E020": "error", "E021": "error",
        "E030": "error", "E031": "error", "E032": "error", "E033": "error",
        "W010": "warning", "W020": "warning", "W021": "warning", "W022": "warning",
        "W030": "warning", "W040": "warning",
        "I010": "info", "I030": "info", "I031": "info", "I040": "info",
    },
    "limits": {
        "timeout_ms": 900,
        "max_loop_depth": 2,
        "max_log_length": 3750,
    },
    "structure": {
        "class_name": "Trader",
        "method_name": "run",
        "return_tuple_length": 3,
    },
    "output": {
        "colors": True,
        "show_requirements": True,
        "show_info": True,
    },
    "behavior": {
        "strict": False,
    },
}


def load_config(config_path: Optional[str] = None) -> dict:
    """Load configuration from YAML file or use defaults."""
    config = DEFAULT_CONFIG.copy()
    
    if not YAML_AVAILABLE:
        return config
    
    # Search order for config files
    search_paths = []
    if config_path:
        search_paths.append(Path(config_path))
    search_paths.extend([
        Path.cwd() / ".prosperity.yaml",
        Path.cwd() / ".prosperity.yml",
        Path.cwd() / "prosperity.yaml",
        Path.cwd() / "prosperity_config.yaml",
        Path.home() / ".prosperity.yaml",
    ])
    
    for path in search_paths:
        if path.exists():
            try:
                with open(path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    if user_config:
                        # Deep merge
                        config = deep_merge(config, user_config)
                return config
            except Exception as e:
                print(f"Warning: Failed to load config from {path}: {e}")
                
    return config


def deep_merge(base: dict, override: dict) -> dict:
    """Deep merge two dictionaries."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def get_severity(config: dict, code: str) -> Severity:
    """Get severity for a given error code from config."""
    sev_str = config.get("severity", {}).get(code, "error")
    if sev_str == "off":
        return Severity.OFF
    return Severity(sev_str)


def is_import_allowed(config: dict, module: str) -> Union[bool, str]:
    """Check if import is allowed. Returns True, False, or 'warn'."""
    imports = config.get("imports", {})
    return imports.get(module, "unknown")


# =============================================================================
# AST VISITORS
# =============================================================================

class ImportChecker(ast.NodeVisitor):
    """Check imports against config."""
    
    def __init__(self, config: dict):
        self.config = config
        self.imports: Set[str] = set()
        self.from_imports: Dict[str, Set[str]] = {}
        self.issues: List[Issue] = []
        
    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            module = alias.name.split('.')[0]
            self.imports.add(module)
            self._check_import(module, node.lineno, alias.name)
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node: ast.ImportFrom):
        module = node.module.split('.')[0] if node.module else ""
        if module not in self.from_imports:
            self.from_imports[module] = set()
        for alias in node.names:
            self.from_imports[module].add(alias.name)
        self._check_import(module, node.lineno, module)
        self.generic_visit(node)
        
    def _check_import(self, module: str, line: int, full_name: str):
        allowed = is_import_allowed(self.config, module)
        severity = get_severity(self.config, "E001")
        
        if severity == Severity.OFF:
            return
            
        if allowed is False:
            self.issues.append(Issue(
                severity=severity,
                code="E001",
                message=f"Forbidden import: '{module}'",
                line=line,
                suggestion=f"Remove '{full_name}'. Official allowed: pandas, numpy, statistics, math, typing, jsonpickle"
            ))
        elif allowed == "warn":
            self.issues.append(Issue(
                severity=Severity.WARNING,
                code="W001",
                message=f"Import '{module}' not in official list but may work",
                line=line,
                suggestion="Test thoroughly - this import may not be available"
            ))
        elif allowed == "unknown":
            self.issues.append(Issue(
                severity=Severity.WARNING,
                code="W001",
                message=f"Unknown import: '{module}'",
                line=line,
                suggestion="Verify this import is allowed in competition"
            ))


class TraderClassChecker(ast.NodeVisitor):
    """Check Trader class structure."""
    
    def __init__(self, config: dict):
        self.config = config
        self.has_trader_class = False
        self.has_run_method = False
        self.run_method_node: Optional[ast.FunctionDef] = None
        self.trader_class_node: Optional[ast.ClassDef] = None
        self.instance_vars: Set[str] = set()
        self.issues: List[Issue] = []
        
    def visit_ClassDef(self, node: ast.ClassDef):
        expected_class = self.config.get("structure", {}).get("class_name", "Trader")
        
        if node.name == expected_class:
            self.has_trader_class = True
            self.trader_class_node = node
            
            expected_method = self.config.get("structure", {}).get("method_name", "run")
            
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if item.name == expected_method:
                        self.has_run_method = True
                        self.run_method_node = item
                        self._check_run_signature(item)
                    elif item.name == "__init__":
                        self._check_init(item)
                        
        self.generic_visit(node)
        
    def _check_run_signature(self, node: ast.FunctionDef):
        args = node.args
        param_names = [arg.arg for arg in args.args]
        
        if len(param_names) < 2:
            severity = get_severity(self.config, "E010")
            if severity != Severity.OFF:
                self.issues.append(Issue(
                    severity=severity,
                    code="E010",
                    message="run() must accept 'state' parameter",
                    line=node.lineno,
                    suggestion="def run(self, state: TradingState) -> tuple[dict, int, str]:"
                ))
            return
            
        if param_names[0] != "self":
            severity = get_severity(self.config, "E011")
            if severity != Severity.OFF:
                self.issues.append(Issue(
                    severity=severity,
                    code="E011",
                    message="run() first parameter must be 'self'",
                    line=node.lineno
                ))
                
    def _check_init(self, node: ast.FunctionDef):
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Attribute):
                        if isinstance(target.value, ast.Name) and target.value.id == "self":
                            self.instance_vars.add(target.attr)


class ReturnChecker(ast.NodeVisitor):
    """Check return statements."""
    
    def __init__(self, config: dict):
        self.config = config
        self.issues: List[Issue] = []
        self.in_run_method = False
        self.has_return = False
        self.return_nodes: List[ast.Return] = []
        
    def check_run_method(self, node: ast.FunctionDef):
        self.in_run_method = True
        self.has_return = False
        self.return_nodes = []
        
        self.visit(node)
        
        if not self.has_return:
            severity = get_severity(self.config, "E030")
            if severity != Severity.OFF:
                self.issues.append(Issue(
                    severity=severity,
                    code="E030",
                    message="run() has no return statement",
                    line=node.lineno,
                    suggestion="return result, conversions, traderData"
                ))
            return
            
        expected_len = self.config.get("structure", {}).get("return_tuple_length", 3)
        
        for ret_node in self.return_nodes:
            if ret_node.value is None:
                severity = get_severity(self.config, "E031")
                if severity != Severity.OFF:
                    self.issues.append(Issue(
                        severity=severity,
                        code="E031",
                        message="run() returns None",
                        line=ret_node.lineno,
                        suggestion="return result, conversions, traderData"
                    ))
            else:
                self._check_return_value(ret_node, expected_len)
                
        self.in_run_method = False
        
    def _check_return_value(self, node: ast.Return, expected_len: int):
        if isinstance(node.value, ast.Tuple):
            if len(node.value.elts) != expected_len:
                severity = get_severity(self.config, "E032")
                if severity != Severity.OFF:
                    self.issues.append(Issue(
                        severity=severity,
                        code="E032",
                        message=f"run() must return {expected_len} values, got {len(node.value.elts)}",
                        line=node.lineno,
                        suggestion="return result, conversions, traderData"
                    ))
            else:
                severity = get_severity(self.config, "I031")
                if severity != Severity.OFF:
                    self.issues.append(Issue(
                        severity=severity,
                        code="I031",
                        message="Return format looks correct",
                        line=node.lineno
                    ))
        elif isinstance(node.value, ast.Dict):
            severity = get_severity(self.config, "E033")
            if severity != Severity.OFF:
                self.issues.append(Issue(
                    severity=severity,
                    code="E033",
                    message="run() returns only dict, must return tuple",
                    line=node.lineno,
                    suggestion="return result, conversions, traderData"
                ))
        elif isinstance(node.value, ast.Name):
            severity = get_severity(self.config, "W030")
            if severity != Severity.OFF:
                self.issues.append(Issue(
                    severity=severity,
                    code="W030",
                    message=f"Ensure run() returns {expected_len}-tuple",
                    line=node.lineno
                ))
        
    def visit_Return(self, node: ast.Return):
        if self.in_run_method:
            self.has_return = True
            self.return_nodes.append(node)
        self.generic_visit(node)


class LoopChecker(ast.NodeVisitor):
    """Check for infinite loops and timeout risks."""
    
    def __init__(self, config: dict):
        self.config = config
        self.issues: List[Issue] = []
        self.loop_depth = 0
        self.max_depth = config.get("limits", {}).get("max_loop_depth", 2)
        
    def visit_While(self, node: ast.While):
        self.loop_depth += 1
        
        if self._is_always_true(node.test):
            has_break = self._has_break_or_return(node.body)
            if not has_break:
                severity = get_severity(self.config, "E020")
                if severity != Severity.OFF:
                    self.issues.append(Issue(
                        severity=severity,
                        code="E020",
                        message="Infinite loop: while True with no break",
                        line=node.lineno,
                        suggestion="Add break condition"
                    ))
            else:
                severity = get_severity(self.config, "W020")
                if severity != Severity.OFF:
                    self.issues.append(Issue(
                        severity=severity,
                        code="W020",
                        message="while True loop - ensure break is reachable",
                        line=node.lineno
                    ))
        else:
            loop_vars = self._get_condition_vars(node.test)
            modified_vars = self._get_modified_vars(node.body)
            
            if loop_vars and not (loop_vars & modified_vars):
                if not self._has_break_or_return(node.body):
                    severity = get_severity(self.config, "W021")
                    if severity != Severity.OFF:
                        self.issues.append(Issue(
                            severity=severity,
                            code="W021",
                            message=f"Loop vars {loop_vars} not modified",
                            line=node.lineno,
                            suggestion="Ensure loop can terminate"
                        ))
                    
        self.generic_visit(node)
        self.loop_depth -= 1
        
    def visit_For(self, node: ast.For):
        self.loop_depth += 1
        
        if self.loop_depth > self.max_depth:
            severity = get_severity(self.config, "W022")
            if severity != Severity.OFF:
                self.issues.append(Issue(
                    severity=severity,
                    code="W022",
                    message=f"Deep loop nesting (depth {self.loop_depth})",
                    line=node.lineno,
                    suggestion="Consider optimizing - timeout risk"
                ))
            
        self.generic_visit(node)
        self.loop_depth -= 1
        
    def visit_Call(self, node: ast.Call):
        func_name = self._get_call_name(node)
        
        if func_name in ("sleep", "time.sleep"):
            severity = get_severity(self.config, "E021")
            if severity != Severity.OFF:
                self.issues.append(Issue(
                    severity=severity,
                    code="E021",
                    message="time.sleep() will cause timeout",
                    line=node.lineno
                ))
            
        self.generic_visit(node)
        
    def _is_always_true(self, node: ast.expr) -> bool:
        if isinstance(node, ast.Constant):
            return bool(node.value)
        if isinstance(node, ast.Name):
            return node.id == "True"
        return False
        
    def _has_break_or_return(self, body: List[ast.stmt]) -> bool:
        for stmt in body:
            if isinstance(stmt, (ast.Break, ast.Return)):
                return True
            if isinstance(stmt, ast.If):
                if self._has_break_or_return(stmt.body) or self._has_break_or_return(stmt.orelse):
                    return True
        return False
        
    def _get_condition_vars(self, node: ast.expr) -> Set[str]:
        return {child.id for child in ast.walk(node) if isinstance(child, ast.Name)}
        
    def _get_modified_vars(self, body: List[ast.stmt]) -> Set[str]:
        modified = set()
        for stmt in body:
            for node in ast.walk(stmt):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            modified.add(target.id)
                elif isinstance(node, ast.AugAssign):
                    if isinstance(node.target, ast.Name):
                        modified.add(node.target.id)
        return modified
        
    def _get_call_name(self, node: ast.Call) -> str:
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                return f"{node.func.value.id}.{node.func.attr}"
        return ""


class PrintChecker(ast.NodeVisitor):
    """Check print statements."""
    
    def __init__(self, config: dict):
        self.config = config
        self.print_count = 0
        self.first_line: Optional[int] = None
        
    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            self.print_count += 1
            if self.first_line is None:
                self.first_line = node.lineno
        self.generic_visit(node)
        
    def get_issue(self) -> Optional[Issue]:
        if self.print_count > 0:
            severity = get_severity(self.config, "I030")
            if severity != Severity.OFF:
                return Issue(
                    severity=severity,
                    code="I030",
                    message=f"Found {self.print_count} print statement(s)",
                    line=self.first_line,
                    suggestion="Output appears in logs - keep it reasonable"
                )
        return None


# =============================================================================
# MAIN CHECKER
# =============================================================================

class ProsperityChecker:
    """Main checker with config support."""
    
    def __init__(self, config: Optional[dict] = None, strict: bool = False):
        self.config = config or load_config()
        self.strict = strict or self.config.get("behavior", {}).get("strict", False)
        
    def check_file(self, filepath: str) -> CheckResult:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
        except FileNotFoundError:
            return CheckResult(valid=False, issues=[
                Issue(Severity.ERROR, "E000", f"File not found: {filepath}")
            ])
        except UnicodeDecodeError:
            return CheckResult(valid=False, issues=[
                Issue(Severity.ERROR, "E000", "File encoding error - use UTF-8")
            ])
            
        return self.check_source(source)
        
    def check_source(self, source: str) -> CheckResult:
        issues: List[Issue] = []
        
        # Parse
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            return CheckResult(valid=False, issues=[
                Issue(Severity.ERROR, "E000", f"Syntax error: {e.msg}", e.lineno, e.offset)
            ])
            
        # Import checker
        import_checker = ImportChecker(self.config)
        import_checker.visit(tree)
        issues.extend(import_checker.issues)
        
        # Check datamodel import
        has_datamodel = "datamodel" in import_checker.imports or "datamodel" in import_checker.from_imports
        if not has_datamodel:
            severity = get_severity(self.config, "E002")
            if severity != Severity.OFF:
                issues.append(Issue(
                    severity=severity,
                    code="E002",
                    message="Missing 'datamodel' import",
                    suggestion="from datamodel import OrderDepth, TradingState, Order"
                ))
            
        # Trader class checker
        trader_checker = TraderClassChecker(self.config)
        trader_checker.visit(tree)
        issues.extend(trader_checker.issues)
        
        expected_class = self.config.get("structure", {}).get("class_name", "Trader")
        expected_method = self.config.get("structure", {}).get("method_name", "run")
        
        if not trader_checker.has_trader_class:
            severity = get_severity(self.config, "E003")
            if severity != Severity.OFF:
                issues.append(Issue(
                    severity=severity,
                    code="E003",
                    message=f"Missing '{expected_class}' class",
                    suggestion=f"class {expected_class}:\n    def {expected_method}(self, state):"
                ))
        elif not trader_checker.has_run_method:
            severity = get_severity(self.config, "E004")
            if severity != Severity.OFF:
                issues.append(Issue(
                    severity=severity,
                    code="E004",
                    message=f"{expected_class} missing '{expected_method}' method"
                ))
            
        # Return checker
        if trader_checker.run_method_node:
            return_checker = ReturnChecker(self.config)
            return_checker.check_run_method(trader_checker.run_method_node)
            issues.extend(return_checker.issues)
            
        # Loop checker
        loop_checker = LoopChecker(self.config)
        loop_checker.visit(tree)
        issues.extend(loop_checker.issues)
        
        # Instance variable warning
        if trader_checker.instance_vars:
            severity = get_severity(self.config, "W040")
            if severity != Severity.OFF:
                issues.append(Issue(
                    severity=severity,
                    code="W040",
                    message=f"Instance vars {trader_checker.instance_vars} may not persist",
                    suggestion="Use traderData with jsonpickle for state"
                ))
            
        # Print checker
        print_checker = PrintChecker(self.config)
        print_checker.visit(tree)
        print_issue = print_checker.get_issue()
        if print_issue:
            issues.append(print_issue)
            
        # Filter out OFF severity
        issues = [i for i in issues if i.severity != Severity.OFF]
        
        # Determine validity
        has_errors = any(i.severity == Severity.ERROR for i in issues)
        if self.strict:
            has_errors = has_errors or any(i.severity == Severity.WARNING for i in issues)
            
        return CheckResult(valid=not has_errors, issues=issues)

