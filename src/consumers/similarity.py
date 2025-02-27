import numpy as np
from scipy.sparse import csr_matrix
from scipy.spatial.distance import cosine

def compute_sparse_vector_similarity(features1, features2):
    print('features1=',features1)
    print('features2=',features2)

   
    size = max(int(features1['size']), int(features2[0]))


    vec1 = csr_matrix((np.array(features1['values'], dtype=float),
                       (np.zeros(len(features1['indices'])), np.array(features1['indices'], dtype=int))), shape=(1, size))
    vec2 = csr_matrix((np.array(features2[2], dtype=float),
                       (np.zeros(len(features2[1])), np.array(features2[1], dtype=int))), shape=(1, size))


    similarity = 1 - cosine(vec1.toarray().flatten(), vec2.toarray().flatten())
    return similarity

def look_for_similarity(current_features,old_features,threshold=0.8):
    max_similarity=-2
    for features in old_features:
        similarity=compute_sparse_vector_similarity(current_features,features)
        if similarity>max_similarity:
            max_similarity=similarity
    return max_similarity