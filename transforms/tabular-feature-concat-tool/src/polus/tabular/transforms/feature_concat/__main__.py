"""Tabular Merger."""
import json
import logging
import os
import pathlib
import time
from typing import Any
from typing import Optional
import pyarrow.feather as feather
import pyarrow.ipc as ipc
import pyarrow as pa
import pyarrow.csv as pv
import pandas as pd
import itertools
from typing import List

import filepattern as fp
import typer
# from polus.tabular.transforms.feature_concat import tabular_merger as tm

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
    file_pattern: str = typer.Option(".+", "--filePattern", help="file_pattern"),
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

    inp_dir = pathlib.Path(inp_dir).resolve()
    out_dir = pathlib.Path(out_dir).resolve()

    assert inp_dir.exists(), f"{inp_dir} doesnot exists!! Please check input path again"
    assert (
        out_dir.exists()
    ), f"{out_dir} doesnot exists!! Please check output path again"

    starttime = time.time()
   
    # Initialize FilePattern object
    fps = fp.FilePattern(inp_dir, file_pattern)
    group_vars = [col.strip() for col in group_by.split(",") if col.strip()]
    features = [col.strip() for col in features.split(",") if col.strip()]

    #Read tables, rename columns, align schemas, and concatenate
    combined_df = []
    for file in fps(group_by=group_vars):
        _, data = file
        tables_to_append = []

        for d in data:
            chvalue = f"{channel_name}{d[0].get(channel_name)}_"
            file_path = pathlib.Path(d[1][0])
            file_extension = file_path.suffix.lower()
            if file_extension in [".arrow", ".feather"] :
                table = feather.read_table(file_path)
            elif file_extension == ".csv":
                table = pv.read_csv(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}. Expected .arrow, .feather, or .csv")
            
            if features:
                table = table.select(features)

            table = table.to_pandas()
            new_column_names = [chvalue + col for col in table.columns]
            # Rename the DataFrame columns
            table.columns = new_column_names

            tables_to_append.append(table)
        
        prf = pd.concat(tables_to_append, axis=1)
        combined_df.append(prf)


    combined_df = pd.concat(combined_df, axis=0)
    platename = pathlib.Path(inp_dir).name
    combined_df["plate"] = platename

    if POLUS_TAB_EXT == ".csv":
        out_name = out_dir.joinpath(f"{platename}.csv")    
        combined_df.to_csv(out_name, index=False)

    elif POLUS_TAB_EXT == ".arrow":
        out_name = out_dir.joinpath(f"{platename}.arrow")
        combined_df = pa.table(combined_df)
        # Open the file and write the table to it
        feather.write_feather(combined_df, out_name)
    else:
        raise ValueError(f"Unsupported output extension: {POLUS_TAB_EXT}. Expected .arrow, .feather, or .csv")


    exec_time = time.time() -starttime
    logger.info(f"Execution time: {time.strftime('%H:%M:%S', time.gmtime(exec_time))}")
    logger.info("Finished Merging of files!")


if __name__ == "__main__":
    app()
