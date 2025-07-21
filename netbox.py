import requests
import json
from typing import Dict, List, Optional, Any


class DotDict:
    """Dictionary subclass that allows attribute access to dictionary keys"""
    
    def __init__(self, data):
        """
        Initialize DotDict with dictionary data
        
        Args:
            data: Dictionary to convert to DotDict
        """
        for key, value in data.items():
            # Convert nested dictionaries and lists of dictionaries
            if isinstance(value, dict):
                value = DotDict(value)
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                value = [DotDict(item) if isinstance(item, dict) else item for item in value]
            
            # Replace hyphens with underscores in key names for attribute access
            key = key.replace('-', '_') if isinstance(key, str) else key
            setattr(self, key, value)
    
    def __getitem__(self, key):
        return getattr(self, key)
    
    def __contains__(self, key):
        return hasattr(self, key)


class NetBoxAPI:
    """Class to interact directly with NetBox API without using pynetbox"""
    
    def __init__(self, url: str, token: str, verify_ssl: bool = True):
        """
        Initialize NetBox API client
        
        Args:
            url: NetBox API URL
            token: NetBox API token
            verify_ssl: Whether to verify SSL certificates
        """
        self.url = url.rstrip('/')
        self.token = token
        self.verify_ssl = verify_ssl
        self.headers = {
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the NetBox API
        
        Args:
            endpoint: API endpoint (e.g. 'ipam/ip-addresses/')
            params: Query parameters
            
        Returns:
            API response as dictionary or list of DotDict objects
        """
        # Check if URL already ends with /api to avoid duplicate
        if self.url.endswith('/api'):
            url = f"{self.url}/{endpoint}"
        else:
            url = f"{self.url}/api/{endpoint}"
            
        # Initialize results and set up pagination parameters
        if params is None:
            params = {}
        
        results = []
        next_url = url
        page_count = 1
        
        # Follow pagination by getting all pages
        while next_url:
            # Print request details before making the request
            print(f"\n--- NetBox API Request (Page {page_count}) ---")
            print(f"URL: {next_url}")
            print(f"Method: GET")
            print(f"Headers: {json.dumps({k: v if k != 'Authorization' else '[REDACTED]' for k, v in self.headers.items()}, indent=2)}")
            print(f"Params: {json.dumps(params, indent=2)}")
            
            # Make the request
            response = requests.get(next_url, headers=self.headers, params=params, verify=self.verify_ssl)
            
            # Print response details
            print(f"\n--- NetBox API Response (Page {page_count}) ---")
            print(f"Status Code: {response.status_code}")
            print(f"Response Time: {response.elapsed.total_seconds():.3f} seconds")
            print(f"Response Size: {len(response.content)} bytes")
            
            # Raise exception for bad status codes
            response.raise_for_status()
            data = response.json()
            
            # Print pagination info if available
            if 'results' in data:
                result_count = len(data['results'])
                total_count = data.get('count', 'unknown')
                print(f"Results: {result_count} items (Page {page_count}, Total: {total_count})")
                if data.get('next'):
                    print(f"Next Page: {data['next']}")
            
            # Add results from this page
            if 'results' in data:
                # Convert each result to DotDict for attribute access
                results.extend([DotDict(item) for item in data['results']])
                next_url = data.get('next')
                # Clear params after first request as they're included in the next URL
                params = {}
                page_count += 1
            else:
                # If no pagination, just return the data as DotDict
                print(f"Single response (non-paginated)")
                return DotDict(data)
                
        # Return compiled results as list of DotDict objects
        print(f"\nCompleted API requests: {page_count-1} page(s), {len(results)} total items retrieved")
        return results
        
    def status(self) -> Dict:
        """
        Get NetBox status information
        
        Returns:
            Status information as a DotDict
        """
        if self.url.endswith('/api'):
            url = f"{self.url}/status/"
        else:
            url = f"{self.url}/api/status/"
        
        # Print request details
        print("\n--- NetBox API Status Request ---")
        print(f"URL: {url}")
        print(f"Method: GET")
        print(f"Headers: {json.dumps({k: v if k != 'Authorization' else '[REDACTED]' for k, v in self.headers.items()}, indent=2)}")
            
        # Make the request
        response = requests.get(url, headers=self.headers, verify=self.verify_ssl)
        
        # Print response details
        print("\n--- NetBox API Status Response ---")
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response.elapsed.total_seconds():.3f} seconds")
        print(f"Response Size: {len(response.content)} bytes")
        
        response.raise_for_status()
        return DotDict(response.json())