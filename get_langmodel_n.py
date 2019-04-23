from _decimal import Decimal

from tools.get_test_data import validation_set, train_test_data
from langModel.faster_lang_model import LanguageModel
from smt import smt_functions
import matplotlib.pyplot as plt


def compute_perplexity_of_sentance(pseud_sentance, lang_model: LanguageModel, n):
    perplexity = lang_model.get_prob_sentance(pseud_sentance) ** (1.0 / n)
    return perplexity


def compute_perplexity():
    results = []
    for _, p in validation_set:
        result_for_p = []
        for n in range(1, 7):
            lang_model = smt_functions.get_language_model(train_test_data, n)
            total = 0
            N = len(p)
            pp = Decimal(compute_perplexity_of_sentance(p, lang_model, N))
            result_for_p.append(pp)
        results.append(result_for_p)
    for i, res in enumerate(results):
        plt.plot([x for x in range(1, 7)], res)
    plt.xlabel('n')
    plt.ylabel('Perplexity of the sentence')
    plt.title('Perplexity of language model on different values of n')
    plt.show()
    for n in range(1, 7):
        data = [res[n - 1] for res in results]
        print(n, sum(data) / len(data))


compute_perplexity()
