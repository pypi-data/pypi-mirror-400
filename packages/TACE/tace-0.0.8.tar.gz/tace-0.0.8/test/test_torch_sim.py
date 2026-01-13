import sys
import torch
import torch_sim as ts
from tace.interface.torchsim import TACETorchSimCalc

# Structure
from ase.build import bulk
atoms = bulk("Cu", "fcc", a=3.58, cubic=True).repeat((2, 2, 2))
atomsList = [atoms] * 3

# TACETorchSimCalc
# model = sys.argv[1]
model = '/home/xuzemin/TACE-OAM-L-R-v1.ckpt'
dtype = torch.float32
device = torch.device("cuda")
torchSimModel = TACETorchSimCalc(model, dtype=dtype, device=device, compute_stress=False)


# run them all simultaneously with batching
trajectory_files = [f"Cu_traj_{i}.h5md" for i in range(len(atomsList))]
final_state = ts.integrate(
    system=atomsList,
    model=torchSimModel,
    n_steps=50,
    timestep=0.002,
    temperature=1000,
    integrator=ts.Integrator.nvt_langevin,
    trajectory_reporter=dict(filenames=trajectory_files, state_frequency=10),
)
final_atoms_list = final_state.to_atoms()

# extract the final energy from the trajectory file
final_energies = []
for filename in trajectory_files:
    with ts.TorchSimTrajectory(filename) as traj:
        final_energies.append(traj.get_array("potential_energy")[-1])

print(final_energies)