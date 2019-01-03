import itertools
import numpy as np
from PIL import Image
import math

def show_heatmap(board):
    n = len(board)
    m = len(board[0])
    max_score = 0
    min_score = math.inf
    for i,j in itertools.product(range(n),range(m)):
        max_score = max(board[i][j],max_score)
        min_score = min(board[i][j],min_score)

    data = np.zeros((n, m, 3), dtype=np.uint8)
    for i, j in itertools.product(range(n), range(m)):
        data[i, j] = [255 * (1 - (board[i][j]-min_score) / (max_score-min_score)), 0, 255 * ((board[i][j] - min_score) / (max_score-min_score))]
    img = Image.fromarray(data, 'RGB')
    img.show()
