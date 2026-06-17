from collections import defaultdict

from predictors.base_predictor import BasePredictor


class MarkovPredictor(BasePredictor):

    name = "Markov"

    def predict(self, data):

        if len(data) < 2:

            return {}

        current = data[0]

        transition = defaultdict(int)

        for i in range(
            len(data)-1
        ):

            if data[i] == current:

                transition[
                    data[i+1]
                ] += 1

        total = sum(
            transition.values()
        )

        if total == 0:

            return {}

        return {
            k: v / total
            for k, v in transition.items()
        }