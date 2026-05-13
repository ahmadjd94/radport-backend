"""
svs_to_dicom.py
---------------
Convert an Aperio SVS whole-slide image to DICOM WSI files
using the wsidicomizer library.

Usage:
    python svs_to_dicom.py input.svs [output_dir]
    python svs_to_dicom.py input.svs output_dir --tile-size 512 --workers 4

Dependencies:
    pip install wsidicomizer
"""

import argparse
import os
import sys
from datetime import date
from pathlib import Path

from wsidicomizer import WsiDicomizer
from wsidicom.metadata import WsiMetadata
from wsidicom.metadata.wsi import Patient, Study, Series, Equipment


# ---------------------------------------------------------------------------
# Metadata helpers
# ---------------------------------------------------------------------------

def build_metadata(
    patient_name: str | None = None,
    patient_id: str | None = None,
    study_instance_uid: str | None = None,
    accession_number: str | None = None,
    series_number: int | None = None,
) -> WsiMetadata:
    """
    Build a WsiMetadata object with optional overrides.

    Any field left as None will fall back to whatever is embedded in the
    source SVS file (or be left blank if the source doesn't carry it).
    """
    patient = Patient(
        name=patient_name,
        identifier=patient_id,
    )

    study = Study(
        study_instance_uid=study_instance_uid,
        accession_number=accession_number,
        study_date=date.today(),
    )

    series = Series(
        series_number=series_number,
    )

    return WsiMetadata(
        patient=patient,
        study=study,
        series=series,
    )


# ---------------------------------------------------------------------------
# Core conversion
# ---------------------------------------------------------------------------

def convert_svs_to_dicom(
    svs_path: str | Path,
    output_dir: str | Path | None = None,
    tile_size: int = 512,
    workers: int | None = None,
    add_missing_levels: bool = False,
    include_levels: list[int] | None = None,
    include_label: bool = True,
    include_overview: bool = True,
    include_thumbnail: bool = True,
    include_confidential: bool = False,   # strip confidential metadata by default
    metadata: WsiMetadata | None = None,
) -> list[str]:
    """
    Convert an SVS file to DICOM WSI files.

    Parameters
    ----------
    svs_path : path to the source .svs file
    output_dir : directory where DICOM files will be written.
                 Defaults to a sub-folder named after the SVS file
                 alongside the source file.
    tile_size : tile size in pixels (default 512)
    workers : number of parallel workers; None = auto
    add_missing_levels : fill in missing pyramid levels down to 1×1 tile
    include_levels : subset of pyramid levels to convert, e.g. [-1, -2]
                     exports only the two highest-resolution levels.
                     None exports all levels.
    include_label : include label image
    include_overview : include overview image
    include_thumbnail : include thumbnail image
    include_confidential : include confidential metadata from the source file
    metadata : optional WsiMetadata to override source-file metadata

    Returns
    -------
    List of paths to the created DICOM files.
    """
    svs_path = Path(svs_path).resolve()

    if not svs_path.exists():
        raise FileNotFoundError(f"SVS file not found: {svs_path}")

    if svs_path.suffix.lower() not in {".svs", ".tif", ".tiff", ".ndpi",
                                        ".scn", ".mrxs", ".bif", ".qptiff"}:
        print(
            f"[WARNING] '{svs_path.suffix}' is not a typical SVS extension. "
            "Attempting conversion anyway.",
            file=sys.stderr,
        )

    # Default output directory: <svs_stem>_dicom/ next to the SVS file
    if output_dir is None:
        output_dir = svs_path.parent / f"{svs_path.stem}_dicom"

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Input  : {svs_path}")
    print(f"[INFO] Output : {output_dir}")
    print(f"[INFO] Tile size: {tile_size}px  |  Workers: {workers or 'auto'}")
    if include_levels is not None:
        print(f"[INFO] Level filter: {include_levels}")

    created_files: list[str] = WsiDicomizer.convert(
        filepath=svs_path,
        output_path=output_dir,
        metadata=metadata,
        tile_size=tile_size,
        add_missing_levels=add_missing_levels,
        include_levels=include_levels,
        include_label=include_label,
        include_overview=include_overview,
        include_thumbnail=include_thumbnail,
        include_confidential=include_confidential,
        workers=workers,
    )

    return created_files


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert an SVS whole-slide image to DICOM using wsidicomizer.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("svs_path", help="Path to the source SVS file.")
    parser.add_argument(
        "output_dir",
        nargs="?",
        default=None,
        help="Directory to write DICOM files (created if absent). "
             "Defaults to <svs_stem>_dicom/ next to the source file.",
    )

    # Conversion options
    parser.add_argument("--tile-size", type=int, default=512,
                        help="Tile size in pixels.")
    parser.add_argument("--workers", type=int, default=None,
                        help="Number of parallel worker threads.")
    parser.add_argument("--add-missing-levels", action="store_true",
                        help="Fill in missing dyadic pyramid levels.")
    parser.add_argument("--levels", type=int, nargs="+", default=None,
                        metavar="N",
                        help="Pyramid level indices to include (e.g. -1 -2 for "
                             "the two highest-resolution levels). Negative "
                             "indices count from the highest resolution.")

    # Image inclusion flags
    parser.add_argument("--no-label", action="store_true",
                        help="Exclude the label image.")
    parser.add_argument("--no-overview", action="store_true",
                        help="Exclude the overview image.")
    parser.add_argument("--no-thumbnail", action="store_true",
                        help="Exclude the thumbnail image.")
    parser.add_argument("--include-confidential", action="store_true",
                        help="Include confidential metadata from the source.")

    # Optional metadata overrides
    meta = parser.add_argument_group("metadata overrides")
    meta.add_argument("--patient-name", default=None,
                      help="Override patient name.")
    meta.add_argument("--patient-id", default=None,
                      help="Override patient ID.")
    meta.add_argument("--accession-number", default=None,
                      help="Override accession number.")
    meta.add_argument("--series-number", type=int, default=None,
                      help="Override series number.")

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Build metadata only if any override was supplied
    metadata = None
    if any([
        args.patient_name,
        args.patient_id,
        args.accession_number,
        args.series_number is not None,
    ]):
        metadata = build_metadata(
            patient_name=args.patient_name,
            patient_id=args.patient_id,
            accession_number=args.accession_number,
            series_number=args.series_number,
        )

    try:
        created = convert_svs_to_dicom(
            svs_path=args.svs_path,
            output_dir=args.output_dir,
            tile_size=args.tile_size,
            workers=args.workers,
            add_missing_levels=args.add_missing_levels,
            include_levels=args.levels,
            include_label=not args.no_label,
            include_overview=not args.no_overview,
            include_thumbnail=not args.no_thumbnail,
            include_confidential=args.include_confidential,
            metadata=metadata,
        )
    except FileNotFoundError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"[ERROR] Conversion failed: {exc}", file=sys.stderr)
        raise

    print(f"\n[OK] Created {len(created)} DICOM file(s):")
    for f in created:
        size_mb = os.path.getsize(f) / 1_048_576
        print(f"  {f}  ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()