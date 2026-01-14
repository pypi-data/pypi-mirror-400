"""Analytics repository - internal API data access layer.

⚠️ INTERNAL API - SUBJECT TO CHANGE ⚠️

Uses internal WATS API endpoints that are not publicly documented.
These endpoints may change without notice. This module should be
replaced with public API endpoints as soon as they become available.

Unit Flow endpoints for production flow visualization:
- POST /api/internal/UnitFlow - Main query endpoint
- GET /api/internal/UnitFlow/Links - Get flow links
- GET /api/internal/UnitFlow/Nodes - Get flow nodes
- POST /api/internal/UnitFlow/SN - Query by serial numbers
- POST /api/internal/UnitFlow/SplitBy - Split flow by dimension
- POST /api/internal/UnitFlow/UnitOrder - Set unit ordering
- GET /api/internal/UnitFlow/Units - Get individual units

The internal API requires the Referer header to be set to the base URL.
"""
from typing import List, Optional, Dict, Any, Union

from ...core import HttpClient
from .models import (
    UnitFlowNode,
    UnitFlowLink,
    UnitFlowUnit,
    UnitFlowFilter,
    UnitFlowResult,
)


class AnalyticsRepositoryInternal:
    """
    Analytics data access layer using internal API.
    
    ⚠️ INTERNAL API - SUBJECT TO CHANGE ⚠️
    
    Provides access to Unit Flow functionality for production flow
    visualization and bottleneck analysis.
    
    Uses:
    - POST /api/internal/UnitFlow
    - GET /api/internal/UnitFlow/Links
    - GET /api/internal/UnitFlow/Nodes
    - POST /api/internal/UnitFlow/SN
    - POST /api/internal/UnitFlow/SplitBy
    - POST /api/internal/UnitFlow/UnitOrder
    - GET /api/internal/UnitFlow/Units
    
    The internal API requires the Referer header.
    """
    
    def __init__(self, http_client: HttpClient, base_url: str):
        """
        Initialize repository with HTTP client and base URL.
        
        Args:
            http_client: The HTTP client for API calls
            base_url: The base URL (needed for Referer header)
        """
        self._http = http_client
        self._base_url = base_url.rstrip('/')
    
    def _internal_get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Make an internal API GET request with Referer header.
        
        ⚠️ INTERNAL: Adds Referer header required by internal API.
        """
        response = self._http.get(
            endpoint,
            params=params,
            headers={"Referer": self._base_url}
        )
        if response.is_success:
            return response.data
        return None
    
    def _internal_post(self, endpoint: str, data: Any = None, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Make an internal API POST request with Referer header.
        
        ⚠️ INTERNAL: Adds Referer header required by internal API.
        """
        response = self._http.post(
            endpoint,
            data=data,
            params=params,
            headers={"Referer": self._base_url}
        )
        if response.is_success:
            return response.data
        return None
    
    # =========================================================================
    # Unit Flow Endpoints
    # =========================================================================
    
    def query_unit_flow(
        self, 
        filter_data: Optional[Union[UnitFlowFilter, Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Query unit flow data with filters.
        
        POST /api/internal/UnitFlow
        
        This is the main endpoint for unit flow queries. Returns nodes
        and links representing how units flow through production.
        
        Args:
            filter_data: UnitFlowFilter or dict with filter parameters
            
        Returns:
            Raw response data containing nodes and links, or None
        """
        if filter_data is None:
            data = {}
        elif isinstance(filter_data, UnitFlowFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = dict(filter_data)
        
        return self._internal_post("/api/internal/UnitFlow", data=data)
    
    def get_unit_flow_links(self) -> List[UnitFlowLink]:
        """
        Get all unit flow links.
        
        GET /api/internal/UnitFlow/Links
        
        Returns the links (edges) between nodes in the unit flow diagram.
        
        Returns:
            List of UnitFlowLink objects
        """
        data = self._internal_get("/api/internal/UnitFlow/Links")
        if data and isinstance(data, list):
            return [UnitFlowLink.model_validate(item) for item in data]
        return []
    
    def get_unit_flow_nodes(self) -> List[UnitFlowNode]:
        """
        Get all unit flow nodes.
        
        GET /api/internal/UnitFlow/Nodes
        
        Returns the nodes (operations/processes) in the unit flow diagram.
        
        Returns:
            List of UnitFlowNode objects
        """
        data = self._internal_get("/api/internal/UnitFlow/Nodes")
        if data and isinstance(data, list):
            return [UnitFlowNode.model_validate(item) for item in data]
        return []
    
    def query_unit_flow_by_serial_numbers(
        self, 
        serial_numbers: List[str],
        filter_data: Optional[Union[UnitFlowFilter, Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Query unit flow for specific serial numbers.
        
        POST /api/internal/UnitFlow/SN
        
        Traces the production flow path for specific units.
        
        Args:
            serial_numbers: List of serial numbers to query
            filter_data: Additional filter parameters
            
        Returns:
            Raw response data containing flow information, or None
        """
        if filter_data is None:
            data = {}
        elif isinstance(filter_data, UnitFlowFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = dict(filter_data)
        
        # Ensure serial numbers are included
        data["serialNumbers"] = serial_numbers
        
        return self._internal_post("/api/internal/UnitFlow/SN", data=data)
    
    def set_unit_flow_split_by(
        self, 
        split_by: str,
        filter_data: Optional[Union[UnitFlowFilter, Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Set the split-by dimension for unit flow analysis.
        
        POST /api/internal/UnitFlow/SplitBy
        
        Splits the flow diagram by a specific dimension (e.g., station, location).
        
        Args:
            split_by: Dimension to split by (e.g., "stationName", "location")
            filter_data: Additional filter parameters
            
        Returns:
            Raw response data with split flow, or None
        """
        if filter_data is None:
            data = {}
        elif isinstance(filter_data, UnitFlowFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = dict(filter_data)
        
        data["splitBy"] = split_by
        
        return self._internal_post("/api/internal/UnitFlow/SplitBy", data=data)
    
    def set_unit_flow_order(
        self, 
        unit_order: str,
        filter_data: Optional[Union[UnitFlowFilter, Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Set the unit ordering for flow analysis.
        
        POST /api/internal/UnitFlow/UnitOrder
        
        Controls how units are ordered in the flow visualization.
        
        Args:
            unit_order: Order specification (e.g., "startTime", "serialNumber")
            filter_data: Additional filter parameters
            
        Returns:
            Raw response data with ordered flow, or None
        """
        if filter_data is None:
            data = {}
        elif isinstance(filter_data, UnitFlowFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = dict(filter_data)
        
        data["unitOrder"] = unit_order
        
        return self._internal_post("/api/internal/UnitFlow/UnitOrder", data=data)
    
    def get_unit_flow_units(self) -> List[UnitFlowUnit]:
        """
        Get individual units from the unit flow.
        
        GET /api/internal/UnitFlow/Units
        
        Returns the list of individual units that have traversed the flow.
        
        Returns:
            List of UnitFlowUnit objects
        """
        data = self._internal_get("/api/internal/UnitFlow/Units")
        if data and isinstance(data, list):
            return [UnitFlowUnit.model_validate(item) for item in data]
        return []
    
    def set_unit_flow_visibility(
        self,
        show_list: Optional[List[str]] = None,
        hide_list: Optional[List[str]] = None,
        filter_data: Optional[Union[UnitFlowFilter, Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Control visibility of operations in the unit flow.
        
        POST /api/internal/UnitFlow (with showList/hideList)
        
        Show or hide specific operations/nodes in the flow diagram.
        This is related to the Show/HideList Operations feature.
        
        Args:
            show_list: List of operation IDs/names to show
            hide_list: List of operation IDs/names to hide
            filter_data: Additional filter parameters
            
        Returns:
            Raw response data with updated visibility, or None
        """
        if filter_data is None:
            data = {}
        elif isinstance(filter_data, UnitFlowFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = dict(filter_data)
        
        if show_list is not None:
            data["showList"] = show_list
        if hide_list is not None:
            data["hideList"] = hide_list
        
        return self._internal_post("/api/internal/UnitFlow", data=data)
    
    def expand_unit_flow_operations(
        self,
        expand: bool = True,
        filter_data: Optional[Union[UnitFlowFilter, Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Expand or collapse operations in the unit flow.
        
        POST /api/internal/UnitFlow (with expandOperations)
        
        Controls whether operations are shown expanded (showing sub-operations)
        or collapsed (aggregated view).
        
        Args:
            expand: True to expand, False to collapse
            filter_data: Additional filter parameters
            
        Returns:
            Raw response data with updated expansion, or None
        """
        if filter_data is None:
            data = {}
        elif isinstance(filter_data, UnitFlowFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = dict(filter_data)
        
        data["expandOperations"] = expand
        
        return self._internal_post("/api/internal/UnitFlow", data=data)
