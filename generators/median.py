# generators/median.py

import random

class MedianProblemGenerator:
    def __init__(self, min_val=1, max_val=20, num_values=7):
        self.min_val = min_val
        self.max_val = max_val
        self.num_values = num_values

    def generate_problem(self):
        values = sorted([random.randint(self.min_val, self.max_val) for _ in range(self.num_values)])
        mid = self.num_values // 2
        if self.num_values % 2 == 1:
            median = values[mid]
        else:
            median = (values[mid - 1] + values[mid]) / 2

        question = f"Find the median of the following numbers:\n{', '.join(map(str, values))}"
        answer = f"The median is {median}"

        return question, answer
