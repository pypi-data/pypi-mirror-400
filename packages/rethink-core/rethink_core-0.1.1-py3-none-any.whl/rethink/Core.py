import urllib.request
import urllib.error
import json
import argparse


class Core:
    """
    A client for interacting with the Rethink API, supporting chat and image generation.

    Attributes:
        base_url (str): The base endpoint for the Rethink API.

        model (str): The identifier of the AI model to be used.
        system_prompt (str): A default system instruction for the AI.
        histories (list): Stores contextual conversation history.
        DOCS_URL (str): Link to the official API documentation.
    """

    base_url = "https://core.rethink.web.id"
    model = "deepseek"
    system_prompt = ""
    histories = []
    DOCS_URL = "https://core.rethink.web.id/docs/generation"

    def __init__(self, api_key, system_prompt="", model="deepseek"):
        """
        Initializes the Rethink Core client.

        Args:
            api_key (str): Your Rethink API authentication key.
            system_prompt (str, optional): Default instruction for chat models. Defaults to "".
            model (str, optional): The model ID to use for requests. Defaults to "deepseek".
        """
        self.api_key = api_key
        self.model = model
        self.system_prompt = system_prompt

    def request(self, payload, path="/api/generate/text"):
        """
        Executes a POST request to the Rethink API.

        Args:
            payload (dict): The JSON-serializable data to send.
            path (str, optional): The endpoint path. Defaults to "/api/generate/text".

        Returns:
            dict: The decoded JSON response from the server.

        Raises:
            Exception: If the payload is invalid or the request fails.
        """
        url = self.base_url + path
        if not isinstance(payload, dict):
            self.throw_error("Payload must be a dictionary")

        data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req) as response:
                result = response.read().decode("utf-8")
                return json.loads(result)
        except urllib.error.HTTPError as e:
            self.throw_error(f"HTTP Error {e.code}: {e.read().decode()}")

    def change_model(self, model):
        """
        Updates the default model for subsequent requests.

        Args:
            model (str): The new model identifier.
        """
        self.model = model

    def set_histories(self, histories):
        """
        Sets the global conversation history.

        Args:
            histories (dict): Dictionary containing history data.
        """
        if not isinstance(histories, dict):
            self.throw_error("Histories must be a dictionary")

        self.histories = histories

    def chat(
        self, messages, histories=None, max_tokens=150, temperature=0.7, stream=False
    ):
        """
        Sends a list of messages to the chat completion endpoint (OpenAI compatible).

        Args:
            messages (list): List of message dicts (e.g., {"role": "user", "content": "..."}).
            max_tokens (int, optional): Maximum tokens for response. Defaults to 150.
            temperature (float, optional): Temperature for response. Defaults to 0.7.
            stream (bool, optional): Enable streaming. Defaults to False.

        Returns:
            dict: The API response in OpenAI chat completion format.
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream,
        }

        if self.system_prompt:
            # Insert system message at the beginning if not already present
            if not messages or messages[0].get("role") != "system":
                payload["messages"] = [
                    {"role": "system", "content": self.system_prompt}
                ] + messages

        response = self.request(payload, "/v1/chat/completions")
        # Parse OpenAI response to custom format
        if "choices" in response and response["choices"]:
            return {"response": response["choices"][0]["message"]}
        return response

    def generate_text(self, prompt, history=None):
        """
        Generates text using AI models.

        Args:
            prompt (str): The prompt/question to generate text for.
            history (list, optional): Conversation history for context.

        Returns:
            dict: The API response with generated content.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
        }

        if history:
            payload["history"] = history

        return self.request(payload, "/api/generate/text")

    def imagine(self, prompt="", width=1024, height=768):
        """
        Generates an image based on a text prompt.

        Args:
            prompt (str): Description of the image to generate.
            width (int, optional): Width of the generated image. Defaults to 1024.
            height (int, optional): Height of the generated image. Defaults to 768.

        Returns:
            dict: The API response containing the image generation results.
        """
        """
        Generates an image based on a text prompt.

        Args:
            prompt (str, optional): Description of the image to generate.
            width (int, optional): Width of the generated image. Defaults to 1024.
            height (int, optional): Height of the generated image. Defaults to 768.

        Returns:
            dict: The API response containing the image generation results.
        """
        if self.system_prompt and prompt == "":
            prompt = self.system_prompt

        if prompt == "":
            self.throw_error("Prompt must be provided")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "width": width,
            "height": height,
        }

        return self.request(payload, "/api/generate/image")

    def throw_error(self, message):
        """
        Standardized error reporting with documentation reference.

        Args:
            message (str): The specific error message.

        Raises:
            Exception: Formatted error including the docs URL.
        """
        raise Exception(
            f"{message}\n\nFor more information, please visit {self.DOCS_URL}"
        )


def main():
    parser = argparse.ArgumentParser(description="Rethink Core CLI")
    parser.add_argument("--api-key", required=True, help="API key for Rethink")
    parser.add_argument("--model", default="deepseek", help="Model to use")
    parser.add_argument("--system-prompt", default="", help="System prompt")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    chat_parser = subparsers.add_parser("chat", help="Start a chat")
    chat_parser.add_argument("message", help="Message to send")

    imagine_parser = subparsers.add_parser("imagine", help="Generate an image")
    imagine_parser.add_argument("prompt", help="Prompt for image generation")
    imagine_parser.add_argument("--width", type=int, default=1024, help="Image width")
    imagine_parser.add_argument("--height", type=int, default=768, help="Image height")

    args = parser.parse_args()

    core = Core(args.api_key, args.system_prompt, args.model)

    if args.command == "chat":
        result = core.chat([{"role": "user", "content": args.message}])
        print(json.dumps(result, indent=2))
    elif args.command == "imagine":
        result = core.imagine(args.prompt, args.width, args.height)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
