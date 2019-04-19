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
        unknown_prefix = 1/len_lexicon
        known_prefix_defaults = {}
        known_prefix_token = {}
        for prefix in total:
            known_prefix_defaults[prefix] = 1/(total[prefix]+len_lexicon)
            known_prefix_token[prefix] = {}
            for tok in ngram_counts[prefix]:
                known_prefix_token[prefix][tok] = (ngram_counts[prefix][tok]+1)/(total[prefix]+len_lexicon)

        def get_prob(prefix,tok):
            if prefix not in known_prefix_defaults:
                return unknown_prefix
            if tok in known_prefix_token[prefix]:
                return known_prefix_token[prefix][tok]
            return known_prefix_defaults[prefix]
        return unknown_prefix,known_prefix_defaults,known_prefix_token
    else:
        print("ERROR: UNKNOWN smoothing type")


class LanguageModel():
    def __init__(self, sentences, n=2, padded=True, variable_func_uniform=False):
        self.n = n
        self.padded = padded
        self.default,self.prefix_defaults,self.grams = get_ngram_model(sentences, n, padded=padded)
        self.variable_func_uniform = variable_func_uniform
        self.log_default = log(self.default)
        self.log_prefix_defaults = {}
        self.log_grams = {}
        for prefix,default in self.prefix_defaults.items():
            self.log_prefix_defaults[prefix] = log(default)
            self.log_grams[prefix] = {}
            for tok,prob in self.grams[prefix].items():
                self.log_grams[prefix][tok] = log(prob)

    def get_prob(self,prefix,tok):
        if prefix not in self.prefix_defaults:
            return self.default
        if tok in self.grams[prefix]:
            return self.grams[prefix][tok]
        return self.prefix_defaults[prefix]

    def get_log_prob(self,prefix,tok):
        if prefix not in self.log_prefix_defaults:
            return self.log_default
        if tok in self.log_grams[prefix]:
            return self.log_grams[prefix][tok]
        return self.log_prefix_defaults[prefix]

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
            prob_sentance *= self.get_prob(tuple(prefix), tok)
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
            prob_sentence += self.get_log_prob(tuple(prefix), tok)
            if n>1:
                prefix.pop(0)
            prefix.append(tok)
        return prob_sentence


    def get_probability_next_phrase(self,current_toks,next_phrase):
        prefix = tuple(["<s>"] * (self.n - 1 - len(current_toks)) + current_toks[1-self.n:])
        product_prob = 1
        for i,tok in enumerate(next_phrase):
            prob = self.get_prob(prefix, tok)
            product_prob *= prob
            prefix = tuple(prefix[1:]+tuple([tok]))
        return product_prob

    def get_log_prob_next_phrase(self, current_toks, next_phrase):
        prefix = tuple(["<s>"] * (self.n - 1 - len(current_toks)) + current_toks[1-self.n:])
        # log(1) = 0
        log_prob = 0
        for i,tok in enumerate(next_phrase):
            log_prob += self.get_log_prob(prefix, tok)
            prefix = tuple(prefix[1:]+tuple([tok]))
        return log_prob

def train_lang_model(sentance_pairs,n):
    return LanguageModel([p for _,p in sentance_pairs],n)


if __name__ == "__main__":

    def equal_to5dp(val1,val2):
        return round(val1,5) == round(val2,5)

    s1 = "I am Sam".split(" ")
    s2 = "Sam I am".split(" ")
    s3 = "I do not like green eggs and ham".split(" ")

    sentances_test = [s1, s2, s3]
    model = LanguageModel(sentances_test, n=2)
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
    print(equal_to5dp(model.get_log_prob_next_phrase(["Sam", "I"], ["am"]), log(0.23076923076923078)))
    print(equal_to5dp(model.get_log_prob_next_phrase(["Sam", "I"], ["not"]), log(0.07692307692307693)))

    # print(model.get_probability_next_phrase(["Sam", "I"],["am"]))
    # print(log(0.23076923076923078))

