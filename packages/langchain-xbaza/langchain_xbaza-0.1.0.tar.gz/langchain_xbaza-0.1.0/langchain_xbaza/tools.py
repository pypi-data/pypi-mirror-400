"""LangChain tools for Xbaza API."""

from typing import Optional, Dict, Any
import requests
from langchain.tools import BaseTool
from pydantic import Field


class XbazaBaseTool(BaseTool):
    """Base tool for Xbaza API interactions."""
    
    base_url: str = Field(
        default="https://xbaza.by/api/ai",
        description="Base URL for Xbaza API"
    )
    user_agent: str = Field(
        default="LangChain-Xbaza",
        description="User-Agent header for API requests"
    )
    
    def _make_request(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Xbaza API."""
        url = f"{self.base_url}/{endpoint}"
        headers = {"User-Agent": self.user_agent}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}


class XbazaJobsTool(XbazaBaseTool):
    """Tool for searching jobs in Belarus via Xbaza API."""
    
    name: str = "xbaza_jobs"
    description: str = (
        "Search for job listings in Belarus. "
        "Input should be a JSON string with optional 'category', 'city', and 'limit' fields. "
        "Example: '{\"category\": \"IT\", \"city\": \"Minsk\", \"limit\": 10}'"
    )
    
    def _run(
        self,
        category: Optional[str] = None,
        city: Optional[str] = None,
        limit: int = 20,
    ) -> str:
        """Execute the tool."""
        params = {"limit": min(limit, 50)}
        if category:
            params["category"] = category
        if city:
            params["city"] = city
        
        data = self._make_request("jobs", params)
        
        if not data.get("success") or "data" not in data:
            return f"Error: {data.get('error', 'Unknown error')}"
        
        jobs = data["data"]
        if not jobs:
            return "No jobs found matching your criteria."
        
        result = f"Found {len(jobs)} jobs:\n\n"
        for i, job in enumerate(jobs, 1):
            result += f"{i}. {job.get('title', 'N/A')}\n"
            if job.get('company'):
                result += f"   Company: {job['company'].get('name', 'N/A')}\n"
            if job.get('city'):
                result += f"   Location: {job['city'].get('name_ru', 'N/A')}\n"
            if job.get('salary_min'):
                salary = f"{job['salary_min']}"
                if job.get('salary_max'):
                    salary += f"-{job['salary_max']}"
                result += f"   Salary: {salary} {job.get('salary_currency', 'BYN')}\n"
            result += "\n"
        
        return result


class XbazaUsersTool(XbazaBaseTool):
    """Tool for searching professionals in Belarus."""
    
    name: str = "xbaza_users"
    description: str = (
        "Search for professionals and specialists in Belarus. "
        "Input should be a search query (name, skills, etc.). "
        "Example: 'React developer' or 'Ivan Petrov'"
    )
    
    def _run(self, query: str, limit: int = 10) -> str:
        """Execute the tool."""
        if not query or len(query) < 2:
            return "Error: Search query must be at least 2 characters long."
        
        params = {"q": query, "limit": min(limit, 50)}
        data = self._make_request("users", params)
        
        if not data.get("success") or "data" not in data:
            return f"Error: {data.get('error', 'Unknown error')}"
        
        users = data["data"]
        if not users:
            return "No professionals found."
        
        result = f"Found {len(users)} professionals:\n\n"
        for i, user in enumerate(users, 1):
            name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            result += f"{i}. {name or 'N/A'}\n"
            if user.get('headline'):
                result += f"   {user['headline']}\n"
            if user.get('location', {}).get('city'):
                result += f"   Location: {user['location']['city'].get('name_ru', 'N/A')}\n"
            result += "\n"
        
        return result


class XbazaBusinessTool(XbazaBaseTool):
    """Tool for searching business listings in Belarus."""
    
    name: str = "xbaza_business"
    description: str = (
        "Search for business for sale listings in Belarus. "
        "Input should be a JSON string with optional 'city', 'minPrice', 'maxPrice', 'limit'. "
        "Example: '{\"city\": \"Minsk\", \"minPrice\": 10000, \"maxPrice\": 100000}'"
    )
    
    def _run(
        self,
        city: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 20,
    ) -> str:
        """Execute the tool."""
        params = {"limit": min(limit, 100)}
        if city:
            params["city"] = city
        if min_price:
            params["minPrice"] = min_price
        if max_price:
            params["maxPrice"] = max_price
        
        data = self._make_request("business", params)
        
        if not data.get("success") or "data" not in data:
            return f"Error: {data.get('error', 'Unknown error')}"
        
        businesses = data["data"]
        if not businesses:
            return "No business listings found."
        
        result = f"Found {len(businesses)} business listings:\n\n"
        for i, business in enumerate(businesses, 1):
            result += f"{i}. {business.get('title', 'N/A')}\n"
            if business.get('price'):
                result += f"   Price: {business['price']} {business.get('price_currency', 'BYN')}\n"
            if business.get('city'):
                result += f"   Location: {business['city'].get('name_ru', 'N/A')}\n"
            if business.get('profit'):
                result += f"   Profit: {business['profit']} {business.get('price_currency', 'BYN')}\n"
            result += "\n"
        
        return result


class XbazaPropertyTool(XbazaBaseTool):
    """Tool for searching commercial real estate in Belarus."""
    
    name: str = "xbaza_property"
    description: str = (
        "Search for commercial real estate in Belarus. "
        "Input should be a JSON string with optional 'propertyType', 'dealType', 'city', 'limit'. "
        "Example: '{\"propertyType\": \"OFFICE\", \"dealType\": \"RENT\", \"city\": \"Minsk\"}'"
    )
    
    def _run(
        self,
        property_type: Optional[str] = None,
        deal_type: Optional[str] = None,
        city: Optional[str] = None,
        limit: int = 20,
    ) -> str:
        """Execute the tool."""
        params = {"limit": min(limit, 100)}
        if property_type:
            params["propertyType"] = property_type
        if deal_type:
            params["dealType"] = deal_type
        if city:
            params["city"] = city
        
        data = self._make_request("property", params)
        
        if not data.get("success") or "data" not in data:
            return f"Error: {data.get('error', 'Unknown error')}"
        
        properties = data["data"]
        if not properties:
            return "No properties found."
        
        result = f"Found {len(properties)} properties:\n\n"
        for i, prop in enumerate(properties, 1):
            result += f"{i}. {prop.get('title', 'N/A')}\n"
            if prop.get('price'):
                result += f"   Price: {prop['price']} {prop.get('price_currency', 'BYN')}\n"
            if prop.get('area'):
                result += f"   Area: {prop['area']} m²\n"
            if prop.get('property_type'):
                result += f"   Type: {prop['property_type']}\n"
            result += "\n"
        
        return result


class XbazaServicesTool(XbazaBaseTool):
    """Tool for searching business services in Belarus."""
    
    name: str = "xbaza_services"
    description: str = (
        "Search for business services in Belarus. "
        "Input should be a JSON string with optional 'category', 'city', 'limit'. "
        "Example: '{\"category\": \"IT\", \"city\": \"Minsk\"}'"
    )
    
    def _run(
        self,
        category: Optional[str] = None,
        city: Optional[str] = None,
        limit: int = 20,
    ) -> str:
        """Execute the tool."""
        params = {"limit": min(limit, 50)}
        if category:
            params["category"] = category
        if city:
            params["city"] = city
        
        data = self._make_request("services", params)
        
        if not data.get("success") or "data" not in data:
            return f"Error: {data.get('error', 'Unknown error')}"
        
        services = data["data"]
        if not services:
            return "No services found."
        
        result = f"Found {len(services)} services:\n\n"
        for i, service in enumerate(services, 1):
            result += f"{i}. {service.get('name', 'N/A')}\n"
            if service.get('price'):
                result += f"   Price: {service['price']} {service.get('price_currency', 'BYN')}\n"
            if service.get('company'):
                result += f"   Company: {service['company'].get('name', 'N/A')}\n"
            if service.get('city'):
                result += f"   Location: {service['city'].get('name_ru', 'N/A')}\n"
            result += "\n"
        
        return result


class XbazaAnalyticsTool(XbazaBaseTool):
    """Tool for getting market analytics from Xbaza API."""
    
    name: str = "xbaza_analytics"
    description: str = (
        "Get market analytics and trends from Belarus job market. "
        "Input should be a JSON string with optional 'type' and 'days'. "
        "Example: '{\"type\": \"overview\", \"days\": 30}'"
    )
    
    def _run(
        self,
        analytics_type: str = "overview",
        days: int = 30,
    ) -> str:
        """Execute the tool."""
        params = {"type": analytics_type, "days": days}
        data = self._make_request("analytics", params)
        
        if not data.get("success") or "data" not in data:
            return f"Error: {data.get('error', 'Unknown error')}"
        
        analytics = data["data"]
        result = f"Market Analytics ({analytics_type}):\n\n"
        
        if "statistics" in analytics:
            stats = analytics["statistics"]
            result += "Statistics:\n"
            for key, value in stats.items():
                result += f"  {key}: {value}\n"
            result += "\n"
        
        if "trends" in analytics:
            trends = analytics["trends"]
            result += "Trends:\n"
            for key, value in trends.items():
                result += f"  {key}: {value}\n"
        
        if "top_categories" in analytics:
            result += "\nTop Categories:\n"
            for cat in analytics["top_categories"][:5]:
                result += f"  {cat.get('category', 'N/A')}: {cat.get('count', 0)} jobs\n"
        
        return result

