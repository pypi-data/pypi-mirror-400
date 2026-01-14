from enum import Enum
import base64
import os
import time
import httpx
import openai
from llm import hookimpl, KeyModel, AsyncKeyModel, Prompt, Response, Options
from llm.utils import simplify_usage_dict
from pydantic import Field
from typing import Iterator, AsyncGenerator, Optional


def _set_usage(response: Response, usage):
    if not usage:
        return
    # if it's a Pydantic model
    if not isinstance(usage, dict):
        if hasattr(usage, "model_dump"):
            usage = usage.model_dump()
        else:
            return
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)
    # drop the raw fields
    usage.pop("input_tokens", None)
    usage.pop("output_tokens", None)
    usage.pop("total_tokens", None)
    response.set_usage(
        input=input_tokens,
        output=output_tokens,
        details=simplify_usage_dict(usage),
    )

def _safe_model_slug(model_name: str) -> str:
    slug = "".join(
        c if c.isalnum() or c in "-._" else "-" for c in model_name.strip()
    ).strip("-_")
    return slug or "image"

def _default_filename(model_name: str) -> str:
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    return f"{_safe_model_slug(model_name)}_{timestamp}.png"

def _disambiguate_path(path: str) -> str:
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    counter = 1
    while True:
        candidate = f"{base}_{counter}{ext}"
        if not os.path.exists(candidate):
            return candidate
        counter += 1

def _resolve_output_path(model_name: str, output_path: Optional[str]) -> str:
    if output_path:
        output_path = os.path.expanduser(output_path)
        if os.path.isdir(output_path):
            path = os.path.join(output_path, _default_filename(model_name))
            return _disambiguate_path(path)
        return output_path
    path = os.path.join(os.getcwd(), _default_filename(model_name))
    return _disambiguate_path(path)

def _write_base64_image(
    model_name: str, b64_data: str, output_path: Optional[str]
) -> str:
    path = _resolve_output_path(model_name, output_path)
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    image_bytes = base64.b64decode(b64_data)
    with open(path, "wb") as file_handle:
        file_handle.write(image_bytes)
    return path


@hookimpl
def register_models(register):
    register(
        OpenAIImageModel("gpt-image-1.5"),
        AsyncOpenAIImageModel("gpt-image-1.5"),
    )
    register(
        GoogleImageModel(
            "gemini-2.5-flash-image",
            "google/nano-banana",
        ),
        AsyncGoogleImageModel(
            "gemini-2.5-flash-image",
            "google/nano-banana",
        ),
    )
    register(
        GoogleImageModel(
            "gemini-3-pro-image-preview",
            "google/nano-banana-pro",
        ),
        AsyncGoogleImageModel(
            "gemini-3-pro-image-preview",
            "google/nano-banana-pro",
        ),
    )

class QualityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class SizeEnum(str, Enum):
    square = "square"
    portrait = "portrait"
    landscape = "landscape"

    @property
    def dimensions(self) -> str:
        return {
            SizeEnum.square: "1024x1024",
            SizeEnum.portrait: "1024x1536",
            SizeEnum.landscape: "1536x1024",
        }[self]

class ImageOptions(Options):
    output: Optional[str] = Field(
        description=(
            "Path to write the output image. Defaults to "
            "./<model>_<timestamp>.png"
        ),
        default=None,
    )
    quality: Optional[QualityEnum] = Field(
        description=(
            "The quality of the image that will be generated."
            "high, medium and low are supported for gpt-image-1.5."
        ),
        default=None,
    )
    size: Optional[SizeEnum] = Field(
        description=(
            "The size of the generated images. One of "
            "square (1024x1024), "
            "landscape (1536x1024), "
            "portrait (1024x1536)"
        ),
        default=None,
    )

class _BaseOpenAIImageModel(KeyModel):
    needs_key = "openai"
    key_env_var = "OPENAI_API_KEY"
    can_stream = False
    supports_schema = False
    attachment_types = {"image/png", "image/jpeg", "image/webp"}

    # Assign the pre-defined Options class
    Options = ImageOptions

    def __init__(self, model_name: str):
        self.model_id = f"openai/{model_name}"
        self.model_name = model_name
        self.output_label = model_name

    def __str__(self):
        return f"OpenAI: {self.model_id}"
        
    def _build_api_kwargs(self, prompt: Prompt) -> dict:
        """Build the dictionary of arguments for the OpenAI API call."""
        if not prompt.prompt:
            raise ValueError("Prompt text is required for image generation/editing.")

        # Access options from the prompt object
        size = (prompt.options.size or SizeEnum.square).dimensions
        quality = (prompt.options.quality or QualityEnum.medium).value

        kwargs = {
            "model": self.model_name,
            "prompt": prompt.prompt,
            "n": 1,
            "size": size,
            "quality": quality,
            # output_format="png",
        }

        return kwargs

class OpenAIImageModel(_BaseOpenAIImageModel, KeyModel):
    """
    Sync model for OpenAI image generation/editing (gpt-image-1.5).
    """

    def execute(
        self,
        prompt: Prompt,
        stream: bool,
        response: Response,
        conversation,
        key: str | None,
    ) -> Iterator[str]:
        client = openai.OpenAI(api_key=self.get_key(key))
        kwargs = self._build_api_kwargs(prompt)

        imgs = [
            a for a in (prompt.attachments or [])
            if a.resolve_type() in self.attachment_types
        ]

        result_b64 = None
        usage = None

        if not imgs:
            api_response = client.images.generate(**kwargs,moderation="low")
        else:
            for img in imgs:
                if not img.path:
                    raise ValueError(f"Attachment must be a local file for editing: {img!r}")

            files = [open(img.path, "rb") for img in imgs]

            try:
                api_response = client.images.edit(
                image=files[0] if len(files) == 1 else files,
                    # mask=
                    **kwargs
                )
            finally:
                for f in files:
                    f.close()

        # pull out the base64 result
        result_b64 = api_response.data[0].b64_json
        if hasattr(api_response, "usage") and api_response.usage:
            usage = api_response.usage

        output_path = _write_base64_image(
            self.output_label, result_b64, prompt.options.output
        )
        response.response_json = {"image_path": output_path}
        if usage:
            _set_usage(response, usage)

        yield output_path


class AsyncOpenAIImageModel(_BaseOpenAIImageModel, AsyncKeyModel):
    """
    Async model for OpenAI image generation/editing (gpt-image-1.5).
    """

    async def execute(
        self,
        prompt: Prompt,
        stream: bool,
        response: Response,
        conversation,
        key: str | None,
    ) -> AsyncGenerator[str, None]:
        client = openai.AsyncOpenAI(api_key=self.get_key(key))
        kwargs = self._build_api_kwargs(prompt)

        imgs = [
            a for a in (prompt.attachments or [])
            if a.resolve_type() in self.attachment_types
        ]

        if not imgs:
            api_response = await client.images.generate(**kwargs,moderation="low")
        else:
            for img in imgs:
                if not img.path:
                    raise ValueError(f"Attachment must be a local file for editing: {img!r}")

            files = [open(img.path, "rb") for img in imgs]

            try:
                api_response = client.images.edit(
                image=files[0] if len(files) == 1 else files,
                    # mask=
                    **kwargs
                )
            finally:
                for f in files:
                    f.close()

        result_b64 = api_response.data[0].b64_json
        if hasattr(api_response, "usage") and api_response.usage:
            _set_usage(response, api_response.usage)

        output_path = _write_base64_image(
            self.output_label, result_b64, prompt.options.output
        )
        response.response_json = {"image_path": output_path}
        yield output_path

class _BaseGoogleImageModel(KeyModel):
    needs_key = "gemini"
    key_env_var = "GEMINI_API_KEY"
    can_stream = False
    supports_schema = False
    attachment_types = {"image/png", "image/jpeg", "image/webp"}
    Options = ImageOptions

    def __init__(self, model_name: str, model_id: str):
        self.model_name = model_name
        self.model_id = model_id
        self.output_label = model_id.split("/", 1)[-1]

    def __str__(self):
        return f"Google: {self.model_id}"

    def _build_payload(self, prompt: Prompt) -> dict:
        if not prompt.prompt and not prompt.attachments:
            raise ValueError(
                "Prompt text or attachments are required for image generation/editing."
            )

        parts = []
        imgs = [
            a for a in (prompt.attachments or [])
            if a.resolve_type() in self.attachment_types
        ]
        for img in imgs:
            if not img.path:
                raise ValueError(
                    f"Attachment must be a local file for editing: {img!r}"
                )
            with open(img.path, "rb") as file_handle:
                image_b64 = base64.b64encode(file_handle.read()).decode("ascii")
            parts.append(
                {
                    "inlineData": {
                        "mimeType": img.resolve_type(),
                        "data": image_b64,
                    }
                }
            )

        if prompt.prompt:
            parts.append({"text": prompt.prompt.strip()})

        if not parts:
            raise ValueError("No valid prompt text or attachments were provided.")

        return {
            "generationConfig": {"responseModalities": ["Image"]},
            "contents": [{"parts": parts}],
        }

    def _extract_image_b64(self, response_data: dict) -> str:
        if err := response_data.get("error"):
            raise ValueError(
                f"API Response Error: {err.get('code')} - {err.get('message')}"
            )

        candidates = response_data.get("candidates") or []
        if not candidates:
            raise ValueError("No candidates returned in the response.")

        finish_reason = candidates[0].get("finishReason")
        if finish_reason in ["PROHIBITED_CONTENT", "NO_IMAGE"]:
            raise ValueError(f"Image was not generated due to {finish_reason}.")

        content = candidates[0].get("content") or {}
        parts = content.get("parts") or []
        for part in parts:
            inline_data = part.get("inlineData")
            if inline_data and inline_data.get("data"):
                return inline_data["data"]

        raise ValueError("No image is present in the response.")

    def _set_usage_from_metadata(self, response: Response, response_data: dict) -> None:
        usage_metadata = response_data.get("usageMetadata") or {}
        if not usage_metadata:
            return
        usage = dict(usage_metadata)
        usage["input_tokens"] = usage_metadata.get("promptTokenCount", 0)
        usage["output_tokens"] = usage_metadata.get("candidatesTokenCount", 0)
        _set_usage(response, usage)


class GoogleImageModel(_BaseGoogleImageModel, KeyModel):
    """
    Sync model for Google Nano Banana image generation/editing.
    """

    def execute(
        self,
        prompt: Prompt,
        stream: bool,
        response: Response,
        conversation,
        key: str | None,
    ) -> Iterator[str]:
        payload = self._build_payload(prompt)
        headers = {"Content-Type": "application/json", "x-goog-api-key": self.get_key(key)}
        api_url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model_name}:generateContent"
        )

        with httpx.Client(timeout=180) as client:
            api_response = client.post(api_url, json=payload, headers=headers)
        response_data = api_response.json()

        result_b64 = self._extract_image_b64(response_data)
        output_path = _write_base64_image(
            self.output_label, result_b64, prompt.options.output
        )
        response.response_json = {
            "image_path": output_path,
            "response_id": response_data.get("responseId"),
        }
        self._set_usage_from_metadata(response, response_data)

        yield output_path


class AsyncGoogleImageModel(_BaseGoogleImageModel, AsyncKeyModel):
    """
    Async model for Google Nano Banana image generation/editing.
    """

    async def execute(
        self,
        prompt: Prompt,
        stream: bool,
        response: Response,
        conversation,
        key: str | None,
    ) -> AsyncGenerator[str, None]:
        payload = self._build_payload(prompt)
        headers = {"Content-Type": "application/json", "x-goog-api-key": self.get_key(key)}
        api_url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model_name}:generateContent"
        )

        async with httpx.AsyncClient(timeout=180) as client:
            api_response = await client.post(api_url, json=payload, headers=headers)
        response_data = api_response.json()

        result_b64 = self._extract_image_b64(response_data)
        output_path = _write_base64_image(
            self.output_label, result_b64, prompt.options.output
        )
        response.response_json = {
            "image_path": output_path,
            "response_id": response_data.get("responseId"),
        }
        self._set_usage_from_metadata(response, response_data)

        yield output_path
