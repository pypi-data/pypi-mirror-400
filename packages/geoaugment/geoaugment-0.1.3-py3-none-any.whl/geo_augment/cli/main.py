import argparse
import os

from geo_augment.io.raster import RasterLoader
from geo_augment.domains.floods.api import (
    synthesize_flood_risk,
    synthesize_flood_labels,
)
from geo_augment.datasets.tiling import tile_raster
from geo_augment.datasets.export import export_npz, export_torch

from geo_augment.config import (
    load_yaml_config,
    build_flood_specs_from_config,
    summarize_specs,
)
from geo_augment.domains.floods.spec import (
    DEFAULT_FLOOD_SPEC,
    DEFAULT_FLOOD_CONSTRAINTS,
    DEFAULT_LATENT_SPEC,
)


def floods_generate(args):
    # -----------------------------
    # 1. Load DEM
    # -----------------------------
    print("Loading DEM...")
    dem = RasterLoader(args.dem).read()

    # -----------------------------
    # 2. Load synthesis specs
    # -----------------------------
    if args.config:
        cfg = load_yaml_config(args.config)
        synthesis_spec, constraints, latent_spec = (
            build_flood_specs_from_config(cfg)
        )
    else:
        synthesis_spec = DEFAULT_FLOOD_SPEC
        constraints = DEFAULT_FLOOD_CONSTRAINTS
        latent_spec = DEFAULT_LATENT_SPEC

    print("\nFlood synthesis configuration:")
    summarize_specs(synthesis_spec, constraints, latent_spec)

    if args.dry_run:
        print("\nDry-run complete. No data generated.")
        return

    # -----------------------------
    # 3. Generate continuous risk
    # -----------------------------
    print("\nGenerating continuous flood risk...")
    risk_maps = synthesize_flood_risk(
        dem=dem,
        synthesis_spec=synthesis_spec,
        constraints=constraints,
        latent_spec=latent_spec,
        n_samples=1,
    )

    risk = risk_maps[0]

    # -----------------------------
    # 4. Optional label derivation
    # -----------------------------
    if args.threshold is not None:
        print(f"Deriving binary labels (threshold={args.threshold})...")
        labels = synthesize_flood_labels(
            risk=risk,
            threshold=args.threshold,
        )
    else:
        labels = None

    # -----------------------------
    # 5. Tiling
    # -----------------------------
    print("Tiling dataset...")
    X, y = tile_raster(
        risk,
        labels, # type: ignore
        tile_size=args.tile_size,
        overlap=args.overlap,
    )

    # -----------------------------
    # 6. Export
    # -----------------------------
    os.makedirs(args.out, exist_ok=True)

    print(f"Exporting dataset ({args.format})...")
    if args.format == "npz":
        export_npz(
            X,
            y,
            out_dir=args.out,
            name="geoaugment_flood",
            metadata={
                "tile_size": args.tile_size,
                "overlap": args.overlap,
                "threshold": args.threshold,
            },
        )
    elif args.format == "torch":
        export_torch(
            X,
            y,
            out_dir=args.out,
            name="geoaugment_flood",
        )
    else:
        raise ValueError("Unsupported export format")

    print("Done.")


def main():
    parser = argparse.ArgumentParser(
        prog="geoaugment",
        description="GeoAugment synthetic GeoAI dataset generator",
    )

    subparsers = parser.add_subparsers(dest="domain")

    floods = subparsers.add_parser("floods", help="Flood-risk datasets")
    floods_sub = floods.add_subparsers(dest="command")

    generate = floods_sub.add_parser(
        "generate", help="Generate flood risk datasets"
    )

    generate.add_argument("--dem", required=True, help="Path to DEM (.tif)")
    generate.add_argument("--out", required=True, help="Output directory")

    generate.add_argument("--config", help="YAML config file")
    generate.add_argument("--dry-run", action="store_true")

    generate.add_argument("--tile-size", type=int, default=256)
    generate.add_argument("--overlap", type=int, default=64)

    generate.add_argument(
        "--threshold",
        type=float,
        help="Optional threshold to derive binary labels",
    )

    generate.add_argument(
        "--format",
        choices=["npz", "torch"],
        default="npz",
    )

    generate.set_defaults(func=floods_generate)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
