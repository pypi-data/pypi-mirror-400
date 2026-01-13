"""Tests for alphai cleanup module."""

import pytest
from unittest.mock import Mock, patch

from alphai.cleanup import CleanupManager, DockerCleanupManager, JupyterCleanupManager


class TestCleanupManager:
    """Tests for the base CleanupManager class."""
    
    def test_init_creates_empty_state(self):
        """Test that initialization creates empty state."""
        manager = CleanupManager()
        assert not manager.has_resources()
        assert not manager._cleanup_done
    
    def test_register_resource(self):
        """Test registering a resource."""
        manager = CleanupManager()
        manager.register_resource('container', 'abc123', lambda: True)
        assert manager.has_resources()
        resource = manager.get_resource('container', 'abc123')
        assert resource is not None
        assert resource['type'] == 'container'
        assert resource['id'] == 'abc123'
    
    def test_unregister_resource(self):
        """Test unregistering a resource."""
        manager = CleanupManager()
        manager.register_resource('container', 'abc123', lambda: True)
        assert manager.has_resources()
        manager.unregister_resource('container', 'abc123')
        assert not manager.has_resources()
    
    def test_add_cleanup_callback(self):
        """Test adding cleanup callbacks."""
        manager = CleanupManager()
        callback = Mock()
        manager.add_cleanup_callback(callback)
        assert manager.has_resources()
    
    def test_cleanup_calls_registered_functions(self):
        """Test that cleanup calls all registered cleanup functions."""
        manager = CleanupManager()
        cleanup_fn = Mock(return_value=True)
        manager.register_resource('container', 'abc123', cleanup_fn)
        
        result = manager.cleanup()
        
        assert result is True
        cleanup_fn.assert_called_once()
        assert manager._cleanup_done
    
    def test_cleanup_calls_callbacks(self):
        """Test that cleanup calls all registered callbacks."""
        manager = CleanupManager()
        callback = Mock()
        manager.add_cleanup_callback(callback)
        
        manager.cleanup()
        
        callback.assert_called_once()
    
    def test_cleanup_only_runs_once(self):
        """Test that cleanup only runs once."""
        manager = CleanupManager()
        cleanup_fn = Mock(return_value=True)
        manager.register_resource('container', 'abc123', cleanup_fn)
        
        manager.cleanup()
        manager.cleanup()
        
        # Should only be called once
        assert cleanup_fn.call_count == 1
    
    def test_cleanup_returns_false_on_failure(self):
        """Test that cleanup returns False if any function fails."""
        manager = CleanupManager()
        cleanup_fn = Mock(return_value=False)
        manager.register_resource('container', 'abc123', cleanup_fn)
        
        result = manager.cleanup()
        
        assert result is False
    
    def test_cleanup_handles_exceptions(self):
        """Test that cleanup handles exceptions gracefully."""
        manager = CleanupManager()
        cleanup_fn = Mock(side_effect=Exception("Test error"))
        manager.register_resource('container', 'abc123', cleanup_fn)
        
        # Should not raise
        result = manager.cleanup()
        
        assert result is False
    
    def test_reset_clears_state(self):
        """Test that reset clears all state."""
        manager = CleanupManager()
        manager.register_resource('container', 'abc123', lambda: True)
        manager.cleanup()
        
        manager.reset()
        
        assert not manager.has_resources()
        assert not manager._cleanup_done


class TestDockerCleanupManager:
    """Tests for DockerCleanupManager."""
    
    def test_set_container(self):
        """Test setting container ID."""
        manager = DockerCleanupManager()
        manager.set_container('abc123')
        assert manager._container_id == 'abc123'
    
    def test_set_tunnel(self):
        """Test setting tunnel ID."""
        manager = DockerCleanupManager()
        manager.set_tunnel('tunnel123')
        assert manager._tunnel_id == 'tunnel123'
    
    def test_set_project(self):
        """Test setting project ID."""
        manager = DockerCleanupManager()
        manager.set_project('project123')
        assert manager._project_id == 'project123'
    
    def test_cleanup_calls_docker_manager(self):
        """Test that cleanup calls docker manager."""
        docker_manager = Mock()
        docker_manager.cleanup_container_and_tunnel.return_value = True
        
        manager = DockerCleanupManager(docker_manager=docker_manager)
        manager.set_container('abc123')
        
        manager.cleanup()
        
        docker_manager.cleanup_container_and_tunnel.assert_called_once()
    
    def test_cleanup_calls_client(self):
        """Test that cleanup calls client for API cleanup."""
        docker_manager = Mock()
        docker_manager.cleanup_container_and_tunnel.return_value = True
        
        client = Mock()
        client.cleanup_tunnel_and_project.return_value = True
        
        manager = DockerCleanupManager(docker_manager=docker_manager, client=client)
        manager.set_container('abc123')
        manager.set_tunnel('tunnel123')
        
        manager.cleanup()
        
        client.cleanup_tunnel_and_project.assert_called_once()


class TestJupyterCleanupManager:
    """Tests for JupyterCleanupManager."""
    
    def test_set_tunnel(self):
        """Test setting tunnel ID."""
        manager = JupyterCleanupManager()
        manager.set_tunnel('tunnel123')
        assert manager._tunnel_id == 'tunnel123'
    
    def test_set_project(self):
        """Test setting project ID."""
        manager = JupyterCleanupManager()
        manager.set_project('project123')
        assert manager._project_id == 'project123'
    
    def test_cleanup_calls_jupyter_manager(self):
        """Test that cleanup calls jupyter manager."""
        jupyter_manager = Mock()
        jupyter_manager.cleanup.return_value = True
        
        manager = JupyterCleanupManager(jupyter_manager=jupyter_manager)
        
        manager.cleanup()
        
        jupyter_manager.cleanup.assert_called_once()

