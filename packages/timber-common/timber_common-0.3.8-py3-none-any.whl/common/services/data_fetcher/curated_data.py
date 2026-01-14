"""
Curated company data loader.
Loads and manages curated company lists from JSON files.
"""
import json
import pandas as pd  # Added for DataFrame support
from pathlib import Path
from functools import lru_cache
from typing import Tuple, Optional, List, Dict

from common.utils.config import config


class CuratedDataLoader:
    """Manages loading and accessing curated company data."""
    
    def __init__(self):
        self.data_dir = config.CURATED_COMPANIES_DIR
        self._cache = {}
    
    @lru_cache(maxsize=1)
    def load_all_indices(self) -> Dict[str, dict]:
        """
        Load all curated index data from JSON files.
        
        Returns:
            Dictionary mapping index_name -> full JSON structure
        """
        all_data = {}
        
        if not self.data_dir.exists():
            print(f"⚠ Curated companies directory not found: {self.data_dir}")
            return all_data
        
        for file_path in self.data_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    index_name = data.get("index_name")
                    
                    if index_name:
                        all_data[index_name] = data
                        print(f"✓ Loaded {file_path.name}")
                    else:
                        print(f"⚠ File {file_path.name} missing 'index_name' key")
                        
            except json.JSONDecodeError as e:
                print(f"✗ Failed to decode JSON from {file_path.name}: {e}")
            except Exception as e:
                print(f"✗ Error reading {file_path.name}: {e}")
        
        return all_data
    
    def get_index_data(self, index_name: str) -> Optional[dict]:
        """
        Get data for a specific index.
        
        Args:
            index_name: Name of the index (e.g., "S&P 500")
            
        Returns:
            Index data dictionary or None
        """
        all_data = self.load_all_indices()
        return all_data.get(index_name)
    
    def get_sectors_for_index(self, index_name: str) -> Dict[str, dict]:
        """
        Get all sectors for an index.
        
        Args:
            index_name: Name of the index
            
        Returns:
            Dictionary of sector data
        """
        index_data = self.get_index_data(index_name)
        if not index_data:
            return {}
        return index_data.get("sectors", {})
    
    def get_companies_by_sector(
        self,
        index_name: str,
        sector_name: str
    ) -> Tuple[List[dict], Optional[str]]:
        """
        Get all companies (heavyweights + disruptive) for a sector.
        
        Args:
            index_name: Name of the index
            sector_name: Name of the sector
            
        Returns:
            Tuple of (companies_list, error_message)
        """
        sectors = self.get_sectors_for_index(index_name)
        
        if not sectors:
            return [], f"Index '{index_name}' not found"
        
        sector_data = sectors.get(sector_name)
        
        if not sector_data:
            # Check if sector is explicitly excluded
            index_data = self.get_index_data(index_name)
            if index_data:
                exclusions = index_data.get("exclusion_reason", [])
                for exc in exclusions:
                    if exc.get("sector") == sector_name:
                        return [], f"Sector '{sector_name}' excluded: {exc.get('reason')}"
            
            return [], f"Sector '{sector_name}' not found in index '{index_name}'"
        
        # Combine heavyweights and disruptive companies
        companies = []
        
        for company in sector_data.get("heavyweights", []):
            company_copy = company.copy()
            company_copy['type'] = 'heavyweight'
            companies.append(company_copy)
        
        for company in sector_data.get("disruptive", []):
            company_copy = company.copy()
            company_copy['type'] = 'disruptive'
            companies.append(company_copy)
        
        if not companies:
            return [], f"No companies found for sector '{sector_name}'"
        
        return companies, None
    
    def get_all_companies(self, index_name: str) -> List[dict]:
        """
        Get all companies across all sectors for an index.
        
        Args:
            index_name: Name of the index
            
        Returns:
            List of all companies
        """
        all_companies = []
        sectors = self.get_sectors_for_index(index_name)
        
        for sector_name in sectors.keys():
            companies, _ = self.get_companies_by_sector(index_name, sector_name)
            all_companies.extend(companies)
        
        return all_companies
    
    # ========================================================================
    # NEW METHOD - Added for investing_operations.py compatibility
    # ========================================================================
    
    def get_companies_by_index(self, index_name: str) -> Tuple[pd.DataFrame, Optional[str]]:
        """
        Get all companies for an index as a DataFrame.
        
        This method is used by the config-driven operations system.
        It wraps get_all_companies() and returns a DataFrame format.
        
        Args:
            index_name: Name of the index (e.g., "S&P 500")
            
        Returns:
            Tuple of (DataFrame with company data, error_message)
            DataFrame columns: ticker, name, sector, type (heavyweight/disruptive), etc.
        """
        try:
            companies = self.get_all_companies(index_name)
            
            if not companies:
                return pd.DataFrame(), f"No companies found for index '{index_name}'"
            
            # Convert list of dicts to DataFrame
            df = pd.DataFrame(companies)
            
            return df, None
            
        except Exception as e:
            return pd.DataFrame(), f"Error loading companies for '{index_name}': {str(e)}"
    
    # ========================================================================
    
    def get_available_indices(self) -> List[str]:
        """Get list of available index names."""
        return list(self.load_all_indices().keys())
    
    def get_available_sectors(self, index_name: str) -> List[str]:
        """Get list of available sectors for an index."""
        sectors = self.get_sectors_for_index(index_name)
        return list(sectors.keys())


# Create a singleton instance
curated_data_loader = CuratedDataLoader()