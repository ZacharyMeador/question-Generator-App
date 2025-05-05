# generators/base.py

class ProblemGenerator:
    def __init__(self):
        pass

    def generate_problem(self):
        raise NotImplementedError("Subclasses must implement this method")
