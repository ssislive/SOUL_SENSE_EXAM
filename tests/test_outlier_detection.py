"""Unit tests for Outlier Detection module"""

import pytest
import numpy as np
from app.outlier_detection import OutlierDetector
from app.db import get_session
from app.models import Score, User, Base
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TestOutlierDetector:
    """Test outlier detection methods"""
    
    @pytest.fixture
    def detector(self):
        """Create detector instance"""
        return OutlierDetector(threshold=2.5)
    
    @pytest.fixture
    def sample_scores(self):
        """Sample scores with outliers"""
        return [23, 25, 24, 26, 25, 24, 25, 23, 150, 22, 24, 25, 26]
    
    @pytest.fixture
    def clean_scores(self):
        """Clean scores without outliers"""
        return [20, 22, 21, 23, 22, 21, 23, 22, 21, 23, 22, 21]
    
    # Z-Score tests
    def test_zscore_detects_outliers(self, detector, sample_scores):
        """Z-score detects outliers"""
        result = detector.detect_outliers_zscore(sample_scores)
        
        assert "outliers" in result
        assert "indices" in result
        assert "z_scores" in result
        assert len(result["outliers"]) > 0, "Should detect at least one outlier"
        assert result["method"] == "zscore"
    
    def test_zscore_clean_data(self, detector, clean_scores):
        """Test Z-score method on clean data"""
        result = detector.detect_outliers_zscore(clean_scores)
        
        assert len(result["outliers"]) == 0, "Should not detect outliers in clean data"
    
    def test_zscore_custom_threshold(self, detector, sample_scores):
        """Test Z-score with custom threshold"""
        result = detector.detect_outliers_zscore(sample_scores, threshold=1.0)
        
        assert result["threshold"] == 1.0
        assert "mean" in result
        assert "std_dev" in result
    
    def test_zscore_empty_list(self, detector):
        """Test Z-score with empty list"""
        result = detector.detect_outliers_zscore([])
        
        assert len(result["outliers"]) == 0
    
    def test_zscore_single_value(self, detector):
        """Test Z-score with single value"""
        result = detector.detect_outliers_zscore([50])
        
        assert len(result["outliers"]) == 0
    
    # ==================== IQR METHOD TESTS ====================
    
    def test_iqr_detects_outliers(self, detector, sample_scores):
        """Test IQR method detects outliers"""
        result = detector.detect_outliers_iqr(sample_scores)
        
        assert "outliers" in result
        assert "indices" in result
        assert result["method"] == "iqr"
        assert len(result["outliers"]) > 0, "Should detect at least one outlier"
    
    def test_iqr_bounds(self, detector, sample_scores):
        """Test IQR bounds calculation"""
        result = detector.detect_outliers_iqr(sample_scores)
        
        assert "lower_bound" in result
        assert "upper_bound" in result
        assert result["lower_bound"] < result["upper_bound"]
    
    def test_iqr_insufficient_data(self, detector):
        """Test IQR with insufficient data"""
        result = detector.detect_outliers_iqr([1, 2, 3])
        
        assert len(result["outliers"]) == 0
    
    # ==================== MODIFIED Z-SCORE TESTS ====================
    
    def test_modified_zscore_detects_outliers(self, detector, sample_scores):
        """Test Modified Z-score method"""
        result = detector.detect_outliers_modified_zscore(sample_scores)
        
        assert "outliers" in result
        assert "indices" in result
        assert "modified_z_scores" in result
        assert result["method"] == "modified-zscore"
    
    def test_modified_zscore_values(self, detector, sample_scores):
        """Test Modified Z-score calculation includes median and MAD"""
        result = detector.detect_outliers_modified_zscore(sample_scores)
        
        assert "median" in result
        assert "mad" in result
        assert result["mad"] >= 0
    
    # ==================== MAD METHOD TESTS ====================
    
    def test_mad_detects_outliers(self, detector, sample_scores):
        """Test MAD method detects outliers"""
        result = detector.detect_outliers_mad(sample_scores)
        
        assert "outliers" in result
        assert "deviations" in result
        assert result["method"] == "mad"
    
    def test_mad_custom_threshold(self, detector, sample_scores):
        """Test MAD with custom threshold"""
        result = detector.detect_outliers_mad(sample_scores, threshold=2.0)
        
        assert result["threshold"] == 2.0
    
    # ==================== ENSEMBLE METHOD TESTS ====================
    
    def test_ensemble_consensus(self, detector, sample_scores):
        """Test Ensemble method with consensus voting"""
        result = detector.detect_outliers_ensemble(sample_scores)
        
        assert "outliers" in result
        assert "votes" in result
        assert "individual_results" in result
        assert result["method"] == "ensemble"
        assert len(result["methods_used"]) >= 4
    
    def test_ensemble_voting(self, detector, sample_scores):
        """Test voting mechanism in ensemble method"""
        result = detector.detect_outliers_ensemble(sample_scores)
        
        votes = result["votes"]
        assert len(votes) == len(sample_scores)
        assert all(0 <= vote <= len(result["methods_used"]) for vote in votes)
    
    def test_ensemble_different_thresholds(self, detector, sample_scores):
        """Test ensemble with different consensus thresholds"""
        result_low = detector.detect_outliers_ensemble(sample_scores, consensus_threshold=0.25)
        result_high = detector.detect_outliers_ensemble(sample_scores, consensus_threshold=0.75)
        
        # Higher threshold should find fewer or equal outliers
        assert len(result_high["outliers"]) <= len(result_low["outliers"])
    
    # ==================== STATISTICAL PROPERTIES TESTS ====================
    
    def test_statistics_consistency(self, detector):
        """Test statistical calculations are consistent"""
        scores = [10, 20, 30, 40, 50]
        
        result = detector.detect_outliers_zscore(scores)
        
        assert result["mean"] == 30
        assert result["std_dev"] == np.std(scores)
    
    def test_iqr_statistical_properties(self, detector):
        """Test IQR calculations"""
        scores = list(range(1, 101))  # 1 to 100
        
        result = detector.detect_outliers_iqr(scores)
        
        assert result["q1"] == np.percentile(scores, 25)
        assert result["q3"] == np.percentile(scores, 75)
        assert result["iqr"] == result["q3"] - result["q1"]
    
    # ==================== EDGE CASE TESTS ====================
    
    def test_all_same_values(self, detector):
        """Test with all identical values"""
        scores = [50, 50, 50, 50, 50]
        
        result = detector.detect_outliers_zscore(scores)
        assert len(result["outliers"]) == 0
        
        result = detector.detect_outliers_iqr(scores)
        assert len(result["outliers"]) == 0
    
    def test_extreme_values(self, detector):
        """Test with extreme values"""
        scores = [1, 2, 3, 4, 5, 100]
        
        result = detector.detect_outliers_ensemble(scores)
        assert len(result["outliers"]) > 0
        assert 100 in result["outliers"]
    
    def test_negative_scores(self, detector):
        """Test with negative scores (shouldn't occur but test robustness)"""
        scores = [-50, 10, 20, 30, 40, 50]
        
        result = detector.detect_outliers_zscore(scores)
        assert "outliers" in result
        assert len(result["outliers"]) > 0
    
    def test_float_scores(self, detector):
        """Test with float scores"""
        scores = [23.5, 24.2, 23.8, 150.3, 22.1]
        
        result = detector.detect_outliers_ensemble(scores)
        assert "outliers" in result
        assert isinstance(result["outliers"][0], float)


class TestOutlierDetectorDatabase:
    """Test suite for database integration"""
    
    @pytest.fixture
    def db_session(self):
        """Create a test database session"""
        session = get_session()
        yield session
        session.close()
    
    @pytest.fixture
    def test_user_with_scores(self, db_session):
        """Create a test user with scores"""
        user = User(username="test_user_outlier")
        db_session.add(user)
        db_session.commit()
        
        # Add scores
        for i, score_val in enumerate([20, 22, 21, 23, 22, 100, 21, 23]):  # 100 is outlier
            score = Score(
                username="test_user_outlier",
                total_score=score_val,
                age=25,
                detailed_age_group="18-25",
                user_id=user.id,
                timestamp=datetime.utcnow().isoformat()
            )
            db_session.add(score)
        
        db_session.commit()
        return user
    
    def test_detect_outliers_for_user(self, db_session, test_user_with_scores):
        """Test outlier detection for a specific user"""
        detector = OutlierDetector()
        
        result = detector.detect_outliers_for_user(
            db_session, 
            "test_user_outlier",
            method="ensemble"
        )
        
        assert "username" in result
        assert "outlier_count" in result
        assert result["username"] == "test_user_outlier"
        assert result["outlier_count"] > 0
        assert "outlier_details" in result
    
    def test_inconsistency_patterns(self, db_session, test_user_with_scores):
        """Test inconsistency pattern detection"""
        detector = OutlierDetector()
        
        result = detector.detect_inconsistency_patterns(
            db_session,
            "test_user_outlier",
            time_window_days=30
        )
        
        assert "username" in result
        assert "time_window_days" in result
        assert "coefficient_of_variation" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
