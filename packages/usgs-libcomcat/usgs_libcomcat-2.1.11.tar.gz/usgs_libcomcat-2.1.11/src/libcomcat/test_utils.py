# stdlib imports
import pathlib

# third party imports
import vcr as vcrpy

TEST_DATA_DIR = pathlib.Path(__file__).parent / ".." / "data" / "cassettes"
vcr = vcrpy.VCR(
    path_transformer=vcrpy.VCR.ensure_suffix(".yaml"),
    cassette_library_dir=str(TEST_DATA_DIR),
    record_mode="once",
    match_on=["uri", "method"],
)
