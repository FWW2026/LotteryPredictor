import pandas as pd


def export_records(records, filename):

    df = pd.DataFrame(records)

    df.to_excel(
        filename,
        index=False
    )