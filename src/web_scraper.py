"""
Web Scraper for Font Sources
Automatically discovers and updates font databases
"""

import os
import json
import asyncio
from typing import List, Dict, Any
import aiohttp
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class WebScraper:
    """Web scraper for discovering new fonts from repositories"""
    
    def __init__(self, database_path: str = './data/font_database.json'):
        """Initialize the web scraper"""
        self.database_path = database_path
        self.font_database = self._load_database()
        self.scraped_sources = []
    
    def _load_database(self) -> Dict[str, Any]:
        """Load font database"""
        if os.path.exists(self.database_path):
            try:
                with open(self.database_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load database: {str(e)}")
        return {'fonts': []}
    
    async def scrape_google_fonts(self) -> List[Dict[str, Any]]:
        """Scrape Google Fonts"""
        fonts = []
        try:
            async with aiohttp.ClientSession() as session:
                url = 'https://www.googleapis.com/webfonts/v1/webfonts?key=AIzaSyB8A4SqM9HFnmT4w9hLmgCn6OMfz-iBE1U&sort=popularity'
                
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        for item in data.get('items', [])[:100]:
                            fonts.append({
                                'name': item.get('family', ''),
                                'type': 'sans-serif',  # Simplified
                                'license': 'free',
                                'source': 'Google Fonts',
                                'url': f"https://fonts.google.com/specimen/{item.get('family', '').replace(' ', '+')}"
                            })
        except Exception as e:
            logger.error(f"Error scraping Google Fonts: {str(e)}")
        
        return fonts
    
    async def scrape_dafont(self) -> List[Dict[str, Any]]:
        """Scrape DaFont"""
        fonts = []
        try:
            async with aiohttp.ClientSession() as session:
                url = 'https://www.dafont.com/new.php'
                
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Find font entries (simplified - actual scraping would be more complex)
                        font_links = soup.find_all('a', class_='l')[:50]
                        
                        for link in font_links:
                            font_name = link.get_text().strip()
                            if font_name:
                                fonts.append({
                                    'name': font_name,
                                    'type': 'unknown',
                                    'license': 'free',
                                    'source': 'DaFont',
                                    'url': f"https://www.dafont.com/{font_name.lower().replace(' ', '-')}"
                                })
        except Exception as e:
            logger.error(f"Error scraping DaFont: {str(e)}")
        
        return fonts
    
    async def scrape_1001fonts(self) -> List[Dict[str, Any]]:
        """Scrape 1001 Fonts"""
        fonts = []
        try:
            async with aiohttp.ClientSession() as session:
                url = 'https://www.1001fonts.com/fonts/popular-fonts.html'
                
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Find font entries
                        font_links = soup.find_all('a', class_='fontfamily')[:50]
                        
                        for link in font_links:
                            font_name = link.get_text().strip()
                            if font_name:
                                fonts.append({
                                    'name': font_name,
                                    'type': 'unknown',
                                    'license': 'free',
                                    'source': '1001 Fonts',
                                    'url': link.get('href', '')
                                })
        except Exception as e:
            logger.error(f"Error scraping 1001 Fonts: {str(e)}")
        
        return fonts
    
    async def scrape_fontspace(self) -> List[Dict[str, Any]]:
        """Scrape Font Space"""
        fonts = []
        try:
            async with aiohttp.ClientSession() as session:
                url = 'https://www.fontspace.com/'
                
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Find font entries
                        font_cards = soup.find_all('div', class_='fs-font-card')[:50]
                        
                        for card in font_cards:
                            link = card.find('a')
                            if link:
                                font_name = link.get('title', '').strip()
                                if font_name:
                                    fonts.append({
                                        'name': font_name,
                                        'type': 'unknown',
                                        'license': 'free',
                                        'source': 'Font Space',
                                        'url': f"https://www.fontspace.com{link.get('href', '')}"
                                    })
        except Exception as e:
            logger.error(f"Error scraping Font Space: {str(e)}")
        
        return fonts
    
    async def scrape_all_sources(self) -> List[Dict[str, Any]]:
        """Scrape all available sources"""
        tasks = [
            self.scrape_google_fonts(),
            self.scrape_dafont(),
            self.scrape_1001fonts(),
            self.scrape_fontspace()
        ]
        
        results = await asyncio.gather(*tasks)
        all_fonts = []
        
        for fonts in results:
            all_fonts.extend(fonts)
        
        # Remove duplicates
        unique_fonts = {}
        for font in all_fonts:
            key = font['name'].lower()
            if key not in unique_fonts:
                unique_fonts[key] = font
        
        return list(unique_fonts.values())
    
    def discover_new_sources(self) -> List[str]:
        """Discover new font sources from search engines"""
        # This would use web search APIs to discover new sources
        potential_sources = [
            'https://www.fontsawesome.com/',
            'https://www.fontsfree.net/',
            'https://www.typewolf.com/',
            'https://www.fontsheroes.com/',
            'https://www.fontdownload.ru/',
        ]
        
        return potential_sources
    
    def update_database_async(self) -> bool:
        """Update database with scraped fonts"""
        try:
            loop = asyncio.get_event_loop()
            new_fonts = loop.run_until_complete(self.scrape_all_sources())
            
            # Merge with existing fonts
            existing_names = {f['name'].lower() for f in self.font_database.get('fonts', [])}
            fonts_to_add = [f for f in new_fonts if f['name'].lower() not in existing_names]
            
            all_fonts = self.font_database.get('fonts', []) + fonts_to_add
            self.font_database['fonts'] = all_fonts
            
            # Save to file
            os.makedirs(os.path.dirname(self.database_path), exist_ok=True)
            with open(self.database_path, 'w', encoding='utf-8') as f:
                json.dump(self.font_database, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Database updated. Added {len(fonts_to_add)} new fonts. Total: {len(all_fonts)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update database: {str(e)}")
            return False
    
    def schedule_scraping(self, interval_seconds: int = 604800) -> None:
        """Schedule periodic scraping (default: weekly)"""
        import schedule
        
        schedule.every(interval_seconds).seconds.do(self.update_database_async)
        
        logger.info(f"Scraping scheduled every {interval_seconds} seconds")
