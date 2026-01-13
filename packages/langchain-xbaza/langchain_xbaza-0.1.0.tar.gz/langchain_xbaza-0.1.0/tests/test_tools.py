"""Tests for Xbaza tools."""

import pytest
from unittest.mock import Mock, patch
from langchain_xbaza.tools import (
    XbazaJobsTool,
    XbazaUsersTool,
    XbazaBusinessTool,
    XbazaPropertyTool,
    XbazaServicesTool,
    XbazaAnalyticsTool,
)


class TestXbazaJobsTool:
    """Tests for XbazaJobsTool."""
    
    def test_tool_initialization(self):
        """Test tool initialization."""
        tool = XbazaJobsTool()
        assert tool.name == "xbaza_jobs"
        assert tool.base_url == "https://xbaza.by/api/ai"
        assert tool.user_agent == "LangChain-Xbaza"
    
    @patch('langchain_xbaza.tools.requests.get')
    def test_successful_job_search(self, mock_get):
        """Test successful job search."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {
                    "title": "Frontend Developer",
                    "company": {"name": "Tech Company"},
                    "city": {"name_ru": "Минск"},
                    "salary_min": 1500,
                    "salary_max": 3000,
                    "salary_currency": "BYN"
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        tool = XbazaJobsTool()
        result = tool._run(category="IT", city="Minsk", limit=10)
        
        assert "Found 1 jobs" in result
        assert "Frontend Developer" in result
        assert "Tech Company" in result
    
    @patch('langchain_xbaza.tools.requests.get')
    def test_no_jobs_found(self, mock_get):
        """Test when no jobs are found."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": []
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        tool = XbazaJobsTool()
        result = tool._run(category="IT")
        
        assert "No jobs found" in result


class TestXbazaUsersTool:
    """Tests for XbazaUsersTool."""
    
    def test_tool_initialization(self):
        """Test tool initialization."""
        tool = XbazaUsersTool()
        assert tool.name == "xbaza_users"
    
    def test_query_validation(self):
        """Test query validation."""
        tool = XbazaUsersTool()
        result = tool._run(query="")
        assert "Error" in result or "at least 2 characters" in result
    
    @patch('langchain_xbaza.tools.requests.get')
    def test_successful_user_search(self, mock_get):
        """Test successful user search."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {
                    "first_name": "Ivan",
                    "last_name": "Petrov",
                    "headline": "Senior Developer",
                    "location": {"city": {"name_ru": "Минск"}}
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        tool = XbazaUsersTool()
        result = tool._run(query="Ivan", limit=10)
        
        assert "Found 1 professionals" in result
        assert "Ivan Petrov" in result


class TestXbazaBusinessTool:
    """Tests for XbazaBusinessTool."""
    
    def test_tool_initialization(self):
        """Test tool initialization."""
        tool = XbazaBusinessTool()
        assert tool.name == "xbaza_business"
    
    @patch('langchain_xbaza.tools.requests.get')
    def test_successful_business_search(self, mock_get):
        """Test successful business search."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {
                    "title": "Cafe for sale",
                    "price": 50000,
                    "price_currency": "BYN",
                    "city": {"name_ru": "Минск"}
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        tool = XbazaBusinessTool()
        result = tool._run(city="Minsk", limit=10)
        
        assert "Found 1 business listings" in result
        assert "Cafe for sale" in result


class TestXbazaPropertyTool:
    """Tests for XbazaPropertyTool."""
    
    def test_tool_initialization(self):
        """Test tool initialization."""
        tool = XbazaPropertyTool()
        assert tool.name == "xbaza_property"
    
    @patch('langchain_xbaza.tools.requests.get')
    def test_successful_property_search(self, mock_get):
        """Test successful property search."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {
                    "title": "Office space",
                    "price": 2000,
                    "area": 100,
                    "property_type": "OFFICE"
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        tool = XbazaPropertyTool()
        result = tool._run(property_type="OFFICE", deal_type="RENT")
        
        assert "Found 1 properties" in result
        assert "Office space" in result


class TestXbazaServicesTool:
    """Tests for XbazaServicesTool."""
    
    def test_tool_initialization(self):
        """Test tool initialization."""
        tool = XbazaServicesTool()
        assert tool.name == "xbaza_services"
    
    @patch('langchain_xbaza.tools.requests.get')
    def test_successful_services_search(self, mock_get):
        """Test successful services search."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {
                    "name": "Web Development",
                    "price": 5000,
                    "company": {"name": "Tech Company"}
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        tool = XbazaServicesTool()
        result = tool._run(category="IT")
        
        assert "Found 1 services" in result
        assert "Web Development" in result


class TestXbazaAnalyticsTool:
    """Tests for XbazaAnalyticsTool."""
    
    def test_tool_initialization(self):
        """Test tool initialization."""
        tool = XbazaAnalyticsTool()
        assert tool.name == "xbaza_analytics"
    
    @patch('langchain_xbaza.tools.requests.get')
    def test_successful_analytics(self, mock_get):
        """Test successful analytics retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "statistics": {
                    "total_jobs": 100,
                    "total_companies": 50
                },
                "trends": {
                    "jobs_growth": "+10%"
                }
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        tool = XbazaAnalyticsTool()
        result = tool._run(analytics_type="overview", days=30)
        
        assert "Market Analytics" in result
        assert "total_jobs" in result

