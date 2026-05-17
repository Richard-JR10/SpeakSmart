"""Fill a test certificate PDF form with a student name.

Usage:
    uv run python scripts/fill_certificate_pdf.py \
        --template templates/certificate_template.pdf \
        --name "Maria Santos" \
        --output generated/certificate-test.pdf

The template PDF must contain a fillable text field named: text_1vcfg
"""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fill the text_1vcfg field in a certificate PDF template."
    )
    parser.add_argument(
        "--template",
        required=True,
        type=Path,
        help="Path to the fillable certificate PDF template.",
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Student name to place in the text_1vcfg form field.",
    )
    parser.add_argument(
        "--output",
        default=Path("generated/certificate-test.pdf"),
        type=Path,
        help="Where to save the filled PDF.",
    )
    return parser.parse_args()


def main() -> None:
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: pypdf. Install it from Backend with: uv add pypdf"
        ) from exc

    args = parse_args()

    if not args.template.exists():
        raise SystemExit(f"Template PDF not found: {args.template}")

    reader = PdfReader(args.template)
    fields = reader.get_fields() or {}

    if "text_1vcfg" not in fields:
        available_fields = ", ".join(fields.keys()) or "none"
        raise SystemExit(
            "The template does not contain a field named 'text_1vcfg'. "
            f"Available fields: {available_fields}"
        )

    writer = PdfWriter()
    writer.clone_document_from_reader(reader)

    for page in writer.pages:
        writer.update_page_form_field_values(
            page,
            {"text_1vcfg": args.name},
            auto_regenerate=True,
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open("wb") as output_file:
        writer.write(output_file)

    print(f"Filled certificate saved to: {args.output}")


if __name__ == "__main__":
    main()
