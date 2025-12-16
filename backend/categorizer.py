import json

class PromptCategorizer:
    def __init__(self, example_prompts_file):
        with open(example_prompts_file, "r") as f:
            self.example_prompts = json.load(f)

    def categorize(self, user_prompt):
        matched_techniques = []
        for item in self.example_prompts:
            if any(word.lower() in user_prompt.lower() for word in item["prompt"].split()):
                matched_techniques.extend(item["techniques"])
        return list(set(matched_techniques))
