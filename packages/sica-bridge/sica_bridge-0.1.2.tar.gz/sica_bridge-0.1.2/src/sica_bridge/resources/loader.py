from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import Any, Dict

import yaml

from sica_bridge.registry import get_component
from sica_bridge.llm.client import VisionInput


def _pkg_path(*parts: str) -> Path:
    return files("sica_bridge").joinpath(*parts)  


def load_rubric(component_id: str) -> Dict[str, Any]:
    spec = get_component(component_id)
    path = _pkg_path("rubrics", spec.rubric_filename)
    if not path.exists():
        raise FileNotFoundError(f"Rubric not found for {component_id}: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise TypeError(f"Rubric file must be a YAML mapping/dict: {path}")
    return data


def load_prompt_template(component_id: str) -> str:
    spec = get_component(component_id)
    path = _pkg_path("prompts", spec.prompt_filename)
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found for {component_id}: {path}")
    return path.read_text(encoding="utf-8")


def load_system_prompt() -> str:
    path = _pkg_path("prompts", "system.md")
    if not path.exists():
        raise FileNotFoundError(f"System prompt not found: {path}")
    return path.read_text(encoding="utf-8")


def _infer_mime_type(filename: str) -> str:
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if ext in ("jpg", "jpeg"):
        return "image/jpeg"
    if ext == "png":
        return "image/png"
    return "application/octet-stream"


def load_reference_images(component_id: str, limit: int | None = None) -> list[VisionInput]:
    """
    Load preset reference images from:
      sica_bridge/assets/damage_examples/<component_id>/
    """
    folder = _pkg_path("assets", "damage_examples", component_id)
    if not folder.exists():
        return []

    meta_path = folder / "meta.yaml"
    captions: dict[str, str] = {}

    if meta_path.exists():
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
        for item in (meta.get("examples") or []):
            if isinstance(item, dict) and "file" in item:
                captions[str(item["file"])] = str(item.get("caption") or "")

    # Prefer ordering from meta.yaml; otherwise load all images
    if captions:
        file_paths = [folder / fname for fname in captions.keys() if (folder / fname).exists()]
    else:
        file_paths = sorted([p for p in folder.iterdir() if p.suffix.lower() in [".jpg", ".jpeg", ".png"]])

    if limit is not None:
        file_paths = file_paths[:limit]

    refs: list[VisionInput] = []
    for p in file_paths:
        refs.append(
            VisionInput(
                image_bytes=p.read_bytes(),
                mime_type=_infer_mime_type(p.name),
                filename=p.name,
                role="reference",
                caption=captions.get(p.name) or p.name,
            )
        )
    return refs
