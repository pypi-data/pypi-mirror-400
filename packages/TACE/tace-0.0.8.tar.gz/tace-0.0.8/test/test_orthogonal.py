import torch
from cartnn import o3

torch.set_printoptions(precision=1, sci_mode=False)
torch.manual_seed(3)
dtype = torch.set_default_dtype(torch.float64)


L = 3
T = torch.randn(3**L)

To_list = []
P1S, D1S, C1S, S1S = o3.ICTD(L)
for P1, D1, C1 in zip(P1S, D1S, C1S):
    To = T @ D1
    To_list.append(To)


G = torch.zeros(len(To_list), len(To_list))
for i in range(len(To_list)):
    for j in range(len(To_list)):
        print(i, j)
        G[i, j] = torch.dot(To_list[i], To_list[j])

print(G)

