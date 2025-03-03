import os
import jax.numpy as jnp
import matplotlib.pyplot as plt
from essos.fields import BiotSavart
from essos.coils import Coils_from_simsopt
from essos.dynamics import Tracing

# Input parameters
tmax = 150
nparticles = 5
R0 = jnp.linspace(1.23, 1.27, nparticles)
trace_tolerance = 1e-7
num_steps = 1500

# Load coils and field
json_file = os.path.join(os.path.dirname(__file__), '..', 'tests', 'input_files', 'biot_savart_LandremanPaulQA.json')
coils = Coils_from_simsopt(json_file, nfp=2)
field = BiotSavart(coils)

# Initialize particles
Z0 = jnp.zeros(nparticles)
phi0 = jnp.zeros(nparticles)
initial_xyz=jnp.array([R0*jnp.cos(phi0), R0*jnp.sin(phi0), Z0]).T

# Trace in ESSOS
tracing = Tracing(field=field, model='FieldLine', initial_conditions=initial_xyz,
                  maxtime=tmax, timesteps=num_steps, tol_step_size=trace_tolerance)
trajectories_ESSOS = tracing.trajectories

# Plot trajectories
fig = plt.figure(figsize=(9, 5))
ax1 = fig.add_subplot(121, projection='3d')
ax2 = fig.add_subplot(122)

coils.plot(ax=ax1, show=False)
tracing.plot(ax=ax1, show=False)

for i, trajectory in enumerate(trajectories_ESSOS):
    ax2.plot(jnp.sqrt(trajectory[:,0]**2+trajectory[:,1]**2), trajectory[:, 2], label=f'Fieldline {i+1}')
ax2.set_xlabel('R (m)')
ax2.set_ylabel('Z (m)')
ax2.legend()
plt.tight_layout()
plt.show()