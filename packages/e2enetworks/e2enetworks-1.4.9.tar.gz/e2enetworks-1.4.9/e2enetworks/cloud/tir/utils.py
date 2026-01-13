import yaml
import json
from typing import Dict, Any
from requests import Response
from types import SimpleNamespace


def load_yaml(
        path: str,
) -> Dict[str, Any]:
    _load_from_local(path)


def _load_from_local(path: str) -> Dict[str, Any]:
    with open(path) as f:
        return yaml.safe_load(f)


def load_json(b: bytes, object_hook=None) -> Dict:
    return json.loads(b, object_hook=object_hook)


def prepare_object(response: Response, _get_raw: bool = False):
    if not response.ok:
        try:
            output = response.json()['errors']
        except:
            output = response.reason
        print("ERROR:", output)
        return False, response

    if _get_raw:
        return True, response

    response = load_json(response.content, object_hook=lambda d: SimpleNamespace(**d))
    if hasattr(response, "data"):
        return True, response.data
    else:
        return True, response


def prepare_response(response: Response) -> Dict:
    if response.ok:
        return load_json(response.content)

    # logger.error("")
    print("api call failed with error:", response.reason)
    return {
        "error": response.reason
    }
