
class UsedToPrepare:
    def __init__(self):
        self.utensils_to = {}
        self.utensils_in_sentence = {}

    def append_to_utensil_in_sentence(self, cv_utensil):
        assert(len(cv_utensil) > 0, "cv_utensil should be larger than 0")

        for utensil in cv_utensil:
            if utensil in self.utensils_in_sentence:
                self.utensils_in_sentence[utensil][0] += cv_utensil[utensil][0]
                self.utensils_in_sentence[utensil][1] += cv_utensil[utensil][1]
            else:
                self.utensils_in_sentence[utensil] = cv_utensil[utensil]

    # def append_data_to_utensils(self, verbs):
    #     for utensil in self.utensils_in_sentence:
    #

