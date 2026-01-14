from dataclasses import asdict
from pathlib import Path
import yaml

from geo_augment.domains.floods.spec import (
    FloodSynthesisSpec,
    FloodConstraints,
    LatentFloodFieldSpec,
)
from geo_augment.domains.floods.validation import validate_all_flood_specs


class GeoAugmentConfigError(ValueError):
    pass


def load_yaml_config(path: str | Path) -> dict:
    path = Path(path)
    if not path.exists():
        raise GeoAugmentConfigError(f"Config file not found: {path}")

    with path.open("r") as f:
        cfg = yaml.safe_load(f)

    if not isinstance(cfg, dict):
        raise GeoAugmentConfigError("YAML config must be a mapping")

    return cfg


def build_flood_specs_from_config(cfg: dict):
    try:
        synth_cfg = cfg.get("synthesis", {})
        constraint_cfg = cfg.get("constraints", {})
        latent_cfg = cfg.get("latent", {})
    except AttributeError:
        raise GeoAugmentConfigError("Invalid config structure")

    synthesis = FloodSynthesisSpec(**synth_cfg)
    constraints = FloodConstraints(**constraint_cfg)
    latent = LatentFloodFieldSpec(**latent_cfg)

    validate_all_flood_specs(
        synthesis=synthesis,
        constraints=constraints,
        latent=latent,
    )

    return synthesis, constraints, latent


def summarize_specs(synthesis, constraints, latent) -> str:
    return (
        "GeoAugment Flood Configuration (validated)\n"
        "-----------------------------------------\n"
        f"Synthesis:\n{asdict(synthesis)}\n\n"
        f"Constraints:\n{asdict(constraints)}\n\n"
        f"Latent Field:\n{asdict(latent)}\n"
    )
