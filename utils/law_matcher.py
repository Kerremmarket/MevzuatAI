"""
Law Matcher Utility
Matches law names from RAG results with full text from Excel dataset
"""

import pandas as pd
from typing import List, Dict, Optional
import logging
from config.config import Config
import os

class LawMatcher:
    def __init__(self, dataset_path: str = None):
        """Initialize Law Matcher"""
        self.dataset_path = dataset_path or os.path.join(Config.DATA_DIR, Config.LEGAL_DATASET)
        self.df = None
        self.logger = logging.getLogger(__name__)
        
        # Load the dataset
        self.load_dataset()
    
    def load_dataset(self):
        """Load the legal dataset from Excel"""
        try:
            self.logger.info(f"Loading dataset from: {self.dataset_path}")
            self.df = pd.read_excel(self.dataset_path)
            self.logger.info(f"Loaded {len(self.df)} legal documents")
            
            # Log column names for debugging
            self.logger.info(f"Columns: {list(self.df.columns)}")
            
        except Exception as e:
            self.logger.error(f"Error loading dataset: {str(e)}")
            raise
    
    def find_law_by_name(self, law_name: str) -> Optional[Dict]:
        """
        Find a law's full information by its name
        
        Args:
            law_name (str): Name of the law to find
            
        Returns:
            Dict: Law information including full text
        """
        try:
            # Try exact match first
            exact_match = self.df[self.df['mevAdi'].str.contains(law_name, case=False, na=False)]
            
            if not exact_match.empty:
                law_data = exact_match.iloc[0]
                return {
                    'law_name': law_data['mevAdi'],
                    'law_type': law_data['law_type'],
                    'law_number': law_data.get('mevzuatNo', ''),
                    'acceptance_date': law_data.get('kabulTarih', ''),
                    'gazette_date': law_data.get('resmiGazeteTarihi', ''),
                    'gazette_number': law_data.get('resmiGazeteSayisi', ''),
                    'full_text': law_data['full_text'],
                    'text_length': law_data.get('text_length', len(law_data['full_text'])),
                    'detail_url': law_data.get('detail_url', '')
                }
            
            # If no exact match, try partial match
            partial_matches = self.df[self.df['mevAdi'].str.contains(
                law_name.split()[0], case=False, na=False
            )]
            
            if not partial_matches.empty:
                # Take the first partial match
                law_data = partial_matches.iloc[0]
                return {
                    'law_name': law_data['mevAdi'],
                    'law_type': law_data['law_type'],
                    'law_number': law_data.get('mevzuatNo', ''),
                    'acceptance_date': law_data.get('kabulTarih', ''),
                    'gazette_date': law_data.get('resmiGazeteTarihi', ''),
                    'gazette_number': law_data.get('resmiGazeteSayisi', ''),
                    'full_text': law_data['full_text'],
                    'text_length': law_data.get('text_length', len(law_data['full_text'])),
                    'detail_url': law_data.get('detail_url', '')
                }
            
            self.logger.warning(f"No match found for law: {law_name}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding law '{law_name}': {str(e)}")
            return None
    
    def find_multiple_laws(self, law_names: List[str]) -> List[Dict]:
        """
        Find multiple laws by their names
        
        Args:
            law_names (List[str]): List of law names to find
            
        Returns:
            List[Dict]: List of law information dictionaries
        """
        results = []
        
        for law_name in law_names:
            law_data = self.find_law_by_name(law_name)
            if law_data:
                results.append(law_data)
        
        self.logger.info(f"Found {len(results)} out of {len(law_names)} requested laws")
        return results
    
    def get_laws_summary(self, law_names: List[str]) -> List[Dict]:
        """
        Get a summary of laws without full text (for display purposes)
        
        Args:
            law_names (List[str]): List of law names
            
        Returns:
            List[Dict]: List of law summaries
        """
        results = []
        
        for law_name in law_names:
            law_data = self.find_law_by_name(law_name)
            if law_data:
                summary = {
                    'law_name': law_data['law_name'],
                    'law_type': law_data['law_type'],
                    'law_number': law_data['law_number'],
                    'acceptance_date': law_data['acceptance_date'],
                    'text_preview': law_data['full_text'][:200] + "..." if len(law_data['full_text']) > 200 else law_data['full_text']
                }
                results.append(summary)
        
        return results
    
    def get_combined_law_text(self, law_names: List[str], max_length: int = 15000) -> str:
        """
        Get combined text from multiple laws for Agent 3
        Truncates if too long to fit in context window
        
        Args:
            law_names (List[str]): List of law names
            max_length (int): Maximum character length
            
        Returns:
            str: Combined law text
        """
        laws = self.find_multiple_laws(law_names)
        combined_text = ""
        
        for law in laws:
            law_section = f"\n\n=== {law['law_name']} ===\n"
            law_section += f"Kanun No: {law['law_number']}\n"
            law_section += f"Kabul Tarihi: {law['acceptance_date']}\n"
            law_section += f"Türü: {law['law_type']}\n\n"
            law_section += law['full_text']
            law_section += "\n" + "="*50
            
            # Check if adding this law would exceed the limit
            if len(combined_text + law_section) > max_length:
                # Truncate the current law text to fit
                remaining_space = max_length - len(combined_text) - len(law_section.split('\n\n')[0]) - 100
                if remaining_space > 200:  # Only add if we have reasonable space
                    truncated_text = law['full_text'][:remaining_space] + "...\n[Metin kısaltıldı]"
                    law_section = f"\n\n=== {law['law_name']} ===\n"
                    law_section += f"Kanun No: {law['law_number']}\n"
                    law_section += f"Kabul Tarihi: {law['acceptance_date']}\n"
                    law_section += f"Türü: {law['law_type']}\n\n"
                    law_section += truncated_text
                    combined_text += law_section
                break
            
            combined_text += law_section
        
        return combined_text
    
    def test_law_matcher(self):
        """Test the law matcher with sample law names"""
        test_law_names = [
            "ÇEVRE KANUNU",
            "İŞ KANUNU", 
            "TÜRK CEZA KANUNU",
            "VERGİ USUL KANUNU"
        ]
        
        print("🧪 Testing Law Matcher")
        print("=" * 50)
        
        for i, law_name in enumerate(test_law_names, 1):
            print(f"\n{i}. Searching for: {law_name}")
            law_data = self.find_law_by_name(law_name)
            
            if law_data:
                print(f"   ✅ Found: {law_data['law_name']}")
                print(f"   📋 Type: {law_data['law_type']}")
                print(f"   📊 Text Length: {law_data['text_length']} characters")
                print(f"   📅 Acceptance Date: {law_data['acceptance_date']}")
            else:
                print(f"   ❌ Not found")

if __name__ == "__main__":
    # Test the law matcher
    matcher = LawMatcher()
    matcher.test_law_matcher()