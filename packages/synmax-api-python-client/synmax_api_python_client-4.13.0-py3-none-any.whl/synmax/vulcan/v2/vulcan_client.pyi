from typing import Literal, Union
from synmax.openapi.client import Result
from datetime import date
class VulcanApiClient:
    def health(self) -> Result:
        """Health check endpoint"""
        ...
    def datacenters(self) -> Result:
        """Get datacenter information"""
        ...
    def underconstruction(self) -> Result:
        """Get under construction datacenters with filtering and aggregation"""
        ...
    def lng_projects(self) -> Result:
        """Get LNG projects with filtering and aggregation"""
        ...
    def metadata_history(self,date_eia_updated_min: date = ...,date_eia_updated_max: date = ...) -> Result:
        """Returns plant metadata on power projects provided by the EIA and comparative metrics against these reports."""
        ...
    def project_rankings(self) -> Result:
        """Get project rankings based on various criteria"""
        ...
    def iir_data(self) -> Result:
        """Get IIR data"""
        ...