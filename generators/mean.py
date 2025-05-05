# generators/mean.py
import random

class MeanProblemGenerator:
    def __init__(self, min_val=1, max_val=20, num_values=5):
        self.min_val = min_val
        self.max_val = max_val
        self.num_values = num_values

    def generate_problem(self):
        values = [random.randint(self.min_val, self.max_val) for _ in range(self.num_values)]
        mean = round(sum(values) / len(values), 2)

        question = f"Find the mean of the following numbers:\n{', '.join(map(str, values))}"
        answer = f"The mean is {mean}"

        return question, answer
