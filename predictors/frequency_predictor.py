from collections import Counter

from predictors.base_predictor import BasePredictor


class FrequencyPredictor(BasePredictor):

    name = "Frequency"

    def predict(self, data):

        counter = Counter(data)

        total = sum(counter.values())

        result = {}

        for k, v in counter.items():

            result[k] = v / total

        return result