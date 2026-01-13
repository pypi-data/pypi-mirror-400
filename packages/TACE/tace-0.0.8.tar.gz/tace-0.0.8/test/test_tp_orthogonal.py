import torch
from cartnn import o3

torch.set_printoptions(precision=4, sci_mode=False)
torch.manual_seed(5)
dtype = torch.set_default_dtype(torch.float64)

import torch
from e3nn import o3
from tqdm import tqdm
from typing import Tuple, List
def ICTD(n_total : int) -> Tuple[List[List[int]], List[torch.Tensor]]:
    n_now = 0
    j_now = 0
    path_list = []
    this_path = []
    this_pathmatrix = o3.wigner_3j(0,0,0)
    pathmatrices_list = []
    # generate paths and path matrices
    def paths_generate(n_now, j_now, this_path, this_pathmatrix, n_total):
        if n_now<=n_total:
            this_path.append(j_now)
            for j in [j_now + 1, j_now, j_now - 1]:
                if not (j_now==0 and (j!=1) ) and n_now+1<=n_total:
                    cgmatrix = o3.wigner_3j(1,j_now,j)
                    this_pathmatrix_ = torch.einsum("abc,dce->dabe",this_pathmatrix,cgmatrix)
                    this_pathmatrix_ = this_pathmatrix_.reshape(cgmatrix.shape[0],-1,cgmatrix.shape[-1])
                    paths_generate(n_now+1,j,this_path.copy(),this_pathmatrix_,n_total)
            if n_now == n_total:
                this_pathmatrix = this_pathmatrix.reshape(-1,this_pathmatrix.shape[-1])
                this_pathmatrix = this_pathmatrix*(1./(this_pathmatrix**2).sum(0)[0]**(0.5)) # normalize
                pathmatrices_list.append(this_pathmatrix)
                path_list.append(this_path)
        return     
    paths_generate(n_now, j_now, this_path, this_pathmatrix, n_total)
    decomp_list = []
    cart2sph_list = []
    for path_matrix in tqdm(pathmatrices_list):
            decomp_list.append(path_matrix@path_matrix.T)
            cart2sph_list.append(path_matrix)
    return path_list, decomp_list, cart2sph_list

L1 = 2
L2 = 2
L3 = L1 + L2

T1 = torch.randn(3**L1) @ ICTD(L1)[1][0]
T2 = torch.randn(3**L2) @ ICTD(L2)[1][0]
T = torch.outer(T1, T2).view(-1)


To_list = []
P1S, D1S, C1S = ICTD(L3)
for P1, D1, C1 in zip(P1S, D1S, C1S):
    To = T @ D1
    To_sph = T @ C1
    print(To_sph)
    To_list.append(To)


# G = torch.zeros(len(To_list), len(To_list))
# for i in range(len(To_list)):
#     for j in range(len(To_list)):
#         G[i, j] = torch.dot(To_list[i], To_list[j])
#         if i == j:
#             print(G[i, j])

mat = torch.stack(To_list)
rank = torch.linalg.matrix_rank(mat)
print(f"Number of linearly independent vectors: {rank}")



