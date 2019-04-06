from nltk import ngrams,FreqDist
from collections import defaultdict
from math import log
def get_ngram_model(sentances, n, smoothing_type="LAPLACE", padded=False):
    '''returns a function (prefix,tok) -> p(tok|prefix)'''
    ngram_counts = defaultdict(lambda :defaultdict(int))
    total = defaultdict(int)
    lexicon = set()
    for sentance in sentances:
        tokens = [x.strip("\n") for x in sentance if x != ""]
        lexicon.update(tokens)
        if padded:
            tokens = ["<s>"]*(n-1) + tokens + ["<\s>"]
        for gram,count in FreqDist(ngrams(tokens,n)).items():
            prefix = gram[0:-1]
            ngram_counts[prefix][gram[-1]] += count
            total[gram[0:-1]] += count
    if smoothing_type == "LAPLACE":
        len_lexicon = len(lexicon)
        def get_prob(prefix,tok):
            if prefix not in total.keys():
                return 1/len_lexicon
            else:
                if tok not in ngram_counts[prefix].keys():
                    return 1/(total[prefix]+len_lexicon)
                else:
                    return (ngram_counts[prefix][tok]+1)/(total[prefix]+len_lexicon)
        return get_prob
    else:
        print("ERROR: UNKNOWN smoothing type")


class LanguageModel():
    def __init__(self, sentances, n=2, padded=True):
        self.n_grams = get_ngram_model(sentances, n, padded=padded)
        self.n = n
        self.padded = padded

    def get_prob_sentance(self, sentence, padded_left=True, padded_right=True):
        """
        :param n: int ngram size if not set then uses pref_n
        :param sentence: List of string tokens
        :param padded_left: boolean
        :param padded_right: boolean
        :return: float
        """
        n = self.n
        if padded_left:
            sentence = ["<s>"] * (n-1) + sentence
        if padded_right:
            sentence += ["</s>"]

        if len(sentence) < n:
            print("Issue sentance to short")
            return 1

        prefix = sentence[0:n - 1]
        prob_sentance = 1
        for tok in sentence[n - 1:]:
            prob_sentance *= self.n_grams(tuple(prefix), tok)
            if n>1:
                prefix.pop(0)
            prefix.append(tok)
        return prob_sentance


    def get_log_prob_sentance(self, sentence, padded_left=True, padded_right=True):
        """
        :param n: int ngram size if not set then uses pref_n
        :param sentence: List of string tokens
        :param padded_left: boolean
        :param padded_right: boolean
        :return: float
        """
        n = self.n
        if padded_left:
            sentence = ["<s>"] * (n-1) + sentence
        if padded_right:
            sentence += ["</s>"]

        if len(sentence) < n:
            print("Issue sentance to short")
            return 0

        prefix = sentence[0:n - 1]
        # log(1) = 0
        prob_sentence = 0
        for tok in sentence[n - 1:]:
            prob_sentence += log(self.n_grams(tuple(prefix), tok))
            if n>1:
                prefix.pop(0)
            prefix.append(tok)
        return prob_sentence


    def get_probability_next_phrase(self,current_toks,next_phrase):
        prefix = tuple(["<s>"] * (self.n - 1 - len(current_toks)) + current_toks[1-self.n:])
        product_prob = 1
        for i,tok in enumerate(next_phrase):
            prob = self.n_grams(prefix, tok)
            product_prob *= prob
            prefix = tuple(prefix[1:]+tuple([tok]))
        return product_prob

    def get_log_probability_next_phrase(self,current_toks,next_phrase):
        prefix = tuple(["<s>"] * (self.n - 1 - len(current_toks)) + current_toks[1-self.n:])
        # log(1) = 0
        log_prob = 0
        for i,tok in enumerate(next_phrase):
            prob = self.n_grams(prefix, tok)
            log_prob += log(prob)
            prefix = tuple(prefix[1:]+tuple([tok]))
        return log_prob

if __name__ == "__main__":

    def equal_to5dp(val1,val2):
        return round(val1,5) == round(val2,5)

    s1 = "I am Sam".split(" ")
    s2 = "Sam I am".split(" ")
    s3 = "I do not like green eggs and ham".split(" ")

    sentances = [s1,s2,s3]
    model = LanguageModel(sentances, n=2)
    print(model.get_prob_sentance(s1) == 0.0007396449704142012)
    print(model.get_prob_sentance(s2) == 0.0004930966469428007)
    print(model.get_prob_sentance(s3) == 1.1659924106543872e-07)
    print()
    print(model.get_probability_next_phrase(["Sam", "I"],["am"]) == 0.23076923076923078)
    print(model.get_probability_next_phrase(["Sam", "I"],["not"]) == 0.07692307692307693)
    print()
    print(equal_to5dp(model.get_log_prob_sentance(s1), log(0.0007396449704142012)))
    print(equal_to5dp(model.get_log_prob_sentance(s2), log(0.0004930966469428007)))
    print(equal_to5dp(model.get_log_prob_sentance(s3), log(1.1659924106543872e-07)))
    print()
    print(equal_to5dp(model.get_log_probability_next_phrase(["Sam", "I"],["am"]), log(0.23076923076923078)))
    print(equal_to5dp(model.get_log_probability_next_phrase(["Sam", "I"],["not"]), log(0.07692307692307693)))

    # print(model.get_probability_next_phrase(["Sam", "I"],["am"]))
    # print(log(0.23076923076923078))

