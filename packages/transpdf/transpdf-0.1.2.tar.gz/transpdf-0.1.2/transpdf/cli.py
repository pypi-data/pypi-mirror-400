# transpdf/cli.py
import click
import sys
import subprocess
import tempfile
from pathlib import Path

# Backend is bundled inside the package
BACKEND_DIR = Path(__file__).parent / "backend"

def ensure_node_installed():
    """Ensure Node.js is available in PATH."""
    import shutil
    if not shutil.which("node"):
        click.echo("❌ Node.js is required but not found.", err=True)
        click.echo("👉 Please install Node.js LTS (v20.x) from https://nodejs.org", err=True)
        sys.exit(1)

def verify_backend():
    """Ensure bundled node_modules exists."""
    node_modules = BACKEND_DIR / "node_modules"
    if not node_modules.exists():
        raise RuntimeError(
            "Bundled dependencies missing! This package is corrupted.\n"
            "Please reinstall: pip install --force-reinstall transpdf"
        )

@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("input_pdf", type=click.Path(exists=True, dir_okay=False))
@click.option("--to", "to_lang", default="ta", help="Target language code (e.g., ta, es, fr, hi). Default: ta")
@click.option("--from", "from_lang", default="en", help="Source language code. Default: en")
@click.option("-o", "--output", type=click.Path(), help="Output PDF path. Default: <input>_translated.pdf")
def main(input_pdf, from_lang, to_lang, output):
    """Translate a PDF from one language to another using Google Translate."""
    ensure_node_installed()
    verify_backend()

    input_path = Path(input_pdf).resolve()
    if output:
        output_path = Path(output).resolve()
    else:
        output_path = input_path.with_name(f"{input_path.stem}_translated.pdf")

    cmd = [
        "node",
        "translate-pdf.mjs",
        str(input_path),
        str(output_path.parent),
        from_lang,
        to_lang
    ]

    click.echo(f"🔄 Translating '{input_path.name}' ({from_lang} → {to_lang})...")
    try:
        result = subprocess.run(
            cmd,
            cwd=BACKEND_DIR,
            capture_output=True,
            encoding="utf-8",          # ← ADD THIS
            errors="replace", 
            text=True,
            timeout=3600  # 1 hour max
        )
        if result.returncode != 0:
            click.echo(f"❌ Translation failed:\n{result.stderr}", err=True)
            sys.exit(1)
        
        if not output_path.exists():
            click.echo("❌ Output PDF was not created.", err=True)
            sys.exit(1)

        click.echo(f"✅ Success! Saved to: {output_path}")
    except subprocess.TimeoutExpired:
        click.echo("⏱️  Translation timed out (large PDF?).", err=True)
        sys.exit(1)

if __name__ == "__main__":
    main()