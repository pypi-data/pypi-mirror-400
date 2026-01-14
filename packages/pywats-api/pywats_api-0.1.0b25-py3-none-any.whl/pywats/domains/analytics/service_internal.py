"""Analytics service - internal API business logic layer.

⚠️ INTERNAL API - SUBJECT TO CHANGE ⚠️

Uses internal WATS API endpoints that are not publicly documented.
These methods may change or be removed without notice.

UNIT FLOW OVERVIEW
==================

The Unit Flow functionality provides visualization and analysis of how units
(products) flow through production processes. This is essential for:

- Identifying bottlenecks in production
- Understanding process flow patterns
- Tracing individual unit paths
- Analyzing throughput and yield at each stage

Key Concepts:
- Nodes: Operations/processes that units pass through (e.g., "Assembly", "Test", "Pack")
- Links: Connections between nodes showing unit transitions
- Units: Individual products being tracked through the flow

Example:
    # Get complete unit flow for a product
    api = pyWATS(base_url="...", token="...")
    
    filter = UnitFlowFilter(
        part_number="WIDGET-001",
        date_from=datetime(2025, 1, 1),
        date_to=datetime(2025, 1, 7)
    )
    
    result = api.analytics_internal.get_unit_flow(filter)
    
    # Analyze the flow
    for node in result.nodes:
        print(f"{node.name}: {node.unit_count} units, {node.yield_percent}% yield")
    
    for link in result.links:
        print(f"  {link.source_name} -> {link.target_name}: {link.unit_count} units")
        
    # Trace specific serial numbers
    units_result = api.analytics_internal.trace_serial_numbers(
        ["SN001", "SN002", "SN003"]
    )
"""
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, Union

logger = logging.getLogger(__name__)

from .repository_internal import AnalyticsRepositoryInternal
from .models import (
    UnitFlowNode,
    UnitFlowLink,
    UnitFlowUnit,
    UnitFlowFilter,
    UnitFlowResult,
)


class AnalyticsServiceInternal:
    """
    Analytics business logic layer using internal API.
    
    ⚠️ INTERNAL API - SUBJECT TO CHANGE ⚠️
    
    Provides Unit Flow analysis for production visualization:
    - Query unit flow with various filters
    - Get flow nodes (operations/processes)
    - Get flow links (transitions between nodes)
    - Trace individual units through the flow
    - Split and reorganize the flow view
    
    Example:
        >>> api = pyWATS(base_url="...", token="...")
        >>> 
        >>> # Get unit flow for a product
        >>> filter = UnitFlowFilter(part_number="WIDGET-001")
        >>> result = api.analytics_internal.get_unit_flow(filter)
        >>> 
        >>> for node in result.nodes:
        ...     print(f"{node.name}: {node.unit_count} units")
    """
    
    def __init__(self, repository_internal: AnalyticsRepositoryInternal):
        """
        Initialize service with internal repository.
        
        Args:
            repository_internal: AnalyticsRepositoryInternal for internal API
        """
        self._repo_internal = repository_internal
    
    # =========================================================================
    # Unit Flow - Main Queries
    # =========================================================================
    
    def get_unit_flow(
        self, 
        filter_data: Optional[Union[UnitFlowFilter, Dict[str, Any]]] = None
    ) -> UnitFlowResult:
        """
        Get complete unit flow data with nodes and links.
        
        This is the main method for unit flow analysis. Returns a complete
        flow diagram showing how units traverse through production operations.
        
        Args:
            filter_data: UnitFlowFilter or dict with filter criteria.
                Common filters:
                - part_number: Product part number
                - date_from/date_to: Date range
                - station_name: Filter by station
                - include_passed/include_failed: Filter by status
                
        Returns:
            UnitFlowResult with nodes, links, and metadata
            
        Example:
            >>> from pywats import UnitFlowFilter
            >>> from datetime import datetime, timedelta
            >>> 
            >>> # Get flow for last 7 days
            >>> filter = UnitFlowFilter(
            ...     part_number="WIDGET-001",
            ...     date_from=datetime.now() - timedelta(days=7),
            ...     include_passed=True,
            ...     include_failed=True
            ... )
            >>> result = api.analytics_internal.get_unit_flow(filter)
            >>> 
            >>> print(f"Found {len(result.nodes)} nodes and {len(result.links)} links")
            >>> for node in result.nodes:
            ...     print(f"  {node.name}: {node.unit_count} units")
        """
        raw_data = self._repo_internal.query_unit_flow(filter_data)
        return self._parse_flow_result(raw_data)
    
    def get_flow_nodes(self) -> List[UnitFlowNode]:
        """
        Get all nodes from the current unit flow state.
        
        Nodes represent operations/processes in the production flow.
        Use get_unit_flow() first to establish the flow context.
        
        Returns:
            List of UnitFlowNode objects
            
        Example:
            >>> nodes = api.analytics_internal.get_flow_nodes()
            >>> for node in nodes:
            ...     print(f"{node.name}: {node.yield_percent}% yield")
        """
        return self._repo_internal.get_unit_flow_nodes()
    
    def get_flow_links(self) -> List[UnitFlowLink]:
        """
        Get all links from the current unit flow state.
        
        Links represent transitions between operations/processes.
        Use get_unit_flow() first to establish the flow context.
        
        Returns:
            List of UnitFlowLink objects
            
        Example:
            >>> links = api.analytics_internal.get_flow_links()
            >>> for link in links:
            ...     print(f"{link.source_name} -> {link.target_name}: {link.unit_count} units")
        """
        return self._repo_internal.get_unit_flow_links()
    
    def get_flow_units(self) -> List[UnitFlowUnit]:
        """
        Get individual units from the current unit flow.
        
        Returns the list of units that have traversed the production flow.
        Use get_unit_flow() first to establish the flow context.
        
        Returns:
            List of UnitFlowUnit objects
            
        Example:
            >>> units = api.analytics_internal.get_flow_units()
            >>> for unit in units:
            ...     print(f"{unit.serial_number}: {unit.status}")
        """
        return self._repo_internal.get_unit_flow_units()
    
    # =========================================================================
    # Unit Flow - Serial Number Tracing
    # =========================================================================
    
    def trace_serial_numbers(
        self, 
        serial_numbers: List[str],
        filter_data: Optional[Union[UnitFlowFilter, Dict[str, Any]]] = None
    ) -> UnitFlowResult:
        """
        Trace the production flow path for specific serial numbers.
        
        Useful for investigating the history of specific units and
        understanding their journey through production.
        
        Args:
            serial_numbers: List of serial numbers to trace
            filter_data: Additional filter parameters
            
        Returns:
            UnitFlowResult showing the flow path for the specified units
            
        Example:
            >>> # Trace specific units
            >>> result = api.analytics_internal.trace_serial_numbers(
            ...     ["SN001", "SN002", "SN003"]
            ... )
            >>> for unit in result.units or []:
            ...     print(f"{unit.serial_number}: path = {unit.node_path}")
        """
        raw_data = self._repo_internal.query_unit_flow_by_serial_numbers(
            serial_numbers, filter_data
        )
        return self._parse_flow_result(raw_data)
    
    # =========================================================================
    # Unit Flow - View Manipulation
    # =========================================================================
    
    def split_flow_by(
        self, 
        dimension: str,
        filter_data: Optional[Union[UnitFlowFilter, Dict[str, Any]]] = None
    ) -> UnitFlowResult:
        """
        Split the unit flow by a specific dimension.
        
        Splits the flow diagram to show parallel paths based on the
        specified dimension (e.g., by station, location, or purpose).
        
        Args:
            dimension: Dimension to split by. Common values:
                - "stationName": Split by test station
                - "location": Split by physical location
                - "purpose": Split by station purpose
                - "processCode": Split by process type
            filter_data: Additional filter parameters
            
        Returns:
            UnitFlowResult with split flow view
            
        Example:
            >>> # Split flow by station
            >>> result = api.analytics_internal.split_flow_by("stationName")
            >>> for node in result.nodes:
            ...     print(f"{node.station_name} - {node.name}: {node.unit_count} units")
        """
        raw_data = self._repo_internal.set_unit_flow_split_by(dimension, filter_data)
        return self._parse_flow_result(raw_data)
    
    def set_unit_order(
        self, 
        order_by: str,
        filter_data: Optional[Union[UnitFlowFilter, Dict[str, Any]]] = None
    ) -> UnitFlowResult:
        """
        Set how units are ordered in the flow visualization.
        
        Args:
            order_by: Order specification. Common values:
                - "startTime": Order by when units entered
                - "endTime": Order by when units exited
                - "serialNumber": Order alphabetically by serial
                - "status": Order by pass/fail status
            filter_data: Additional filter parameters
            
        Returns:
            UnitFlowResult with reordered units
            
        Example:
            >>> # Order by start time
            >>> result = api.analytics_internal.set_unit_order("startTime")
        """
        raw_data = self._repo_internal.set_unit_flow_order(order_by, filter_data)
        return self._parse_flow_result(raw_data)
    
    def show_operations(
        self,
        operation_ids: List[str],
        filter_data: Optional[Union[UnitFlowFilter, Dict[str, Any]]] = None
    ) -> UnitFlowResult:
        """
        Show specific operations in the unit flow diagram.
        
        Use this to focus on specific operations of interest.
        
        Args:
            operation_ids: List of operation IDs or names to show
            filter_data: Additional filter parameters
            
        Returns:
            UnitFlowResult with updated visibility
            
        Example:
            >>> # Show only assembly and test operations
            >>> result = api.analytics_internal.show_operations(
            ...     ["Assembly", "EndOfLineTest"]
            ... )
        """
        raw_data = self._repo_internal.set_unit_flow_visibility(
            show_list=operation_ids, 
            filter_data=filter_data
        )
        return self._parse_flow_result(raw_data)
    
    def hide_operations(
        self,
        operation_ids: List[str],
        filter_data: Optional[Union[UnitFlowFilter, Dict[str, Any]]] = None
    ) -> UnitFlowResult:
        """
        Hide specific operations from the unit flow diagram.
        
        Use this to simplify the view by hiding less relevant operations.
        
        Args:
            operation_ids: List of operation IDs or names to hide
            filter_data: Additional filter parameters
            
        Returns:
            UnitFlowResult with updated visibility
            
        Example:
            >>> # Hide packaging operations
            >>> result = api.analytics_internal.hide_operations(
            ...     ["Packaging", "Labeling"]
            ... )
        """
        raw_data = self._repo_internal.set_unit_flow_visibility(
            hide_list=operation_ids, 
            filter_data=filter_data
        )
        return self._parse_flow_result(raw_data)
    
    def expand_operations(
        self,
        expand: bool = True,
        filter_data: Optional[Union[UnitFlowFilter, Dict[str, Any]]] = None
    ) -> UnitFlowResult:
        """
        Expand or collapse operations in the unit flow.
        
        When expanded, shows detailed sub-operations within each process.
        When collapsed, shows an aggregated view.
        
        Args:
            expand: True to expand operations, False to collapse
            filter_data: Additional filter parameters
            
        Returns:
            UnitFlowResult with updated expansion state
            
        Example:
            >>> # Expand to see detailed operations
            >>> result = api.analytics_internal.expand_operations(True)
            >>> 
            >>> # Collapse for high-level view
            >>> result = api.analytics_internal.expand_operations(False)
        """
        raw_data = self._repo_internal.expand_unit_flow_operations(
            expand, filter_data
        )
        return self._parse_flow_result(raw_data)
    
    # =========================================================================
    # Helper Methods
    # =========================================================================
    
    def _parse_flow_result(self, raw_data: Optional[Dict[str, Any]]) -> UnitFlowResult:
        """
        Parse raw API response into UnitFlowResult.
        
        Args:
            raw_data: Raw response from the API
            
        Returns:
            Parsed UnitFlowResult object
        """
        if raw_data is None:
            return UnitFlowResult(nodes=[], links=[])
        
        nodes = []
        links = []
        units = None
        total_units = None
        
        # Parse nodes
        if "nodes" in raw_data and isinstance(raw_data["nodes"], list):
            nodes = [UnitFlowNode.model_validate(n) for n in raw_data["nodes"]]
        
        # Parse links
        if "links" in raw_data and isinstance(raw_data["links"], list):
            links = [UnitFlowLink.model_validate(l) for l in raw_data["links"]]
        
        # Parse units if present
        if "units" in raw_data and isinstance(raw_data["units"], list):
            units = [UnitFlowUnit.model_validate(u) for u in raw_data["units"]]
        
        # Parse total count
        if "totalUnits" in raw_data:
            total_units = raw_data["totalUnits"]
        elif "total_units" in raw_data:
            total_units = raw_data["total_units"]
        
        return UnitFlowResult(
            nodes=nodes,
            links=links,
            units=units,
            total_units=total_units
        )
    
    def get_bottlenecks(
        self,
        filter_data: Optional[Union[UnitFlowFilter, Dict[str, Any]]] = None,
        min_yield_threshold: float = 90.0
    ) -> List[UnitFlowNode]:
        """
        Identify potential bottlenecks in the production flow.
        
        Returns nodes with yield below the specified threshold,
        sorted by yield (worst first).
        
        Args:
            filter_data: Filter criteria for the flow query
            min_yield_threshold: Yield threshold below which to flag as bottleneck (default 90%)
            
        Returns:
            List of UnitFlowNode objects representing potential bottlenecks
            
        Example:
            >>> # Find operations with less than 95% yield
            >>> bottlenecks = api.analytics_internal.get_bottlenecks(
            ...     filter_data=UnitFlowFilter(part_number="WIDGET-001"),
            ...     min_yield_threshold=95.0
            ... )
            >>> for node in bottlenecks:
            ...     print(f"⚠️ {node.name}: {node.yield_percent}% yield")
        """
        result = self.get_unit_flow(filter_data)
        
        bottlenecks = []
        for node in result.nodes or []:
            if node.yield_percent is not None and node.yield_percent < min_yield_threshold:
                bottlenecks.append(node)
        
        # Sort by yield (worst first)
        bottlenecks.sort(key=lambda n: n.yield_percent or 0)
        
        return bottlenecks
    
    def get_flow_summary(
        self,
        filter_data: Optional[Union[UnitFlowFilter, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Get a summary of the unit flow statistics.
        
        Provides high-level metrics about the production flow.
        
        Args:
            filter_data: Filter criteria for the flow query
            
        Returns:
            Dictionary with summary statistics
            
        Example:
            >>> summary = api.analytics_internal.get_flow_summary(
            ...     UnitFlowFilter(part_number="WIDGET-001")
            ... )
            >>> print(f"Total nodes: {summary['total_nodes']}")
            >>> print(f"Total units: {summary['total_units']}")
            >>> print(f"Average yield: {summary['avg_yield']:.1f}%")
        """
        result = self.get_unit_flow(filter_data)
        
        total_units = 0
        total_pass = 0
        total_fail = 0
        yields = []
        
        for node in result.nodes or []:
            if node.unit_count:
                total_units = max(total_units, node.unit_count)
            if node.pass_count:
                total_pass = max(total_pass, node.pass_count)
            if node.fail_count:
                total_fail = max(total_fail, node.fail_count)
            if node.yield_percent is not None:
                yields.append(node.yield_percent)
        
        avg_yield = sum(yields) / len(yields) if yields else 0.0
        min_yield = min(yields) if yields else 0.0
        max_yield = max(yields) if yields else 0.0
        
        return {
            "total_nodes": len(result.nodes or []),
            "total_links": len(result.links or []),
            "total_units": result.total_units or total_units,
            "passed_units": total_pass,
            "failed_units": total_fail,
            "avg_yield": avg_yield,
            "min_yield": min_yield,
            "max_yield": max_yield,
        }
