"""Production repository - internal API data access layer.

⚠️ INTERNAL API - SUBJECT TO CHANGE ⚠️

Uses internal WATS API endpoints that are not publicly documented.
These endpoints may change without notice. This module should be
replaced with public API endpoints as soon as they become available.

The internal API requires the Referer header to be set to the base URL.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...core import HttpClient
from .models import UnitPhase


class ProductionRepositoryInternal:
    """
    Production data access layer using internal API.
    
    ⚠️ INTERNAL API - SUBJECT TO CHANGE ⚠️
    
    Uses:
    - GET /api/internal/Mes/GetUnitPhases
    - GET /api/internal/Production/GetUnit
    - GET /api/internal/Production/GetUnitHierarchy
    - GET /api/internal/Production/GetUnitStateHistory
    - GET /api/internal/Production/GetUnitPhase
    - GET /api/internal/Production/GetUnitProcess
    - GET /api/internal/Production/GetUnitInfo
    - GET /api/internal/Production/GetUnitContents
    - POST /api/internal/Production/CreateUnit
    - POST /api/internal/Production/AddChildUnit
    - POST /api/internal/Production/RemoveChildUnit
    - POST /api/internal/Production/RemoveAllChildUnits
    - GET /api/internal/Production/CheckChildUnits
    - GET /api/internal/Production/SerialNumbers
    - GET /api/internal/Production/SerialNumbers/Count
    - PUT /api/internal/Production/SerialNumbers/Free
    - DELETE /api/internal/Production/SerialNumbers/Free
    - GET /api/internal/Production/SerialNumbers/Ranges
    - GET /api/internal/Production/SerialNumbers/Statistics
    - GET /api/internal/Production/GetSites
    - GET /api/internal/Production/isConnected
    
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
    
    def _internal_post(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None
    ) -> Any:
        """
        Make an internal API POST request with Referer header.
        
        ⚠️ INTERNAL: Adds Referer header required by internal API.
        """
        response = self._http.post(
            endpoint,
            params=params,
            data=data,
            headers={"Referer": self._base_url}
        )
        if response.is_success:
            return response.data
        return None
    
    def _internal_put(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None
    ) -> Any:
        """
        Make an internal API PUT request with Referer header.
        
        ⚠️ INTERNAL: Adds Referer header required by internal API.
        """
        response = self._http.put(
            endpoint,
            params=params,
            data=data,
            headers={"Referer": self._base_url}
        )
        if response.is_success:
            return response.data
        return None
    
    def _internal_delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None
    ) -> bool:
        """
        Make an internal API DELETE request with Referer header.
        
        ⚠️ INTERNAL: Adds Referer header required by internal API.
        """
        response = self._http.delete(
            endpoint,
            params=params,
            data=data,
            headers={"Referer": self._base_url}
        )
        return response.is_success
    
    # =========================================================================
    # Connection Check
    # =========================================================================
    
    def is_connected(self) -> bool:
        """
        Check if Production module is connected.
        
        GET /api/internal/Production/isConnected
        
        ⚠️ INTERNAL API
        
        Returns:
            True if connected
        """
        result = self._internal_get("/api/internal/Production/isConnected")
        return result is not None
    
    # =========================================================================
    # Unit Phases (MES)
    # =========================================================================
    
    def get_unit_phases(self) -> List[UnitPhase]:
        """
        Get all available unit phases.

        GET /api/internal/Mes/GetUnitPhases

        ⚠️ INTERNAL API - Uses internal endpoint with Referer header.
        
        Unit phases define production workflow states (e.g., "In Test", 
        "Passed", "Failed", "In Repair").

        Returns:
            List of UnitPhase objects
        """
        data = self._internal_get("/api/internal/Mes/GetUnitPhases")
        if data:
            return [UnitPhase.model_validate(item) for item in data]
        return []
    
    # =========================================================================
    # Sites
    # =========================================================================
    
    def get_sites(self) -> List[Dict[str, Any]]:
        """
        Get all production sites.
        
        GET /api/internal/Production/GetSites
        
        ⚠️ INTERNAL API
        
        Returns:
            List of site dictionaries
        """
        data = self._internal_get("/api/internal/Production/GetSites")
        if data and isinstance(data, list):
            return data
        return []
    
    # =========================================================================
    # Unit Operations
    # =========================================================================
    
    def get_unit(
        self,
        serial_number: str,
        part_number: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get a unit by serial number.
        
        GET /api/internal/Production/GetUnit
        
        ⚠️ INTERNAL API
        
        Args:
            serial_number: Unit serial number (required)
            part_number: Unit part number (optional)
            
        Returns:
            Unit data dictionary or None if not found
        """
        params: Dict[str, Any] = {"serialNumber": serial_number}
        if part_number:
            params["partNumber"] = part_number
        return self._internal_get("/api/internal/Production/GetUnit", params)
    
    def get_unit_info(
        self,
        serial_number: str,
        part_number: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get unit information.
        
        GET /api/internal/Production/GetUnitInfo
        
        ⚠️ INTERNAL API
        
        Args:
            serial_number: Unit serial number
            part_number: Unit part number
            
        Returns:
            Unit info dictionary or None
        """
        params = {"serialNumber": serial_number, "partNumber": part_number}
        return self._internal_get("/api/internal/Production/GetUnitInfo", params)
    
    def get_unit_hierarchy(
        self,
        serial_number: str,
        part_number: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the complete unit hierarchy (parent/child relationships).
        
        GET /api/internal/Production/GetUnitHierarchy
        
        ⚠️ INTERNAL API
        
        Args:
            serial_number: Unit serial number
            part_number: Unit part number
            
        Returns:
            Hierarchy data dictionary or None
        """
        params = {"serialNumber": serial_number, "partNumber": part_number}
        return self._internal_get("/api/internal/Production/GetUnitHierarchy", params)
    
    def get_unit_state_history(
        self,
        serial_number: str,
        part_number: str
    ) -> List[Dict[str, Any]]:
        """
        Get the unit state change history.
        
        GET /api/internal/Production/GetUnitStateHistory
        
        ⚠️ INTERNAL API
        
        Args:
            serial_number: Unit serial number
            part_number: Unit part number
            
        Returns:
            List of state change records
        """
        params = {"serialNumber": serial_number, "partNumber": part_number}
        data = self._internal_get("/api/internal/Production/GetUnitStateHistory", params)
        if data and isinstance(data, list):
            return data
        return []
    
    def get_unit_phase(
        self,
        serial_number: str,
        part_number: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the current phase of a unit.
        
        GET /api/internal/Production/GetUnitPhase
        
        ⚠️ INTERNAL API
        
        Args:
            serial_number: Unit serial number
            part_number: Unit part number
            
        Returns:
            Phase data dictionary or None
        """
        params = {"serialNumber": serial_number, "partNumber": part_number}
        return self._internal_get("/api/internal/Production/GetUnitPhase", params)
    
    def get_unit_process(
        self,
        serial_number: str,
        part_number: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the current process of a unit.
        
        GET /api/internal/Production/GetUnitProcess
        
        ⚠️ INTERNAL API
        
        Args:
            serial_number: Unit serial number
            part_number: Unit part number
            
        Returns:
            Process data dictionary or None
        """
        params = {"serialNumber": serial_number, "partNumber": part_number}
        return self._internal_get("/api/internal/Production/GetUnitProcess", params)
    
    def get_unit_contents(
        self,
        serial_number: str,
        part_number: str,
        revision: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get unit contents (BOM/components).
        
        GET /api/internal/Production/GetUnitContents
        
        ⚠️ INTERNAL API
        
        Args:
            serial_number: Unit serial number
            part_number: Unit part number
            revision: Unit revision
            
        Returns:
            Contents data dictionary or None
        """
        params = {
            "serialNumber": serial_number,
            "partNumber": part_number,
            "revision": revision
        }
        return self._internal_get("/api/internal/Production/GetUnitContents", params)
    
    def create_unit(
        self,
        serial_number: str,
        part_number: str,
        revision: str,
        batch_number: Optional[str] = None,
        unit_phase: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new unit in the production system.
        
        POST /api/internal/Production/CreateUnit
        
        ⚠️ INTERNAL API
        
        Args:
            serial_number: Unit serial number
            part_number: Unit part number
            revision: Unit revision
            batch_number: Optional batch number
            unit_phase: Optional initial unit phase ID
            
        Returns:
            Created unit data or None
        """
        params: Dict[str, Any] = {
            "serialNumber": serial_number,
            "partNumber": part_number,
            "revision": revision
        }
        if batch_number:
            params["batchNumber"] = batch_number
        if unit_phase is not None:
            params["unitPhase"] = unit_phase
        return self._internal_post("/api/internal/Production/CreateUnit", params=params)
    
    # =========================================================================
    # Child Unit Operations
    # =========================================================================
    
    def add_child_unit(
        self,
        serial_number: str,
        part_number: str,
        child_serial_number: str,
        child_part_number: str,
        check_part_number: str,
        check_revision: str,
        culture_code: str = "en-US",
        check_phase: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Add a child unit to a parent unit.
        
        POST /api/internal/Production/AddChildUnit
        
        ⚠️ INTERNAL API
        
        Args:
            serial_number: Parent unit serial number
            part_number: Parent unit part number
            child_serial_number: Child unit serial number
            child_part_number: Child unit part number
            check_part_number: Part number to check against
            check_revision: Revision to check against
            culture_code: Culture code for error messages (default: en-US)
            check_phase: Whether to check phase compatibility
            
        Returns:
            Result data or None
        """
        params: Dict[str, Any] = {
            "serialNumber": serial_number,
            "partNumber": part_number,
            "childSerialNumber": child_serial_number,
            "childPartNumber": child_part_number,
            "checkPartNumber": check_part_number,
            "checkRevision": check_revision,
            "cultureCode": culture_code
        }
        if check_phase is not None:
            params["checkPhase"] = check_phase
        return self._internal_post("/api/internal/Production/AddChildUnit", params=params)
    
    def remove_child_unit(
        self,
        serial_number: str,
        part_number: str,
        child_serial_number: str,
        child_part_number: str,
        culture_code: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Remove a child unit from a parent unit.
        
        POST /api/internal/Production/RemoveChildUnit
        
        ⚠️ INTERNAL API
        
        Args:
            serial_number: Parent unit serial number
            part_number: Parent unit part number
            child_serial_number: Child unit serial number
            child_part_number: Child unit part number
            culture_code: Optional culture code for error messages
            
        Returns:
            Result data or None
        """
        params: Dict[str, Any] = {
            "serialNumber": serial_number,
            "partNumber": part_number,
            "childSerialNumber": child_serial_number,
            "childPartNumber": child_part_number
        }
        if culture_code:
            params["cultureCode"] = culture_code
        return self._internal_post("/api/internal/Production/RemoveChildUnit", params=params)
    
    def remove_all_child_units(
        self,
        serial_number: str,
        part_number: str,
        culture_code: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Remove all child units from a parent unit.
        
        POST /api/internal/Production/RemoveAllChildUnits
        
        ⚠️ INTERNAL API
        
        Args:
            serial_number: Parent unit serial number
            part_number: Parent unit part number
            culture_code: Optional culture code for error messages
            
        Returns:
            Result data or None
        """
        params: Dict[str, Any] = {
            "serialNumber": serial_number,
            "partNumber": part_number
        }
        if culture_code:
            params["cultureCode"] = culture_code
        return self._internal_post("/api/internal/Production/RemoveAllChildUnits", params=params)
    
    def check_child_units(
        self,
        parent_serial_number: str,
        parent_part_number: str,
        culture_code: str = "en-US"
    ) -> Optional[Dict[str, Any]]:
        """
        Check child units of a parent unit.
        
        GET /api/internal/Production/CheckChildUnits
        
        ⚠️ INTERNAL API
        
        Args:
            parent_serial_number: Parent unit serial number
            parent_part_number: Parent unit part number
            culture_code: Culture code for error messages
            
        Returns:
            Check result data or None
        """
        params = {
            "ParentSerialNumber": parent_serial_number,
            "ParentPartNumber": parent_part_number,
            "CultureCode": culture_code
        }
        return self._internal_get("/api/internal/Production/CheckChildUnits", params)
    
    # =========================================================================
    # Serial Number Management
    # =========================================================================
    
    def find_serial_numbers(
        self,
        serial_number_type: str,
        start_address: str,
        end_address: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Find all serial numbers in a range.
        
        GET /api/internal/Production/SerialNumbers
        
        ⚠️ INTERNAL API
        
        Args:
            serial_number_type: Type of serial numbers to find
            start_address: Start of range
            end_address: End of range
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of serial number records
        """
        params: Dict[str, Any] = {
            "serialNumberType": serial_number_type,
            "startAddress": start_address,
            "endAddress": end_address
        }
        if start_date:
            params["startDate"] = start_date.isoformat()
        if end_date:
            params["endDate"] = end_date.isoformat()
        data = self._internal_get("/api/internal/Production/SerialNumbers", params)
        if data and isinstance(data, list):
            return data
        return []
    
    def get_serial_number_count(
        self,
        serial_number_type: str,
        start_address: Optional[str] = None,
        end_address: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> Optional[int]:
        """
        Get count of serial numbers in a range.
        
        GET /api/internal/Production/SerialNumbers/Count
        
        ⚠️ INTERNAL API
        
        Args:
            serial_number_type: Type of serial numbers to count
            start_address: Optional start of range
            end_address: Optional end of range
            from_date: Optional start date filter
            to_date: Optional end date filter
            
        Returns:
            Count of serial numbers or None
        """
        params: Dict[str, Any] = {"serialNumberType": serial_number_type}
        if start_address:
            params["startAddress"] = start_address
        if end_address:
            params["endAddress"] = end_address
        if from_date:
            params["fromDate"] = from_date.isoformat()
        if to_date:
            params["toDate"] = to_date.isoformat()
        return self._internal_get("/api/internal/Production/SerialNumbers/Count", params)
    
    def free_serial_numbers(
        self,
        ranges: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Free reserved serial numbers in specified ranges.
        
        PUT /api/internal/Production/SerialNumbers/Free
        
        ⚠️ INTERNAL API
        
        Does not affect taken serial numbers.
        
        Args:
            ranges: List of range definitions with serialNumberType, startAddress, endAddress
            
        Returns:
            Result data or None
        """
        return self._internal_put(
            "/api/internal/Production/SerialNumbers/Free",
            data=ranges
        )
    
    def delete_free_serial_numbers(
        self,
        ranges: List[Dict[str, Any]]
    ) -> bool:
        """
        Delete free serial numbers in specified ranges.
        
        DELETE /api/internal/Production/SerialNumbers/Free
        
        ⚠️ INTERNAL API
        
        Does not affect taken serial numbers.
        
        Args:
            ranges: List of range definitions with serialNumberType, startAddress, endAddress
            
        Returns:
            True if successful
        """
        return self._internal_delete(
            "/api/internal/Production/SerialNumbers/Free",
            data=ranges
        )
    
    def get_serial_number_ranges(
        self,
        serial_number_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get current serial number ranges.
        
        GET /api/internal/Production/SerialNumbers/Ranges
        
        ⚠️ INTERNAL API
        
        Args:
            serial_number_type: Optional filter by type
            
        Returns:
            List of range records
        """
        params: Dict[str, Any] = {}
        if serial_number_type:
            params["serialNumberType"] = serial_number_type
        data = self._internal_get(
            "/api/internal/Production/SerialNumbers/Ranges",
            params if params else None
        )
        if data and isinstance(data, list):
            return data
        return []
    
    def get_serial_number_statistics(
        self,
        serial_number_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get statistics for serial numbers.
        
        GET /api/internal/Production/SerialNumbers/Statistics
        
        ⚠️ INTERNAL API
        
        Args:
            serial_number_type: Optional filter by type
            
        Returns:
            Statistics data or None
        """
        params: Dict[str, Any] = {}
        if serial_number_type:
            params["serialNumberType"] = serial_number_type
        return self._internal_get(
            "/api/internal/Production/SerialNumbers/Statistics",
            params if params else None
        )
