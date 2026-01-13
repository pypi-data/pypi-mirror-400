import pandas as pd
import os
import numpy as np
import re


def try_to_numeric(x):
    """
    Attempt to convert a value to a numeric type using pandas. If conversion fails, return the original value.
    Parameters:
        x: Value to convert.
    Returns:
        Numeric value or original value if conversion fails.
    """
    try:
        return pd.to_numeric(x)
    except Exception:
        return x


def process_data(seclines):
    """
    Process a section of lines from a file into a pandas DataFrame.
    Parameters:
        seclines (list of str): Lines representing a data section, with the first line as column headers.
    Returns:
        pd.DataFrame: DataFrame with columns and converted numeric values.
    """
    column_line = seclines[0].replace("\t", "").replace("#", "").strip()
    columns = column_line.split()
    # Use list comprehension for efficiency
    data = [
        [part.replace("E", "e") for part in line.split()]
        for line in seclines[1:]
        if line.strip() and "--" not in line
    ]
    df_temp = pd.DataFrame(data, columns=columns)
    df_temp = df_temp.apply(try_to_numeric)
    return df_temp


def read_outputTHX(file_path):
    """
    Read and process a THX output file, extracting time-stepped node data into a DataFrame.
    Parameters:
        file_path (str): Path to the THX output file.
    Returns:
        pd.DataFrame: DataFrame containing node data for all time steps.
    """

    with open(file_path, "r") as f:
        lines = f.readlines()

    times = []
    for line in lines:
        if "Time ==> " in line:
            time_value = float(line.split()[-1])
            times.append(time_value)

    section_indices = []
    for i, line in enumerate(lines):
        if "node" in line.lower():
            section_indices.append(i)
    section_indices.append(len(lines))

    df_heads = pd.DataFrame()
    for i, j in zip(section_indices[:-1], section_indices[1:]):
        seclines = lines[i:j]
        df_temp = process_data(seclines)
        df_temp["Time"] = times[i]
        df_heads = pd.concat([df_heads, df_temp], ignore_index=True)
    return df_heads


def read_outputSPX(file_path):
    """
    Read and process an SPX output file, extracting time-stepped node data into a DataFrame.
    Parameters:
        file_path (str): Path to the SPX output file.
    Returns:
        pd.DataFrame: DataFrame containing node data for all time steps.
    """

    with open(file_path, "r") as f:
        lines = f.readlines()

    times = []
    for line in lines:
        if "Time ==> " in line:
            time_value = float(line.split()[-1])
            times.append(time_value)

    section_indices = []
    for i, line in enumerate(lines):
        if "node" in line.lower():
            section_indices.append(i)
    section_indices.append(len(lines))

    df_spx = pd.DataFrame()
    l = 0
    for i, j in zip(section_indices[:-1], section_indices[1:]):
        if j != len(lines):
            j -= 3
        seclines = lines[i:j]
        column_line = seclines[0].replace("\t", "").replace("#", "").strip()
        columns = column_line.split()
        # Use list comprehension for efficiency
        data = [
            line.split()
            for line in seclines[2:]
            if line.strip() and not any(x in line for x in ("--", "#"))
        ]
        df_temp = pd.DataFrame(data, columns=columns)
        df_temp["Time"] = times[l]
        l += 1
        df_temp = df_temp.apply(try_to_numeric)
        df_spx = pd.concat([df_spx, df_temp], ignore_index=True)
    return df_spx


def read_outputSPT(file_path):
    """
    Read and process an SPT output file into a DataFrame, skipping header rows.
    Parameters:
        file_path (str): Path to the SPT output file.
    Returns:
        pd.DataFrame: DataFrame containing SPT data.
    """
    skiprows = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11]

    df = pd.read_csv(file_path, skiprows=skiprows, sep=r"\s+")
    cols = [col.strip() for col in df.columns]
    cols = cols[1:]
    df = df.iloc[:, :-1]
    df.columns = cols
    return df


def read_outhx(filepath):
    """
    Reads a core output file containing node data and time blocks, and returns the data as a pandas DataFrame.
    The function parses lines in the file to extract time information and node data (node ID, X, Y, and head values).
    Each data entry is associated with the corresponding time block.
    Parameters
    ----------
    filepath : str
        Path to the core output file to be read.
    Returns
    -------
    pandas.DataFrame
        DataFrame containing columns: 'Time', 'Node', 'X', 'Y', 'Head', with one row per node entry.
    """

    data = []
    time = None
    with open(filepath, "r") as f:
        for line in f:
            # Detect time block
            time_match = re.match(r"# Time ==> *([0-9.Ee+-]+)", line)
            if time_match:
                time = float(time_match.group(1))
                continue
            # Detect data lines (node, x, y, head)
            if re.match(r"^\s*\d+", line):
                parts = line.split()
                if len(parts) == 4:
                    node = int(parts[0])
                    x = float(parts[1])
                    y = float(parts[2])
                    head = float(parts[3])
                    data.append(
                        {"Time": time, "Node": node, "X": x, "Y": y, "Head": head}
                    )
    df = pd.DataFrame(data)
    return df
