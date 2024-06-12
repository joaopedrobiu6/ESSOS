from ESSOS import CreateEquallySpacedCurves, Coils, Particles, optimize, loss, optimize_adam
from MagneticField import B_norm

import jax.numpy as jnp
import jax
from jax import grad

import matplotlib.pyplot as plt
from time import time

# Show on which platform JAX is running.
print("JAX running on", jax.devices()[0].platform.upper())

n_curves=3
order=3
r = 1.7
A = 6. # Aspect ratio
R = A*r

loss_r = r/5
maxtime = 1e-6
timesteps=200

particles = Particles(20)

curves = CreateEquallySpacedCurves(n_curves, order, R, r, nfp=4, stellsym=True)
stel = Coils(curves, jnp.array([1e7, 1e7, 1e7]))

initial_values = stel.initial_conditions(particles, R, loss_r)
initial_vperp = initial_values[4, :]

trajectories = stel.trace_trajectories(particles, initial_values, maxtime=maxtime, timesteps=timesteps, n_segments=100)
stel.order = 4

plt.figure()
for i in range(len(trajectories)):
    plt.plot(jnp.array(range(len(trajectories[0])))*maxtime/timesteps, trajectories[i, :, 3])
plt.title("Parallel Velocity")
plt.xlabel("time [s]")
plt.ylabel(r"parallel velocity [ms$^{-1}$]")
plt.savefig("examples/non_opt_v_par.png")

normB = jnp.apply_along_axis(B_norm, 0, initial_values[:3, :], stel.gamma(), stel.currents)
μ = particles.mass*initial_vperp**2/(2*normB)

plt.figure()
for i in range(len(trajectories)):
    normB = jnp.apply_along_axis(B_norm, 1, trajectories[i, :, :3], stel.gamma(), stel.currents)
    plt.plot(jnp.array(range(len(trajectories[0])))*maxtime/timesteps, (μ[i]*normB + 0.5*particles.mass*trajectories[i, :, 3]**2)/particles.energy)
plt.title("Energy Conservation")
plt.xlabel("time [s]")
plt.ylabel(r"$\frac{E}{E_\alpha}$")
plt.savefig("examples/non_opt_energy.png")

stel.plot(trajectories=trajectories, title="Initial Stellator", save_as="examples/non_opt_stellator.png", show=False)

############################################################################################################

start = time()
loss_value = loss(stel.dofs, stel.dofs_currents, stel, particles, R, initial_values, maxtime, timesteps, 100)
end = time()
print(f"Loss function initial value: {loss_value:.8f}")
print(f"Took: {end-start:.2f} seconds")

start = time()
loss_value = loss(stel.dofs, stel.dofs_currents, stel, particles, R, initial_values, maxtime, timesteps, 100)
end = time()
print(f"Compiled took: {end-start:.2f} seconds")

"""
start = time()
grad_loss_value = grad(loss, argnums=0)(stel.dofs, stel.dofs_currents, stel, 100, particles, maxtime, timesteps, R, loss_r)
end = time()
print(f"Grad loss function initial value: {grad_loss_value}")
print(f"Took: {end-start:.2f} seconds")

start = time()
grad_loss_value = grad(loss, argnums=0)(stel.dofs, stel.dofs_currents, stel, 100, particles, maxtime, timesteps, R, loss_r)
end = time()
print(f"Compiled took: {end-start:.2f} seconds")
"""

optimize(stel, particles, R, initial_values, maxtime=maxtime, timesteps=timesteps, n_segments=100)

curves_segments = stel.gamma()
trajectories = stel.trace_trajectories(particles, initial_values, maxtime=maxtime, timesteps=timesteps, n_segments=100)

plt.figure()
for i in range(len(trajectories)):
    plt.plot(jnp.array(range(len(trajectories[0])))*maxtime/timesteps, trajectories[i, :, 3])
plt.title("Parallel Velocity")
plt.xlabel("time [s]")
plt.ylabel(r"parallel velocity [ms$^{-1}$]")
plt.savefig("examples/opt_v_par.png")

normB = jnp.apply_along_axis(B_norm, 0, initial_values[:3, :], curves_segments, stel.currents)
μ = particles.mass*initial_vperp**2/(2*normB)

plt.figure()
for i in range(len(trajectories)):
    normB = jnp.apply_along_axis(B_norm, 1, trajectories[i, :, :3], curves_segments, stel.currents)
    plt.plot(jnp.array(range(len(trajectories[0])))*maxtime/timesteps, (μ[i]*normB + 0.5*particles.mass*trajectories[i, :, 3]**2)/particles.energy)
plt.title("Energy Conservation")
plt.xlabel("time [s]")
plt.ylabel(r"$\frac{E}{E_\alpha}$")
plt.savefig("examples/opt_energy.png")

stel.plot(show=True, trajectories=trajectories, title="Optimized Stellator", save_as="examples/opt_stellator.png")
