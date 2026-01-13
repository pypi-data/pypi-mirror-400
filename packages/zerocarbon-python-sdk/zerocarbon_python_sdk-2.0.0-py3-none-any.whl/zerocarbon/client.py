"""
ZeroCarbon SDK Client
"""

import requests
from typing import Dict, List, Optional, Any
from .exceptions import AuthenticationError, InvalidRequestError, APIError


class ZeroCarbon:
    """Main client for ZeroCarbon API"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.zerocarbon.codes/v1",
        test_mode: bool = False
    ):
        """
        Initialize ZeroCarbon client
        
        Args:
            api_key: Your API key (get from dashboard)
            base_url: API base URL (default: production)
            test_mode: Enable test mode (no real charges)
        """
        if not api_key:
            raise AuthenticationError("API key is required")
        
        self.api_key = api_key
        self.base_url = base_url
        self.test_mode = test_mode
        
        self.calculate = CalculateAPI(self)
        self.offsets = OffsetsAPI(self)
        self.brsr = BRSRAPI(self)
        self.bulk = BulkAPI(self)
        self.webhooks = WebhooksAPI(self)
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """Make HTTP request to API"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ZeroCarbon-Python/2.0.0"
        }
        
        if self.test_mode:
            headers["X-Test-Mode"] = "true"
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif e.response.status_code == 400:
                raise InvalidRequestError(e.response.json().get("error", str(e)))
            else:
                raise APIError(f"API error: {e.response.json().get('error', str(e))}")
        
        except requests.exceptions.RequestException as e:
            raise APIError(f"Network error: {str(e)}")


class CalculateAPI:
    """Emissions calculation endpoints"""
    
    def __init__(self, client: ZeroCarbon):
        self.client = client
    
    def flight(
        self,
        origin: str,
        destination: str,
        cabin_class: str = "economy",
        passengers: int = 1,
        round_trip: bool = False
    ) -> Dict:
        """
        Calculate flight emissions
        
        Args:
            origin: Origin airport code (e.g., "DEL")
            destination: Destination airport code (e.g., "BOM")
            cabin_class: "economy", "premium_economy", "business", or "first"
            passengers: Number of passengers
            round_trip: Whether it's a round trip
        
        Returns:
            Dict with emissions_kg_co2e and breakdown
        """
        return self.client._request("POST", "/calculate/flight", {
            "origin": origin,
            "destination": destination,
            "cabin_class": cabin_class,
            "passengers": passengers,
            "round_trip": round_trip
        })
    
    def electricity(
        self,
        amount_kwh: float,
        country: str = "IN",
        state: Optional[str] = None,
        renewable_percentage: float = 0
    ) -> Dict:
        """
        Calculate electricity emissions
        
        Args:
            amount_kwh: Electricity consumed in kWh
            country: Country code (default: "IN")
            state: State name for region-specific factors
            renewable_percentage: % of renewable energy (0-100)
        
        Returns:
            Dict with emissions_kg_co2e and grid mix
        """
        return self.client._request("POST", "/calculate/electricity", {
            "amount_kwh": amount_kwh,
            "country": country,
            "state": state,
            "renewable_percentage": renewable_percentage
        })
    
    def fuel(
        self,
        fuel_type: str,
        amount: float,
        unit: str = "liters"
    ) -> Dict:
        """
        Calculate fuel combustion emissions
        
        Args:
            fuel_type: Type of fuel ("petrol", "diesel", "natural_gas", "lpg", "coal", "kerosene")
            amount: Amount of fuel
            unit: Unit of measurement ("liters" or "kg")
        
        Returns:
            Dict with emissions_kg_co2e
        """
        return self.client._request("POST", "/calculate/fuel", {
            "fuel_type": fuel_type,
            "amount": amount,
            "unit": unit
        })
    
    def spend(
        self,
        amount: float,
        currency: str = "INR",
        category: str = "electricity",
        description: Optional[str] = None
    ) -> Dict:
        """
        Calculate emissions from spend (AI-powered matching)
        
        Args:
            amount: Amount spent
            currency: Currency code (default: "INR")
            category: Spend category
            description: Optional description for better matching
        
        Returns:
            Dict with emissions_kg_co2e and matched factor
        """
        return self.client._request("POST", "/calculate/spend", {
            "amount": amount,
            "currency": currency,
            "category": category,
            "description": description
        })


class OffsetsAPI:
    """Carbon offsetting endpoints"""
    
    def __init__(self, client: ZeroCarbon):
        self.client = client
    
    def get_recommendations(
        self,
        emissions_kg_co2e: Optional[float] = None,
        budget_usd: Optional[float] = None,
        location: Optional[str] = None,
        project_types: Optional[List[str]] = None
    ) -> Dict:
        """
        Get offset project recommendations
        
        Args:
            emissions_kg_co2e: Amount to offset in kg CO2e
            budget_usd: Maximum budget in USD
            location: Geographic preference
            project_types: List of preferred project types
        
        Returns:
            Dict with recommended projects
        """
        emissions_tonnes = (emissions_kg_co2e or 0) / 1000
        return self.client._request("POST", "/offsets/recommendations", {
            "emissions_tonnes": emissions_tonnes,
            "budget_usd": budget_usd,
            "location": location,
            "project_types": project_types
        })
            "preferred_region": preferred_region,
            "max_budget_usd": max_budget_usd
        })
    
    def purchase(
        self,
        project_id: str,
        quantity_kg_co2e: float,
        retirement_reason: str = "Carbon offsetting",
        beneficiary_name: Optional[str] = None
    ) -> Dict:
        """
        Purchase and retire carbon credits
        
        Args:
            project_id: ID of the carbon project
            quantity_kg_co2e: Quantity to offset
            retirement_reason: Reason for retirement
            beneficiary_name: Beneficiary name for certificate
        
        Returns:
            Dict with transaction details and certificate URL
        """
        return self.client._request("POST", "/offsets/purchase", {
            "project_id": project_id,
            "quantity_kg_co2e": quantity_kg_co2e,
            "retirement_reason": retirement_reason,
            "beneficiary_name": beneficiary_name
        })


class BRSRAPI:
    """BRSR reporting endpoints"""
    
    def __init__(self, client: ZeroCarbon):
        self.client = client
    
    def generate_report(
        self,
        company_id: str,
        financial_year: str,
        format: str = "pdf",
        include_sections: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate BRSR report
        
        Args:
            company_id: Company ID
            financial_year: Financial year (e.g., "2024-25")
            format: Output format ("pdf" or "json")
            include_sections: Sections to include (default: all)
        
        Returns:
            Dict with report URL and metadata
        """
        return self.client._request("POST", "/brsr/generate-report", {
            "company_id": company_id,
            "financial_year": financial_year,
            "format": format,
            "include_sections": include_sections or ["A", "B", "C"]
        })


class BulkAPI:
    """Bulk data upload endpoints"""
    
    def __init__(self, client: ZeroCarbon):
        self.client = client
    
    def upload(self, file_path: str) -> Dict:
        """
        Upload CSV file with emissions data
        
        Args:
            file_path: Path to CSV file
        
        Returns:
            Dict with upload status
        """
        # TODO: Implement file upload
        raise NotImplementedError("Bulk upload coming soon")


class WebhooksAPI:
    """Webhook management endpoints"""
    
    def __init__(self, client: ZeroCarbon):
        self.client = client
    
    def register(
        self,
        url: str,
        events: List[str],
        secret: Optional[str] = None
    ) -> Dict:
        """
        Register a webhook
        
        Args:
            url: Webhook URL (must be HTTPS)
            events: List of events to subscribe to
            secret: Optional webhook secret
        
        Returns:
            Dict with webhook details and secret
        """
        return self.client._request("POST", "/webhooks/register", {
            "url": url,
            "events": events,
            "secret": secret
        })
