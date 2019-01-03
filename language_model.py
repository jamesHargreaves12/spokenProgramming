from nltk import ngrams,FreqDist
from collections import defaultdict


def get_ngram_model(sentances, n, smoothing_type="LAPLACE", padded=False):
    '''returns a function (prefix,tok) -> p(tok|prefix)'''
    ngram_counts = defaultdict(lambda :defaultdict(int))
    total = defaultdict(int)
    lexicon = set()
    for sentance in sentances:
        tokens = [x.strip("\n") for x in sentance.split(" ") if x != ""]
        lexicon.update(tokens)
        if padded:
            tokens = ["<s>"] + tokens + ["<\s>"]
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


def get_prob_sentance(ngrams_prob, n, sentance):
    if len(sentance) < n:
        print("Issue sentance to short")
        return

    prefix = sentance[0:n-1]
    prob_sentance = 1
    for tok in sentance[n-1:]:
        # print(tuple(prefix),tok,ngrams_prob(tuple(prefix),tok))
        prob_sentance *= ngrams_prob(tuple(prefix),tok)
        prefix.pop(0)
        prefix.append(tok)
    return prob_sentance


if __name__ == "__main__":
    s1 = "<s> I am Sam </s>"
    s2 = "<s> Sam I am </s>"
    s3 = "<s> I do not like green eggs and ham </s>"

    sentances = [s1,s2,s3]
    for N in range(2,5):
        model = get_ngram_model(sentances,N)
        print(get_prob_sentance(model,N,s1.split(" ")))
        print(get_prob_sentance(model,N,s2.split(" ")))
        print(get_prob_sentance(model,N,s3.split(" ")))
        print()