import math

from collections import defaultdict

from predictors.base_predictor import BasePredictor


class ExpPredictor(BasePredictor):

    name = "ExpWeighted"

    def predict(self, data):

        score = defaultdict(float)

        n = len(data)

        for i, value in enumerate(data):

            weight = math.exp(
                -(i / n)
            )

            score[value] += weight

        total = sum(score.values())

        return {
            k: v / total
            for k, v in score.items()
        }