import json

class BestPracticesRetriever:
    def __init__(self, file_path):
        with open(file_path, "r") as f:
            self.best_practices = json.load(f)

    def get_best_practices(self, techniques):
        return {tech: self.best_practices.get(tech, "No practice found") for tech in techniques}
5

# import json

# class BestPractices:
#     def __init__(self):
#         self.data = json.load(open("data/best_practices.json"))

#     def get(self, techniques):
#         return {t: self.data[t] for t in techniques}
