"""
LightGBM model predictor for habit success prediction.
"""
import lightgbm as lgb
import numpy as np
import pandas as pd
import json
import os
from typing import Dict, List, Tuple
from datetime import datetime


class HabitPredictor:
    """Predictor class for habit success using LightGBM."""
    
    def __init__(self, model_path: str = "/app/models/habit_model.txt"):
        """
        Initialize predictor with trained model.
        
        Args:
            model_path: Path to saved LightGBM model
        """
        self.model_path = model_path
        self.metadata_path = model_path.replace('.txt', '_metadata.json')
        self.model = None
        self.feature_names = None
        self.feature_importance = None
        
        self._load_model()
    
    def _load_model(self):
        """Load the trained model and metadata."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Model not found at {self.model_path}. "
                "Please run trainer.py first to generate the model."
            )
        
        # Load model
        self.model = lgb.Booster(model_file=self.model_path)
        
        # Load metadata
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, 'r') as f:
                metadata = json.load(f)
                self.feature_names = metadata.get('feature_names', [])
                self.feature_importance = metadata.get('feature_importance', {})
        else:
            # Fallback to model's feature names
            self.feature_names = self.model.feature_name()
            self.feature_importance = {}
    
    def prepare_features(self, habit_data: dict, user_data: dict, context: dict) -> pd.DataFrame:
        """
        Prepare features from habit, user, and context data.
        
        Args:
            habit_data: Dictionary with habit information
            user_data: Dictionary with user information
            context: Dictionary with contextual information
            
        Returns:
            DataFrame with features ready for prediction
        """
        # Extract features
        features = {
            'difficulty_rating': habit_data.get('difficulty_rating', 3),
            'importance_rating': habit_data.get('importance_rating', 3),
            'current_streak': habit_data.get('current_streak', 0),
            'longest_streak': habit_data.get('longest_streak', 0),
            'habit_age_days': habit_data.get('habit_age_days', 1),
            
            'time_of_day': self._encode_time_of_day(context.get('time_of_day', 'morning')),
            'day_of_week': context.get('day_of_week', datetime.now().weekday()),
            'is_weekend': int(context.get('day_of_week', datetime.now().weekday()) >= 5),
            
            'completion_rate_7d': habit_data.get('completion_rate_7d', 0.5),
            'completion_rate_30d': habit_data.get('completion_rate_30d', 0.5),
            'avg_mood': habit_data.get('avg_mood', 3.0),
            'avg_energy': habit_data.get('avg_energy', 3.0),
            
            'pet_level': user_data.get('pet_level', 1),
            'pet_happiness': user_data.get('pet_happiness', 50),
        }
        
        # Create DataFrame with correct feature order
        df = pd.DataFrame([features])
        
        # Ensure all expected features are present
        for feat in self.feature_names:
            if feat not in df.columns:
                df[feat] = 0
        
        # Reorder columns to match training
        df = df[self.feature_names]
        
        return df
    
    def _encode_time_of_day(self, time_str: str) -> int:
        """Encode time of day string to integer."""
        mapping = {
            'morning': 0,
            'afternoon': 1,
            'evening': 2,
            'night': 3
        }
        return mapping.get(time_str.lower(), 0)
    
    def predict(
        self,
        habit_data: dict,
        user_data: dict,
        context: dict = None
    ) -> Tuple[float, List[Dict[str, float]]]:
        """
        Predict habit success probability.
        
        Args:
            habit_data: Dictionary with habit information
            user_data: Dictionary with user information
            context: Optional dictionary with contextual information
            
        Returns:
            Tuple of (risk_score, feature_importance_list)
        """
        if context is None:
            context = {}
        
        # Prepare features
        X = self.prepare_features(habit_data, user_data, context)
        
        # Make prediction
        success_probability = self.model.predict(X)[0]
        risk_score = 1.0 - success_probability  # Risk of failure
        
        # Get feature importance for this prediction
        feature_importance_list = self._get_top_features(X, n=5)
        
        return risk_score, feature_importance_list
    
    def _get_top_features(self, X: pd.DataFrame, n: int = 5) -> List[Dict[str, float]]:
        """
        Get top N most important features for the prediction.
        
        Args:
            X: Feature DataFrame
            n: Number of top features to return
            
        Returns:
            List of dictionaries with feature names and importance scores
        """
        if not self.feature_importance:
            # Use model's feature importance
            importance = self.model.feature_importance(importance_type='gain')
            self.feature_importance = dict(zip(self.feature_names, importance.tolist()))
        
        # Sort by importance
        sorted_features = sorted(
            self.feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return top N
        top_features = [
            {
                'feature': feat,
                'importance': float(imp),
                'value': float(X[feat].iloc[0]) if feat in X.columns else 0.0
            }
            for feat, imp in sorted_features[:n]
        ]
        
        return top_features
    
    def get_recommendation(self, risk_score: float, feature_importance: List[Dict]) -> str:
        """
        Generate a recommendation based on prediction.
        
        Args:
            risk_score: Predicted risk score (0-1)
            feature_importance: List of important features
            
        Returns:
            Recommendation string
        """
        if risk_score < 0.3:
            return "Great momentum! Keep up the excellent work. Your habit is on track."
        elif risk_score < 0.6:
            recommendation = "You're doing well, but there's room for improvement. "
            
            # Add specific advice based on top feature
            if feature_importance:
                top_feature = feature_importance[0]['feature']
                if 'completion_rate' in top_feature:
                    recommendation += "Try to maintain consistency in your completions."
                elif 'streak' in top_feature:
                    recommendation += "Focus on building your streak day by day."
                elif 'difficulty' in top_feature:
                    recommendation += "Consider adjusting the difficulty to match your capacity."
                elif 'energy' in top_feature:
                    recommendation += "Schedule this habit when your energy levels are higher."
            
            return recommendation
        else:
            return (
                "This habit needs attention. Consider breaking it into smaller steps, "
                "adjusting the timing, or seeking support from the community."
            )


# Global predictor instance
_predictor = None


def get_predictor() -> HabitPredictor:
    """Get or create global predictor instance."""
    global _predictor
    if _predictor is None:
        _predictor = HabitPredictor()
    return _predictor
