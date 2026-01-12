import pandas as pd
import numpy as np
import logging
from app.exceptions import ValidationError

logger = logging.getLogger(__name__)

class DataCleaner:
    """
    Pipeline for cleaning and validating SoulSense data.
    """
    
    @staticmethod
    def clean_age(age):
        """
        Validate and clip age to realistic bounds (5-120).
        Returns None if invalid/missing and cannot be fixed.
        """
        if age is None or str(age).strip() == "":
            logger.warning("Age input is missing or empty")
            return None
        
        try:
            age = int(float(age)) # Handle "25.0" string
        except (ValueError, TypeError):
            logger.warning(f"Invalid age format: {age}")
            return None
            
        # Clip outliers
        if age < 5:
            logger.warning(f"Age {age} too low, clipping to 5")
            return 5
        if age > 120:
            logger.warning(f"Age {age} too high, clipping to 120")
            return 120
            
        return age

    @staticmethod
    def clean_score(score, max_possible=None):
        """
        Ensure score is non-negative and optionally within max bounds.
        """
        if score is None:
            return 0
            
        try:
            score = int(float(score))
        except (ValueError, TypeError):
            logger.warning(f"Invalid score format: {score}")
            return 0
            
        if score < 0:
            logger.warning(f"Negative score {score} detected, setting to 0")
            return 0
            
        if max_possible and score > max_possible:
            logger.warning(f"Score {score} exceeds max {max_possible}, clipping")
            return max_possible
            
        return score

    @staticmethod
    def clean_inputs(q_scores, age, total_score):
        """
        Clean a full set of inputs for prediction.
        Returns cleaned (q_scores, age, total_score)
        """
        # Clean Age
        clean_age = DataCleaner.clean_age(age)
        if clean_age is None:
            clean_age = 25 # Default fallback
            
        # Clean Scores
        clean_total = DataCleaner.clean_score(total_score, max_possible=125) # 25 questions * 5
        
        # Clean Q-Scores list
        clean_q_scores = []
        if q_scores:
            clean_q_scores = [DataCleaner.clean_score(s, 5) for s in q_scores]
        
        return clean_q_scores, clean_age, clean_total

    @staticmethod
    def clean_dataframe(df):
        """
        Apply cleaning rules to a pandas DataFrame (e.g. for ML training).
        """
        if df is None or df.empty:
            logger.warning("Empty dataframe provided for cleaning")
            return df
            
        # 1. Drop duplicates
        initial_len = len(df)
        df = df.drop_duplicates()
        if len(df) < initial_len:
            logger.info(f"Dropped {initial_len - len(df)} duplicate rows")

        # 2. Clean Age
        if 'age' in df.columns:
            # Coerce errors to NaN, then fill or drop
            df['age'] = pd.to_numeric(df['age'], errors='coerce')
            
            # Fill missing ages with median (simple imputation)
            median_age = df['age'].median()
            if pd.isna(median_age):
                median_age = 30 # Fallback
                
            df['age'] = df['age'].fillna(median_age)
            
            # Clip values
            df['age'] = df['age'].clip(lower=5, upper=120)

        # 3. Clean Scores
        if 'total_score' in df.columns:
            df['total_score'] = pd.to_numeric(df['total_score'], errors='coerce')
            df['total_score'] = df['total_score'].fillna(0).clip(lower=0)
            
        logger.info("Dataframe cleaning complete")
        return df

if __name__ == "__main__":
    # Self-test
    print("Testing DataCleaner...")
    print(f"Clean Age (150): {DataCleaner.clean_age(150)}")
    print(f"Clean Age (-5): {DataCleaner.clean_age(-5)}")
    print(f"Clean Age ('abc'): {DataCleaner.clean_age('abc')}")
    print(f"Clean Score (10, 5): {DataCleaner.clean_score(10, 5)}")
