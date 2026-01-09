from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml

from opendpp.core.artifact import Profile


@dataclass(frozen=True)
class LoadedProfile:
    manifest: Profile
    base_dir: Path


def resolve_profile_path(profile_ref: str) -> Path:
    candidate = Path(profile_ref)
    if candidate.is_file():
        return candidate

    bundled = Path("profiles") / profile_ref / "profile.yaml"
    if bundled.is_file():
        return bundled

    raise FileNotFoundError(f"Profile not found: {profile_ref}")


def load_profile(profile_ref: str) -> LoadedProfile:
    path = resolve_profile_path(profile_ref)
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    manifest = Profile.model_validate(data)
    return LoadedProfile(manifest=manifest, base_dir=path.parent)


def _resolve_list(base_dir: Path, paths: Iterable[str]) -> list[str]:
    resolved: list[str] = []
    for entry in paths:
        entry_path = Path(entry)
        if not entry_path.is_absolute():
            entry_path = (base_dir / entry_path).resolve()
        resolved.append(str(entry_path))
    return resolved


def resolve_artifact_paths(profile: LoadedProfile) -> LoadedProfile:
    manifest = profile.manifest
    manifest.artifacts.schemas = _resolve_list(profile.base_dir, manifest.artifacts.schemas)
    manifest.artifacts.shapes = _resolve_list(profile.base_dir, manifest.artifacts.shapes)
    manifest.artifacts.openapi = _resolve_list(profile.base_dir, manifest.artifacts.openapi)
    manifest.artifacts.rules = _resolve_list(profile.base_dir, manifest.artifacts.rules)
    manifest.artifacts.contexts = _resolve_list(profile.base_dir, manifest.artifacts.contexts)
    return profile
