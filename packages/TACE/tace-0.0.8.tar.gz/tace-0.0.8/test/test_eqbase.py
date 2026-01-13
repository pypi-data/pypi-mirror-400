from cartnn.o3._ictd import general_equivariant_basis_generator



space_1 = {"space":[[1,2],[1,3]],"parity":-1}
space_2 = {"space":[[1,3]],"parity":-1}

AS, BS = general_equivariant_basis_generator(space_1, space_2)


for A, B in zip(AS, BS):
    print(A)
    print(B.shape)