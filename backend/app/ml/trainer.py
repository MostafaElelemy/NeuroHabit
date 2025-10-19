"""
LightGBM model trainer for habit success prediction.
Generates synthetic training data and trains a model.
"""
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score
import os
import json


def generate_synthetic_data(n_samples: int = 1000) -> pd.DataFrame:
    """
    Generate synthetic habit tracking data for training.
    
    Args:
        n_samples: Number of samples to generate
        
    Returns:
        DataFrame with features and target
    """
    np.random.seed(42)
    
    data = {
        # Habit characteristics
        'difficulty_rating': np.random.randint(1, 6, n_samples),
        'importance_rating': np.random.randint(1, 6, n_samples),
        'current_streak': np.random.randint(0, 100, n_samples),
        'longest_streak': np.random.randint(0, 150, n_samples),
        'habit_age_days': np.random.randint(1, 365, n_samples),
        
        # User context
        'time_of_day': np.random.choice([0, 1, 2, 3], n_samples),  # morning, afternoon, evening, night
        'day_of_week': np.random.randint(0, 7, n_samples),
        'is_weekend': np.random.randint(0, 2, n_samples),
        
        # Historical performance
        'completion_rate_7d': np.random.uniform(0, 1, n_samples),
        'completion_rate_30d': np.random.uniform(0, 1, n_samples),
        'avg_mood': np.random.uniform(1, 5, n_samples),
        'avg_energy': np.random.uniform(1, 5, n_samples),
        
        # Pet stats (gamification)
        'pet_level': np.random.randint(1, 50, n_samples),
        'pet_happiness': np.random.randint(0, 101, n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Generate target based on features (with some logic)
    # Higher completion rates, lower difficulty, higher importance -> higher success
    success_probability = (
        0.3 * df['completion_rate_30d'] +
        0.2 * (6 - df['difficulty_rating']) / 5 +
        0.2 * df['importance_rating'] / 5 +
        0.15 * (df['current_streak'] > 7).astype(int) +
        0.1 * df['avg_energy'] / 5 +
        0.05 * (df['pet_happiness'] / 100)
    )
    
    # Add some noise
    success_probability += np.random.normal(0, 0.1, n_samples)
    success_probability = np.clip(success_probability, 0, 1)
    
    # Binary target: will the habit be completed?
    df['success'] = (success_probability > 0.5).astype(int)
    
    return df


def train_model(save_path: str = "/app/models/habit_model.txt") -> dict:
    """
    Train LightGBM model on synthetic data.
    
    Args:
        save_path: Path to save the trained model
        
    Returns:
        Dictionary with training metrics
    """
    print("Generating synthetic training data...")
    df = generate_synthetic_data(n_samples=5000)
    
    # Prepare features and target
    feature_cols = [col for col in df.columns if col != 'success']
    X = df[feature_cols]
    y = df['success']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Create LightGBM datasets
    train_data = lgb.Dataset(X_train, label=y_train)
    test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
    
    # Set parameters
    params = {
        'objective': 'binary',
        'metric': 'binary_logloss',
        'boosting_type': 'gbdt',
        'num_leaves': 31,
        'learning_rate': 0.05,
        'feature_fraction': 0.9,
        'bagging_fraction': 0.8,
        'bagging_freq': 5,
        'verbose': 0
    }
    
    # Train model
    print("Training LightGBM model...")
    model = lgb.train(
        params,
        train_data,
        num_boost_round=100,
        valid_sets=[test_data],
        valid_names=['test']
    )
    
    # Evaluate
    y_pred_proba = model.predict(X_test)
    y_pred = (y_pred_proba > 0.5).astype(int)
    
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_pred_proba)
    
    print(f"\nModel Performance:")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"AUC-ROC: {auc:.4f}")
    
    # Feature importance
    importance = model.feature_importance(importance_type='gain')
    feature_importance = dict(zip(feature_cols, importance.tolist()))
    
    print("\nTop 5 Feature Importances:")
    sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
    for feat, imp in sorted_features[:5]:
        print(f"  {feat}: {imp:.2f}")
    
    # Save model
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    model.save_model(save_path)
    print(f"\nModel saved to: {save_path}")
    
    # Save feature names and metadata
    metadata = {
        'feature_names': feature_cols,
        'feature_importance': feature_importance,
        'accuracy': accuracy,
        'auc': auc,
        'n_samples': len(df),
        'n_features': len(feature_cols)
    }
    
    metadata_path = save_path.replace('.txt', '_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadata saved to: {metadata_path}")
    
    return metadata


if __name__ == "__main__":
    """Run training when script is executed directly."""
    print("=" * 60)
    print("NeuroHabit ML Model Training")
    print("=" * 60)
    
    metrics = train_model()
    
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
