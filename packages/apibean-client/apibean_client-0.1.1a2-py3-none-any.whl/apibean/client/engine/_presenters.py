from dataclasses import dataclass
import json
import httpx
import yaml

IMPORTANT_HEADERS = {
    "content-type",
    "content-length",
    "date",
    "server",
    "x-request-id",
    "x-trace-id",
}

@dataclass
class YamlResponsePresenter:
    sort_keys: bool = False

    def render(self, response: httpx.Response, body_only: bool=False) -> str:
        return yaml.safe_dump(
            self._build_response_view(response, body_only),
            sort_keys=self.sort_keys,
            allow_unicode=True,
            default_flow_style=False,
        )

    def _build_response_view(self, response: httpx.Response, body_only: bool=False) -> dict:
        if body_only:
            return {
                "Response": {
                    "body": self._parse_body(response),
                }
            }
        return {
            "Response": {
                "status": {
                    "code": response.status_code,
                    "reason": response.reason_phrase,
                },
                "headers": self._filter_headers(response.headers),
                "timing": {
                    "elapsed_ms": int(
                        response.elapsed.total_seconds() * 1000
                    )
                },
                "body": self._parse_body(response),
            }
        }

    def _filter_headers(self, headers: httpx.Headers) -> dict[str, str]:
        return {
            k.lower(): v
            for k, v in headers.items()
            if k.lower() in IMPORTANT_HEADERS
        }

    def _parse_body(self, response: httpx.Response):
        content_type = response.headers.get("content-type", "")

        if "application/json" in content_type:
            try:
                data = response.json()
                if isinstance(data, list):
                    return {"items": data}
                return {"data": data}
            except Exception:
                return {"text": response.text}

        if content_type.startswith("text/"):
            return {"text": response.text}

        return {"binary": "<binary content omitted>"}


class JsonResponsePresenter(YamlResponsePresenter):
    def render(self, response: httpx.Response, body_only: bool=False) -> str:
        return json.dumps(
            self._build_response_view(response, body_only),
            sort_keys=self.sort_keys,
            ensure_ascii=False,
        )


class TextResponsePresenter:
    def render(self, response: httpx.Response, body_only: bool=False) -> str:
        if body_only:
            return json.dumps(response.json(), indent=2)
        if response.is_success:
            return str(response)
        else:
            return (
                str(response),
                json.dumps(response.json(), indent=2)
            )
