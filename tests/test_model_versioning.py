"""
Tests for Model Versioning System

Tests cover:
- Model registration and retrieval
- Semantic versioning
- Experiment tracking
- Model comparison and rollback
"""

import pytest
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock
from datetime import datetime, timezone

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model_versioning import (
    SemanticVersion,
    ModelRegistry,
    ExperimentTracker,
    ModelVersioningManager,
    ModelMetadata,
    ExperimentRecord,
    create_versioning_manager
)


class TestSemanticVersion:
    """Tests for SemanticVersion class"""
    
    def test_parse_version(self):
        """Test parsing version string"""
        v = SemanticVersion("2.3.4")
        assert v.major == 2
        assert v.minor == 3
        assert v.patch == 4
    
    def test_default_version(self):
        """Test default version is 1.0.0"""
        v = SemanticVersion()
        assert str(v) == "1.0.0"
    
    def test_bump_major(self):
        """Test major version bump"""
        v = SemanticVersion("1.2.3")
        new_v = v.bump_major()
        assert str(new_v) == "2.0.0"
    
    def test_bump_minor(self):
        """Test minor version bump"""
        v = SemanticVersion("1.2.3")
        new_v = v.bump_minor()
        assert str(new_v) == "1.3.0"
    
    def test_bump_patch(self):
        """Test patch version bump"""
        v = SemanticVersion("1.2.3")
        new_v = v.bump_patch()
        assert str(new_v) == "1.2.4"
    
    def test_version_comparison(self):
        """Test version comparison"""
        v1 = SemanticVersion("1.0.0")
        v2 = SemanticVersion("1.1.0")
        v3 = SemanticVersion("2.0.0")
        
        assert v1 < v2
        assert v2 < v3
        assert not v3 < v1
    
    def test_version_equality(self):
        """Test version equality"""
        v1 = SemanticVersion("1.2.3")
        v2 = SemanticVersion("1.2.3")
        assert v1 == v2


class TestModelRegistry:
    """Tests for ModelRegistry class"""
    
    @pytest.fixture
    def temp_registry(self):
        """Create a temporary registry for testing"""
        temp_dir = tempfile.mkdtemp()
        registry_path = os.path.join(temp_dir, "registry")
        registry = ModelRegistry(registry_path)
        yield registry
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_model(self):
        """Create a mock model for testing"""
        model = MagicMock()
        model.predict = MagicMock(return_value=[0])
        return model
    
    def test_create_registry(self, temp_registry):
        """Test registry creation"""
        assert temp_registry.registry_path.exists()
        assert temp_registry.models_path.exists()
    
    def test_register_model(self, temp_registry, mock_model):
        """Test model registration"""
        metadata = temp_registry.register_model(
            model=mock_model,
            name="test_model",
            description="Test model",
            metrics={"accuracy": 0.95}
        )
        
        assert metadata.name == "test_model"
        assert metadata.version == "1.0.0"
        assert metadata.metrics["accuracy"] == 0.95
    
    def test_get_model(self, temp_registry, mock_model):
        """Test model retrieval"""
        temp_registry.register_model(
            model=mock_model,
            name="test_model"
        )
        
        model_data, metadata = temp_registry.get_model("test_model")
        
        assert model_data["model"] is not None
        assert metadata.name == "test_model"
    
    def test_version_bumping(self, temp_registry, mock_model):
        """Test automatic version bumping"""
        # Register first version
        meta1 = temp_registry.register_model(
            model=mock_model,
            name="test_model"
        )
        assert meta1.version == "1.0.0"
        
        # Register patch version
        meta2 = temp_registry.register_model(
            model=mock_model,
            name="test_model",
            bump_type="patch"
        )
        assert meta2.version == "1.0.1"
        
        # Register minor version
        meta3 = temp_registry.register_model(
            model=mock_model,
            name="test_model",
            bump_type="minor"
        )
        assert meta3.version == "1.1.0"
        
        # Register major version
        meta4 = temp_registry.register_model(
            model=mock_model,
            name="test_model",
            bump_type="major"
        )
        assert meta4.version == "2.0.0"
    
    def test_list_models(self, temp_registry, mock_model):
        """Test listing models"""
        temp_registry.register_model(model=mock_model, name="model_a")
        temp_registry.register_model(model=mock_model, name="model_b")
        
        models = temp_registry.list_models()
        
        assert len(models) == 2
        names = [m["name"] for m in models]
        assert "model_a" in names
        assert "model_b" in names
    
    def test_list_versions(self, temp_registry, mock_model):
        """Test listing versions"""
        temp_registry.register_model(model=mock_model, name="test_model")
        temp_registry.register_model(model=mock_model, name="test_model")
        temp_registry.register_model(model=mock_model, name="test_model")
        
        versions = temp_registry.list_versions("test_model")
        
        assert len(versions) == 3
    
    def test_promote_to_production(self, temp_registry, mock_model):
        """Test promoting model to production"""
        temp_registry.register_model(model=mock_model, name="test_model")
        temp_registry.register_model(model=mock_model, name="test_model")
        
        result = temp_registry.promote_to_production("test_model", "1.0.0")
        
        assert result is True
        versions = temp_registry.list_versions("test_model")
        prod_version = [v for v in versions if v["is_production"]]
        assert len(prod_version) == 1
        assert prod_version[0]["version"] == "1.0.0"
    
    def test_compare_versions(self, temp_registry, mock_model):
        """Test version comparison"""
        temp_registry.register_model(
            model=mock_model,
            name="test_model",
            metrics={"accuracy": 0.80}
        )
        temp_registry.register_model(
            model=mock_model,
            name="test_model",
            metrics={"accuracy": 0.85}
        )
        
        comparison = temp_registry.compare_versions(
            "test_model", "1.0.0", "1.0.1"
        )
        
        assert comparison["version1"] == "1.0.0"
        assert comparison["version2"] == "1.0.1"
        assert comparison["metrics_comparison"]["accuracy"]["improved"] is True
    
    def test_delete_version(self, temp_registry, mock_model):
        """Test version deletion"""
        temp_registry.register_model(model=mock_model, name="test_model")
        temp_registry.register_model(model=mock_model, name="test_model")
        
        result = temp_registry.delete_version("test_model", "1.0.0")
        
        assert result is True
        versions = temp_registry.list_versions("test_model")
        assert len(versions) == 1
    
    def test_cannot_delete_production(self, temp_registry, mock_model):
        """Test that production model cannot be deleted without force"""
        temp_registry.register_model(model=mock_model, name="test_model")
        temp_registry.promote_to_production("test_model", "1.0.0")
        
        with pytest.raises(ValueError):
            temp_registry.delete_version("test_model", "1.0.0")


class TestExperimentTracker:
    """Tests for ExperimentTracker class"""
    
    @pytest.fixture
    def temp_tracker(self):
        """Create a temporary tracker for testing"""
        temp_dir = tempfile.mkdtemp()
        tracker = ExperimentTracker(temp_dir)
        yield tracker
        shutil.rmtree(temp_dir)
    
    def test_start_experiment(self, temp_tracker):
        """Test starting an experiment"""
        exp_id = temp_tracker.start_experiment(
            name="test_experiment",
            description="Testing"
        )
        
        assert exp_id.startswith("exp_")
        exp = temp_tracker.get_experiment(exp_id)
        assert exp.name == "test_experiment"
        assert exp.status == "running"
    
    def test_log_metrics(self, temp_tracker):
        """Test logging metrics"""
        exp_id = temp_tracker.start_experiment(name="test")
        temp_tracker.log_metrics(exp_id, {"accuracy": 0.9, "loss": 0.1})
        
        exp = temp_tracker.get_experiment(exp_id)
        assert exp.metrics["accuracy"] == 0.9
        assert exp.metrics["loss"] == 0.1
    
    def test_log_artifact(self, temp_tracker):
        """Test logging artifacts"""
        exp_id = temp_tracker.start_experiment(name="test")
        temp_tracker.log_artifact(exp_id, "config", {"key": "value"})
        
        exp = temp_tracker.get_experiment(exp_id)
        assert "config.json" in exp.artifacts
    
    def test_complete_experiment(self, temp_tracker):
        """Test completing an experiment"""
        exp_id = temp_tracker.start_experiment(name="test")
        temp_tracker.complete_experiment(exp_id, model_version="1.0.0")
        
        exp = temp_tracker.get_experiment(exp_id)
        assert exp.status == "completed"
        assert exp.model_version == "1.0.0"
    
    def test_fail_experiment(self, temp_tracker):
        """Test failing an experiment"""
        exp_id = temp_tracker.start_experiment(name="test")
        temp_tracker.fail_experiment(exp_id, "Test error")
        
        exp = temp_tracker.get_experiment(exp_id)
        assert exp.status == "failed"
        assert "Test error" in exp.notes
    
    def test_list_experiments(self, temp_tracker):
        """Test listing experiments"""
        temp_tracker.start_experiment(name="exp1")
        exp2 = temp_tracker.start_experiment(name="exp2")
        temp_tracker.complete_experiment(exp2)
        
        all_exps = temp_tracker.list_experiments()
        completed = temp_tracker.list_experiments(status="completed")
        running = temp_tracker.list_experiments(status="running")
        
        assert len(all_exps) == 2
        assert len(completed) == 1
        assert len(running) == 1
    
    def test_list_experiments_with_tags(self, temp_tracker):
        """Test listing experiments with tag filter"""
        temp_tracker.start_experiment(name="exp1", tags=["prod"])
        temp_tracker.start_experiment(name="exp2", tags=["dev"])
        
        prod_exps = temp_tracker.list_experiments(tags=["prod"])
        
        assert len(prod_exps) == 1
        assert prod_exps[0]["name"] == "exp1"
    
    def test_compare_experiments(self, temp_tracker):
        """Test comparing experiments"""
        exp1 = temp_tracker.start_experiment(name="exp1")
        temp_tracker.log_metrics(exp1, {"accuracy": 0.8})
        
        exp2 = temp_tracker.start_experiment(name="exp2")
        temp_tracker.log_metrics(exp2, {"accuracy": 0.9})
        
        comparison = temp_tracker.compare_experiments([exp1, exp2])
        
        assert len(comparison["experiments"]) == 2
        assert "accuracy" in comparison["metrics_comparison"]
    
    def test_get_best_experiment(self, temp_tracker):
        """Test getting best experiment"""
        exp1 = temp_tracker.start_experiment(name="exp1")
        temp_tracker.log_metrics(exp1, {"accuracy": 0.8})
        temp_tracker.complete_experiment(exp1)
        
        exp2 = temp_tracker.start_experiment(name="exp2")
        temp_tracker.log_metrics(exp2, {"accuracy": 0.9})
        temp_tracker.complete_experiment(exp2)
        
        best = temp_tracker.get_best_experiment("accuracy", maximize=True)
        
        assert best["experiment_id"] == exp2


class TestModelVersioningManager:
    """Tests for ModelVersioningManager class"""
    
    @pytest.fixture
    def temp_manager(self):
        """Create a temporary manager for testing"""
        temp_dir = tempfile.mkdtemp()
        registry_path = os.path.join(temp_dir, "registry")
        experiments_path = os.path.join(temp_dir, "experiments")
        manager = ModelVersioningManager(registry_path, experiments_path)
        yield manager
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_model(self):
        """Create a mock model"""
        return MagicMock()
    
    def test_start_and_end_run(self, temp_manager, mock_model):
        """Test full experiment workflow"""
        # Start run
        exp_id = temp_manager.start_run(
            name="test_run",
            hyperparameters={"lr": 0.01}
        )
        
        # Log metrics
        temp_manager.log_metrics({"accuracy": 0.95})
        
        # End run and register model
        metadata = temp_manager.end_run(
            model=mock_model,
            model_name="test_model"
        )
        
        assert metadata is not None
        assert metadata.name == "test_model"
        
        # Check experiment was completed
        exp = temp_manager.tracker.get_experiment(exp_id)
        assert exp.status == "completed"
    
    def test_fail_run(self, temp_manager):
        """Test failing a run"""
        exp_id = temp_manager.start_run(name="test_run")
        temp_manager.fail_run("Test error")
        
        exp = temp_manager.tracker.get_experiment(exp_id)
        assert exp.status == "failed"
    
    def test_promote_model(self, temp_manager, mock_model):
        """Test promoting model to production"""
        temp_manager.start_run(name="test")
        temp_manager.end_run(model=mock_model, model_name="test_model")
        
        result = temp_manager.promote_model("test_model", "1.0.0")
        
        assert result is True
    
    def test_generate_summary(self, temp_manager, mock_model):
        """Test generating summary"""
        temp_manager.start_run(name="test")
        temp_manager.log_metrics({"accuracy": 0.9})
        temp_manager.end_run(model=mock_model, model_name="test_model")
        
        summary = temp_manager.generate_summary()
        
        assert "MODEL VERSIONING SYSTEM SUMMARY" in summary
        assert "test_model" in summary


class TestCreateVersioningManager:
    """Tests for create_versioning_manager function"""
    
    def test_create_default_manager(self):
        """Test creating manager with default paths"""
        manager = create_versioning_manager()
        
        assert manager is not None
        assert manager.registry is not None
        assert manager.tracker is not None
    
    def test_create_custom_manager(self):
        """Test creating manager with custom paths"""
        temp_dir = tempfile.mkdtemp()
        registry_path = os.path.join(temp_dir, "custom_registry")
        experiments_path = os.path.join(temp_dir, "custom_experiments")
        
        manager = create_versioning_manager(registry_path, experiments_path)
        
        assert manager is not None
        assert Path(registry_path).exists()
        assert Path(experiments_path).exists()
        
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
