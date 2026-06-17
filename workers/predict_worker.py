from concurrent.futures import ThreadPoolExecutor

from PySide6.QtCore import (
    QThread,
    Signal
)

from utils.feature_extractor import (
    extract_last_numbers,
    extract_last_zodiac
)

from predictors.frequency_predictor import (
    FrequencyPredictor
)

from predictors.exp_predictor import (
    ExpPredictor
)

from predictors.bayes_predictor import (
    BayesPredictor
)

from predictors.markov_predictor import (
    MarkovPredictor
)


class PredictWorker(QThread):

    finished = Signal(dict)

    def __init__(
        self,
        records,
        history_size
    ):
        super().__init__()

        self.records = records
        self.history_size = history_size

    def run(self):

        records = self.records[
            :self.history_size
        ]

        number_data = (
            extract_last_numbers(
                records
            )
        )

        zodiac_data = (
            extract_last_zodiac(
                records
            )
        )

        predictors = [

            FrequencyPredictor(),

            ExpPredictor(),

            BayesPredictor(),

            MarkovPredictor()
        ]

        result = {}

        def execute(p):

            return (
                p.name,
                {
                    "number":
                    p.predict(
                        number_data
                    ),

                    "zodiac":
                    p.predict(
                        zodiac_data
                    )
                }
            )

        with ThreadPoolExecutor(
            max_workers=4
        ) as pool:

            futures = [
                pool.submit(
                    execute,
                    p
                )
                for p in predictors
            ]

            for f in futures:

                name, data = (
                    f.result()
                )

                result[name] = data

        self.finished.emit(
            result
        )