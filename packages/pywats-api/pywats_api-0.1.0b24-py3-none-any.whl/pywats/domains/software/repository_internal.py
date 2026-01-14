"""Software repository - internal API data access layer.

⚠️ INTERNAL API - SUBJECT TO CHANGE ⚠️

Uses internal WATS API endpoints that are not publicly documented.
These endpoints may change without notice. This module should be
replaced with public API endpoints as soon as they become available.

The internal API requires the Referer header to be set to the base URL.
"""
from typing import List, Optional, Dict, Any, Union
from uuid import UUID

from ...core import HttpClient
from .models import Package
from .enums import PackageStatus


class SoftwareRepositoryInternal:
    """
    Software data access layer using internal API.
    
    ⚠️ INTERNAL API - SUBJECT TO CHANGE ⚠️
    
    Uses:
    - GET /api/internal/Software/isConnected
    - GET /api/internal/Software/File
    - GET /api/internal/Software/File/{id}
    - POST /api/internal/Software/File (upload single file)
    - POST /api/internal/Software/Files (upload multiple files)
    - GET /api/internal/Software/CheckFile
    - POST /api/internal/Software/DeletePackageFolder
    - POST /api/internal/Software/DeletePackageFolderFiles
    - POST /api/internal/Software/PostPackageFolder
    - POST /api/internal/Software/UpdatePackageFolder
    - GET /api/internal/Software/GetPackageHistory
    - GET /api/internal/Software/GetPackageDownloadHistory
    - GET /api/internal/Software/GetRevokedPackages
    - GET /api/internal/Software/GetAvailablePackages
    - GET /api/internal/Software/GetSoftwareEntityDetails
    - GET /api/internal/Software/Log
    
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
    
    # =========================================================================
    # Connection Check
    # =========================================================================
    
    def is_connected(self) -> bool:
        """
        Check if Software module is connected.
        
        GET /api/internal/Software/isConnected
        
        ⚠️ INTERNAL API
        
        Returns:
            True if connected
        """
        result = self._internal_get("/api/internal/Software/isConnected")
        return result is not None
    
    # =========================================================================
    # File Operations
    # =========================================================================
    
    def get_file(self, file_id: Union[str, UUID]) -> Optional[Dict[str, Any]]:
        """
        Get file metadata by ID.
        
        GET /api/internal/Software/File/{id}
        
        ⚠️ INTERNAL API
        
        Args:
            file_id: File UUID
            
        Returns:
            File metadata dictionary or None
        """
        return self._internal_get(f"/api/internal/Software/File/{file_id}")
    
    def check_file(
        self,
        package_id: Union[str, UUID],
        parent_folder_id: Union[str, UUID],
        file_path: str,
        checksum: str,
        file_date_epoch: int
    ) -> Optional[Dict[str, Any]]:
        """
        Check if a file already exists on the server.
        
        GET /api/internal/Software/CheckFile
        
        ⚠️ INTERNAL API
        
        Used before uploading to avoid duplicate uploads.
        
        Args:
            package_id: Package UUID
            parent_folder_id: Parent folder UUID
            file_path: File path within package
            checksum: MD5 or SHA1 checksum
            file_date_epoch: File date as Unix epoch
            
        Returns:
            Check result dictionary or None
        """
        params = {
            "packageId": str(package_id),
            "parentFolderId": str(parent_folder_id),
            "filePath": file_path,
            "checksum": checksum,
            "fileDateEpoch": file_date_epoch
        }
        return self._internal_get("/api/internal/Software/CheckFile", params)
    
    # =========================================================================
    # Folder Operations
    # =========================================================================
    
    def create_package_folder(
        self,
        package_id: Union[str, UUID],
        folder_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new folder in a package.
        
        POST /api/internal/Software/PostPackageFolder
        
        ⚠️ INTERNAL API
        
        Args:
            package_id: Package UUID
            folder_data: Folder definition (SoftwareEntity)
            
        Returns:
            Created folder data or None
        """
        return self._internal_post(
            "/api/internal/Software/PostPackageFolder",
            params={"packageId": str(package_id)},
            data=folder_data
        )
    
    def update_package_folder(
        self,
        folder_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing package folder.
        
        POST /api/internal/Software/UpdatePackageFolder
        
        ⚠️ INTERNAL API
        
        Args:
            folder_data: Updated folder definition (SoftwareEntity)
            
        Returns:
            Updated folder data or None
        """
        return self._internal_post(
            "/api/internal/Software/UpdatePackageFolder",
            data=folder_data
        )
    
    def delete_package_folder(
        self,
        package_folder_id: Union[str, UUID]
    ) -> Optional[Dict[str, Any]]:
        """
        Delete a package folder.
        
        POST /api/internal/Software/DeletePackageFolder
        
        ⚠️ INTERNAL API
        
        Args:
            package_folder_id: Folder UUID to delete
            
        Returns:
            Result or None
        """
        return self._internal_post(
            "/api/internal/Software/DeletePackageFolder",
            params={"packageFolderId": str(package_folder_id)}
        )
    
    def delete_package_folder_files(
        self,
        file_ids: List[Union[str, UUID]]
    ) -> Optional[Dict[str, Any]]:
        """
        Delete multiple files from a package folder.
        
        POST /api/internal/Software/DeletePackageFolderFiles
        
        ⚠️ INTERNAL API
        
        Args:
            file_ids: List of file UUIDs to delete (comma-separated)
            
        Returns:
            Result or None
        """
        ids_str = ",".join(str(fid) for fid in file_ids)
        return self._internal_post(
            "/api/internal/Software/DeletePackageFolderFiles",
            params={"packageFolderFileIds": ids_str}
        )
    
    # =========================================================================
    # Package History & Validation
    # =========================================================================
    
    def get_package_history(
        self,
        tags: str,
        status: Optional[int] = None,
        all_versions: Optional[bool] = None
    ) -> List[Package]:
        """
        Get package history by tags.
        
        GET /api/internal/Software/GetPackageHistory
        
        ⚠️ INTERNAL API
        
        Args:
            tags: Tags to filter by (comma-separated)
            status: Optional status filter (0=Draft, 1=Pending, 2=Released, 3=Revoked)
            all_versions: Whether to include all versions
            
        Returns:
            List of Package objects
        """
        params: Dict[str, Any] = {"tags": tags}
        if status is not None:
            params["status"] = status
        if all_versions is not None:
            params["allVersions"] = all_versions
        data = self._internal_get("/api/internal/Software/GetPackageHistory", params)
        if data and isinstance(data, list):
            return [Package.model_validate(item) for item in data]
        return []
    
    def get_package_download_history(
        self,
        client_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get package download history for a client.
        
        GET /api/internal/Software/GetPackageDownloadHistory
        
        ⚠️ INTERNAL API
        
        Args:
            client_id: Client identifier
            
        Returns:
            List of download records
        """
        params = {"clientId": client_id}
        data = self._internal_get("/api/internal/Software/GetPackageDownloadHistory", params)
        if data and isinstance(data, list):
            return data
        return []
    
    def get_revoked_packages(
        self,
        installed_packages: List[Union[str, UUID]],
        include_revoked_only: Optional[bool] = None
    ) -> List[str]:
        """
        Get list of revoked package IDs from installed packages.
        
        GET /api/internal/Software/GetRevokedPackages
        
        ⚠️ INTERNAL API
        
        Args:
            installed_packages: List of installed package UUIDs
            include_revoked_only: Only return revoked without newer released version
            
        Returns:
            List of revoked package UUIDs (as strings)
        """
        params: Dict[str, Any] = {
            "installedPackages": ",".join(str(p) for p in installed_packages)
        }
        if include_revoked_only is not None:
            params["includeRevokedOnly"] = include_revoked_only
        data = self._internal_get("/api/internal/Software/GetRevokedPackages", params)
        if data and isinstance(data, list):
            return data
        return []
    
    def get_available_packages(
        self,
        installed_packages: List[Union[str, UUID]]
    ) -> List[Package]:
        """
        Check server for new versions of installed packages.
        
        GET /api/internal/Software/GetAvailablePackages
        
        ⚠️ INTERNAL API
        
        Args:
            installed_packages: List of installed package UUIDs
            
        Returns:
            List of Package objects with newer versions available
        """
        params = {
            "installedPackages": ",".join(str(p) for p in installed_packages)
        }
        data = self._internal_get("/api/internal/Software/GetAvailablePackages", params)
        if data and isinstance(data, list):
            return [Package.model_validate(item) for item in data]
        return []
    
    def get_software_entity_details(
        self,
        package_id: Union[str, UUID]
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a software package.
        
        GET /api/internal/Software/GetSoftwareEntityDetails
        
        ⚠️ INTERNAL API
        
        Args:
            package_id: Package UUID
            
        Returns:
            Detailed entity data or None
        """
        params = {"packageId": str(package_id)}
        return self._internal_get("/api/internal/Software/GetSoftwareEntityDetails", params)
    
    # =========================================================================
    # Logging
    # =========================================================================
    
    def log_download(
        self,
        package_id: Union[str, UUID],
        download_size: int
    ) -> Optional[Dict[str, Any]]:
        """
        Log a package download.
        
        GET /api/internal/Software/Log
        
        ⚠️ INTERNAL API
        
        Args:
            package_id: Package UUID that was downloaded
            download_size: Size of downloaded data in bytes
            
        Returns:
            Log result or None
        """
        params = {
            "packageId": str(package_id),
            "downloadSize": download_size
        }
        return self._internal_get("/api/internal/Software/Log", params)
