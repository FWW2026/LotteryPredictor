import pandas as pd

from datetime import datetime


def export_prediction(
    result,
    history_size
):

    filename = (
        f"Prediction_"
        f"{history_size}_"
        f"{datetime.now():%Y%m%d_%H%M}"
        f".xlsx"
    )

    with pd.ExcelWriter(
        filename
    ) as writer:

        for method, data in (
            result.items()
        ):

            number_df = pd.DataFrame(
                list(
                    data["number"].items()
                ),
                columns=[
                    "Number",
                    "Probability"
                ]
            )

            zodiac_df = pd.DataFrame(
                list(
                    data["zodiac"].items()
                ),
                columns=[
                    "Zodiac",
                    "Probability"
                ]
            )

            number_df.to_excel(
                writer,
                sheet_name=
                method+"_Number",
                index=False
            )

            zodiac_df.to_excel(
                writer,
                sheet_name=
                method+"_Zodiac",
                index=False
            )

    return filename