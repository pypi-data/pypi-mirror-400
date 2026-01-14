import hashlib
import json
from typing import Any, Dict, TypeAlias, List

Image: TypeAlias = str | List[str]
ImageOptionsDict: TypeAlias = dict[str, str | bool | int | float]
ImageOptions: TypeAlias = ImageOptionsDict | dict[int, ImageOptionsDict]
ImageCaptions: TypeAlias = str | dict[int, str]
_SCALARS = (str, bool, int, float)


def compute_question_sha256(question) -> str:
    blob = {
        "slug": question.slug,
        "qid": question.qid,
        "version": getattr(question, "version", None),
        "text": question.text,
        "choices": question.choices,
    }
    blob_json = json.dumps(
        blob, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    sha256 = hashlib.sha256(blob_json).hexdigest()
    return sha256

def _norm_images(img: Any) -> List[str]:
    """Normalize image into a list[str]."""
    if img is None:
        return []
    if isinstance(img, str):
        return [img]
    if isinstance(img, list):
        if not all(isinstance(x, str) for x in img):
            raise TypeError("image must be a string or a list of strings.")
        return img
    raise TypeError("image must be a string, a list of strings, or null.")

def _norm_opts(opts: Any) -> Dict[int, ImageOptionsDict]:
    """
    Normalize image_options into dict[int, dict[str, scalar]].
    - flat dict[str->scalar]  -> {0: dict}
    - dict[int -> dict[str->scalar]] -> as-is (validated)
    """
    if opts is None:
        return {}
    if not isinstance(opts, dict):
        raise TypeError("image_options must be a dict or null.")

    keys = list(opts.keys())
    if all(isinstance(k, str) for k in keys):
        # flat dict → {0: dict}
        if not all(isinstance(v, _SCALARS) for v in opts.values()):
            raise ValueError("image_options flat form must map str -> (str|bool|int|float).")
        return {0: dict(opts)}  # shallow copy
    if all(isinstance(k, int) for k in keys):
        # nested dict[int -> dict[str->scalar]]
        out: Dict[int, ImageOptionsDict] = {}
        for i, sub in opts.items():
            if not isinstance(sub, dict) or not all(isinstance(k, str) for k in sub.keys()):
                raise TypeError("image_options indexed form must be dict[int -> dict[str -> scalar]].")
            if not all(isinstance(v, _SCALARS) for v in sub.values()):
                raise ValueError("image_options values must be (str|bool|int|float).")
            out[int(i)] = dict(sub)  # shallow copy
        return out

    raise ValueError("image_options keys must be all str (flat) or all int (indexed).")


def _norm_caps(caps: Any) -> Dict[int, str]:
    """Normalize image_captions into dict[int, str]. A single string becomes {0: <str>}."""
    if caps is None:
        return {}
    if isinstance(caps, str):
        return {0: caps}
    if isinstance(caps, dict):
        if not all(isinstance(k, int) and isinstance(v, str) for k, v in caps.items()):
            raise TypeError("image_captions must be dict[int, str] or a single string.")
        return {int(k): v for k, v in caps.items()}
    raise TypeError("image_captions must be a string, dict[int, str], or null.")

def relativize_paths(base_path, paths: List[str]) -> List[str]:
    """Convert absolute paths to relative paths based on base_path."""
    from pathlib import Path

    base = Path(base_path).resolve()
    rel_paths = []
    for p in paths:
        p_path = Path(p).resolve()
        rel_p = p_path.relative_to(base, walk_up=True)
        rel_paths.append(str(rel_p))
    return rel_paths