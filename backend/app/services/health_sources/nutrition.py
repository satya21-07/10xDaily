import os
import pandas as pd
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from app.services.health_sources.base import HealthDataSource

logger = logging.getLogger(__name__)

class ExcelNutritionSource(HealthDataSource):
    """Fetches nutrition data from a local Excel file (Anuvaad INDB 2024)."""
    
    _df: Optional[pd.DataFrame] = None
    
    def __init__(self, excel_path: str = r"d:\10xDaily\frontend\projects\mobile-app\src\assets\Anuvaad_INDB_2024.11.xlsx"):
        self.excel_path = excel_path
        
        # Load the dataframe once globally to avoid reloading on every request
        if ExcelNutritionSource._df is None:
            try:
                logger.info(f"Loading nutrition data from {self.excel_path}")
                ExcelNutritionSource._df = pd.read_excel(self.excel_path, sheet_name=0)
                # Drop rows where food_name is NaN and convert names to string
                ExcelNutritionSource._df = ExcelNutritionSource._df.dropna(subset=['food_name'])
                ExcelNutritionSource._df['food_name'] = ExcelNutritionSource._df['food_name'].astype(str)
            except Exception as e:
                logger.error(f"Failed to load excel nutrition data: {e}")
                ExcelNutritionSource._df = pd.DataFrame()
        
    def get_source_metadata(self) -> Dict[str, str]:
        return {
            "name": "Anuvaad INDB 2024 (Indian Food Composition)",
            "url": "local_excel_file",
            "type": "nutrition",
            "retrieved_at": datetime.now(timezone.utc).isoformat()
        }
        
    def fetch_data(self, topic: str) -> Optional[Dict[str, Any]]:
        if ExcelNutritionSource._df is None or ExcelNutritionSource._df.empty:
            logger.warning("Excel data not loaded.")
            return None
            
        try:
            # Simple keyword search (case-insensitive)
            # Find the first row where the food_name contains the topic
            search_str = topic.lower()
            
            # For exact matches or 'contains'
            matches = ExcelNutritionSource._df[ExcelNutritionSource._df['food_name'].str.lower().str.contains(search_str, na=False)]
            
            if matches.empty:
                # If no direct match, return None to trigger fallback
                return None
                
            # Take the first match
            food = matches.iloc[0]
            
            extracted_data = {
                "food_name": food.get("food_name"),
                "calories_kcal": self._safe_float(food.get("energy_kcal")),
                "protein_g": self._safe_float(food.get("protein_g")),
                "carbohydrates_g": self._safe_float(food.get("carb_g")),
                "fiber_g": self._safe_float(food.get("fibre_g")),
                "fat_g": self._safe_float(food.get("fat_g"))
            }
            
            return {k: v for k, v in extracted_data.items() if v is not None and not pd.isna(v)}
            
        except Exception as e:
            logger.error(f"Error occurred while searching excel data: {e}")
            return None
            
    def _safe_float(self, val) -> Optional[float]:
        try:
            return float(val)
        except (ValueError, TypeError):
            return None
