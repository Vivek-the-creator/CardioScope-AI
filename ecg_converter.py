# ecg_converter.py

import wfdb
import os
import pandas as pd

def convert_record_to_csv(record_name, input_dir, output_dir):
    """
    Converts a PhysioNet ECG record (.dat/.hea) to CSV.
    
    Args:
        record_name (str): Filename without extension (e.g., '100')
        input_dir (str): Folder where .dat/.hea are stored
        output_dir (str): Folder to save .csv
    Returns:
        dict: metadata with leads, sampling rate, and CSV path
    """
    record_path = os.path.join(input_dir, record_name)
    record = wfdb.rdrecord(record_path)
    
    # Extract signal & lead info
    signal = record.p_signal
    leads = record.sig_name
    fs = record.fs
    
    df = pd.DataFrame(signal, columns=leads)
    csv_path = os.path.join(output_dir, f"{record_name}.csv")
    df.to_csv(csv_path, index=False)

    return {
        "record": record_name,
        "leads": leads,
        "sampling_rate": fs,
        "csv_path": csv_path
    }
