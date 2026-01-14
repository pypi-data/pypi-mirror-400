"""Analytics domain module.

Provides statistics, KPIs, yield analysis, and dashboard data services.

BACKEND API MAPPING
-------------------
This module maps to the WATS backend '/api/App/*' endpoints.
We chose 'analytics' as the Python module name because it better describes
the functionality (yield analysis, KPIs, statistics, OEE) while 'App' is the
legacy backend controller name.

All API calls in this module target /api/App/* endpoints:
- GET/POST /api/App/DynamicYield
- GET/POST /api/App/DynamicRepair  
- GET/POST /api/App/TopFailed
- GET/POST /api/App/TestStepAnalysis
- etc.

Internal API endpoints (⚠️ subject to change):
- POST /api/internal/UnitFlow
- GET /api/internal/UnitFlow/Links
- GET /api/internal/UnitFlow/Nodes
- POST /api/internal/UnitFlow/SN
- POST /api/internal/UnitFlow/SplitBy
- POST /api/internal/UnitFlow/UnitOrder
- GET /api/internal/UnitFlow/Units

This is purely a naming choice for better developer experience.
"""
from .enums import YieldDataType, ProcessType
from .models import (
    YieldData,
    ProcessInfo,
    LevelInfo,
    ProductGroup,
    StepAnalysisRow,
    # New typed models
    TopFailedStep,
    RepairStatistics,
    RepairHistoryRecord,
    MeasurementData,
    AggregatedMeasurement,
    OeeAnalysisResult,
    # Unit Flow models (internal API)
    UnitFlowNode,
    UnitFlowLink,
    UnitFlowUnit,
    UnitFlowFilter,
    UnitFlowResult,
)
from .repository import AnalyticsRepository
from .service import AnalyticsService

# Internal API (⚠️ subject to change)
from .repository_internal import AnalyticsRepositoryInternal
from .service_internal import AnalyticsServiceInternal

# Backward compatibility aliases (deprecated)
AppRepository = AnalyticsRepository
AppService = AnalyticsService

__all__ = [
    # Enums
    "YieldDataType",
    "ProcessType",
    # Models
    "YieldData",
    "ProcessInfo",
    "LevelInfo",
    "ProductGroup",
    "StepAnalysisRow",
    # New typed models
    "TopFailedStep",
    "RepairStatistics",
    "RepairHistoryRecord",
    "MeasurementData",
    "AggregatedMeasurement",
    "OeeAnalysisResult",
    # Unit Flow models (internal API)
    "UnitFlowNode",
    "UnitFlowLink",
    "UnitFlowUnit",
    "UnitFlowFilter",
    "UnitFlowResult",
    # Repository & Service
    "AnalyticsRepository",
    "AnalyticsService",
    # Internal API (⚠️ subject to change)
    "AnalyticsRepositoryInternal",
    "AnalyticsServiceInternal",
]

