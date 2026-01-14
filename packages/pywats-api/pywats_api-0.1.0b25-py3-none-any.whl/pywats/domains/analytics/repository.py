"""Analytics repository - data access layer.

All API interactions for statistics, KPIs, yield analysis, and dashboard data.
Note: Maps to the WATS /api/App/* endpoints (backend naming).
"""
from typing import Optional, List, Dict, Any, Union, TYPE_CHECKING, cast
import logging

if TYPE_CHECKING:
    from ...core import HttpClient
    from ...core.exceptions import ErrorHandler

from .models import (
    YieldData,
    ProcessInfo,
    LevelInfo,
    ProductGroup,
    StepAnalysisRow,
    TopFailedStep,
    RepairStatistics,
    RepairHistoryRecord,
    MeasurementData,
    AggregatedMeasurement,
    OeeAnalysisResult,
)
from ..report.models import WATSFilter, ReportHeader


class AnalyticsRepository:
    """
    Analytics/Statistics data access layer.

    Handles all WATS API interactions for statistics, KPIs, and yield analysis.
    Maps to /api/App/* endpoints on the backend.
    """

    def __init__(
        self, 
        http_client: "HttpClient",
        error_handler: Optional["ErrorHandler"] = None
    ):
        """
        Initialize with HTTP client.

        Args:
            http_client: HttpClient for making HTTP requests
            error_handler: ErrorHandler for response handling (optional for backward compat)
        """
        from ...core.exceptions import ErrorHandler, ErrorMode
        self._http_client = http_client
        self._error_handler = error_handler or ErrorHandler(ErrorMode.STRICT)

    # =========================================================================
    # System Info
    # =========================================================================

    def get_version(self) -> Optional[str]:
        """
        Get server/api version.

        GET /api/App/Version

        Returns:
            Version string (e.g., "24.1.0") or None
        """
        response = self._http_client.get("/api/App/Version")
        data = self._error_handler.handle_response(
            response, operation="get_version", allow_empty=True
        )
        return str(data) if data else None

    def get_processes(
        self,
        include_test_operations: Optional[bool] = None,
        include_repair_operations: Optional[bool] = None,
        include_wip_operations: Optional[bool] = None,
        include_inactive_processes: Optional[bool] = None,
    ) -> List[ProcessInfo]:
        """
        Get processes with optional filtering.

        GET /api/App/Processes

        By default (no filters), retrieves active processes marked as 
        isTestOperation, isRepairOperation, or isWipOperation.

        Args:
            include_test_operations: Include processes marked as IsTestOperation
            include_repair_operations: Include processes marked as IsRepairOperation
            include_wip_operations: Include processes marked as IsWipOperation
            include_inactive_processes: Include inactive processes

        Returns:
            List of ProcessInfo objects
        """
        params: Dict[str, Any] = {}
        if include_test_operations is not None:
            params["includeTestOperations"] = include_test_operations
        if include_repair_operations is not None:
            params["includeRepairOperations"] = include_repair_operations
        if include_wip_operations is not None:
            params["includeWipOperations"] = include_wip_operations
        if include_inactive_processes is not None:
            params["includeInactiveProcesses"] = include_inactive_processes

        response = self._http_client.get(
            "/api/App/Processes", 
            params=params if params else None
        )
        data = self._error_handler.handle_response(
            response, operation="get_processes", allow_empty=True
        )
        if data:
            return [ProcessInfo.model_validate(item) for item in data]
        return []

    def get_levels(self) -> List[LevelInfo]:
        """
        Retrieves all ClientGroups (levels).

        GET /api/App/Levels

        Returns:
            List of LevelInfo objects
        """
        response = self._http_client.get("/api/App/Levels")
        data = self._error_handler.handle_response(
            response, operation="get_levels", allow_empty=True
        )
        if data:
            return [LevelInfo.model_validate(item) for item in data]
        return []

    def get_product_groups(
        self,
        include_filters: Optional[bool] = None
    ) -> List[ProductGroup]:
        """
        Retrieves all ProductGroups.

        GET /api/App/ProductGroups

        Args:
            include_filters: Include or exclude product group filters (default: None)

        Returns:
            List of ProductGroup objects
        """
        params: Dict[str, Any] = {}
        if include_filters is not None:
            params["includeFilters"] = include_filters

        response = self._http_client.get(
            "/api/App/ProductGroups",
            params=params if params else None
        )
        data = self._error_handler.handle_response(
            response, operation="get_product_groups", allow_empty=True
        )
        if data:
            return [ProductGroup.model_validate(item) for item in data]
        return []

    # =========================================================================
    # Yield Statistics
    # =========================================================================

    def get_dynamic_yield(
        self, filter_data: Union[WATSFilter, Dict[str, Any]]
    ) -> List[YieldData]:
        """
        Calculate yield by custom dimensions (PREVIEW).

        POST /api/App/DynamicYield

        Args:
            filter_data: WATSFilter object or dict with:
                - dimensions (str): Semicolon-separated list of dimensions and KPIs.
                  Order and direction are specified here (e.g., "unitCount desc;partNumber").
                  
                  Supported dimensions:
                  partNumber, productName, stationName, location, purpose, revision,
                  testOperation, processCode, swFilename, swVersion, productGroup, level,
                  period, batchNumber, operator, fixtureId, socketIndex, errorCode,
                  miscInfoDescription, miscInfoString, stepCausedUutFailure,
                  stepPathCausedUutFailure, assetSerialNumber, assetName
                  
                  Supported KPIs (can be ordered with asc/desc):
                  unitCount, fpCount, spCount, tpCount, lpCount, fpy, spy, tpy, lpy,
                  testYieldCount, testReportCount, testYield, firstUtc, lastUtc,
                  fpFailCount, spFailCount, tpFailCount, lpFailCount, retestCount,
                  ppmFpy, ppmSpy, ppmTpy, ppmLpy, ppmTestYield
                  
                - period_count (int): Number of time periods to return
                - date_grouping (DateGrouping): Period grouping (HOUR, DAY, WEEK, MONTH, etc.)
                - top_count (int): Limit results to top N entries
                - Other standard WATSFilter fields (part_number, station_name, etc.)

        Returns:
            List of YieldData objects ordered as specified in dimensions
            
        Examples:
            >>> # Top 10 products by unit count, last 30 days
            >>> filter = WATSFilter(
            ...     dimensions="unitCount desc;partNumber;testOperation",
            ...     period_count=30,
            ...     date_grouping=DateGrouping.DAY,
            ...     top_count=10
            ... )
            >>> 
            >>> # Yield by station and period
            >>> filter = WATSFilter(
            ...     dimensions="stationName;period;fpy desc",
            ...     period_count=7,
            ...     date_grouping=DateGrouping.DAY,
            ...     part_number="WIDGET-001"
            ... )

        Note:
            - Results are ordered by the sequence in the dimensions parameter
            - Direction hints: "asc" (ascending) or "desc" (descending)
            - Only requested KPIs are returned (all if none specified)
            - When using period-based filtering, includeCurrentPeriod defaults to True
        """
        if isinstance(filter_data, WATSFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = dict(filter_data) if filter_data else {}

        # IMPORTANT: When using period-based filtering, the API requires
        # includeCurrentPeriod=True to return results (server behavior).
        # Default to True if periodCount or dateGrouping is set but
        # includeCurrentPeriod is not explicitly provided.
        if ("periodCount" in data or "dateGrouping" in data) and "includeCurrentPeriod" not in data:
            data["includeCurrentPeriod"] = True

        # Some WATS servers require `dimensions` in the query string.
        # To be robust across server versions:
        # - If the payload is only `dimensions`, send it as query param + empty JSON body.
        # - If there are other filters, keep `dimensions` in the body and also send it
        #   as a query param.
        params: Optional[Dict[str, Any]] = None
        if isinstance(data, dict) and data.get("dimensions"):
            dimensions = data.get("dimensions")
            params = {"dimensions": dimensions}
            if len(data.keys()) == 1:
                data = {}

        # Always send an object body (not null) for these preview endpoints.
        if not data:
            data = {}

        response = self._http_client.post(
            "/api/App/DynamicYield", data=data, params=params
        )
        result = self._error_handler.handle_response(
            response, operation="get_dynamic_yield", allow_empty=True
        )
        if result:
            return [YieldData.model_validate(item) for item in result]
        return []

    def get_volume_yield(
        self,
        filter_data: Optional[Union[WATSFilter, Dict[str, Any]]] = None,
        product_group: Optional[str] = None,
        level: Optional[str] = None,
    ) -> List[YieldData]:
        """
        Volume/Yield list.

        GET/POST /api/App/VolumeYield

        Args:
            filter_data: WATSFilter object or dict (for POST)
            product_group: Product group filter (for GET)
            level: Level filter (for GET)

        Returns:
            List of YieldData objects
        """
        if filter_data:
            if isinstance(filter_data, WATSFilter):
                data = filter_data.model_dump(by_alias=True, exclude_none=True)
            else:
                data = filter_data
            response = self._http_client.post("/api/App/VolumeYield", data=data)
        else:
            params: Dict[str, Any] = {}
            if product_group:
                params["productGroup"] = product_group
            if level:
                params["level"] = level
            response = self._http_client.get(
                "/api/App/VolumeYield", params=params if params else None
            )
        result = self._error_handler.handle_response(
            response, operation="get_volume_yield", allow_empty=True
        )
        if result:
            return [YieldData.model_validate(item) for item in result]
        return []

    def get_high_volume(
        self,
        filter_data: Optional[Union[WATSFilter, Dict[str, Any]]] = None,
        product_group: Optional[str] = None,
        level: Optional[str] = None,
    ) -> List[YieldData]:
        """
        High Volume list.

        GET/POST /api/App/HighVolume

        Args:
            filter_data: WATSFilter object or dict (for POST)
            product_group: Product group filter (for GET)
            level: Level filter (for GET)

        Returns:
            List of YieldData objects
        """
        if filter_data:
            if isinstance(filter_data, WATSFilter):
                data = filter_data.model_dump(by_alias=True, exclude_none=True)
            else:
                data = filter_data
            response = self._http_client.post("/api/App/HighVolume", data=data)
        else:
            params: Dict[str, Any] = {}
            if product_group:
                params["productGroup"] = product_group
            if level:
                params["level"] = level
            response = self._http_client.get(
                "/api/App/HighVolume", params=params if params else None
            )
        result = self._error_handler.handle_response(
            response, operation="get_high_volume", allow_empty=True
        )
        if result:
            return [YieldData.model_validate(item) for item in result]
        return []

    def get_high_volume_by_product_group(
        self, filter_data: Union[WATSFilter, Dict[str, Any]]
    ) -> List[YieldData]:
        """
        Yield by product group sorted by volume.

        POST /api/App/HighVolumeByProductGroup

        Args:
            filter_data: WATSFilter object or dict

        Returns:
            List of YieldData objects
        """
        if isinstance(filter_data, WATSFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = filter_data
        response = self._http_client.post(
            "/api/App/HighVolumeByProductGroup", data=data
        )
        result = self._error_handler.handle_response(
            response, operation="get_high_volume_by_product_group", allow_empty=True
        )
        if result:
            return [YieldData.model_validate(item) for item in result]
        return []

    def get_worst_yield(
        self,
        filter_data: Optional[Union[WATSFilter, Dict[str, Any]]] = None,
        product_group: Optional[str] = None,
        level: Optional[str] = None,
    ) -> List[YieldData]:
        """
        Worst Yield list.

        GET/POST /api/App/WorstYield

        Args:
            filter_data: WATSFilter object or dict (for POST)
            product_group: Product group filter (for GET)
            level: Level filter (for GET)

        Returns:
            List of YieldData objects
        """
        if filter_data:
            if isinstance(filter_data, WATSFilter):
                data = filter_data.model_dump(by_alias=True, exclude_none=True)
            else:
                data = filter_data
            response = self._http_client.post("/api/App/WorstYield", data=data)
        else:
            params: Dict[str, Any] = {}
            if product_group:
                params["productGroup"] = product_group
            if level:
                params["level"] = level
            response = self._http_client.get(
                "/api/App/WorstYield", params=params if params else None
            )
        result = self._error_handler.handle_response(
            response, operation="get_worst_yield", allow_empty=True
        )
        if result:
            return [YieldData.model_validate(item) for item in result]
        return []

    def get_worst_yield_by_product_group(
        self, filter_data: Union[WATSFilter, Dict[str, Any]]
    ) -> List[YieldData]:
        """
        Yield by product group sorted by lowest yield.

        POST /api/App/WorstYieldByProductGroup

        Args:
            filter_data: WATSFilter object or dict

        Returns:
            List of YieldData objects
        """
        if isinstance(filter_data, WATSFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = filter_data
        response = self._http_client.post(
            "/api/App/WorstYieldByProductGroup", data=data
        )
        result = self._error_handler.handle_response(
            response, operation="get_worst_yield_by_product_group", allow_empty=True
        )
        if result:
            return [YieldData.model_validate(item) for item in result]
        return []

    # =========================================================================
    # Repair Statistics
    # =========================================================================

    def get_dynamic_repair(
        self, filter_data: Union[WATSFilter, Dict[str, Any]]
    ) -> List[RepairStatistics]:
        """
        Calculate repair statistics by custom dimensions (PREVIEW).

        POST /api/App/DynamicRepair

        Args:
            filter_data: WATSFilter object or dict with:
                - dimensions (str): Semicolon-separated list of dimensions and KPIs.
                  Order and direction are specified here (e.g., "repairCount desc;partNumber").
                  
                  Supported dimensions:
                  partNumber, revision, productName, productGroup, unitType, repairOperation,
                  period, level, stationName, location, purpose, operator,
                  miscInfoDescription, miscInfoString, repairCode, repairCategory,
                  repairType, componentRef, componentNumber, componentRevision,
                  componentVendor, componentDescription, functionBlock, referencedStep,
                  referencedStepPath, testOperation, testPeriod, testLevel,
                  testStationName, testLocation, testPurpose, testOperator,
                  batchNumber, swFilename, swVersion
                  
                  Supported KPIs (can be ordered with asc/desc):
                  repairReportCount, repairCount
                  
                - period_count (int): Number of time periods to return
                - date_grouping (DateGrouping): Period grouping (HOUR, DAY, WEEK, MONTH, etc.)
                - top_count (int): Limit results to top N entries
                - Other standard WATSFilter fields (part_number, repair_operation, etc.)

        Returns:
            List of RepairStatistics objects ordered as specified in dimensions
            
        Examples:
            >>> # Top 10 by repair count, last 30 days
            >>> filter = WATSFilter(
            ...     dimensions="repairCount desc;repairReportCount desc;partNumber;repairOperation",
            ...     period_count=30,
            ...     date_grouping=DateGrouping.DAY,
            ...     top_count=10
            ... )
            >>> 
            >>> # Repairs by operation and period
            >>> filter = WATSFilter(
            ...     dimensions="repairOperation;period;repairCount desc",
            ...     period_count=7,
            ...     date_grouping=DateGrouping.DAY
            ... )

        Note:
            - Results are ordered by the sequence in the dimensions parameter
            - Direction hints: "asc" (ascending) or "desc" (descending)
            - Only requested KPIs are returned (all if none specified)
            - When using period-based filtering, includeCurrentPeriod defaults to True
        """
        if isinstance(filter_data, WATSFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = dict(filter_data) if filter_data else {}

        # IMPORTANT: When using period-based filtering, the API requires
        # includeCurrentPeriod=True to return results (server behavior).
        # Default to True if periodCount or dateGrouping is set but
        # includeCurrentPeriod is not explicitly provided.
        if ("periodCount" in data or "dateGrouping" in data) and "includeCurrentPeriod" not in data:
            data["includeCurrentPeriod"] = True

        # Some WATS servers require `dimensions` in the query string.
        # To be robust across server versions:
        # - If the payload is only `dimensions`, send it as query param + empty JSON body.
        # - If there are other filters, keep `dimensions` in the body and also send it
        #   as a query param.
        params: Optional[Dict[str, Any]] = None
        if isinstance(data, dict) and data.get("dimensions"):
            dimensions = data.get("dimensions")
            params = {"dimensions": dimensions}
            if len(data.keys()) == 1:
                data = {}

        # Always send an object body (not null) for these preview endpoints.
        if not data:
            data = {}

        response = self._http_client.post(
            "/api/App/DynamicRepair", data=data, params=params
        )
        result = self._error_handler.handle_response(
            response, operation="get_dynamic_repair", allow_empty=True
        )
        if result:
            items = result if isinstance(result, list) else [result]
            return [RepairStatistics.model_validate(item) for item in items]
        return []

    def get_related_repair_history(
        self, part_number: str, revision: str
    ) -> List[RepairHistoryRecord]:
        """
        Get list of repaired failures related to the part number and revision.

        GET /api/App/RelatedRepairHistory

        Args:
            part_number: Product part number
            revision: Product revision

        Returns:
            List of RepairHistoryRecord objects with repair details
        """
        params: Dict[str, Any] = {
            "partNumber": part_number,
            "revision": revision,
        }
        response = self._http_client.get(
            "/api/App/RelatedRepairHistory", params=params
        )
        result = self._error_handler.handle_response(
            response, operation="get_related_repair_history", allow_empty=True
        )
        if result:
            items = result if isinstance(result, list) else [result]
            return [RepairHistoryRecord.model_validate(item) for item in items]
        return []

    # =========================================================================
    # Failure Analysis
    # =========================================================================

    def get_top_failed(
        self,
        filter_data: Optional[Union[WATSFilter, Dict[str, Any]]] = None,
        *,
        product_group: Optional[str] = None,
        level: Optional[str] = None,
        part_number: Optional[str] = None,
        revision: Optional[str] = None,
        top_count: Optional[int] = None,
    ) -> List[TopFailedStep]:
        """
        Get the top failed steps.

        GET/POST /api/App/TopFailed

        Args:
            filter_data: WATSFilter object or dict (for POST)
            product_group: Filter by product group (GET only)
            level: Filter by production level (GET only)
            part_number: Filter by part number (GET only)
            revision: Filter by revision (GET only)
            top_count: Maximum number of results (GET only)

        Returns:
            List of TopFailedStep objects with failure statistics
        """
        if filter_data:
            if isinstance(filter_data, WATSFilter):
                data = filter_data.model_dump(by_alias=True, exclude_none=True)
            else:
                data = filter_data
            response = self._http_client.post("/api/App/TopFailed", data=data)
        else:
            params: Dict[str, Any] = {}
            if product_group:
                params["productGroup"] = product_group
            if level:
                params["level"] = level
            if part_number:
                params["partNumber"] = part_number
            if revision:
                params["revision"] = revision
            if top_count is not None:
                params["topCount"] = top_count
            response = self._http_client.get(
                "/api/App/TopFailed", params=params if params else None
            )
        result = self._error_handler.handle_response(
            response, operation="get_top_failed", allow_empty=True
        )
        if result:
            items = result if isinstance(result, list) else [result]
            return [TopFailedStep.model_validate(item) for item in items]
        return []

    def get_test_step_analysis(
        self, filter_data: Union[WATSFilter, Dict[str, Any]]
    ) -> List[StepAnalysisRow]:
        """
        Get step and measurement statistics (PREVIEW).

        POST /api/App/TestStepAnalysis

        Args:
            filter_data: WATSFilter object or dict

        Returns:
            List of StepAnalysisRow rows
        """
        if isinstance(filter_data, WATSFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = filter_data
        response = self._http_client.post("/api/App/TestStepAnalysis", data=data)
        result = self._error_handler.handle_response(
            response, operation="get_test_step_analysis", allow_empty=True
        )
        if result:
            raw_items: List[Any]
            if isinstance(result, list):
                raw_items = result
            else:
                raw_items = [result]
            return [StepAnalysisRow.model_validate(item) for item in raw_items]
        return []

    # =========================================================================
    # Measurements
    # =========================================================================

    @staticmethod
    def _normalize_measurement_path(path: str) -> str:
        """
        Convert user-friendly path format to API format.
        
        The API expects paths using paragraph mark (¶) as separator:
        - "MainSequence¶Step Group¶Step Name" for steps
        - "MainSequence¶Step Group¶Step Name¶¶MeasurementName" for multi-numeric
        
        This method converts common formats:
        - "/" separator -> "¶"
        - "::" for measurement name -> "¶¶"
        
        Args:
            path: User-provided path (e.g., "Main/Step/Test" or "Main/Step/Test::Meas1")
            
        Returns:
            API-formatted path with ¶ separators
        """
        if not path:
            return path
        
        # Already in API format
        if "¶" in path:
            return path
        
        # Handle measurement name separator (:: -> ¶¶)
        if "::" in path:
            step_path, measurement_name = path.rsplit("::", 1)
            step_path = step_path.replace("/", "¶")
            return f"{step_path}¶¶{measurement_name}"
        
        # Simple path conversion
        return path.replace("/", "¶")

    def get_measurements(
        self, 
        filter_data: Union[WATSFilter, Dict[str, Any]],
        *,
        measurement_paths: Optional[str] = None,
    ) -> List[MeasurementData]:
        """
        Get numeric measurements by measurement path (PREVIEW).

        POST /api/App/Measurements

        IMPORTANT: This API requires partNumber and testOperation filters.
        Without them, it returns measurements from the last 7 days of most 
        failed steps, which can cause timeouts.

        Args:
            filter_data: WATSFilter object or dict with filters. 
                REQUIRED: part_number and test_operation to avoid timeout.
            measurement_paths: Measurement path(s) as query parameter.
                Format: "Step Group¶Step Name¶¶MeasurementName"
                Multiple paths separated by semicolon (;)
                Can use "/" which will be converted to "¶"

        Returns:
            List of MeasurementData objects with individual measurement values
            
        Example:
            >>> # Get specific measurement with proper filters
            >>> data = analytics.get_measurements(
            ...     WATSFilter(part_number="PROD-001", test_operation="EOL Test"),
            ...     measurement_paths="Main¶Voltage Test¶¶Output"
            ... )
        """
        if isinstance(filter_data, WATSFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = dict(filter_data)
        
        # Build query params for measurementPaths
        params: Dict[str, str] = {}
        
        # Check for measurement_path in data (legacy support) and move to query param
        if "measurement_path" in data:
            measurement_paths = measurement_paths or data.pop("measurement_path")
        if "measurementPath" in data:
            measurement_paths = measurement_paths or data.pop("measurementPath")
            
        if measurement_paths:
            params["measurementPaths"] = self._normalize_measurement_path(measurement_paths)
        
        response = self._http_client.post(
            "/api/App/Measurements", 
            data=data,
            params=params if params else None
        )
        result = self._error_handler.handle_response(
            response, operation="get_measurements", allow_empty=True
        )
        if result:
            # API returns nested structure: [{measurementPath, measurements: [...]}]
            # Extract the nested measurements arrays
            all_measurements = []
            items = result if isinstance(result, list) else [result]
            for item in items:
                if isinstance(item, dict) and "measurements" in item:
                    # New API format with nested measurements array
                    for m in item.get("measurements", []):
                        all_measurements.append(MeasurementData.model_validate(m))
                else:
                    # Legacy flat format (backwards compat)
                    all_measurements.append(MeasurementData.model_validate(item))
            return all_measurements
        return []

    def get_aggregated_measurements(
        self, 
        filter_data: Union[WATSFilter, Dict[str, Any]],
        *,
        measurement_paths: Optional[str] = None,
    ) -> List[AggregatedMeasurement]:
        """
        Get aggregated numeric measurements by measurement path.

        POST /api/App/AggregatedMeasurements

        IMPORTANT: This API requires partNumber and testOperation filters.
        Without them, it returns measurements from the last 7 days of most 
        failed steps, which can cause timeouts.

        Args:
            filter_data: WATSFilter object or dict with filters.
                REQUIRED: part_number and test_operation to avoid timeout.
            measurement_paths: Measurement path(s) as query parameter.
                Format: "Step Group¶Step Name¶¶MeasurementName"
                Multiple paths separated by semicolon (;)
                Can use "/" which will be converted to "¶"

        Returns:
            List of AggregatedMeasurement objects with statistics (min, max, avg, cpk, etc.)
            
        Example:
            >>> # Get aggregated stats with proper filters
            >>> data = analytics.get_aggregated_measurements(
            ...     WATSFilter(part_number="PROD-001", test_operation="EOL Test"),
            ...     measurement_paths="Main¶Voltage Test¶¶Output"
            ... )
        """
        if isinstance(filter_data, WATSFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = dict(filter_data)
        
        # Build query params for measurementPaths
        params: Dict[str, str] = {}
        
        # Check for measurement_path in data (legacy support) and move to query param
        if "measurement_path" in data:
            measurement_paths = measurement_paths or data.pop("measurement_path")
        if "measurementPath" in data:
            measurement_paths = measurement_paths or data.pop("measurementPath")
            
        if measurement_paths:
            params["measurementPaths"] = self._normalize_measurement_path(measurement_paths)
            
        response = self._http_client.post(
            "/api/App/AggregatedMeasurements", 
            data=data,
            params=params if params else None
        )
        result = self._error_handler.handle_response(
            response, operation="get_aggregated_measurements", allow_empty=True
        )
        if result:
            # API returns nested structure: [{measurementPath, measurements: [...]}]
            # Extract the nested measurements arrays
            all_measurements = []
            items = result if isinstance(result, list) else [result]
            for item in items:
                if isinstance(item, dict) and "measurements" in item:
                    # New API format with nested measurements array
                    for m in item.get("measurements", []):
                        all_measurements.append(AggregatedMeasurement.model_validate(m))
                else:
                    # Legacy flat format (backwards compat)
                    all_measurements.append(AggregatedMeasurement.model_validate(item))
            return all_measurements
        return []

    # =========================================================================
    # OEE (Overall Equipment Effectiveness)
    # =========================================================================

    def get_oee_analysis(
        self, filter_data: Union[WATSFilter, Dict[str, Any]]
    ) -> Optional[OeeAnalysisResult]:
        """
        Overall Equipment Effectiveness - analysis.

        POST /api/App/OeeAnalysis

        Args:
            filter_data: WATSFilter object or dict with filters like:
                - part_number: Filter by product
                - station_name: Filter by station
                - date_from/date_to: Time range

        Returns:
            OeeAnalysisResult object with OEE metrics (availability, performance, quality)
        """
        if isinstance(filter_data, WATSFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = filter_data
        response = self._http_client.post("/api/App/OeeAnalysis", data=data)
        result = self._error_handler.handle_response(
            response, operation="get_oee_analysis", allow_empty=True
        )
        if result:
            return OeeAnalysisResult.model_validate(result)
        return None

    # =========================================================================
    # Serial Number and Unit History
    # =========================================================================

    def get_serial_number_history(
        self, filter_data: Union[WATSFilter, Dict[str, Any]]
    ) -> List[ReportHeader]:
        """
        Serial Number History.

        POST /api/App/SerialNumberHistory

        Args:
            filter_data: WATSFilter object or dict

        Returns:
            List of ReportHeader objects
        """
        if isinstance(filter_data, WATSFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = filter_data
        response = self._http_client.post("/api/App/SerialNumberHistory", data=data)
        result = self._error_handler.handle_response(
            response, operation="get_serial_number_history", allow_empty=True
        )
        if result:
            return [
                ReportHeader.model_validate(item) for item in result
            ]
        return []

    def get_uut_reports(
        self,
        filter_data: Optional[Union[WATSFilter, Dict[str, Any]]] = None,
        *,
        product_group: Optional[str] = None,
        level: Optional[str] = None,
        part_number: Optional[str] = None,
        revision: Optional[str] = None,
        serial_number: Optional[str] = None,
        status: Optional[str] = None,
        top_count: Optional[int] = None,
    ) -> List[ReportHeader]:
        """
        Returns UUT report header info.

        GET/POST /api/App/UutReport

        Args:
            filter_data: WATSFilter object or dict (for POST)
            product_group: Filter by product group (GET only)
            level: Filter by production level (GET only)
            part_number: Filter by part number (GET only)
            revision: Filter by revision (GET only)
            serial_number: Filter by serial number (GET only)
            status: Filter by status (GET only)
            top_count: Maximum results, default 1000 (GET only)

        Returns:
            List of ReportHeader objects
        """
        if filter_data:
            if isinstance(filter_data, WATSFilter):
                data = filter_data.model_dump(by_alias=True, exclude_none=True)
            else:
                data = filter_data
            response = self._http_client.post("/api/App/UutReport", data=data)
        else:
            params: Dict[str, Any] = {}
            if product_group:
                params["productGroup"] = product_group
            if level:
                params["level"] = level
            if part_number:
                params["partNumber"] = part_number
            if revision:
                params["revision"] = revision
            if serial_number:
                params["serialNumber"] = serial_number
            if status:
                params["status"] = status
            if top_count is not None:
                params["topCount"] = top_count
            response = self._http_client.get(
                "/api/App/UutReport", params=params if params else None
            )
        result = self._error_handler.handle_response(
            response, operation="get_uut_reports", allow_empty=True
        )
        if result:
            return [
                ReportHeader.model_validate(item) for item in result
            ]
        return []

    def get_uur_reports(
        self, filter_data: Union[WATSFilter, Dict[str, Any]]
    ) -> List[ReportHeader]:
        """
        Returns UUR report header info.

        POST /api/App/UurReport

        Args:
            filter_data: WATSFilter object or dict

        Returns:
            List of ReportHeader objects
        """
        if isinstance(filter_data, WATSFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = filter_data
        response = self._http_client.post("/api/App/UurReport", data=data)
        result = self._error_handler.handle_response(
            response, operation="get_uur_reports", allow_empty=True
        )
        if result:
            return [
                ReportHeader.model_validate(item) for item in result
            ]
        return []
