import pytest
from unittest.mock import patch, Mock
import urllib.error
import json
from src.rethink.Core import Core
import dotenv
import os

dotenv.load_dotenv()

API_KEY = os.getenv("RETHINK_API_KEY")


class TestCore:
    def test_init(self):
        core = Core(API_KEY, "test_prompt", "test_model")
        assert core.api_key == API_KEY
        assert core.model == "test_model"
        assert core.system_prompt == "test_prompt"
        assert core.histories == []

    def test_change_model(self):
        core = Core(API_KEY)
        core.change_model("new_model")
        assert core.model == "new_model"

    def test_set_histories(self):
        core = Core(API_KEY)
        core.set_histories({"test": "history"})
        assert core.histories == {"test": "history"}

    def test_set_histories_invalid_type(self):
        core = Core(API_KEY)
        with pytest.raises(Exception, match="Histories must be a dictionary"):
            core.set_histories("not_dict")

    def test_throw_error(self):
        core = Core(API_KEY)
        with pytest.raises(Exception, match="Test message"):
            core.throw_error("Test message")

    @patch("urllib.request.urlopen")
    def test_request_success(self, mock_urlopen):
        mock_response = Mock()
        mock_response.read.return_value = b'{"result": "success"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        mock_urlopen.return_value.__exit__.return_value = None

        core = Core(API_KEY)
        result = core.request({"test": "payload"})
        assert result == {"result": "success"}

        # Verify the call
        mock_urlopen.assert_called_once()
        args, kwargs = mock_urlopen.call_args
        req = args[0]
        assert req.full_url == "https://core.rethink.web.id/api/generate/text"
        assert req.method == "POST"
        assert json.loads(req.data) == {"test": "payload"}
        assert req.headers["Authorization"] == f"Bearer {API_KEY}"

    @patch("urllib.request.urlopen")
    def test_request_http_error_404(self, mock_urlopen):
        from email.message import EmailMessage

        fp_mock = Mock()
        fp_mock.read.return_value = b"Not Found"
        hdrs = EmailMessage()
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://core.rethink.web.id/api/generate/text",
            code=404,
            msg="Not Found",
            hdrs=hdrs,
            fp=fp_mock,
        )

        core = Core(API_KEY)
        with pytest.raises(Exception, match="HTTP Error 404: Not Found"):
            core.request({})

    @patch("urllib.request.urlopen")
    def test_request_http_error_401(self, mock_urlopen):
        from email.message import EmailMessage

        fp_mock = Mock()
        fp_mock.read.return_value = b'{"error": "Invalid API key"}'
        hdrs = EmailMessage()
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://core.rethink.web.id/api/generate/text",
            code=401,
            msg="Unauthorized",
            hdrs=hdrs,
            fp=fp_mock,
        )

        core = Core(API_KEY)
        with pytest.raises(Exception, match="HTTP Error 401: .*Invalid API key.*"):
            core.request({})

    @patch("urllib.request.urlopen")
    def test_request_http_error_429(self, mock_urlopen):
        from email.message import EmailMessage

        fp_mock = Mock()
        fp_mock.read.return_value = b'{"error": "Rate limit exceeded"}'
        hdrs = EmailMessage()
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://core.rethink.web.id/api/generate/text",
            code=429,
            msg="Too Many Requests",
            hdrs=hdrs,
            fp=fp_mock,
        )

        core = Core(API_KEY)
        with pytest.raises(Exception, match="HTTP Error 429: .*Rate limit exceeded.*"):
            core.request({})

    @patch("urllib.request.urlopen")
    def test_request_http_error_500(self, mock_urlopen):
        from email.message import EmailMessage

        fp_mock = Mock()
        fp_mock.read.return_value = b'{"error": "Internal server error"}'
        hdrs = EmailMessage()
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://core.rethink.web.id/api/generate/text",
            code=500,
            msg="Internal Server Error",
            hdrs=hdrs,
            fp=fp_mock,
        )

        core = Core(API_KEY)
        with pytest.raises(
            Exception, match="HTTP Error 500: .*Internal server error.*"
        ):
            core.request({})

    def test_request_invalid_payload(self):
        core = Core(API_KEY)
        with pytest.raises(Exception, match="Payload must be a dictionary"):
            core.request("not_dict")

    @patch.object(Core, "request")
    def test_chat(self, mock_request):
        mock_request.return_value = {
            "response": {"role": "assistant", "content": "Hello! How can I help you?"}
        }
        core = Core(API_KEY, "sys_prompt")
        result = core.chat([{"role": "user", "content": "hi"}])
        assert result == {
            "response": {"role": "assistant", "content": "Hello! How can I help you?"}
        }
        mock_request.assert_called_once_with(
            {
                "model": "deepseek",
                "messages": [
                    {"role": "system", "content": "sys_prompt"},
                    {"role": "user", "content": "hi"},
                ],
                "max_tokens": 150,
                "temperature": 0.7,
                "stream": False,
            },
            "/v1/chat/completions",
        )

    @patch.object(Core, "request")
    def test_chat_with_histories(self, mock_request):
        mock_request.return_value = {
            "response": {
                "role": "assistant",
                "content": "Continuing the conversation...",
            }
        }
        core = Core(API_KEY)
        histories = {"prev": "chat"}
        result = core.chat([{"role": "user", "content": "hi"}])
        assert result == {
            "response": {
                "role": "assistant",
                "content": "Continuing the conversation...",
            }
        }
        mock_request.assert_called_once_with(
            {
                "model": "deepseek",
                "messages": [{"role": "user", "content": "hi"}],
                "max_tokens": 150,
                "temperature": 0.7,
                "stream": False,
            },
            "/v1/chat/completions",
        )

    @patch.object(Core, "request")
    def test_imagine_with_prompt(self, mock_request):
        mock_request.return_value = {
            "url": "https://example.com/generated_image.png",
            "model": "deepseek",
            "width": 512,
            "height": 256,
        }
        core = Core(API_KEY)
        result = core.imagine("test prompt", 512, 256)
        assert result == {
            "url": "https://example.com/generated_image.png",
            "model": "deepseek",
            "width": 512,
            "height": 256,
        }
        mock_request.assert_called_once_with(
            {
                "model": "deepseek",
                "prompt": "test prompt",
                "width": 512,
                "height": 256,
            },
            "/api/generate/image",
        )

    @patch.object(Core, "request")
    def test_imagine_with_system_prompt(self, mock_request):
        mock_request.return_value = {
            "url": "https://example.com/system_generated_image.png",
            "model": "deepseek",
            "width": 1024,
            "height": 768,
        }
        core = Core(API_KEY, system_prompt="sys prompt")
        result = core.imagine("", 1024, 768)
        assert result == {
            "url": "https://example.com/system_generated_image.png",
            "model": "deepseek",
            "width": 1024,
            "height": 768,
        }
        mock_request.assert_called_once_with(
            {
                "model": "deepseek",
                "prompt": "sys prompt",
                "width": 1024,
                "height": 768,
            },
            "/api/generate/image",
        )

    def test_imagine_no_prompt_error(self):
        core = Core(API_KEY)
        with pytest.raises(Exception, match="Prompt must be provided"):
            core.imagine("")

    @patch("urllib.request.urlopen")
    def test_request_malformed_json(self, mock_urlopen):
        mock_response = Mock()
        mock_response.read.return_value = b"invalid json"
        mock_urlopen.return_value.__enter__.return_value = mock_response
        mock_urlopen.return_value.__exit__.return_value = None

        core = Core(API_KEY)
        with pytest.raises(json.JSONDecodeError):
            core.request({"test": "payload"})

    @patch("urllib.request.urlopen")
    def test_request_network_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Network is unreachable")

        core = Core(API_KEY)
        with pytest.raises(urllib.error.URLError):
            core.request({"test": "payload"})

    def test_imagine_no_prompt_no_system_error(self):
        core = Core(API_KEY, system_prompt="")
        with pytest.raises(Exception, match="Prompt must be provided"):
            core.imagine("")

    @patch.object(Core, "request")
    def test_chat_empty_messages(self, mock_request):
        mock_request.return_value = {
            "response": {"role": "assistant", "content": "How can I help?"}
        }
        core = Core(API_KEY)
        result = core.chat([])
        assert result == {
            "response": {"role": "assistant", "content": "How can I help?"}
        }

    @patch.object(Core, "request")
    def test_imagine_zero_dimensions(self, mock_request):
        mock_request.return_value = {
            "image": {
                "url": "https://example.com/zero_dim.png",
                "width": 0,
                "height": 0,
            }
        }
        core = Core(API_KEY)
        result = core.imagine("test", 0, 0)
        assert result == {
            "image": {
                "url": "https://example.com/zero_dim.png",
                "width": 0,
                "height": 0,
            }
        }
