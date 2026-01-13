#!/usr/bin/env python3
"""
Test Suite 1: Client Session Lifecycle

Tests session creation, metadata management, and lifecycle operations.
"""
import os
import sys
import tempfile
import pytest
import pandas as pd
from pathlib import Path

# Add parent directory and src/lib to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src" / "lib"))

from featrixsphere import FeatrixSphereClient


@pytest.fixture(scope="module")
def client():
    """Create FeatrixSphere client - use local if SPHERE_URL set, else skip tests."""
    sphere_url = os.getenv("SPHERE_URL", "http://localhost:8000")
    client = FeatrixSphereClient(base_url=sphere_url)
    
    # Test connection
    try:
        # Simple health check - try to get sessions (will fail gracefully if server down)
        client._get_json("/health")
        return client
    except Exception as e:
        pytest.skip(f"Cannot connect to Sphere API at {sphere_url}: {e}")


@pytest.fixture
def sample_csv_file():
    """Create temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("col1,col2,target\n")
        f.write("a,1,yes\n")
        f.write("b,2,no\n")
        f.write("c,3,yes\n")
        f.write("a,4,no\n")
        f.write("b,5,yes\n")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except:
        pass


@pytest.fixture
def sample_dataframe():
    """Create sample DataFrame for testing."""
    return pd.DataFrame({
        'feature1': ['apple', 'banana', 'cherry', 'date', 'elderberry'],
        'feature2': [10, 20, 30, 40, 50],
        'feature3': [1.1, 2.2, 3.3, 4.4, 5.5],
        'target': ['good', 'bad', 'good', 'bad', 'good']
    })


class TestSessionCreation:
    """Test session creation from different sources."""
    
    def test_create_session_from_file(self, client, sample_csv_file):
        """Test creating session by uploading CSV file."""
        session_info = client.upload_file_and_create_session(
            file_path=Path(sample_csv_file),
            name="test_file_upload"
        )
        
        assert session_info is not None
        assert session_info.session_id is not None
        assert session_info.status in ["pending", "training", "completed"]
        
        # Cleanup
        try:
            client.mark_for_deletion(session_info.session_id)
        except:
            pass
    
    def test_create_session_from_dataframe(self, client, sample_dataframe):
        """Test creating session from pandas DataFrame."""
        session_info = client.upload_df_and_create_session(
            df=sample_dataframe,
            filename="test_df.csv",
            name="test_df_upload"
        )
        
        assert session_info is not None
        assert session_info.session_id is not None
        
        # Cleanup
        try:
            client.mark_for_deletion(session_info.session_id)
        except:
            pass
    
    def test_create_session_with_metadata(self, client, sample_dataframe):
        """Test creating session with custom metadata."""
        metadata = {
            "test_name": "pytest_session_creation",
            "test_number": 42,
            "test_bool": True
        }
        
        session_info = client.upload_df_and_create_session(
            df=sample_dataframe,
            filename="test_metadata.csv",
            name="test_with_metadata",
            metadata=metadata
        )
        
        assert session_info is not None
        
        # Verify metadata was stored
        status = client.get_session_status(session_info.session_id)
        assert status.user_metadata is not None
        assert status.user_metadata.get("test_name") == "pytest_session_creation"
        assert status.user_metadata.get("test_number") == 42
        
        # Cleanup
        try:
            client.mark_for_deletion(session_info.session_id)
        except:
            pass


class TestSessionMetadata:
    """Test metadata management operations."""
    
    def test_update_metadata_merge(self, client, sample_dataframe):
        """Test updating metadata in merge mode."""
        # Create session with initial metadata
        initial_metadata = {"key1": "value1", "key2": "value2"}
        session_info = client.upload_df_and_create_session(
            df=sample_dataframe,
            filename="test_merge.csv",
            metadata=initial_metadata
        )
        
        # Update with merge (should add new key, preserve existing)
        update_metadata = {"key3": "value3"}
        result = client.update_user_metadata(
            session_info.session_id,
            update_metadata,
            write_mode="merge"
        )
        
        # Verify all keys present
        status = client.get_session_status(session_info.session_id)
        assert status.user_metadata.get("key1") == "value1"
        assert status.user_metadata.get("key2") == "value2"
        assert status.user_metadata.get("key3") == "value3"
        
        # Cleanup
        try:
            client.mark_for_deletion(session_info.session_id)
        except:
            pass
    
    def test_update_metadata_replace(self, client, sample_dataframe):
        """Test updating metadata in replace mode."""
        # Create session with initial metadata
        initial_metadata = {"key1": "value1", "key2": "value2"}
        session_info = client.upload_df_and_create_session(
            df=sample_dataframe,
            filename="test_replace.csv",
            metadata=initial_metadata
        )
        
        # Update with replace (should replace all)
        update_metadata = {"key3": "value3"}
        result = client.update_user_metadata(
            session_info.session_id,
            update_metadata,
            write_mode="replace"
        )
        
        # Verify only new key present
        status = client.get_session_status(session_info.session_id)
        assert status.user_metadata.get("key1") is None
        assert status.user_metadata.get("key2") is None
        assert status.user_metadata.get("key3") == "value3"
        
        # Cleanup
        try:
            client.mark_for_deletion(session_info.session_id)
        except:
            pass


class TestSessionStatus:
    """Test session status and monitoring."""
    
    def test_get_session_status(self, client, sample_dataframe):
        """Test getting session status."""
        session_info = client.upload_df_and_create_session(
            df=sample_dataframe,
            filename="test_status.csv"
        )
        
        status = client.get_session_status(session_info.session_id)
        
        assert status is not None
        assert status.session_id == session_info.session_id
        assert hasattr(status, 'status')
        assert hasattr(status, 'jobs')
        
        # Cleanup
        try:
            client.mark_for_deletion(session_info.session_id)
        except:
            pass
    
    def test_get_session_models(self, client, sample_dataframe):
        """Test getting session models/predictors."""
        session_info = client.upload_df_and_create_session(
            df=sample_dataframe,
            filename="test_models.csv"
        )
        
        # Wait a bit for training to start
        import time
        time.sleep(2)
        
        models = client.get_session_models(session_info.session_id)
        
        assert models is not None
        assert isinstance(models, dict)
        
        # Cleanup
        try:
            client.mark_for_deletion(session_info.session_id)
        except:
            pass


class TestSessionLifecycle:
    """Test session lifecycle operations."""
    
    def test_session_deletion(self, client, sample_dataframe):
        """Test marking session for deletion."""
        session_info = client.upload_df_and_create_session(
            df=sample_dataframe,
            filename="test_delete.csv"
        )
        
        # Mark for deletion
        result = client.mark_for_deletion(session_info.session_id)
        
        assert result is not None
        # Session should still exist but marked for deletion
        status = client.get_session_status(session_info.session_id)
        assert status is not None


class TestUploadOptimizations:
    """Test upload optimizations: Parquet conversion, file size warnings."""
    
    def test_dataframe_uses_parquet(self, sample_dataframe):
        """Test that DataFrames are always uploaded as Parquet format."""
        import io
        import pandas as pd
        from unittest.mock import Mock, patch
        
        # Create a client without server connection
        sphere_url = os.getenv("SPHERE_URL", "http://localhost:8000")
        client = FeatrixSphereClient(base_url=sphere_url)
        
        # Mock the _make_request to capture what's being uploaded
        original_make_request = client._make_request
        
        uploaded_files = {}
        def capture_upload(method, endpoint, **kwargs):
            if 'files' in kwargs:
                for key, file_tuple in kwargs['files'].items():
                    uploaded_files[key] = {
                        'filename': file_tuple[0],
                        'content': file_tuple[1],
                        'content_type': file_tuple[2] if len(file_tuple) > 2 else None
                    }
            # Return a mock successful response
            from unittest.mock import Mock
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'session_id': 'test-session-123',
                'status': 'ready'
            }
            return mock_response
        
        client._make_request = capture_upload
        
        try:
            # Upload DataFrame
            session_info = client.upload_df_and_create_session(
                df=sample_dataframe,
                filename="test_df.csv",
                name="test_parquet_upload"
            )
            
            # Verify Parquet was used
            assert 'file' in uploaded_files
            assert uploaded_files['file']['filename'].endswith('.parquet')
            assert uploaded_files['file']['content_type'] == 'application/octet-stream'
            
            # Verify it's actually valid Parquet
            parquet_content = uploaded_files['file']['content']
            parquet_buffer = io.BytesIO(parquet_content)
            df_readback = pd.read_parquet(parquet_buffer)
            assert len(df_readback) == len(sample_dataframe)
            assert list(df_readback.columns) == list(sample_dataframe.columns)
            
        finally:
            client._make_request = original_make_request
    
    def test_large_csv_converts_to_parquet(self):
        """Test that CSV files > 1MB are automatically converted to Parquet."""
        import io
        import pandas as pd
        import tempfile
        from unittest.mock import Mock
        
        # Create a large CSV file (> 1MB)
        large_df = pd.DataFrame({
            'col' + str(i): ['x' * 100] * 2000 for i in range(10)  # ~2MB CSV
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            large_df.to_csv(f.name, index=False)
            temp_path = f.name
        
        try:
            # Create a client without server connection
            sphere_url = os.getenv("SPHERE_URL", "http://localhost:8000")
            client = FeatrixSphereClient(base_url=sphere_url)
            
            # Mock the _make_request to capture what's being uploaded
            original_make_request = client._make_request
            
            uploaded_files = {}
            def capture_upload(method, endpoint, **kwargs):
                if 'files' in kwargs:
                    for key, file_tuple in kwargs['files'].items():
                        uploaded_files[key] = {
                            'filename': file_tuple[0],
                            'content': file_tuple[1],
                            'content_type': file_tuple[2] if len(file_tuple) > 2 else None
                        }
                # Return a mock successful response
                from unittest.mock import Mock
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'session_id': 'test-session-123',
                    'status': 'ready'
                }
                return mock_response
            
            client._make_request = capture_upload
            
            try:
                # Upload large CSV
                session_info = client.upload_df_and_create_session(
                    file_path=temp_path,
                    name="test_large_csv"
                )
                
                # Verify Parquet was used (not CSV.gz)
                assert 'file' in uploaded_files
                assert uploaded_files['file']['filename'].endswith('.parquet')
                assert uploaded_files['file']['content_type'] == 'application/octet-stream'
                
                # Verify it's valid Parquet
                parquet_content = uploaded_files['file']['content']
                parquet_buffer = io.BytesIO(parquet_content)
                df_readback = pd.read_parquet(parquet_buffer)
                assert len(df_readback) == len(large_df)
                
            finally:
                client._make_request = original_make_request
        finally:
            # Cleanup
            try:
                os.unlink(temp_path)
            except:
                pass
    
    def test_small_csv_stays_csv(self, sample_csv_file):
        """Test that small CSV files (< 1MB) remain as CSV.gz."""
        import io
        import gzip
        from unittest.mock import Mock
        
        # Create a client without server connection
        sphere_url = os.getenv("SPHERE_URL", "http://localhost:8000")
        client = FeatrixSphereClient(base_url=sphere_url)
        
        # Mock the _make_request to capture what's being uploaded
        original_make_request = client._make_request
        
        uploaded_files = {}
        def capture_upload(method, endpoint, **kwargs):
            if 'files' in kwargs:
                for key, file_tuple in kwargs['files'].items():
                    uploaded_files[key] = {
                        'filename': file_tuple[0],
                        'content': file_tuple[1],
                        'content_type': file_tuple[2] if len(file_tuple) > 2 else None
                    }
            # Return a mock successful response
            from unittest.mock import Mock
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'session_id': 'test-session-123',
                'status': 'ready'
            }
            return mock_response
        
        client._make_request = capture_upload
        
        try:
            # Upload small CSV
            session_info = client.upload_df_and_create_session(
                file_path=Path(sample_csv_file),
                name="test_small_csv"
            )
            
            # Verify CSV.gz was used (not Parquet)
            assert 'file' in uploaded_files
            assert uploaded_files['file']['filename'].endswith('.csv.gz')
            assert uploaded_files['file']['content_type'] == 'application/gzip'
            
            # Verify it's valid gzipped CSV
            gz_content = uploaded_files['file']['content']
            gz_buffer = io.BytesIO(gz_content)
            with gzip.GzipFile(fileobj=gz_buffer, mode='rb') as gz:
                csv_content = gz.read().decode('utf-8')
                assert 'col1,col2,target' in csv_content
            
        finally:
            client._make_request = original_make_request


class TestUploadOptimizationsIntegration:
    """Integration tests for upload optimizations - requires real server connection."""
    
    @pytest.fixture(autouse=True)
    def setup_integration_client(self):
        """Set up client for integration tests."""
        sphere_url = os.getenv("SPHERE_URL", "https://sphere-api.featrix.com")
        self.integration_client = FeatrixSphereClient(base_url=sphere_url)
        
        # Test connection
        try:
            self.integration_client._get_json("/health")
        except Exception as e:
            pytest.skip(f"Cannot connect to Sphere API at {sphere_url}: {e}")
    
    def test_dataframe_upload_uses_parquet_integration(self, sample_dataframe, setup_integration_client):
        """Integration test: Verify DataFrame uploads use Parquet format on real server."""
        import io
        import pandas as pd
        from unittest.mock import patch
        
        # Capture the actual request being made
        original_request = self.integration_client.session.request
        captured_files = {}
        
        def capture_request(method, url, **kwargs):
            if 'files' in kwargs:
                for key, file_tuple in kwargs['files'].items():
                    captured_files[key] = {
                        'filename': file_tuple[0],
                        'content': file_tuple[1] if hasattr(file_tuple[1], 'read') else file_tuple[1],
                        'content_type': file_tuple[2] if len(file_tuple) > 2 else None
                    }
            # Call original request
            return original_request(method, url, **kwargs)
        
        self.integration_client.session.request = capture_request
        
        try:
            # Upload DataFrame - should use Parquet
            session_info = self.integration_client.upload_df_and_create_session(
                df=sample_dataframe,
                filename="test_integration_df.csv",
                name="test_integration_parquet"
            )
            
            # Verify Parquet was used
            assert 'file' in captured_files
            assert captured_files['file']['filename'].endswith('.parquet'), \
                f"Expected .parquet file, got {captured_files['file']['filename']}"
            assert captured_files['file']['content_type'] == 'application/octet-stream'
            
            # Verify it's valid Parquet by reading it back
            file_content = captured_files['file']['content']
            if hasattr(file_content, 'read'):
                file_content = file_content.read()
            
            parquet_buffer = io.BytesIO(file_content)
            df_readback = pd.read_parquet(parquet_buffer)
            assert len(df_readback) == len(sample_dataframe)
            assert list(df_readback.columns) == list(sample_dataframe.columns)
            
            # Verify session was created
            assert session_info is not None
            assert session_info.session_id is not None
            
            # Cleanup
            try:
                self.integration_client.mark_for_deletion(session_info.session_id)
            except:
                pass
                
        finally:
            self.integration_client.session.request = original_request
    
    def test_large_csv_converts_to_parquet_integration(self, setup_integration_client):
        """Integration test: Verify large CSV files are converted to Parquet on real server."""
        import io
        import pandas as pd
        import tempfile
        
        # Create a large CSV file (> 1MB)
        large_df = pd.DataFrame({
            'col' + str(i): ['x' * 100] * 2000 for i in range(10)  # ~2MB CSV
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            large_df.to_csv(f.name, index=False)
            temp_path = f.name
        
        try:
            # Capture the actual request being made
            original_request = self.integration_client.session.request
            captured_files = {}
            
            def capture_request(method, url, **kwargs):
                if 'files' in kwargs:
                    for key, file_tuple in kwargs['files'].items():
                        captured_files[key] = {
                            'filename': file_tuple[0],
                            'content': file_tuple[1] if hasattr(file_tuple[1], 'read') else file_tuple[1],
                            'content_type': file_tuple[2] if len(file_tuple) > 2 else None
                        }
                # Call original request
                return original_request(method, url, **kwargs)
            
            self.integration_client.session.request = capture_request
            
            try:
                # Upload large CSV - should convert to Parquet
                session_info = self.integration_client.upload_df_and_create_session(
                    file_path=temp_path,
                    name="test_integration_large_csv"
                )
                
                # Verify Parquet was used (not CSV.gz)
                assert 'file' in captured_files
                assert captured_files['file']['filename'].endswith('.parquet'), \
                    f"Expected .parquet file for large CSV, got {captured_files['file']['filename']}"
                assert captured_files['file']['content_type'] == 'application/octet-stream'
                
                # Verify it's valid Parquet
                file_content = captured_files['file']['content']
                if hasattr(file_content, 'read'):
                    file_content = file_content.read()
                
                parquet_buffer = io.BytesIO(file_content)
                df_readback = pd.read_parquet(parquet_buffer)
                assert len(df_readback) == len(large_df)
                
                # Verify session was created
                assert session_info is not None
                assert session_info.session_id is not None
                
                # Cleanup
                try:
                    self.integration_client.mark_for_deletion(session_info.session_id)
                except:
                    pass
                    
            finally:
                self.integration_client.session.request = original_request
        finally:
            # Cleanup temp file
            try:
                os.unlink(temp_path)
            except:
                pass
    
    def test_small_csv_stays_csv_integration(self, sample_csv_file, setup_integration_client):
        """Integration test: Verify small CSV files remain as CSV.gz on real server."""
        import io
        import gzip
        
        # Capture the actual request being made
        original_request = self.integration_client.session.request
        captured_files = {}
        
        def capture_request(method, url, **kwargs):
            if 'files' in kwargs:
                for key, file_tuple in kwargs['files'].items():
                    captured_files[key] = {
                        'filename': file_tuple[0],
                        'content': file_tuple[1] if hasattr(file_tuple[1], 'read') else file_tuple[1],
                        'content_type': file_tuple[2] if len(file_tuple) > 2 else None
                    }
            # Call original request
            return original_request(method, url, **kwargs)
        
        self.integration_client.session.request = capture_request
        
        try:
            # Upload small CSV - should stay as CSV.gz
            session_info = self.integration_client.upload_df_and_create_session(
                file_path=Path(sample_csv_file),
                name="test_integration_small_csv"
            )
            
            # Verify CSV.gz was used (not Parquet)
            assert 'file' in captured_files
            assert captured_files['file']['filename'].endswith('.csv.gz'), \
                f"Expected .csv.gz file for small CSV, got {captured_files['file']['filename']}"
            assert captured_files['file']['content_type'] == 'application/gzip'
            
            # Verify it's valid gzipped CSV
            file_content = captured_files['file']['content']
            if hasattr(file_content, 'read'):
                file_content = file_content.read()
            
            gz_buffer = io.BytesIO(file_content)
            with gzip.GzipFile(fileobj=gz_buffer, mode='rb') as gz:
                csv_content = gz.read().decode('utf-8')
                assert 'col1,col2,target' in csv_content
            
            # Verify session was created
            assert session_info is not None
            assert session_info.session_id is not None
            
            # Cleanup
            try:
                self.integration_client.mark_for_deletion(session_info.session_id)
            except:
                pass
                
        finally:
            self.integration_client.session.request = original_request


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])

