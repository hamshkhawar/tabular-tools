"""Tabular Feature Concat Tool."""
import json
import logging
import os
import typer
import pathlib
import typing
from typing import Optional
import polus.tabular.transforms.feature_concat as fc

app = typer.Typer()

# Initialize the logger
logging.basicConfig(
    format="%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
logger = logging.getLogger("polus.tabular.transforms.feature_concat")
logger.setLevel(os.environ.get("POLUS_LOG", logging.INFO))
POLUS_TAB_EXT = os.environ.get("POLUS_TAB_EXT", ".arrow")


@app.command()
def main(  # noqa: PLR0913
    inp_dir: pathlib.Path = typer.Option(
        ...,
        "--inpDir",
        help="Input generic data collection to be processed by this plugin",
    ),
    file_pattern: str = typer.Option(..., "--filePattern", help="file_pattern"),
    group_by: str = typer.Option(
        ...,
        "--groupBy",
        help="Group files based on variable"
    ),
    channel_name: str = typer.Option(
        ...,
        "--channelName",
        help="Variable for channel name",
    ),
    features:Optional[str] =
        typer.Option(
            None,
            "--features",
            help="List of selected features",
        ),
    meta_dir:Optional[pathlib.Path] =
        typer.Option(
            None,
            "--metaDir",
            help="Path to metadata file",
        ),
    out_dir: pathlib.Path = typer.Option(..., "--outDir", help="Output collection"),
    preview: Optional[bool] = typer.Option(
        False,
        "--preview",
        help="Output a JSON preview of files",
    ),
) -> None:
    """CLI for the tool."""
    logger.info(f"inpDir = {inp_dir}")
    logger.info(f"outDir = {out_dir}")
    logger.info(f"filePattern = {file_pattern}")
    logger.info(f"groupBy = {group_by}")
    logger.info(f"channelName = {channel_name}")
    logger.info(f"features = {features}")
    logger.info(f"metaDir = {meta_dir}")

    inp_dir = pathlib.Path(inp_dir).resolve()
    out_dir = pathlib.Path(out_dir).resolve()

    if preview:
        with open(pathlib.Path(out_dir).joinpath("preview.json"), "w") as fw:
            out_files: typing.Dict[str, typing.Union[typing.List, str]] = {
                r"filepattern": file_pattern,
                "outDir": [],
            }
            platename = f"{pathlib.Path(inp_dir).name}{POLUS_TAB_EXT}"
            out_files["outDir"]= platename  # type: ignore
            json.dump(out_files, fw, indent=2)

    else:
        fc.feat_concat(inp_dir=inp_dir, 
                out_dir=out_dir, 
                file_pattern=file_pattern, 
                group_by=group_by, 
                channel_name=channel_name, 
                features=features, 
                meta_dir=meta_dir
                )

     


if __name__ == "__main__":
    app()
