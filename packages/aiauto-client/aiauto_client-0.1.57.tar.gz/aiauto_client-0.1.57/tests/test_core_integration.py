"""Tests for core module integration with mocks."""

from unittest.mock import MagicMock, patch

import optuna
import pytest

from aiauto.core import (
    AIAutoController,
    StudyWrapper,
    TrialController,
    WaitOption,
    _fetch_available_gpu_models,
)
from aiauto.http_client import ConnectRPCError


class TestFetchAvailableGpuModels:
    """Test _fetch_available_gpu_models function."""

    @patch("aiauto.core.requests.get")
    def test_success(self, mock_get):
        """Test successful GPU model fetch."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"name": "gpu-3090", "nodeLabels": {}},
            {"name": "gpu-4090", "nodeLabels": {}},
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = _fetch_available_gpu_models("https://api.example.com", "test-token")

        # Converts kebab-case to underscore
        assert result == {"gpu_3090", "gpu_4090"}
        mock_get.assert_called_once_with(
            "https://api.example.com/api/gpu-flavors",
            headers={"Authorization": "Bearer test-token"},
            timeout=5,
        )

    @patch("aiauto.core.requests.get")
    def test_network_error(self, mock_get):
        """Test network error raises ValueError."""
        mock_get.side_effect = Exception("Connection refused")

        with pytest.raises(ValueError, match="Failed to fetch available GPU models"):
            _fetch_available_gpu_models("https://api.example.com", "test-token")

    @patch("aiauto.core.requests.get")
    def test_empty_response(self, mock_get):
        """Test empty GPU list."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = _fetch_available_gpu_models("https://api.example.com", "test-token")
        assert result == set()


class TestAIAutoControllerMethods:
    """Test AIAutoController methods with mocks."""

    @patch("aiauto.core.os.path.isdir")
    @patch("aiauto.core.makedirs")
    @patch("aiauto.core.optuna.artifacts.FileSystemArtifactStore")
    def test_get_artifact_store_local(self, mock_store_class, mock_makedirs, mock_isdir):
        """Test get_artifact_store creates local store when /artifacts doesn't exist."""
        AIAutoController._instances.clear()

        # /artifacts doesn't exist, ./artifacts doesn't exist either
        mock_isdir.side_effect = lambda path: False
        mock_store = MagicMock()
        mock_store_class.return_value = mock_store

        with patch.object(AIAutoController, "__init__", return_value=None):
            controller = AIAutoController.__new__(AIAutoController, "token-test")
            controller._artifact_store = None

            result = controller.get_artifact_store()

            assert result is mock_store
            mock_makedirs.assert_called_once_with("./artifacts", exist_ok=True)

    @patch("aiauto.core.os.path.isdir")
    @patch("aiauto.core.optuna.artifacts.FileSystemArtifactStore")
    def test_get_artifact_store_container(self, mock_store_class, mock_isdir):
        """Test get_artifact_store uses /artifacts in container environment."""
        AIAutoController._instances.clear()

        # /artifacts exists (container environment)
        mock_isdir.return_value = True
        mock_store = MagicMock()
        mock_store_class.return_value = mock_store

        with patch.object(AIAutoController, "__init__", return_value=None):
            controller = AIAutoController.__new__(AIAutoController, "token-test")
            controller._artifact_store = None

            result = controller.get_artifact_store()

            assert result is mock_store
            mock_store_class.assert_called_once_with("/artifacts")


class TestTrialControllerMethods:
    """Test TrialController methods."""

    def test_get_trial(self):
        """Test get_trial returns the trial."""
        TrialController._instances.clear()
        storage = optuna.storages.InMemoryStorage()
        study = optuna.create_study(storage=storage, study_name="test-get-trial")
        trial = study.ask()

        tc = TrialController(trial)
        result = tc.get_trial()

        assert result is trial
        study.tell(trial, 1.0)

    @patch("aiauto.core.save_note")
    def test_log_triggers_save_note_every_5_logs(self, mock_save_note):
        """Test log calls _save_note every 5 logs."""
        TrialController._instances.clear()
        storage = optuna.storages.InMemoryStorage()
        study = optuna.create_study(storage=storage, study_name="test-log-save")
        trial = study.ask()

        tc = TrialController(trial)

        # Log 4 times - should not trigger save_note
        for i in range(4):
            tc.log(f"Log {i}")
        assert mock_save_note.call_count == 0

        # 5th log should trigger save_note
        tc.log("Log 5")
        assert mock_save_note.call_count == 1

        # 10th log should trigger again
        for i in range(5):
            tc.log(f"Log {i + 6}")
        assert mock_save_note.call_count == 2

        study.tell(trial, 1.0)

    @patch("aiauto.core.save_note")
    def test_save_note_failure_continues(self, mock_save_note):
        """Test _save_note failure doesn't raise, just logs warning."""
        TrialController._instances.clear()
        mock_save_note.side_effect = Exception("Save failed")

        storage = optuna.storages.InMemoryStorage()
        study = optuna.create_study(storage=storage, study_name="test-save-fail")
        trial = study.ask()

        tc = TrialController(trial)

        # Log 5 times to trigger _save_note - should not raise
        for i in range(5):
            tc.log(f"Log {i}")

        # Logs should still be accumulated
        assert len(tc.logs) == 5
        study.tell(trial, 1.0)

    @patch("aiauto.core.save_note")
    def test_flush_with_logs(self, mock_save_note):
        """Test flush saves remaining logs."""
        TrialController._instances.clear()
        storage = optuna.storages.InMemoryStorage()
        study = optuna.create_study(storage=storage, study_name="test-flush")
        trial = study.ask()

        tc = TrialController(trial)
        tc.log("Log 1")
        tc.log("Log 2")

        tc.flush()
        assert mock_save_note.call_count == 1
        study.tell(trial, 1.0)

    @patch("aiauto.core.save_note")
    def test_flush_without_logs(self, mock_save_note):
        """Test flush with no logs does nothing."""
        TrialController._instances.clear()
        storage = optuna.storages.InMemoryStorage()
        study = optuna.create_study(storage=storage, study_name="test-flush-empty")
        trial = study.ask()

        tc = TrialController(trial)
        tc.flush()

        assert mock_save_note.call_count == 0
        study.tell(trial, 1.0)


class TestAIAutoControllerInit:
    """Test AIAutoController initialization with mocks."""

    @patch("aiauto.core.ConnectRPCClient")
    @patch("aiauto.core.optuna.storages.GrpcStorageProxy")
    @patch("aiauto.core.tempfile.mkdtemp")
    def test_init_success(self, mock_mkdtemp, mock_grpc_storage, mock_client_class):
        """Test successful initialization."""
        AIAutoController._instances.clear()

        mock_client = MagicMock()
        mock_client.call_rpc.return_value = {
            "journalGrpcStorageProxyHostExternal": "storage.example.com:50051",
            "journalGrpcStorageProxyHostInternal": "storage-internal:50051",
            "dashboardUrl": "https://dashboard.example.com",
        }
        mock_client_class.return_value = mock_client
        mock_mkdtemp.return_value = "/tmp/test-tmp"

        controller = AIAutoController("test-token-init")

        assert controller.token == "test-token-init"
        assert controller.dashboard_url == "https://dashboard.example.com"
        assert controller.tmp_dir == "/tmp/test-tmp"
        mock_grpc_storage.assert_called_once_with(host="storage.example.com", port=50051)

    @patch("aiauto.core.ConnectRPCClient")
    def test_init_no_storage_host_raises_error(self, mock_client_class):
        """Test initialization fails when no storage host returned."""
        from tenacity import stop_after_attempt

        AIAutoController._instances.clear()

        mock_client = MagicMock()
        mock_client.call_rpc.return_value = {
            "journalGrpcStorageProxyHostExternal": "",  # Empty triggers retryable error
        }
        mock_client_class.return_value = mock_client

        # Patch to fail fast (empty host raises ConnectRPCError which is retryable)
        with patch("aiauto.core.stop_after_delay", return_value=stop_after_attempt(1)):  # noqa: SIM117
            with pytest.raises(RuntimeError, match="Failed to initialize workspace"):
                AIAutoController("test-token-no-host")

    @patch("aiauto.core.ConnectRPCClient")
    def test_init_retry_timeout(self, mock_client_class):
        """Test initialization timeout after retries."""
        AIAutoController._instances.clear()

        mock_client = MagicMock()
        # Simulate retryable error
        mock_client.call_rpc.side_effect = ConnectRPCError("unavailable", "Not ready")
        mock_client_class.return_value = mock_client

        # Patch retry to fail fast
        with patch("aiauto.core.stop_after_delay", return_value=lambda x: True):  # noqa: SIM117
            with pytest.raises(RuntimeError):
                AIAutoController("test-token-timeout")

    @patch("aiauto.core.ConnectRPCClient")
    @patch("aiauto.core.optuna.storages.GrpcStorageProxy")
    @patch("aiauto.core.tempfile.mkdtemp")
    def test_init_already_initialized(self, mock_mkdtemp, mock_grpc_storage, mock_client_class):
        """Test re-initialization with same token returns same instance."""
        AIAutoController._instances.clear()

        mock_client = MagicMock()
        mock_client.call_rpc.return_value = {
            "journalGrpcStorageProxyHostExternal": "storage.example.com:50051",
        }
        mock_client_class.return_value = mock_client
        mock_mkdtemp.return_value = "/tmp/test"

        controller1 = AIAutoController("same-token")
        controller2 = AIAutoController("same-token")

        assert controller1 is controller2
        # __init__ should return early for already initialized
        assert mock_client.call_rpc.call_count == 1


class TestAIAutoControllerCreateStudy:
    """Test AIAutoController.create_study method."""

    @patch("aiauto.core.ConnectRPCClient")
    @patch("aiauto.core.optuna.storages.GrpcStorageProxy")
    @patch("aiauto.core.tempfile.mkdtemp")
    def test_create_study_success(self, mock_mkdtemp, mock_grpc_storage, mock_client_class):
        """Test successful study creation."""
        AIAutoController._instances.clear()

        mock_client = MagicMock()
        mock_client.call_rpc.side_effect = [
            # EnsureWorkspace response
            {"journalGrpcStorageProxyHostExternal": "storage.example.com:50051"},
            # CreateStudy response
            {"studyName": "test-study"},
        ]
        mock_client_class.return_value = mock_client
        mock_mkdtemp.return_value = "/tmp/test"

        controller = AIAutoController("token-create-study")
        wrapper = controller.create_study("test-study", direction="minimize")

        assert isinstance(wrapper, StudyWrapper)
        assert wrapper.study_name == "test-study"

    @patch("aiauto.core.ConnectRPCClient")
    @patch("aiauto.core.optuna.storages.GrpcStorageProxy")
    @patch("aiauto.core.tempfile.mkdtemp")
    def test_create_study_no_direction_raises_error(
        self, mock_mkdtemp, mock_grpc_storage, mock_client_class
    ):
        """Test create_study without direction raises error."""
        AIAutoController._instances.clear()

        mock_client = MagicMock()
        mock_client.call_rpc.return_value = {
            "journalGrpcStorageProxyHostExternal": "storage.example.com:50051"
        }
        mock_client_class.return_value = mock_client
        mock_mkdtemp.return_value = "/tmp/test"

        controller = AIAutoController("token-no-direction")

        with pytest.raises(
            ValueError, match="Either 'direction' or 'directions' must be specified"
        ):
            controller.create_study("test-study", direction=None, directions=None)

    @patch("aiauto.core.ConnectRPCClient")
    @patch("aiauto.core.optuna.storages.GrpcStorageProxy")
    @patch("aiauto.core.tempfile.mkdtemp")
    def test_create_study_both_direction_raises_error(
        self, mock_mkdtemp, mock_grpc_storage, mock_client_class
    ):
        """Test create_study with both direction and directions raises error."""
        AIAutoController._instances.clear()

        mock_client = MagicMock()
        mock_client.call_rpc.return_value = {
            "journalGrpcStorageProxyHostExternal": "storage.example.com:50051"
        }
        mock_client_class.return_value = mock_client
        mock_mkdtemp.return_value = "/tmp/test"

        controller = AIAutoController("token-both")

        with pytest.raises(ValueError, match="Cannot specify both"):
            controller.create_study("test-study", direction="minimize", directions=["minimize"])


class TestStudyWrapperGetStudy:
    """Test StudyWrapper.get_study method."""

    def test_get_study_success(self):
        """Test successful get_study."""
        mock_controller = MagicMock()
        storage = optuna.storages.InMemoryStorage()

        wrapper = StudyWrapper("get-study-test", storage, mock_controller)
        study = wrapper.get_study()

        assert study is not None
        assert study.study_name == "get-study-test"

    def test_get_study_caches_result(self):
        """Test get_study caches the study."""
        mock_controller = MagicMock()
        storage = optuna.storages.InMemoryStorage()

        wrapper = StudyWrapper("cache-test", storage, mock_controller)
        study1 = wrapper.get_study()
        study2 = wrapper.get_study()

        assert study1 is study2


class TestStudyWrapperOptimize:
    """Test StudyWrapper.optimize method."""

    def test_optimize_cpu_with_custom_dev_shm_raises_error(self):
        """Test CPU with custom dev_shm_size raises error."""
        mock_controller = MagicMock()
        mock_storage = MagicMock()

        wrapper = StudyWrapper("opt-test", mock_storage, mock_controller)

        with pytest.raises(ValueError, match="can only be used with GPU"):
            wrapper.optimize(
                lambda t: 1.0,
                n_trials=1,
                use_gpu=False,
                dev_shm_size="2Gi",
            )

    def test_optimize_dev_shm_exceeds_max_raises_error(self):
        """Test dev_shm_size exceeding 4Gi raises error."""
        mock_controller = MagicMock()
        mock_storage = MagicMock()

        wrapper = StudyWrapper("opt-test2", mock_storage, mock_controller)

        with pytest.raises(ValueError, match="exceeds max size"):
            wrapper.optimize(
                lambda t: 1.0,
                n_trials=1,
                use_gpu=True,
                dev_shm_size="8Gi",
            )

    def test_optimize_tmp_cache_exceeds_max_raises_error(self):
        """Test tmp_cache_size exceeding 4Gi raises error."""
        mock_controller = MagicMock()
        mock_storage = MagicMock()

        wrapper = StudyWrapper("opt-test3", mock_storage, mock_controller)

        with pytest.raises(ValueError, match="exceeds max size"):
            wrapper.optimize(
                lambda t: 1.0,
                n_trials=1,
                tmp_cache_size="10Gi",
            )

    def test_optimize_invalid_gpu_model_type_raises_error(self):
        """Test invalid gpu_model type raises error."""
        mock_controller = MagicMock()
        mock_storage = MagicMock()

        wrapper = StudyWrapper("opt-test4", mock_storage, mock_controller)

        with pytest.raises(ValueError, match="gpu_model must be str or dict"):
            wrapper.optimize(
                lambda t: 1.0,
                n_trials=1,
                gpu_model=123,  # Invalid type
            )

    @patch("aiauto.core._fetch_available_gpu_models")
    def test_optimize_invalid_gpu_model_name_raises_error(self, mock_fetch_gpu):
        """Test invalid GPU model name raises error."""
        mock_fetch_gpu.return_value = {"gpu_3090", "gpu_4090"}
        mock_controller = MagicMock()
        mock_storage = MagicMock()

        wrapper = StudyWrapper("opt-test5", mock_storage, mock_controller)

        with pytest.raises(ValueError, match="Invalid GPU model"):
            wrapper.optimize(
                lambda t: 1.0,
                n_trials=1,
                gpu_model="gpu_9999",  # Invalid model
            )

    @patch("aiauto.core._fetch_available_gpu_models")
    def test_optimize_gpu_allocation_exceeds_n_trials(self, mock_fetch_gpu):
        """Test GPU allocation exceeding n_trials raises error."""
        mock_fetch_gpu.return_value = {"gpu_3090", "gpu_4090"}
        mock_controller = MagicMock()
        mock_storage = MagicMock()

        wrapper = StudyWrapper("opt-test6", mock_storage, mock_controller)

        with pytest.raises(ValueError, match="exceeds n_trials"):
            wrapper.optimize(
                lambda t: 1.0,
                n_trials=5,
                gpu_model={"gpu_3090": 3, "gpu_4090": 4},  # Total 7 > 5
            )

    @patch("aiauto.core._fetch_available_gpu_models")
    def test_optimize_gpu_allocation_negative_value(self, mock_fetch_gpu):
        """Test negative GPU allocation value raises error."""
        mock_fetch_gpu.return_value = {"gpu_3090"}
        mock_controller = MagicMock()
        mock_storage = MagicMock()

        wrapper = StudyWrapper("opt-test7", mock_storage, mock_controller)

        with pytest.raises(ValueError, match="must be positive"):
            wrapper.optimize(
                lambda t: 1.0,
                n_trials=5,
                gpu_model={"gpu_3090": -1},
            )

    @patch("aiauto.core._fetch_available_gpu_models")
    def test_optimize_no_gpu_available_raises_error(self, mock_fetch_gpu):
        """Test no GPU available raises error."""
        mock_fetch_gpu.return_value = set()  # No GPUs
        mock_controller = MagicMock()
        mock_storage = MagicMock()

        wrapper = StudyWrapper("opt-test8", mock_storage, mock_controller)

        with pytest.raises(ValueError, match="No GPU models available"):
            wrapper.optimize(
                lambda t: 1.0,
                n_trials=1,
                gpu_model="gpu_3090",
            )

    @patch("aiauto.core._fetch_available_gpu_models")
    def test_optimize_success(self, mock_fetch_gpu):
        """Test successful optimize call."""
        mock_fetch_gpu.return_value = {"gpu_3090"}

        mock_controller = MagicMock()
        mock_controller.token = "test-token"
        mock_controller.client.base_url = "https://api.example.com"
        mock_controller.client.call_rpc.return_value = {"trialbatchName": "tb-12345"}
        mock_storage = MagicMock()

        wrapper = StudyWrapper("opt-success", mock_storage, mock_controller)

        result = wrapper.optimize(
            lambda t: 1.0,
            n_trials=1,
            wait_option=WaitOption.WAIT_NO,
        )

        assert result == "tb-12345"


class TestStudyWrapperGetStatus:
    """Test StudyWrapper.get_status method."""

    def test_get_status_success(self):
        """Test successful get_status."""
        mock_controller = MagicMock()
        mock_controller.client.call_rpc.return_value = {
            "studyName": "status-test",
            "trialbatches": {
                "tb-123": {
                    "trialbatchName": "tb-123",
                    "countActive": 2,
                    "countSucceeded": 3,
                    "countPruned": 1,
                    "countFailed": 0,
                    "countTotal": 6,
                    "countCompleted": 4,
                }
            },
            "dashboardUrl": "https://dashboard.example.com",
            "updatedAt": "2024-01-01T00:00:00Z",
        }
        mock_storage = MagicMock()

        wrapper = StudyWrapper("status-test", mock_storage, mock_controller)
        result = wrapper.get_status()

        assert result["study_name"] == "status-test"
        assert "tb-123" in result["trialbatches"]
        assert result["trialbatches"]["tb-123"]["count_completed"] == 4


class TestStudyWrapperIsTrialFinished:
    """Test StudyWrapper.is_trial_finished method."""

    def test_is_trial_finished_no_trialbatch_raises_error(self):
        """Test is_trial_finished without trialbatch raises error."""
        mock_controller = MagicMock()
        mock_storage = MagicMock()

        wrapper = StudyWrapper("finished-test", mock_storage, mock_controller)
        wrapper._last_trialbatch_name = None

        with pytest.raises(ValueError, match="trialbatch_name is required"):
            wrapper.is_trial_finished(5)  # Trial number without trialbatch

    def test_is_trial_finished_by_trial_number(self):
        """Test is_trial_finished finds trial by number."""
        mock_controller = MagicMock()
        mock_controller.client.call_rpc.return_value = {
            "studyName": "test",
            "trialbatches": {
                "tb-123": {
                    "trialbatchName": "tb-123",
                    "countCompleted": 1,
                    "completedTrials": {"pod-abc": {"trialNumber": 5, "state": "COMPLETE"}},
                }
            },
        }
        mock_storage = MagicMock()

        wrapper = StudyWrapper("finished-test2", mock_storage, mock_controller)
        wrapper._last_trialbatch_name = "tb-123"

        result = wrapper.is_trial_finished(5)
        assert result is True

    def test_is_trial_finished_by_pod_name(self):
        """Test is_trial_finished finds trial by pod name."""
        mock_controller = MagicMock()
        mock_controller.client.call_rpc.return_value = {
            "studyName": "test",
            "trialbatches": {
                "tb-123": {
                    "trialbatchName": "tb-123",
                    "countCompleted": 1,
                    "completedTrials": {"pod-abc": {"trialNumber": 5}},
                }
            },
        }
        mock_storage = MagicMock()

        wrapper = StudyWrapper("finished-test3", mock_storage, mock_controller)

        result = wrapper.is_trial_finished("pod-abc", trialbatch_name="tb-123")
        assert result is True

    def test_is_trial_finished_not_found(self):
        """Test is_trial_finished returns False when not found."""
        mock_controller = MagicMock()
        mock_controller.client.call_rpc.return_value = {
            "studyName": "test",
            "trialbatches": {
                "tb-123": {
                    "trialbatchName": "tb-123",
                    "countCompleted": 0,
                    "completedTrials": {},
                }
            },
        }
        mock_storage = MagicMock()

        wrapper = StudyWrapper("finished-test4", mock_storage, mock_controller)

        result = wrapper.is_trial_finished("pod-xyz", trialbatch_name="tb-123")
        assert result is False


class TestStudyWrapperWait:
    """Test StudyWrapper.wait method."""

    def test_wait_no_trialbatch_raises_error(self):
        """Test wait without trialbatch raises error."""
        mock_controller = MagicMock()
        mock_storage = MagicMock()

        wrapper = StudyWrapper("wait-test", mock_storage, mock_controller)
        wrapper._last_trialbatch_name = None

        with pytest.raises((ValueError, RuntimeError)):
            wrapper.wait(5)  # Trial number without trialbatch

    def test_wait_success(self):
        """Test wait returns True when trial finishes."""
        mock_controller = MagicMock()
        mock_controller.client.call_rpc.return_value = {
            "studyName": "test",
            "trialbatches": {
                "tb-123": {
                    "trialbatchName": "tb-123",
                    "countCompleted": 1,
                    "completedTrials": {"pod-abc": {"trialNumber": 5}},
                }
            },
        }
        mock_storage = MagicMock()

        wrapper = StudyWrapper("wait-success", mock_storage, mock_controller)
        wrapper._last_trialbatch_name = "tb-123"

        result = wrapper.wait(5, timeout=5)
        assert result is True


class TestStudyWrapperWaitForTrialbatch:
    """Test StudyWrapper._wait_for_trialbatch method."""

    def test_wait_all_trials_success(self):
        """Test waiting for all trials."""
        mock_controller = MagicMock()
        mock_controller.client.call_rpc.return_value = {
            "studyName": "test",
            "trialbatches": {
                "tb-123": {
                    "trialbatchName": "tb-123",
                    "countCompleted": 5,
                }
            },
        }
        mock_storage = MagicMock()

        wrapper = StudyWrapper("wait-all", mock_storage, mock_controller)

        # Should not raise
        wrapper._wait_for_trialbatch("tb-123", 5, WaitOption.WAIT_ALL_TRIALS, timeout=5)

    def test_wait_atleast_one_success(self):
        """Test waiting for at least one trial."""
        mock_controller = MagicMock()
        mock_controller.client.call_rpc.return_value = {
            "studyName": "test",
            "trialbatches": {
                "tb-123": {
                    "trialbatchName": "tb-123",
                    "countCompleted": 1,
                }
            },
        }
        mock_storage = MagicMock()

        wrapper = StudyWrapper("wait-one", mock_storage, mock_controller)

        # Should not raise
        wrapper._wait_for_trialbatch("tb-123", 5, WaitOption.WAIT_ATLEAST_ONE_TRIAL, timeout=5)

    def test_wait_trialbatch_not_found(self):
        """Test waiting for non-existent trialbatch."""
        mock_controller = MagicMock()
        mock_controller.client.call_rpc.return_value = {
            "studyName": "test",
            "trialbatches": {},
        }
        mock_storage = MagicMock()

        wrapper = StudyWrapper("wait-notfound", mock_storage, mock_controller)

        with pytest.raises(RuntimeError, match="not found"):
            wrapper._wait_for_trialbatch("tb-999", 5, WaitOption.WAIT_ALL_TRIALS, timeout=1)


class TestStudyWrapperOptimizeAdvanced:
    """Test advanced optimize scenarios."""

    @patch("aiauto.core._fetch_available_gpu_models")
    def test_optimize_with_gpu_model_dict(self, mock_fetch_gpu):
        """Test optimize with GPU model dict allocation."""
        mock_fetch_gpu.return_value = {"gpu_3090", "gpu_4090"}

        mock_controller = MagicMock()
        mock_controller.token = "test-token"
        mock_controller.client.base_url = "https://api.example.com"
        mock_controller.client.call_rpc.return_value = {"trialbatchName": "tb-gpu"}
        mock_storage = MagicMock()

        wrapper = StudyWrapper("opt-gpu-dict", mock_storage, mock_controller)

        result = wrapper.optimize(
            lambda t: 1.0,
            n_trials=10,
            gpu_model={"gpu_3090": 5, "gpu_4090": 3},  # Total 8 < 10
            wait_option=WaitOption.WAIT_NO,
        )

        assert result == "tb-gpu"

    @patch("aiauto.core._fetch_available_gpu_models")
    def test_optimize_with_gpu_model_string(self, mock_fetch_gpu):
        """Test optimize with GPU model string."""
        mock_fetch_gpu.return_value = {"gpu_4090"}

        mock_controller = MagicMock()
        mock_controller.token = "test-token"
        mock_controller.client.base_url = "https://api.example.com"
        mock_controller.client.call_rpc.return_value = {"trialbatchName": "tb-str"}
        mock_storage = MagicMock()

        wrapper = StudyWrapper("opt-gpu-str", mock_storage, mock_controller)

        result = wrapper.optimize(
            lambda t: 1.0,
            n_trials=5,
            gpu_model="gpu_4090",
            wait_option=WaitOption.WAIT_NO,
        )

        assert result == "tb-str"

    def test_optimize_failure_raises_runtime_error(self):
        """Test optimize failure wraps exception."""
        mock_controller = MagicMock()
        mock_controller.client.call_rpc.side_effect = Exception("Network error")
        mock_storage = MagicMock()

        wrapper = StudyWrapper("opt-fail", mock_storage, mock_controller)

        with pytest.raises(RuntimeError, match="Failed to start optimization"):
            wrapper.optimize(lambda t: 1.0, n_trials=1, wait_option=WaitOption.WAIT_NO)

    def test_optimize_with_custom_resources(self):
        """Test optimize with custom resource requests/limits."""
        mock_controller = MagicMock()
        mock_controller.client.call_rpc.return_value = {"trialbatchName": "tb-resources"}
        mock_storage = MagicMock()

        wrapper = StudyWrapper("opt-resources", mock_storage, mock_controller)

        result = wrapper.optimize(
            lambda t: 1.0,
            n_trials=1,
            resources_requests={"cpu": "4", "memory": "8Gi"},
            resources_limits={"cpu": "8", "memory": "16Gi"},
            wait_option=WaitOption.WAIT_NO,
        )

        assert result == "tb-resources"


class TestAIAutoControllerCreateStudyAdvanced:
    """Test advanced create_study scenarios."""

    @patch("aiauto.core.ConnectRPCClient")
    @patch("aiauto.core.optuna.storages.GrpcStorageProxy")
    @patch("aiauto.core.tempfile.mkdtemp")
    def test_create_study_with_directions(self, mock_mkdtemp, mock_grpc_storage, mock_client_class):
        """Test create_study with multi-objective directions."""
        AIAutoController._instances.clear()

        mock_client = MagicMock()
        mock_client.call_rpc.side_effect = [
            {"journalGrpcStorageProxyHostExternal": "storage.example.com:50051"},
            {"studyName": "multi-obj"},
        ]
        mock_client_class.return_value = mock_client
        mock_mkdtemp.return_value = "/tmp/test"

        controller = AIAutoController("token-multi")
        wrapper = controller.create_study(
            "multi-obj", direction=None, directions=["minimize", "maximize"]
        )

        assert wrapper.study_name == "multi-obj"

    @patch("aiauto.core.ConnectRPCClient")
    @patch("aiauto.core.optuna.storages.GrpcStorageProxy")
    @patch("aiauto.core.tempfile.mkdtemp")
    def test_create_study_failure(self, mock_mkdtemp, mock_grpc_storage, mock_client_class):
        """Test create_study wraps exceptions."""
        AIAutoController._instances.clear()

        mock_client = MagicMock()
        mock_client.call_rpc.side_effect = [
            {"journalGrpcStorageProxyHostExternal": "storage.example.com:50051"},
            Exception("Server error"),
        ]
        mock_client_class.return_value = mock_client
        mock_mkdtemp.return_value = "/tmp/test"

        controller = AIAutoController("token-fail")

        with pytest.raises(RuntimeError, match="Failed to create study"):
            controller.create_study("fail-study")


class TestStudyWrapperGetStatusAdvanced:
    """Test advanced get_status scenarios."""

    def test_get_status_with_trialbatch_filter(self):
        """Test get_status with trialbatch_name filter."""
        mock_controller = MagicMock()
        mock_controller.client.call_rpc.return_value = {
            "studyName": "test",
            "trialbatches": {
                "tb-123": {
                    "trialbatchName": "tb-123",
                    "countCompleted": 2,
                }
            },
        }
        mock_storage = MagicMock()

        wrapper = StudyWrapper("status-filter", mock_storage, mock_controller)
        result = wrapper.get_status(trialbatch_name="tb-123")

        assert "tb-123" in result["trialbatches"]

    def test_get_status_failure(self):
        """Test get_status wraps exceptions."""
        mock_controller = MagicMock()
        mock_controller.client.call_rpc.side_effect = Exception("Network error")
        mock_storage = MagicMock()

        wrapper = StudyWrapper("status-fail", mock_storage, mock_controller)

        with pytest.raises(RuntimeError, match="Failed to get status"):
            wrapper.get_status()


class TestStudyWrapperIsTrialFinishedAdvanced:
    """Test advanced is_trial_finished scenarios."""

    def test_is_trial_finished_trialbatch_not_in_response(self):
        """Test is_trial_finished when trialbatch not in response."""
        mock_controller = MagicMock()
        mock_controller.client.call_rpc.return_value = {
            "studyName": "test",
            "trialbatches": {},
        }
        mock_storage = MagicMock()

        wrapper = StudyWrapper("finished-notfound", mock_storage, mock_controller)

        result = wrapper.is_trial_finished("pod-xyz", trialbatch_name="tb-999")
        assert result is False

    def test_is_trial_finished_trial_number_not_found(self):
        """Test is_trial_finished when trial number not in completed trials."""
        mock_controller = MagicMock()
        mock_controller.client.call_rpc.return_value = {
            "studyName": "test",
            "trialbatches": {
                "tb-123": {
                    "trialbatchName": "tb-123",
                    "countCompleted": 1,
                    "completedTrials": {"pod-abc": {"trialNumber": 1}},
                }
            },
        }
        mock_storage = MagicMock()

        wrapper = StudyWrapper("finished-num-notfound", mock_storage, mock_controller)
        wrapper._last_trialbatch_name = "tb-123"

        result = wrapper.is_trial_finished(999)  # Non-existent trial number
        assert result is False

    def test_is_trial_finished_exception_returns_false(self):
        """Test is_trial_finished returns False on exception."""
        mock_controller = MagicMock()
        mock_controller.client.call_rpc.side_effect = Exception("Network error")
        mock_storage = MagicMock()

        wrapper = StudyWrapper("finished-error", mock_storage, mock_controller)

        result = wrapper.is_trial_finished("pod-xyz", trialbatch_name="tb-123")
        assert result is False

    def test_is_trial_finished_no_trialbatch_returns_false(self):
        """Test is_trial_finished returns False when no trialbatch tracked (pod name)."""
        mock_controller = MagicMock()
        mock_storage = MagicMock()

        wrapper = StudyWrapper("finished-no-tb", mock_storage, mock_controller)
        wrapper._last_trialbatch_name = None

        # Pod name query with no trialbatch should return False, not raise
        result = wrapper.is_trial_finished("pod-xyz")
        assert result is False


class TestAIAutoControllerInitRetryError:
    """Test AIAutoController init error handling.

    Note: Lines 235-241 (except RetryError) are unreachable because reraise=True
    causes tenacity to re-raise the original exception instead of RetryError.
    Tests verify the actual behavior (generic Exception handler).
    """

    @patch("aiauto.core.ConnectRPCClient")
    def test_init_retryable_error_wraps_with_message(self, mock_client_class):
        """Test initialization with retryable error wraps with helpful message."""
        from tenacity import stop_after_attempt

        AIAutoController._instances.clear()

        mock_client = MagicMock()
        mock_client.call_rpc.side_effect = ConnectRPCError("unavailable", "Not ready")
        mock_client_class.return_value = mock_client

        # Patch stop_after_delay to fail immediately (stop after 1 attempt)
        # With reraise=True, the underlying exception is re-raised (not RetryError)
        with patch("aiauto.core.stop_after_delay", return_value=stop_after_attempt(1)):  # noqa: SIM117
            with pytest.raises(RuntimeError, match="Failed to initialize workspace"):
                AIAutoController("token-retry-error")


class TestStudyWrapperGetStudyWrappedAsk:
    """Test StudyWrapper.get_study wrapped_ask functionality (lines 431-443)."""

    def test_wrapped_ask_sets_user_attr(self):
        """Test wrapped ask sets trialbatch_name user attr."""
        mock_controller = MagicMock()
        storage = optuna.storages.InMemoryStorage()

        wrapper = StudyWrapper("ask-test", storage, mock_controller)
        study = wrapper.get_study()

        # Call ask which should be wrapped
        trial = study.ask()

        # Check that trialbatch_name was set
        assert trial.user_attrs.get("trialbatch_name") == "ask_tell_local"

        study.tell(trial, 1.0)

    def test_wrapped_ask_logs_warning(self):
        """Test wrapped ask logs warning about local execution."""
        mock_controller = MagicMock()
        storage = optuna.storages.InMemoryStorage()

        wrapper = StudyWrapper("ask-warn", storage, mock_controller)

        with patch("aiauto.core.logger") as mock_logger:
            study = wrapper.get_study()
            trial = study.ask()

            # Verify warnings were logged
            assert mock_logger.warning.call_count >= 3
            study.tell(trial, 1.0)

    def test_wrapped_ask_handles_set_user_attr_failure(self):
        """Test wrapped ask continues even if set_user_attr fails (line 440-441)."""
        mock_controller = MagicMock()
        storage = optuna.storages.InMemoryStorage()

        wrapper = StudyWrapper("ask-fail", storage, mock_controller)
        study = wrapper.get_study()

        # Patch Trial's set_user_attr to fail (study.ask() returns Trial, not FrozenTrial)
        with patch.object(  # noqa: SIM117
            optuna.trial.Trial, "set_user_attr", side_effect=Exception("attr error")
        ):
            # Should not raise, just log warning
            with patch("aiauto.core.logger") as mock_logger:
                trial = study.ask()
                assert trial is not None
                # Verify warning was logged for the failed set_user_attr
                mock_logger.warning.assert_called()

        study.tell(trial, 1.0)


class TestStudyWrapperGetStudyRetryError:
    """Test StudyWrapper.get_study error handling.

    Note: Lines 447-453 (except RetryError) are unreachable because reraise=True
    causes tenacity to re-raise the original exception instead of RetryError.
    Tests verify the actual behavior (generic Exception handler).
    """

    def test_get_study_error_wraps_with_message(self):
        """Test get_study wraps exception with helpful message."""
        from tenacity import stop_after_attempt

        mock_controller = MagicMock()
        # Use a storage that will fail
        mock_storage = MagicMock()
        mock_storage.get_study_id_from_name.side_effect = Exception("Connection failed")

        wrapper = StudyWrapper("retry-study", mock_storage, mock_controller)

        # Patch stop_after_delay to fail immediately (stop after 1 attempt)
        # With reraise=True, the underlying exception is re-raised (not RetryError)
        with patch("aiauto.core.stop_after_delay", return_value=stop_after_attempt(1)):  # noqa: SIM117
            with pytest.raises(RuntimeError, match="Failed to get study"):
                wrapper.get_study()


class TestStudyWrapperOptimizeDevShmInvalidFormat:
    """Test optimize dev_shm_size/tmp_cache_size invalid format re-raise (lines 541, 556)."""

    def test_dev_shm_size_invalid_format_reraise(self):
        """Test dev_shm_size invalid format re-raises with context (line 541)."""
        mock_controller = MagicMock()
        mock_storage = MagicMock()

        wrapper = StudyWrapper("dev-shm-invalid", mock_storage, mock_controller)

        with pytest.raises(ValueError, match="dev_shm_size:.*Invalid size format"):
            wrapper.optimize(
                lambda t: 1.0,
                n_trials=1,
                use_gpu=True,
                dev_shm_size="invalid",
            )

    def test_tmp_cache_size_invalid_format_reraise(self):
        """Test tmp_cache_size invalid format re-raises with context (line 556)."""
        mock_controller = MagicMock()
        mock_storage = MagicMock()

        wrapper = StudyWrapper("tmp-cache-invalid", mock_storage, mock_controller)

        with pytest.raises(ValueError, match="tmp_cache_size:.*Invalid size format"):
            wrapper.optimize(
                lambda t: 1.0,
                n_trials=1,
                tmp_cache_size="badformat",
            )


class TestStudyWrapperOptimizeGpuDefaults:
    """Test optimize GPU default values (lines 565, 574)."""

    @patch("aiauto.core._fetch_available_gpu_models")
    def test_optimize_gpu_default_resources(self, mock_fetch_gpu):
        """Test GPU optimization uses default resources (line 565)."""
        mock_fetch_gpu.return_value = {"gpu_3090"}

        mock_controller = MagicMock()
        mock_controller.token = "test-token"
        mock_controller.client.base_url = "https://api.example.com"
        mock_controller.client.call_rpc.return_value = {"trialbatchName": "tb-gpu-default"}
        mock_storage = MagicMock()

        wrapper = StudyWrapper("gpu-default", mock_storage, mock_controller)

        wrapper.optimize(
            lambda t: 1.0,
            n_trials=1,
            use_gpu=True,
            gpu_model="gpu_3090",
            resources_requests=None,  # Will use GPU defaults
            wait_option=WaitOption.WAIT_NO,
        )

        # Verify call was made with GPU default resources (nested under "batch")
        call_args = mock_controller.client.call_rpc.call_args
        request_data = call_args[0][1]
        assert request_data["batch"]["resourcesRequests"]["cpu"] == "2"
        assert request_data["batch"]["resourcesRequests"]["memory"] == "4Gi"

    @patch("aiauto.core._fetch_available_gpu_models")
    def test_optimize_gpu_default_runtime_image(self, mock_fetch_gpu):
        """Test GPU optimization uses default runtime image (line 574)."""
        mock_fetch_gpu.return_value = {"gpu_3090"}

        mock_controller = MagicMock()
        mock_controller.token = "test-token"
        mock_controller.client.base_url = "https://api.example.com"
        mock_controller.client.call_rpc.return_value = {"trialbatchName": "tb-gpu-image"}
        mock_storage = MagicMock()

        wrapper = StudyWrapper("gpu-image", mock_storage, mock_controller)

        wrapper.optimize(
            lambda t: 1.0,
            n_trials=1,
            use_gpu=True,
            gpu_model="gpu_3090",
            runtime_image=None,  # Will use GPU default
            wait_option=WaitOption.WAIT_NO,
        )

        # Verify call was made with GPU default image (nested under "batch")
        call_args = mock_controller.client.call_rpc.call_args
        request_data = call_args[0][1]
        assert "pytorch" in request_data["batch"]["runtimeImage"]
        assert "cuda" in request_data["batch"]["runtimeImage"]


class TestStudyWrapperOptimizeWithWait:
    """Test optimize with wait options (line 613)."""

    def test_optimize_with_wait_all_calls_wait_for_trialbatch(self):
        """Test optimize with WAIT_ALL calls _wait_for_trialbatch (line 613)."""
        mock_controller = MagicMock()
        mock_controller.client.call_rpc.side_effect = [
            {"trialbatchName": "tb-wait-all"},  # Optimize response
            {  # get_status response
                "studyName": "test",
                "trialbatches": {
                    "tb-wait-all": {"trialbatchName": "tb-wait-all", "countCompleted": 5}
                },
            },
        ]
        mock_storage = MagicMock()

        wrapper = StudyWrapper("opt-wait-all", mock_storage, mock_controller)

        result = wrapper.optimize(
            lambda t: 1.0,
            n_trials=5,
            wait_option=WaitOption.WAIT_ALL_TRIALS,
            wait_timeout=5,
        )

        assert result == "tb-wait-all"

    def test_optimize_with_wait_atleast_one_calls_wait_for_trialbatch(self):
        """Test optimize with WAIT_ATLEAST_ONE calls _wait_for_trialbatch."""
        mock_controller = MagicMock()
        mock_controller.client.call_rpc.side_effect = [
            {"trialbatchName": "tb-wait-one"},  # Optimize response
            {  # get_status response
                "studyName": "test",
                "trialbatches": {
                    "tb-wait-one": {"trialbatchName": "tb-wait-one", "countCompleted": 1}
                },
            },
        ]
        mock_storage = MagicMock()

        wrapper = StudyWrapper("opt-wait-one", mock_storage, mock_controller)

        result = wrapper.optimize(
            lambda t: 1.0,
            n_trials=5,
            wait_option=WaitOption.WAIT_ATLEAST_ONE_TRIAL,
            wait_timeout=5,
        )

        assert result == "tb-wait-one"


class TestStudyWrapperWaitForTrialbatchTimeout:
    """Test _wait_for_trialbatch poll behavior (lines 645, 650).

    Note: Line 657 (except RetryError) is unreachable because reraise=True
    causes tenacity to re-raise the original exception instead of RetryError.
    Tests verify the actual poll behavior (RuntimeError during retry).
    """

    def test_wait_all_poll_raises_when_incomplete(self):
        """Test wait_all_trials poll raises RuntimeError when trials incomplete (line 645)."""
        from tenacity import stop_after_attempt

        mock_controller = MagicMock()
        # Always return incomplete status
        mock_controller.client.call_rpc.return_value = {
            "studyName": "test",
            "trialbatches": {
                "tb-timeout": {"trialbatchName": "tb-timeout", "countCompleted": 2}  # < 5
            },
        }
        mock_storage = MagicMock()

        wrapper = StudyWrapper("wait-timeout", mock_storage, mock_controller)

        # With reraise=True, the RuntimeError from poll is re-raised
        with patch("aiauto.core.stop_after_delay", return_value=stop_after_attempt(1)):  # noqa: SIM117
            with pytest.raises(RuntimeError, match="Waiting for all trials"):
                wrapper._wait_for_trialbatch("tb-timeout", 5, WaitOption.WAIT_ALL_TRIALS, timeout=1)

    def test_wait_atleast_one_poll_raises_when_zero(self):
        """Test wait_atleast_one poll raises RuntimeError when zero complete (line 650)."""
        from tenacity import stop_after_attempt

        mock_controller = MagicMock()
        # Always return zero completed
        mock_controller.client.call_rpc.return_value = {
            "studyName": "test",
            "trialbatches": {"tb-timeout2": {"trialbatchName": "tb-timeout2", "countCompleted": 0}},
        }
        mock_storage = MagicMock()

        wrapper = StudyWrapper("wait-timeout2", mock_storage, mock_controller)

        # With reraise=True, the RuntimeError from poll is re-raised
        with patch("aiauto.core.stop_after_delay", return_value=stop_after_attempt(1)):  # noqa: SIM117
            with pytest.raises(RuntimeError, match="Waiting for at least one trial"):
                wrapper._wait_for_trialbatch(
                    "tb-timeout2", 5, WaitOption.WAIT_ATLEAST_ONE_TRIAL, timeout=1
                )


class TestStudyWrapperWaitTimeout:
    """Test StudyWrapper.wait scenarios (lines 801, 815).

    Note: Lines 822-827 (except RetryError -> return False) are unreachable
    because reraise=True causes tenacity to re-raise the original exception.
    Tests verify the actual behavior (RuntimeError during poll).
    """

    def test_wait_no_trialbatch_name_raises_error(self):
        """Test wait raises RuntimeError when no trialbatch_name (line 801)."""
        mock_controller = MagicMock()
        mock_storage = MagicMock()

        wrapper = StudyWrapper("wait-no-tb", mock_storage, mock_controller)
        wrapper._last_trialbatch_name = None

        # Use string (pod name) to bypass the ValueError for trial numbers,
        # and reach line 801 (RuntimeError for no TrialBatch tracked)
        with pytest.raises(RuntimeError, match="No TrialBatch tracked"):
            wrapper.wait("pod-xyz", trialbatch_name=None)

    def test_wait_poll_raises_when_not_finished(self):
        """Test wait poll raises RuntimeError when trial not finished (line 815)."""
        from tenacity import stop_after_attempt

        mock_controller = MagicMock()
        # Trial never finishes
        mock_controller.client.call_rpc.return_value = {
            "studyName": "test",
            "trialbatches": {
                "tb-wait-timeout": {
                    "trialbatchName": "tb-wait-timeout",
                    "countCompleted": 0,
                    "completedTrials": {},
                }
            },
        }
        mock_storage = MagicMock()

        wrapper = StudyWrapper("wait-timeout-false", mock_storage, mock_controller)
        wrapper._last_trialbatch_name = "tb-wait-timeout"

        # With reraise=True, the RuntimeError from poll is re-raised
        with patch("aiauto.core.stop_after_delay", return_value=stop_after_attempt(1)):  # noqa: SIM117
            with pytest.raises(RuntimeError, match="Waiting for trial"):
                wrapper.wait(999, timeout=1)  # Trial 999 never completes
