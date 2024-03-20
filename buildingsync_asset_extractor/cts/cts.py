
from pathlib import Path

import pandas as pd
from styleframe import StyleFrame

BLANK_CTS_FILE_PATH = Path(__file__).parent / "CTS Comprehensive Evaluation Upload Template_20240312_021125.xlsx"


def building_sync_to_cts(files: list[Path], out_file: Path) -> None:
    # import blank template
    df = pd.read_excel(BLANK_CTS_FILE_PATH, sheet_name="Evaluation Upload Template")

    # fill template
    data = pd.Series(index=df.index)
    data["Facility Name"] = "boo!"
    df.loc[3] = data

    # write back out
    sf = StyleFrame.read_excel_as_template(BLANK_CTS_FILE_PATH, df=df, sheet_name="Evaluation Upload Template")
    writer = sf.to_excel(out_file, row_to_add_filters=0)
    writer.close()
