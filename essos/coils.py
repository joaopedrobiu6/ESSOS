import jax.numpy as jnp
from jax.lax import select, fori_loop
from jax import tree_util, vmap
from .plot import fix_matplotlib_3d

class Curves:
    """
    Class to store the curves

    -----------
    Attributes:
        dofs (jnp.ndarray - shape (n_indcurves, 3, 2*order+1)): Fourier Coefficients of the independent curves
        n_segments (int): Number of segments to discretize the curves
        nfp (int): Number of field periods
        stellsym (bool): Stellarator symmetry
        order (int): Order of the Fourier series
        curves jnp.ndarray - shape (n_indcurves*nfp*(1+stellsym), 3, 2*order+1)): Curves obtained by applying rotations and flipping corresponding to nfp fold rotational symmetry and optionally stellarator symmetry
        gamma (jnp.array - shape (n_coils, n_segments, 3)): Discretized curves
        gamma_dash (jnp.array - shape (n_coils, n_segments, 3)): Discretized curves derivatives

    """
    def __init__(self, dofs: jnp.ndarray, n_segments: int = 100, nfp: int = 1, stellsym: bool = True):
        assert isinstance(dofs, jnp.ndarray), "dofs must be a jnp.ndarray"
        assert dofs.ndim == 3, "dofs must be a 3D array with shape (n_curves, 3, 2*order+1)"
        assert dofs.shape[1] == 3, "dofs must have shape (n_curves, 3, 2*order+1)"
        assert dofs.shape[2] % 2 == 1, "dofs must have shape (n_curves, 3, 2*order+1)"
        assert isinstance(n_segments, int), "n_segments must be an integer"
        assert n_segments > 2, "n_segments must be greater than 2"
        assert isinstance(nfp, int), "nfp must be a positive integer"
        assert nfp > 0, "nfp must be a positive integer"
        assert isinstance(stellsym, bool), "stellsym must be a boolean"
    
        self._dofs = dofs
        self._n_segments = n_segments
        self._nfp = nfp
        self._stellsym = stellsym
        self._order = dofs.shape[2]//2
        self._curves = apply_symmetries_to_curves(self.dofs, self.nfp, self.stellsym)
        self._set_gamma()

    def __str__(self):
        return f"nfp stellsym order\n{self.nfp} {self.stellsym} {self.order}\n"\
             + f"Degrees of freedom\n{repr(self.dofs.tolist())}\n"
                
    def __repr__(self):
        return f"nfp stellsym order\n{self.nfp} {self.stellsym} {self.order}\n"\
             + f"Degrees of freedom\n{repr(self.dofs.tolist())}\n"

    def _tree_flatten(self):
        children = (self._dofs,)  # arrays / dynamic values
        aux_data = {"n_segments": self._n_segments, "nfp": self._nfp, "stellsym": self._stellsym}  # static values
        return (children, aux_data)

    @classmethod
    def _tree_unflatten(cls, aux_data, children):
        return cls(*children, **aux_data)
    
    def _set_gamma(self):
        """ Initializes the discritized curves and their derivatives"""

        # Create the quadpoints
        quadpoints = jnp.linspace(0, 1, self.n_segments, endpoint=False)
                        
        # Create the gamma and gamma_dash
        def fori_createdata(order_index: int, data: jnp.ndarray) -> jnp.ndarray:
            return data[0] + jnp.einsum("ij,k->ikj", self._curves[:, :, 2 * order_index - 1], jnp.sin(2 * jnp.pi * order_index * quadpoints)) + jnp.einsum("ij,k->ikj", self._curves[:, :, 2 * order_index], jnp.cos(2 * jnp.pi * order_index * quadpoints)), \
                   data[1] + jnp.einsum("ij,k->ikj", self._curves[:, :, 2 * order_index - 1], 2*jnp.pi*order_index*jnp.cos(2 * jnp.pi * order_index * quadpoints)) + jnp.einsum("ij,k->ikj", self._curves[:, :, 2 * order_index], -2*jnp.pi*order_index*jnp.sin(2 * jnp.pi * order_index * quadpoints))
        
        gamma = jnp.einsum("ij,k->ikj", self._curves[:, :, 0], jnp.ones(self.n_segments))
        gamma_dash = jnp.zeros((jnp.size(self._curves, 0), self.n_segments, 3))
        gamma, gamma_dash = fori_loop(1, self._order+1, fori_createdata, (gamma, gamma_dash)) 
        
        length = jnp.array([jnp.mean(jnp.linalg.norm(d1gamma, axis=1)) for d1gamma in gamma_dash])

        # Set the attributes
        self._gamma = gamma
        self._gamma_dash = gamma_dash
        self._length = length
    
    @property
    def dofs(self):
        return self._dofs
    
    @dofs.setter
    def dofs(self, new_dofs):
        assert isinstance(new_dofs, jnp.ndarray)
        assert new_dofs.ndim == 3
        assert jnp.size(new_dofs, 1) == 3
        assert jnp.size(new_dofs, 2) % 2 == 1
        self._dofs = new_dofs
        self._order = jnp.size(new_dofs, 2)//2
        self._curves = apply_symmetries_to_curves(self.dofs, self.nfp, self.stellsym)
        self._set_gamma()
    
    @property
    def curves(self):
        return self._curves
    
    @property 
    def order(self):
        return self._order
    
    @order.setter
    def order(self, new_order):
        assert isinstance(new_order, int)
        assert new_order > 0
        self._dofs = jnp.pad(self.dofs, ((0, 0), (0, 0), (0, 2*(new_order-self._order)))) if new_order > self._order else self.dofs[:, :, :2*(new_order)+1]
        self._order = new_order
        self._curves = apply_symmetries_to_curves(self.dofs, self.nfp, self.stellsym)
        self._set_gamma()

    @property
    def n_segments(self):
        return self._n_segments
    
    @n_segments.setter
    def n_segments(self, new_n_segments):
        assert isinstance(new_n_segments, int)
        assert new_n_segments > 2
        self._n_segments = new_n_segments
        self._set_gamma()
    
    @property
    def nfp(self):
        return self._nfp
    
    @nfp.setter
    def nfp(self, new_nfp):
        assert isinstance(new_nfp, int)
        assert new_nfp > 0
        self._nfp = new_nfp
        self._curves = apply_symmetries_to_curves(self.dofs, self.nfp, self.stellsym)
        self._set_gamma()
    
    @property
    def stellsym(self):
        return self._stellsym
    
    @stellsym.setter
    def stellsym(self, new_stellsym):
        assert isinstance(new_stellsym, bool)
        self._stellsym = new_stellsym
        self._curves = apply_symmetries_to_curves(self.dofs, self.nfp, self.stellsym)
        self._set_gamma()
    
    @property
    def gamma(self):
        return self._gamma
    
    @property
    def gamma_dash(self):
        return self._gamma_dash
    
    @property
    def length(self):
        return self._length
    
    def save_curves(self, filename: str):
        """
        Save the curves to a file
        """
        with open(filename, "a") as file:
            file.write(f"nfp stellsym order\n")
            file.write(f"{self.nfp} {self.stellsym} {self.order}\n")
            file.write(f"Degrees of freedom\n")
            file.write(f"{repr(self.dofs.tolist())}\n")
            
    def to_simsopt(self):
        from simsopt.geo import CurveXYZFourier
        curves_simsopt = []
        for dofs in self.dofs:
            curve = CurveXYZFourier(self.n_segments, self.order)
            curve.x = jnp.reshape(dofs, (curve.x.shape))
            curves_simsopt.append(curve)
        return curves_simsopt
    
    def plot(self, ax=None, show=True, plot_derivative=False, close=False, axis_equal=True, **kwargs):
        def rep(data):
            if close:
                return jnp.concatenate((data, [data[0]]))
            else:
                return data

        import matplotlib.pyplot as plt 
        if ax is None or ax.name != "3d":
            fig = plt.figure()
            ax = fig.add_subplot(projection='3d')
        for gamma, gammadash in zip(self.gamma, self.gamma_dash):
            x = rep(gamma[:, 0])
            y = rep(gamma[:, 1])
            z = rep(gamma[:, 2])
            if plot_derivative:
                xt = rep(gammadash[:, 0])
                yt = rep(gammadash[:, 1])
                zt = rep(gammadash[:, 2])
            ax.plot(x, y, z, **kwargs, color='green', linestyle='dashed', linewidth=2)
            if plot_derivative:
                ax.quiver(x, y, z, 0.1 * xt, 0.1 * yt, 0.1 * zt, arrow_length_ratio=0.1, color="r")
        if axis_equal:
            fix_matplotlib_3d(ax)
        if show:
            plt.show()
    
class Curves_from_simsopt(Curves):
    def __init__(self, simsopt_curves, nfp=1, stellsym=True):
        dofs = jnp.reshape(jnp.array(
            [curve.x for curve in simsopt_curves]
        ), (len(simsopt_curves), 3, 2*simsopt_curves[0].order+1))
        n_segments = len(simsopt_curves[0].quadpoints)
        super().__init__(dofs, n_segments, nfp, stellsym)

tree_util.register_pytree_node(Curves,
                               Curves._tree_flatten,
                               Curves._tree_unflatten)

class Coils(Curves):
    def __init__(self, curves: Curves, dofs_currents: jnp.ndarray):
        assert isinstance(curves, Curves)
        assert isinstance(dofs_currents, jnp.ndarray)
        assert jnp.size(dofs_currents) == jnp.size(curves.dofs, 0)
        super().__init__(curves.dofs, curves.n_segments, curves.nfp, curves.stellsym)
        self._dofs_currents = dofs_currents
        self._currents = apply_symmetries_to_currents(self._dofs_currents, self.nfp, self.stellsym)

    def __str__(self):
        return f"nfp stellsym order\n{self.nfp} {self.stellsym} {self.order}\n"\
             + f"Degrees of freedom\n{repr(self.dofs.tolist())}\n" \
             + f"Currents degrees of freedom\n{repr(self.dofs_currents.tolist())}\n"
                
    def __repr__(self):
        return f"nfp stellsym order\n{self.nfp} {self.stellsym} {self.order}\n"\
             + f"Degrees of freedom\n{repr(self.dofs.tolist())}\n" \
             + f"Currents degrees of freedom\n{repr(self.dofs_currents.tolist())}\n"
    
    @property
    def dofs_currents(self):
        return self._dofs_currents
    
    @dofs_currents.setter
    def dofs_currents(self, new_dofs_currents):
        self._dofs_currents = new_dofs_currents
        self._currents = apply_symmetries_to_currents(self._dofs_currents, self.nfp, self.stellsym)
    
    @property
    def currents(self):
        return self._currents
    
    def _tree_flatten(self):
        children = (Curves(self.dofs, self.n_segments, self.nfp, self.stellsym), self._dofs_currents)  # arrays / dynamic values
        aux_data = {}  # static values
        return (children, aux_data)

    def save_coils(self, filename: str, text=""):
        """
        Save the coils to a file
        """
        with open(filename, "a") as file:
            file.write(f"nfp stellsym order\n")
            file.write(f"{self.nfp} {self.stellsym} {self.order}\n")
            file.write(f"Degrees of freedom\n")
            file.write(f"{repr(self.dofs.tolist())}\n")
            file.write(f"Currents degrees of freedom\n")
            file.write(f"{repr(self._dofs_currents.tolist())}\n")
            # file.write(f"Loss\n")
            file.write(f"{text}\n")
    
    def to_simsopt(self):
        from simsopt.field import Coil as Coil_SIMSOPT, Current as Current_SIMSOPT, coils_via_symmetries
        from simsopt.geo import CurveXYZFourier
        cuves_simsopt = []
        currents_simsopt = []
        for dofs, current in zip(self.dofs, self.dofs_currents):
            curve = CurveXYZFourier(self.n_segments, self.order)
            curve.x = jnp.reshape(dofs, (curve.x.shape))
            cuves_simsopt.append(curve)
            currents_simsopt.append(Current_SIMSOPT(current))
        return coils_via_symmetries(cuves_simsopt, currents_simsopt, self.nfp, self.stellsym)

class Coils_from_simsopt(Coils):
    def __init__(self, simsopt_coils, nfp=1, stellsym=True):
        curves = [c.curve for c in simsopt_coils]
        currents = jnp.array([c.current.get_value() for c in simsopt_coils])
        super().__init__(Curves_from_simsopt(curves, nfp, stellsym), currents)

tree_util.register_pytree_node(Coils,
                               Coils._tree_flatten,
                               Coils._tree_unflatten)


def CreateEquallySpacedCurves(n_curves: int,
                              order: int,
                              R: float,
                              r: float,
                              n_segments: int = 100,
                              nfp: int = 1,
                              stellsym: bool = False) -> jnp.ndarray:
    # Compute angles for all curves at once
    angles = (jnp.arange(n_curves) + 0.5) * (2 * jnp.pi) / ((1 + int(stellsym)) * nfp * n_curves)

    # Initialize curves array
    curves = jnp.zeros((n_curves, 3, 1 + 2 * order))

    # Compute x, y, and z components efficiently
    curves = curves.at[:, 0, 0].set(jnp.cos(angles) * R)  # x[0]
    curves = curves.at[:, 0, 2].set(jnp.cos(angles) * r)  # x[2]
    curves = curves.at[:, 1, 0].set(jnp.sin(angles) * R)  # y[0]
    curves = curves.at[:, 1, 2].set(jnp.sin(angles) * r)  # y[2]
    curves = curves.at[:, 2, 1].set(-r)                   # z[1] (constant for all)

    return Curves(curves, n_segments=n_segments, nfp=nfp, stellsym=stellsym)

def apply_symmetries_to_curves(base_curves, nfp, stellsym):
    flip_matrix = jnp.array([[1, 0, 0],
                             [0, -1, 0],
                             [0, 0, -1]])
    if stellsym:
        flipped_curves = jnp.einsum("aic,ib->abc", base_curves, flip_matrix)
        curves = jnp.concatenate([base_curves, flipped_curves], axis=0)
    else:
        curves = base_curves
    angles = jnp.linspace(0, 2 * jnp.pi * (nfp - 1) / nfp, nfp)[1:]
    rotation_matrices = jnp.stack([
        jnp.stack([jnp.cos(angles), -jnp.sin(angles), jnp.zeros_like(angles)], axis=-1),
        jnp.stack([jnp.sin(angles), jnp.cos(angles), jnp.zeros_like(angles)], axis=-1),
        jnp.stack([jnp.zeros_like(angles), jnp.zeros_like(angles), jnp.ones_like(angles)], axis=-1)
    ], axis=-2)
    rotated_curves = vmap(lambda R: jnp.einsum("aic,ib->abc", base_curves, R))(rotation_matrices)
    rotated_curves = rotated_curves.reshape(-1, *base_curves.shape[1:])
    if stellsym:
        flipped_rotated_curves = jnp.einsum("aic,ib->abc", rotated_curves, flip_matrix)
        rotated_curves = jnp.concatenate([flipped_rotated_curves, rotated_curves], axis=0)
    old_rotated_curves = rotated_curves
    for i in range(len(base_curves)):
        rotated_curves = rotated_curves.at[i].set(old_rotated_curves[-len(base_curves)+i])
        rotated_curves = rotated_curves.at[-len(base_curves)+i].set(old_rotated_curves[i])
    curves = jnp.concatenate([curves, rotated_curves], axis=0)
    return curves

def apply_symmetries_to_currents(base_currents, nfp, stellsym): 
    # flip_list = jnp.array([1, -1]) if stellsym else jnp.array([1])  # 1 for no flip, -1 for flip
    # flips = jnp.repeat(flip_list, nfp)  # Repeat for each field period
    # currents = jnp.tile(base_currents, len(flips)) * flips[:, None]  # Apply flips
    # return currents

    flip_list = [False, True] if stellsym else [False]
    currents = []
    for k in range(0, nfp):
        for flip in flip_list:
            for i in range(len(base_currents)):
                current = -base_currents[i] if flip else base_currents[i]
                currents.append(current)
    return jnp.array(currents)