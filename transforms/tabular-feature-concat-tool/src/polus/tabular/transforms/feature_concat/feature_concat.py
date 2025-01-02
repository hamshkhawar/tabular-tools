"""Tabular Feature Concat Tool."""
import logging
import os
import pathlib
import time
from typing import Any
from typing import Optional
import pyarrow.feather as feather
import pyarrow as pa
import pyarrow.csv as pv
import pandas as pd
import filepattern as fp
import time
from multiprocessing import Pool


logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("POLUS_LOG", logging.INFO))
POLUS_TAB_EXT = os.environ.get("POLUS_TAB_EXT", ".arrow")

# Set max_workers based on CPU count
NUM_WORKERS = os.cpu_count() // 2 
if NUM_WORKERS < 1:
   NUM_WORKERS = 1  


def read_metadata(meta_dir:pathlib.Path):
    """
    Reads and concatenates metadata files (CSV, Arrow, Feather) from a directory.

    Args:
        meta_dir: Directory containing the metadata files.

    Returns:
        pandas.DataFrame: Concatenated DataFrame of the metadata files, or None if no valid files are found.
    """
    meta_files = []
    for f in pathlib.Path(meta_dir).iterdir():
        if f.suffix == ".csv":
            table = pv.read_csv(f)
        elif f.suffix in [".arrow", ".feather"]:
            table = feather.read_table(f)
        else:
            continue
        meta_files.append(table.to_pandas())
    return pd.concat(meta_files, axis=0) if meta_files else None

def process_file(file:pathlib.Path, group_vars:list[str], channel_name:str, features:list[str], meta_cols:Optional[list[str]]):
    """
    Processes a file and returns a concatenated DataFrame.

    Reads a file (.arrow, .feather, or .csv), selects specified features, renames columns with 
    a channel name, and creates a 'well' column based on the grouping variables.

    Args:
        file: Path to the file to process.
        group_vars: List of row and column keys for grouping.
        meta_cols: Optional feature name for merging metadata file.
        channel_name: Base name for renaming columns.
        features: List of feature names to select.

    Returns:
        pandas.DataFrame: Concatenated DataFrame with processed data.
    """

    _, data = file
    tables_to_append = []

    for d in data:
        chvalue = f"{channel_name}{d[0].get(channel_name)}_"
        file_path = pathlib.Path(d[1][0])
        file_extension = file_path.suffix.lower()

        # Read file based on extension
        if file_extension in [".arrow", ".feather"]:
            table = feather.read_table(file_path)
        elif file_extension == ".csv":
            table = pv.read_csv(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}. Expected .arrow, .feather, or .csv")

        if features:
            table = table.select(features)

        table = table.to_pandas()
 
        table.columns = [chvalue.upper() + col for col in table.columns] 

        if meta_cols:
            for col in meta_cols:
                table[col] = None

            rowname = d[0].get(group_vars[0])
            table[meta_cols[0]] = rowname
            if len(meta_cols) == 2 and len(group_vars) == 2:
                colname = d[0].get(group_vars[1])
                table[meta_cols[1]] = colname

        else:
            table["well"] = None
            rowname = d[0].get(group_vars[0])

            if len(group_vars) == 2:
                colname = d[0].get(group_vars[1])
                table["well"] = f"{rowname}{int(colname):02d}"
            else:
                table["well"] = f"{rowname}"
        tables_to_append.append(table)


    return pd.concat(tables_to_append, axis=1)

def feat_concat(inp_dir: pathlib.Path, 
                out_dir: pathlib.Path, 
                file_pattern: str, 
                group_by: str, 
                channel_name: str, 
                features: Optional[str] = None, 
                meta_dir: Optional[pathlib.Path] = None,
                meta_cols: Optional[str] = None,
                plate_name:Optional[str] = None, 
                num_workers: int = NUM_WORKERS):

    """
    Concatenates features from multiple files and saves the result.

    Processes input files based on a pattern, merges with optional metadata,
    renames columns, and outputs the concatenated DataFrame in the specified format.

    Args:
        inp_dir: Directory with input files.
        out_dir: Directory to save the output.
        file_pattern: File pattern for matching input files.
        group_by: Columns to group by.
        channel_name: Base name for renaming columns.
        features: Optional list of features to select.
        meta_dir: Optional directory for metadata files.
        meta_cols: Optional feature name for merging metadata file.
        plate_name: Optional directory name for merging with metadata files.
        num_workers: Number of parallel workers.
    """

    starttime = time.time()

    # Validate paths
    inp_dir = pathlib.Path(inp_dir).resolve()
    out_dir = pathlib.Path(out_dir).resolve()
    assert inp_dir.exists(), f"{inp_dir} does not exist!"
    assert out_dir.exists(), f"{out_dir} does not exist!"

    # Read metadata if provided
    metadata = read_metadata(meta_dir) if meta_dir else None
    

    # # Prepare group and feature variables
    group_vars = [col.strip() for col in group_by.split(",") if col.strip()]
    meta_cols = [col.strip() for col in meta_cols.split(",") if col.strip()]
    features = [col.strip() for col in features.split(",") if col.strip()] if features else []

    # Initialize FilePattern object
    fps = fp.FilePattern(inp_dir, file_pattern)

    # Process files in parallel
    with Pool(num_workers) as pool:
        results = pool.starmap(
            process_file, 
            [(file, group_vars, channel_name, features, meta_cols) for file in fps(group_by=group_vars)]
        )

    # # # # Combine results
    results = [df.loc[:, ~df.columns.duplicated()] for df in results]
    combined_df = pd.concat(results, axis=0, ignore_index=True)
    
    if combined_df.shape[0] == 0:
        msg=f"Please check the filepattern again"
        raise ValueError(msg)
    
    if plate_name:
        platename = plate_name
    else:
        platename = inp_dir.name
    

    combined_df["plate"] = platename

    # # Filter and rename columns
    image_columns = combined_df.filter(regex="_image").columns[:2].tolist()
    varcolumns = combined_df.filter(regex=f"^(?!.*_image|plate|well|{meta_cols[0]}|{meta_cols[1]})").columns.tolist()
    merge_columns = ["plate", "well"] if meta_cols is None else ["plate"] + [meta_cols[0]] + [meta_cols[1]]
    combined_df = combined_df[merge_columns + image_columns + varcolumns]
    combined_df.columns = combined_df.columns.str.replace(r".*_(intensity_image|mask_image)", r"\1", regex=True)

    # Merge with metadata if available
    if meta_cols is None:
        merge_keys = ["plate", "well"]
    elif len(meta_cols) == 1:
        merge_keys = ["plate"] + [meta_cols[0]]
    elif len(meta_cols) == 2:
        merge_keys = ["plate"] + [meta_cols[0]] + [meta_cols[1]]
    else:
        raise ValueError("meta_cols should have at most 2 elements")
    
    combined_df = (
        pd.merge(metadata, combined_df, on=merge_keys, how="inner")
        .drop_duplicates()
    )

    # # Write output
    platename = inp_dir.name
    if POLUS_TAB_EXT == ".csv":
        combined_df.to_csv(out_dir / f"{platename}.csv", index=False)
    elif POLUS_TAB_EXT == ".arrow":
        feather.write_feather(pa.table(combined_df), out_dir / f"{platename}.arrow")
    else:
        raise ValueError(f"Unsupported output extension: {POLUS_TAB_EXT}")

    logger.info(f"Execution time: {time.strftime('%H:%M:%S', time.gmtime(time.time() - starttime))}")
    logger.info("Finished merging files!")
