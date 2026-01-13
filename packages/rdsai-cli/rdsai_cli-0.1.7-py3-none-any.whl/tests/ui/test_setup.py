"""Tests for ui.metacmd.setup module - setup and configuration functionality."""

from unittest.mock import AsyncMock, MagicMock
from unittest.mock import patch as mock_patch

import aiohttp
import pytest
from pydantic import SecretStr

from config import get_default_config
from exception import Reload
from ui.metacmd.setup import (
    get_model_context_size,
    reload,
    setup,
)

# Import private classes for testing
from ui.metacmd.setup import (
    _FormField,
    _Platform,
    _SetupResult,
)


class TestFormField:
    """Tests for _FormField class."""

    def test_form_field_init(self):
        """Test _FormField initialization."""
        field = _FormField(
            name="test_field",
            label="Test Field",
            default_value="default",
            placeholder="Enter value...",
            is_password=False,
        )
        assert field.name == "test_field"
        assert field.label == "Test Field"
        assert field.default_value == "default"
        assert field.placeholder == "Enter value..."
        assert field.is_password is False
        assert field.buffer.text == "default"

    def test_form_field_value(self):
        """Test _FormField value property."""
        field = _FormField(name="test", label="Test")
        field.buffer.text = "  test value  "
        assert field.value == "test value"

    def test_form_field_display_value_password(self):
        """Test _FormField display_value for password field."""
        field = _FormField(name="test", label="Test", is_password=True)
        field.buffer.text = "secret123"
        display = field.display_value
        assert display == "*" * min(len("secret123"), 20)

    def test_form_field_display_value_empty(self):
        """Test _FormField display_value for empty field."""
        field = _FormField(name="test", label="Test")
        field.buffer.text = ""
        assert field.display_value == "(empty)"

    def test_form_field_display_value_normal(self):
        """Test _FormField display_value for normal field."""
        field = _FormField(name="test", label="Test")
        field.buffer.text = "normal value"
        assert field.display_value == "normal value"


class TestGetModelContextSize:
    """Tests for get_model_context_size function."""

    def test_get_model_context_size_exact_match(self):
        """Test get_model_context_size with exact match."""
        size = get_model_context_size("gpt-4o")
        assert size == 128_000

    def test_get_model_context_size_case_insensitive(self):
        """Test get_model_context_size with case-insensitive match."""
        size = get_model_context_size("GPT-4O")
        assert size == 128_000

    def test_get_model_context_size_partial_match(self):
        """Test get_model_context_size with partial match."""
        size = get_model_context_size("gpt-4o-mini")
        assert size == 128_000

    def test_get_model_context_size_not_found(self):
        """Test get_model_context_size with unknown model."""
        size = get_model_context_size("unknown-model-xyz")
        assert size is None

    def test_get_model_context_size_claude(self):
        """Test get_model_context_size with Claude model."""
        size = get_model_context_size("claude-3-5-sonnet-20241022")
        assert size == 200_000

    def test_get_model_context_size_gemini(self):
        """Test get_model_context_size with Gemini model."""
        size = get_model_context_size("gemini-1.5-pro")
        assert size == 2_097_152

    def test_get_model_context_size_qwen(self):
        """Test get_model_context_size with Qwen model."""
        size = get_model_context_size("qwen3-max")
        assert size == 262_144


class TestFetchMaxContextSize:
    """Tests for _fetch_max_context_size function."""

    @pytest.mark.asyncio
    async def test_fetch_max_context_size_predefined(self):
        """Test _fetch_max_context_size with predefined model."""
        from ui.metacmd.setup import _fetch_max_context_size

        size = await _fetch_max_context_size("", "", "gpt-4o", "openai")
        assert size == 128_000

    @pytest.mark.asyncio
    async def test_fetch_max_context_size_no_base_url(self):
        """Test _fetch_max_context_size without base_url."""
        from ui.metacmd.setup import _fetch_max_context_size

        size = await _fetch_max_context_size("", "key", "unknown-model", "openai")
        assert size is None

    @pytest.mark.asyncio
    async def test_fetch_max_context_size_unsupported_platform(self):
        """Test _fetch_max_context_size with unsupported platform."""
        from ui.metacmd.setup import _fetch_max_context_size

        size = await _fetch_max_context_size("https://api.example.com", "key", "model", "openai")
        assert size is None

    @pytest.mark.asyncio
    async def test_fetch_max_context_size_qwen_api_success(self):
        """Test _fetch_max_context_size with Qwen API success."""
        from ui.metacmd.setup import _fetch_max_context_size

        mock_response_data = {
            "extra_info": {
                "default_envs": {
                    "max_tokens": 262144,
                }
            }
        }

        with mock_patch("ui.metacmd.setup.new_client_session") as mock_session:
            # Create mock response that acts as async context manager
            mock_response = MagicMock()
            mock_response.json = AsyncMock(return_value=mock_response_data)
            # Make it an async context manager
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            # Create mock session instance - get() should return the response directly
            mock_session_instance = MagicMock()
            mock_session_instance.get = MagicMock(return_value=mock_response)

            # Setup session context manager
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=None)

            size = await _fetch_max_context_size(
                "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "test-key",
                "qwen-model",
                "qwen",
            )
            assert size == 262144

    @pytest.mark.asyncio
    async def test_fetch_max_context_size_openai_format(self):
        """Test _fetch_max_context_size with OpenAI format."""
        from ui.metacmd.setup import _fetch_max_context_size

        mock_response_data = {"context_length": 128000}

        with mock_patch("ui.metacmd.setup.new_client_session") as mock_session:
            # Create mock response that acts as async context manager
            mock_response = MagicMock()
            mock_response.json = AsyncMock(return_value=mock_response_data)
            # Make it an async context manager
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            # Create mock session instance - get() should return the response directly
            mock_session_instance = MagicMock()
            mock_session_instance.get = MagicMock(return_value=mock_response)

            # Setup session context manager
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=None)

            size = await _fetch_max_context_size(
                "https://api.example.com/v1",
                "test-key",
                "test-model",
                "qwen",
            )
            assert size == 128000

    @pytest.mark.asyncio
    async def test_fetch_max_context_size_api_error(self):
        """Test _fetch_max_context_size with API error."""
        from ui.metacmd.setup import _fetch_max_context_size

        with mock_patch("ui.metacmd.setup.new_client_session") as mock_session:
            # Create mock response that raises error in context manager
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = aiohttp.ClientError("Connection failed")

            # Make __aenter__ raise the error
            async def aenter_side_effect():
                raise aiohttp.ClientError("Connection failed")

            mock_response.__aenter__ = AsyncMock(side_effect=aenter_side_effect)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            # Create mock session instance - get() should return the response directly
            mock_session_instance = MagicMock()
            mock_session_instance.get = MagicMock(return_value=mock_response)

            # Setup session context manager
            mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session.return_value.__aexit__ = AsyncMock(return_value=None)

            with pytest.raises(aiohttp.ClientError):
                await _fetch_max_context_size(
                    "https://api.example.com/v1",
                    "test-key",
                    "test-model",
                    "qwen",
                )


class TestPromptChoice:
    """Tests for _prompt_choice function."""

    @pytest.mark.asyncio
    async def test_prompt_choice_success(self):
        """Test _prompt_choice with successful selection."""
        from ui.metacmd.setup import _prompt_choice

        with mock_patch("ui.metacmd.setup.ChoiceInput") as mock_choice_input:
            mock_instance = AsyncMock()
            mock_instance.prompt_async = AsyncMock(return_value="Option 1")
            mock_choice_input.return_value = mock_instance

            result = await _prompt_choice(header="Select option", choices=["Option 1", "Option 2"])
            assert result == "Option 1"
            mock_instance.prompt_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_prompt_choice_empty_choices(self):
        """Test _prompt_choice with empty choices."""
        from ui.metacmd.setup import _prompt_choice

        result = await _prompt_choice(header="Select option", choices=[])
        assert result is None

    @pytest.mark.asyncio
    async def test_prompt_choice_keyboard_interrupt(self):
        """Test _prompt_choice with KeyboardInterrupt."""
        from ui.metacmd.setup import _prompt_choice

        with mock_patch("ui.metacmd.setup.ChoiceInput") as mock_choice_input:
            mock_instance = AsyncMock()
            mock_instance.prompt_async = AsyncMock(side_effect=KeyboardInterrupt())
            mock_choice_input.return_value = mock_instance

            result = await _prompt_choice(header="Select option", choices=["Option 1"])
            assert result is None

    @pytest.mark.asyncio
    async def test_prompt_choice_eof_error(self):
        """Test _prompt_choice with EOFError."""
        from ui.metacmd.setup import _prompt_choice

        with mock_patch("ui.metacmd.setup.ChoiceInput") as mock_choice_input:
            mock_instance = AsyncMock()
            mock_instance.prompt_async = AsyncMock(side_effect=EOFError())
            mock_choice_input.return_value = mock_instance

            result = await _prompt_choice(header="Select option", choices=["Option 1"])
            assert result is None


class TestSetup:
    """Tests for setup command and _setup function."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock ShellREPL app."""
        return MagicMock()

    @pytest.fixture
    def mock_config(self):
        """Create a mock Config."""
        return get_default_config()

    @pytest.mark.asyncio
    async def test_setup_cancelled(self, mock_app):
        """Test setup when user cancels."""
        with (
            mock_patch("ui.metacmd.setup._setup", return_value=None),
            mock_patch("ui.metacmd.setup.console") as mock_console,
        ):
            await setup(mock_app, [])
            # Should not raise Reload when cancelled
            assert True

    @pytest.mark.asyncio
    async def test_setup_success(self, mock_app, mock_config):
        """Test setup with successful configuration."""
        setup_result = _SetupResult(
            language="en",
            platform=_Platform(
                id="openai",
                name="OpenAI",
                default_base_url="https://api.openai.com/v1",
                suggested_models=["gpt-4o"],
            ),
            base_url="https://api.openai.com/v1",
            api_key=SecretStr("test-key"),
            model_name="gpt-4o",
            max_context_size=128000,
            max_output_tokens=None,
        )

        with (
            mock_patch("ui.metacmd.setup._setup", return_value=setup_result),
            mock_patch("ui.metacmd.setup.load_config", return_value=mock_config),
            mock_patch("ui.metacmd.setup.save_config") as mock_save,
            mock_patch("ui.metacmd.setup.console") as mock_console,
            mock_patch("ui.metacmd.setup.asyncio.sleep", new_callable=AsyncMock),
            mock_patch("ui.metacmd.setup.console.clear"),
            pytest.raises(Reload),
        ):
            await setup(mock_app, [])
            mock_save.assert_called_once()
            assert mock_config.default_model == "gpt-4o"
            assert mock_config.language == "en"

    @pytest.mark.asyncio
    async def test_setup_with_max_output_tokens(self, mock_app, mock_config):
        """Test setup with max_output_tokens (Anthropic)."""
        setup_result = _SetupResult(
            language="en",
            platform=_Platform(
                id="anthropic",
                name="Anthropic (Claude)",
                default_base_url="",
                suggested_models=[],
                needs_base_url=False,
                needs_max_output_tokens=True,
            ),
            base_url="",
            api_key=SecretStr("test-key"),
            model_name="claude-3-5-sonnet-20241022",
            max_context_size=200000,
            max_output_tokens=4096,
        )

        with (
            mock_patch("ui.metacmd.setup._setup", return_value=setup_result),
            mock_patch("ui.metacmd.setup.load_config", return_value=mock_config),
            mock_patch("ui.metacmd.setup.save_config") as mock_save,
            mock_patch("ui.metacmd.setup.console") as mock_console,
            mock_patch("ui.metacmd.setup.asyncio.sleep", new_callable=AsyncMock),
            mock_patch("ui.metacmd.setup.console.clear"),
            pytest.raises(Reload),
        ):
            await setup(mock_app, [])
            mock_save.assert_called_once()
            saved_config = mock_save.call_args[0][0]
            assert saved_config.models["claude-3-5-sonnet-20241022"].max_output_tokens == 4096

    @pytest.mark.asyncio
    async def test_setup_flow_language_selection(self, mock_app, mock_config):
        """Test _setup flow with language selection."""
        from ui.metacmd.setup import _setup

        with (
            mock_patch("ui.metacmd.setup.load_config", return_value=mock_config),
            mock_patch("ui.metacmd.setup._prompt_choice") as mock_prompt,
            mock_patch("ui.metacmd.setup.console") as mock_console,
        ):
            # User cancels at language selection
            mock_prompt.return_value = None

            result = await _setup()
            assert result is None
            mock_prompt.assert_called_once()

    @pytest.mark.asyncio
    async def test_setup_flow_platform_selection(self, mock_app, mock_config):
        """Test _setup flow with platform selection."""
        from ui.metacmd.setup import _setup

        with (
            mock_patch("ui.metacmd.setup.load_config", return_value=mock_config),
            mock_patch("ui.metacmd.setup._prompt_choice") as mock_prompt,
            mock_patch("ui.metacmd.setup.console") as mock_console,
        ):
            # User selects language, then cancels at platform selection
            mock_prompt.side_effect = ["English (en)", None]

            result = await _setup()
            assert result is None
            assert mock_prompt.call_count == 2

    @pytest.mark.asyncio
    async def test_setup_flow_form_cancelled(self, mock_app, mock_config):
        """Test _setup flow when form is cancelled."""
        from ui.metacmd.setup import _setup

        with (
            mock_patch("ui.metacmd.setup.load_config", return_value=mock_config),
            mock_patch("ui.metacmd.setup._prompt_choice") as mock_prompt,
            mock_patch("ui.metacmd.setup._run_form") as mock_form,
            mock_patch("ui.metacmd.setup.console") as mock_console,
        ):
            from ui.metacmd.setup import _FormResult

            mock_prompt.side_effect = ["English (en)", "OpenAI"]
            mock_form.return_value = _FormResult(submitted=False, values={})

            result = await _setup()
            assert result is None

    @pytest.mark.asyncio
    async def test_setup_flow_form_validation_error(self, mock_app, mock_config):
        """Test _setup flow with form validation errors."""
        from ui.metacmd.setup import _setup, _FormResult

        with (
            mock_patch("ui.metacmd.setup.load_config", return_value=mock_config),
            mock_patch("ui.metacmd.setup._prompt_choice") as mock_prompt,
            mock_patch("ui.metacmd.setup._run_form") as mock_form,
            mock_patch("ui.metacmd.setup.console") as mock_console,
        ):
            # User selects language and platform
            mock_prompt.side_effect = [
                "English (en)",
                "OpenAI",
                "Cancel setup",  # User cancels after validation error
            ]

            # First form submission with empty values (validation will fail)
            mock_form.return_value = _FormResult(
                submitted=True, values={"base_url": "", "api_key": "", "model_name": ""}
            )

            result = await _setup()
            assert result is None

    @pytest.mark.asyncio
    async def test_setup_flow_successful_complete(self, mock_app, mock_config):
        """Test _setup flow with successful completion."""
        from ui.metacmd.setup import _setup, _FormResult

        with (
            mock_patch("ui.metacmd.setup.load_config", return_value=mock_config),
            mock_patch("ui.metacmd.setup._prompt_choice") as mock_prompt,
            mock_patch("ui.metacmd.setup._run_form") as mock_form,
            mock_patch("ui.metacmd.setup._fetch_max_context_size") as mock_fetch,
            mock_patch("ui.metacmd.setup.console") as mock_console,
        ):
            mock_prompt.side_effect = [
                "English (en)",
                "OpenAI",
                "Yes, save and apply",
            ]

            mock_form.return_value = _FormResult(
                submitted=True,
                values={
                    "base_url": "https://api.openai.com/v1",
                    "api_key": "test-key",
                    "model_name": "gpt-4o",
                },
            )

            mock_fetch.return_value = 128000

            result = await _setup()
            assert result is not None
            assert result.language == "en"
            assert result.model_name == "gpt-4o"
            assert result.max_context_size == 128000

    @pytest.mark.asyncio
    async def test_setup_flow_fetch_context_size_error(self, mock_app, mock_config):
        """Test _setup flow when fetching context size fails."""
        from ui.metacmd.setup import _setup, _FormResult

        with (
            mock_patch("ui.metacmd.setup.load_config", return_value=mock_config),
            mock_patch("ui.metacmd.setup._prompt_choice") as mock_prompt,
            mock_patch("ui.metacmd.setup._run_form") as mock_form,
            mock_patch("ui.metacmd.setup._fetch_max_context_size") as mock_fetch,
            mock_patch("ui.metacmd.setup.console") as mock_console,
        ):
            mock_prompt.side_effect = [
                "English (en)",
                "OpenAI",
                "Yes, save and apply",
                "Continue without context size",  # User chooses to continue
            ]

            mock_form.return_value = _FormResult(
                submitted=True,
                values={
                    "base_url": "https://api.openai.com/v1",
                    "api_key": "test-key",
                    "model_name": "gpt-4o",
                },
            )

            mock_fetch.side_effect = aiohttp.ClientError("Connection failed")

            result = await _setup()
            assert result is not None
            assert result.max_context_size == 0  # Should default to 0


class TestReload:
    """Tests for reload command."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock ShellREPL app."""
        return MagicMock()

    def test_reload_raises_exception(self, mock_app):
        """Test reload raises Reload exception."""
        with pytest.raises(Reload):
            reload(mock_app, [])


class TestRunForm:
    """Tests for _run_form function.

    Note: Full testing of _run_form requires complex mocking of prompt_toolkit internals.
    These tests verify basic structure and field handling.
    """

    def test_form_field_creation(self):
        """Test that form fields can be created correctly."""
        from ui.metacmd.setup import _FormField

        fields = [
            _FormField(name="field1", label="Field 1"),
            _FormField(name="field2", label="Field 2"),
        ]

        assert len(fields) == 2
        assert fields[0].name == "field1"
        assert fields[1].name == "field2"
        assert fields[0].label == "Field 1"
        assert fields[1].label == "Field 2"
