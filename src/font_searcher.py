"""
Font Search Engine
Handles font searching across multiple repositories
"""

import os
import json
from typing import List, Dict, Any, Optional
from urllib.parse import quote
import logging

logger = logging.getLogger(__name__)


class FontSearcher:
    """Search for fonts across multiple repositories"""
    
    def __init__(self, database_path: str = './data/font_database.json'):
        """Initialize the font searcher"""
        self.database_path = database_path
        self.font_database = self._load_database()
        self.font_sources = self._load_font_sources()
    
    def _load_database(self) -> Dict[str, Any]:
        """Load font database from file"""
        if os.path.exists(self.database_path):
            try:
                with open(self.database_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load font database: {str(e)}")
        return {'fonts': []}
    
    def _load_font_sources(self) -> Dict[str, Dict[str, str]]:
        """Load available font sources"""
        return {
            'Google Fonts': {
                'url': 'https://fonts.google.com',
                'type': 'free',
                'search_pattern': 'https://fonts.google.com/?query={query}',
                'priority': 1
            },
            'MyFonts': {
                'url': 'https://www.myfonts.com',
                'type': 'commercial',
                'search_pattern': 'https://www.myfonts.com/search/{query}/',
                'priority': 2
            },
            'Font Squirrel': {
                'url': 'https://www.fontsquirrel.com',
                'type': 'free',
                'search_pattern': 'https://www.fontsquirrel.com/fonts?search={query}',
                'priority': 1
            },
            'DaFont': {
                'url': 'https://www.dafont.com',
                'type': 'free',
                'search_pattern': 'https://www.dafont.com/search.php?q={query}',
                'priority': 1
            },
            '1001 Fonts': {
                'url': 'https://www.1001fonts.com',
                'type': 'mixed',
                'search_pattern': 'https://www.1001fonts.com/search.html?search={query}',
                'priority': 2
            },
            'Font Space': {
                'url': 'https://www.fontspace.com',
                'type': 'free',
                'search_pattern': 'https://www.fontspace.com/search?q={query}',
                'priority': 1
            },
            'Creative Fabrica': {
                'url': 'https://www.creativefabrica.com',
                'type': 'subscription',
                'search_pattern': 'https://www.creativefabrica.com/search/?q={query}',
                'priority': 3
            },
            'Adobe Fonts': {
                'url': 'https://fonts.adobe.com',
                'type': 'commercial',
                'search_pattern': 'https://fonts.adobe.com/search?q={query}',
                'priority': 2
            },
            'YouWorkForThem': {
                'url': 'https://www.youworkforthem.com/fontlens',
                'type': 'commercial',
                'search_pattern': 'https://www.youworkforthem.com/fonts?search={query}',
                'priority': 2
            },
            'WhatFontIs': {
                'url': 'https://www.whatfontis.com',
                'type': 'free',
                'search_pattern': 'https://www.whatfontis.com/?s={query}',
                'priority': 1
            },
            'Global Fonts': {
                'url': 'https://globalfonts.pro',
                'type': 'commercial',
                'search_pattern': 'https://globalfonts.pro/search?q={query}',
                'priority': 2
            },
            'FontHub': {
                'url': 'https://fontshub.pro',
                'type': 'mixed',
                'search_pattern': 'https://fontshub.pro/search/?q={query}',
                'priority': 2
            },
            'Font Download': {
                'url': 'https://font.download',
                'type': 'free',
                'search_pattern': 'https://font.download/search/{query}',
                'priority': 1
            },
            'Font Park': {
                'url': 'https://fontpark.com',
                'type': 'mixed',
                'search_pattern': 'https://fontpark.com/en/search.html?q={query}',
                'priority': 2
            },
            'WebFont Free': {
                'url': 'https://webfontfree.com',
                'type': 'free',
                'search_pattern': 'https://webfontfree.com/?s={query}',
                'priority': 1
            },
            'Elements Envato': {
                'url': 'https://elements.envato.com/fonts',
                'type': 'commercial',
                'search_pattern': 'https://elements.envato.com/fonts/?search={query}',
                'priority': 2
            },
            'SandollCloud': {
                'url': 'https://www.sandollcloud.com',
                'type': 'commercial',
                'search_pattern': 'https://www.sandollcloud.com/?s={query}',
                'priority': 2
            }
        }
    
    def search(self, query: str, font_type: Optional[str] = None, 
               license_type: Optional[str] = None, max_results: int = 50) -> Dict[str, Any]:
        """
        Search for fonts
        
        Args:
            query: Font name or description
            font_type: Filter by type (serif, sans-serif, script, etc.)
            license_type: Filter by license (free, commercial, subscription)
            max_results: Maximum number of results to return
            
        Returns:
            Search results with sources and links
        """
        try:
            logger.info(f"Searching for fonts: {query}")
            
            # Normalize query
            query_normalized = query.lower().strip()
            
            # Search in local database
            local_results = self._search_local_database(query_normalized, font_type, license_type)
            
            # Generate source links
            source_links = self._generate_source_links(query)
            
            # Compile results
            results = {
                'query': query,
                'local_matches': local_results[:max_results],
                'source_links': source_links,
                'total_results': len(local_results),
                'filters_applied': {
                    'type': font_type,
                    'license': license_type
                }
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return {
                'query': query,
                'error': str(e),
                'local_matches': [],
                'source_links': self._generate_source_links(query)
            }
    
    def _search_local_database(self, query: str, font_type: Optional[str] = None,
                              license_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search in local font database"""
        results = []
        
        for font in self.font_database.get('fonts', []):
            # Check name match
            font_name = font.get('name', '').lower()
            if query not in font_name and font_name != query:
                continue
            
            # Check type filter
            if font_type and font.get('type', '').lower() != font_type.lower():
                continue
            
            # Check license filter
            if license_type and font.get('license', '').lower() != license_type.lower():
                continue
            
            results.append(font)
        
        return sorted(results, key=lambda x: x.get('relevance', 0), reverse=True)
    
    def _generate_source_links(self, query: str) -> List[Dict[str, str]]:
        """Generate search links for all font sources"""
        sources = []
        query_encoded = quote(query.replace(' ', '+'))
        
        # Sort by priority
        sorted_sources = sorted(self.font_sources.items(), 
                               key=lambda x: x[1].get('priority', 999))
        
        for source_name, source_info in sorted_sources:
            search_url = source_info['search_pattern'].format(query=query_encoded)
            sources.append({
                'name': source_name,
                'url': search_url,
                'availability': source_info['type'],
                'baseUrl': source_info['url'],
                'priority': source_info.get('priority', 999)
            })
        
        return sources
    
    def bulk_search(self, queries: List[str]) -> Dict[str, Any]:
        """
        Search for multiple fonts at once
        
        Args:
            queries: List of font names to search
            
        Returns:
            Dictionary with results for each query
        """
        results = {}
        
        for query in queries:
            results[query] = self.search(query)
        
        return results
    
    def get_sources(self) -> List[Dict[str, Any]]:
        """Get all available font sources"""
        sources = []
        
        for name, info in self.font_sources.items():
            sources.append({
                'name': name,
                'url': info['url'],
                'type': info['type'],
                'priority': info.get('priority', 999)
            })
        
        return sorted(sources, key=lambda x: x['priority'])
    
    def filter_fonts(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter fonts based on criteria
        
        Args:
            criteria: Dictionary with filter criteria
                - name: partial name match
                - type: font type
                - license: license type
                - weight: font weight
                - style: font style
        
        Returns:
            Filtered list of fonts
        """
        results = self.font_database.get('fonts', [])
        
        if 'name' in criteria:
            name_lower = criteria['name'].lower()
            results = [f for f in results if name_lower in f.get('name', '').lower()]
        
        if 'type' in criteria:
            results = [f for f in results if f.get('type', '').lower() == criteria['type'].lower()]
        
        if 'license' in criteria:
            results = [f for f in results if f.get('license', '').lower() == criteria['license'].lower()]
        
        if 'weight' in criteria:
            results = [f for f in results if criteria['weight'] in f.get('weights', [])]
        
        if 'style' in criteria:
            results = [f for f in results if criteria['style'] in f.get('styles', [])]
        
        return results
    
    def get_font_details(self, font_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific font"""
        for font in self.font_database.get('fonts', []):
            if font.get('name', '').lower() == font_name.lower():
                return font
        
        return None
    
    def update_database(self, fonts: List[Dict[str, Any]]) -> bool:
        """Update the font database"""
        try:
            self.font_database['fonts'] = fonts
            
            # Save to file
            os.makedirs(os.path.dirname(self.database_path), exist_ok=True)
            with open(self.database_path, 'w', encoding='utf-8') as f:
                json.dump(self.font_database, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Database updated with {len(fonts)} fonts")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update database: {str(e)}")
            return False
