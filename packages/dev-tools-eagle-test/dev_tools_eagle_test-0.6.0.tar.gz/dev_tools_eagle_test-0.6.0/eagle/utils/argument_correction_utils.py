# imports
from Levenshtein import distance as levenshtein_distance

# auxiliar functions
def find_most_similar(candidate: str, possible_choices: list) -> str:

    most_similar = None
    most_similar_distance = 999999
    for choice in possible_choices:
        distance = levenshtein_distance(candidate, choice)
        if distance < most_similar_distance:
            most_similar = choice
            most_similar_distance = distance
    return most_similar

# Classes
class ArgumentCorrector:

    def __init__(self, right_to_wrong_dict):
        self.right_to_wrong_dict = right_to_wrong_dict
        
        # Wrong to right dict creation
        self.wrong_to_right_dict = {}
        for right, wrong_list in right_to_wrong_dict.items():
            self.wrong_to_right_dict[right] = right
            for wrong in wrong_list:
                self.wrong_to_right_dict[wrong] = right

    def find_right(self, wrong: str) -> str:
        
        # Find, among the wrongs from wrong_to_right_dict, the most similar to the wrong argument in terms of Levenshtein distance
        most_similar = find_most_similar(wrong, list(self.wrong_to_right_dict.keys()))
        right = self.wrong_to_right_dict.get(most_similar, wrong)
        return right
