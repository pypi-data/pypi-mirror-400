from pathlib import Path
import xarray as xr


LIBRARY_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = LIBRARY_DIR.parent
SAMPLE_DATA_DIR = LIBRARY_DIR / "sample_data"

xr.set_options(display_expand_coords=False, display_expand_data=False)