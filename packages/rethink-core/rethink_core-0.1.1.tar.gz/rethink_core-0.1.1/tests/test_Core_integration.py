import pytest
import os
from src.rethink.Core import Core
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RETHINK_API_KEY")


class TestCoreIntegration:
    """Integration tests that make real API calls to Rethink service.

    WARNING: These tests consume API quota and may incur costs.
    Only run manually when needed.
    """

    @pytest.mark.skipif(not API_KEY, reason="RETHINK_API_KEY not set")
    def test_real_chat_request(self):
        core = Core(
            API_KEY, system_prompt="You are a helpful assistant.", model="mistral"
        )
        messages = [{"role": "user", "content": "Hello, say hi back"}]
        result = core.chat(messages)

        print(result)
        assert "response" in result
        assert "content" in result["response"]
        assert isinstance(result["response"]["content"], str)

    @pytest.mark.skipif(not API_KEY, reason="RETHINK_API_KEY not set")
    def test_real_imagine_request(self):
        core = Core(API_KEY)
        result = core.imagine("a simple red circle", 256, 256)
        print(result)

        assert "url" in result
        assert isinstance(result["url"], str)

    @pytest.mark.skipif(not API_KEY, reason="RETHINK_API_KEY not set")
    def test_real_request_error_handling(self):
        core = Core("invalid_key")
        messages = [{"role": "user", "content": "test"}]

        with pytest.raises(Exception, match="HTTP Error 401"):
            core.chat(messages)
