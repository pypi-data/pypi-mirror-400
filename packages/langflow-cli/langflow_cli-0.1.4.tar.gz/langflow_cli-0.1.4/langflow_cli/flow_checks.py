"""Flow validation checks."""

from typing import Any, Optional, List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from langflow_cli.api_client import LangflowAPIClient

from enum import Enum
import click


class FlowCheck(Enum):
    """Enumeration of available flow checks."""
    LAST_TESTED_VERSION = "LAST_TESTED_VERSION"
    HAS_EDITTED_COMPONENTS = "HAS_EDITTED_COMPONENTS"
    HAS_DATA = "HAS_DATA"
    HAS_NODES = "HAS_NODES"
    HAS_EDGES = "HAS_EDGES"
    HAS_NAME = "HAS_NAME"
    HAS_DESCRIPTION = "HAS_DESCRIPTION"


def _check_last_tested_version(flow: Dict[str, Any], client: "LangflowAPIClient") -> Dict[str, Any]:
    """Check if flow has last_tested_version and compare with current version from client."""
    has_version = "last_tested_version" in flow
    version_value = flow.get("last_tested_version")
    matches_current = None
    current_version = None
    passed = False
    
    if has_version and version_value:
        try:
            version_info = client.get_version()
            current_version = version_info.get("version")
            if current_version and version_value:
                matches_current = str(version_value).strip() == str(current_version).strip()
                # Pass only if versions match
                passed = matches_current is True
            else:
                # Has version but can't compare - treat as passed (version exists)
                passed = True
        except Exception:
            # If we can't get version, just report that we have a version but can't compare
            passed = True
    else:
        # No version specified - treat as failed
        passed = False
    
    return {
        "check": "LAST_TESTED_VERSION",
        "passed": passed,
        "details": {
            "has_version": has_version,
            "version": version_value,
            "matches_current": matches_current,
            "current_version": current_version
        }
    }


def _check_has_editted_components(flow: Dict[str, Any]) -> Dict[str, Any]:
    """Check if flow has edited components (nodes in data)."""
    data = flow.get("data", {})
    nodes = data.get("nodes", []) if isinstance(data, dict) else []
    has_components = len(nodes) > 0
    
    return {
        "check": "HAS_EDITTED_COMPONENTS",
        "passed": has_components,
        "details": {
            "has_components": has_components,
            "node_count": len(nodes) if isinstance(nodes, list) else 0
        }
    }


def _check_has_data(flow: Dict[str, Any]) -> Dict[str, Any]:
    """Check if flow has data field."""
    has_data = "data" in flow and flow.get("data") is not None
    
    return {
        "check": "HAS_DATA",
        "passed": has_data,
        "details": {
            "has_data": has_data
        }
    }


def _check_has_nodes(flow: Dict[str, Any]) -> Dict[str, Any]:
    """Check if flow has nodes in data."""
    data = flow.get("data", {})
    nodes = data.get("nodes", []) if isinstance(data, dict) else []
    has_nodes = isinstance(nodes, list) and len(nodes) > 0
    
    return {
        "check": "HAS_NODES",
        "passed": has_nodes,
        "details": {
            "has_nodes": has_nodes,
            "node_count": len(nodes) if isinstance(nodes, list) else 0
        }
    }


def _check_has_edges(flow: Dict[str, Any]) -> Dict[str, Any]:
    """Check if flow has edges in data."""
    data = flow.get("data", {})
    edges = data.get("edges", []) if isinstance(data, dict) else []
    has_edges = isinstance(edges, list) and len(edges) > 0
    
    return {
        "check": "HAS_EDGES",
        "passed": has_edges,
        "details": {
            "has_edges": has_edges,
            "edge_count": len(edges) if isinstance(edges, list) else 0
        }
    }


def _check_has_name(flow: Dict[str, Any]) -> Dict[str, Any]:
    """Check if flow has a name."""
    has_name = "name" in flow and flow.get("name") is not None and flow.get("name") != ""
    
    return {
        "check": "HAS_NAME",
        "passed": has_name,
        "details": {
            "has_name": has_name,
            "name": flow.get("name")
        }
    }


def _check_has_description(flow: Dict[str, Any]) -> Dict[str, Any]:
    """Check if flow has a description."""
    has_description = "description" in flow and flow.get("description") is not None and flow.get("description") != ""
    
    return {
        "check": "HAS_DESCRIPTION",
        "passed": has_description,
        "details": {
            "has_description": has_description,
            "description": flow.get("description")
        }
    }


# Mapping of check names to their functions
_CHECK_FUNCTIONS = {
    FlowCheck.LAST_TESTED_VERSION: _check_last_tested_version,
    FlowCheck.HAS_EDITTED_COMPONENTS: _check_has_editted_components,
    FlowCheck.HAS_DATA: _check_has_data,
    FlowCheck.HAS_NODES: _check_has_nodes,
    FlowCheck.HAS_EDGES: _check_has_edges,
    FlowCheck.HAS_NAME: _check_has_name,
    FlowCheck.HAS_DESCRIPTION: _check_has_description,
}


def perform_flow_checks(
    flow: Dict[str, Any],
    checks: List[str],
    client: "LangflowAPIClient"
) -> List[Dict[str, Any]]:
    """
    Perform checks on a flow and return results for each check.
    
    Args:
        flow: Flow dictionary to check
        checks: List of check names (e.g., ["LAST_TESTED_VERSION", "HAS_EDITTED_COMPONENTS"])
        client: LangflowAPIClient instance (required for LAST_TESTED_VERSION check)
        
    Returns:
        List of check results, each containing:
        - check: Name of the check
        - passed: Boolean indicating if check passed
        - details: Dictionary with check-specific details
        
    Raises:
        ValueError: If an unknown check name is provided
    """
    results = []
    
    for check_name in checks:
        # Convert string to FlowCheck enum if needed
        try:
            if isinstance(check_name, str):
                check_enum = FlowCheck(check_name.upper())
            else:
                check_enum = check_name
        except ValueError:
            raise ValueError(f"Unknown check: {check_name}. Available checks: {[c.value for c in FlowCheck]}")
        
        # Get the check function
        check_func = _CHECK_FUNCTIONS.get(check_enum)
        if not check_func:
            raise ValueError(f"Check function not found for: {check_name}")
        
        # Perform the check
        if check_enum == FlowCheck.LAST_TESTED_VERSION:
            result = check_func(flow, client)
        else:
            result = check_func(flow)
        
        results.append(result)
    
    return results


def list_all_checks() -> List[str]:
    """
    Get a list of all available check names.
    
    Returns:
        List of all check names as strings
    """
    return [check.value for check in FlowCheck]


def validate_flow_with_checks(
    flow: Dict[str, Any],
    client: "LangflowAPIClient",
    checks: Optional[List[str]] = None,
    ignore_failures: bool = False,
    console=None
) -> bool:
    """
    Perform flow checks and present results to the user. If any check fails,
    ask the user for confirmation before continuing.
    
    Args:
        flow: Flow dictionary to check
        client: LangflowAPIClient instance (required for LAST_TESTED_VERSION check)
        checks: Optional list of check names to run. If None, runs all checks.
        ignore_failures: If True, skip user confirmation and continue even if checks fail
        console: Optional Rich console instance for output
        
    Returns:
        True if should continue, False if should abort
        
    Raises:
        click.Abort: If user chooses to abort after seeing failed checks
    """
    # Import here to avoid circular dependencies
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    
    if console is None:
        console = Console()
    
    # If no checks specified, run all checks
    if checks is None:
        checks = list_all_checks()
    
    # Perform the checks
    check_results = perform_flow_checks(flow, checks, client)
    
    # Determine which checks failed
    failed_checks = [r for r in check_results if not r.get("passed", False)]
    
    # If all checks passed, continue automatically
    if not failed_checks:
        return True
    
    # Display results
    console.print("\n[bold]Flow Validation Results[/bold]\n")
    
    # Create a table for results
    table = Table(show_header=True, header_style="bold")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details")
    
    # Add all results to table
    for result in check_results:
        check_name = result["check"]
        passed = result.get("passed", False)
        
        if passed:
            status = "[green]✓ PASS[/green]"
            details_str = "Check passed"
        else:
            status = "[red]✗ FAIL[/red]"
            # Format details for display
            details = result.get("details", {})
            details_str = str(details) if details else "Check failed"
        
        table.add_row(check_name, status, details_str)
    
    console.print(table)
    
    # If ignore_failures is True, continue without asking
    if ignore_failures:
        console.print("\n[yellow]Continuing despite failed checks (ignore flag enabled)[/yellow]")
        return True
    
    # Ask user for confirmation
    console.print("\n[yellow]⚠[/yellow]  Some checks failed or have warnings.")
    if not click.confirm("Continue anyway?"):
        console.print("[yellow]Operation cancelled.[/yellow]")
        raise click.Abort()
    
    return True

