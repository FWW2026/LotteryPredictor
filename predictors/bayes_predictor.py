from collections import Counter

from predictors.base_predictor import BasePredictor


class BayesPredictor(BasePredictor):

    name = "Bayes"

    def predict(self, data):

        alpha = 1

        counter = Counter(data)

        universe = set(data)

        total = sum(counter.values())

        k = len(universe)

        result = {}

        for item in universe:

            result[item] = (
                counter[item] + alpha
            ) / (
                total + alpha * k
            )

        return result