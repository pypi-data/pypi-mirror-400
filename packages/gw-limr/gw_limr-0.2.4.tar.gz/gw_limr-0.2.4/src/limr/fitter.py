import jax
import jax.numpy as jnp
from functools import partial
from tinygp import kernels, transforms, GaussianProcess
import jaxopt
import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler



class TinyGPModel:
    def __init__(self, kernel_fn=None, standardise_X=False, standardise_y=False):
        """
        Initialize the TinyGPModel.

        Parameters
        ----------
        kernel_fn : callable or None
            A function that takes `params` as input and returns a tinygp kernel.
            If None, a default ExpSquared kernel is used.
        standardise_X : bool
            If True, apply sklearn's StandardScaler to X.
        standardise_y : bool
            If True, apply sklearn's StandardScaler to y.
        """
        self.kernel_fn = kernel_fn
        self.standardise_X = standardise_X
        self.standardise_y = standardise_y
        self.is_fitted = False

        self.X_scaler = None
        self.y_scaler = None

    # ============================================================
    # FIT
    # ============================================================
    def fit(self, X_train, y_train, params=None, log_diag=None):
        """Fit the GP model to training data.
        If log_diag given then this is a fixed parameter and is not
        optimised over. 
        """
        self.log_diag = log_diag
        X_train = np.asarray(X_train)
        y_train = np.asarray(y_train)

        # Standardize if requested
        if self.standardise_X:
            self.X_scaler = StandardScaler().fit(X_train)
            X_train = self.X_scaler.transform(X_train)
        if self.standardise_y:
            self.y_scaler = StandardScaler().fit(y_train.reshape(-1, 1))
            y_train = self.y_scaler.transform(y_train.reshape(-1, 1))[:,0]

        self.n_dim = X_train.shape[1]
        func = partial(self.build_gp, X_train=X_train)
        
        # Default parameter initialization
        if params is None:
            params = {
                "log_amp": 1.0,
                "log_scale": np.ones(self.n_dim),
            }
            if self.log_diag is None:
                params['log_diag'] = 0.1
        elif 'log_diag' in params and self.log_diag is not None:
            raise ValueError(f"user has supplied {self.log_diag = } in both the params dict and as an input. Only one is allowed.")

        @jax.jit
        def loss(params):
            return -func(params)[0].log_probability(y_train)

        solver = jaxopt.ScipyMinimize(fun=loss)
        soln = solver.run(params)

        self.gp, self.best_params = func(soln.params)
        self.X_train = X_train
        self.y_train = y_train
        self.is_fitted = True

        return self

    # ============================================================
    # BUILD GP
    # ============================================================
    def build_gp(self, params, X_train):
        """Build a tinygp GaussianProcess given kernel parameters and data."""
        if self.kernel_fn is not None:
            kernel = self.kernel_fn(params)
        else:
            kernel = jnp.exp(params["log_amp"]) * transforms.Linear(
                jnp.exp(-params["log_scale"]), kernels.ExpSquared()
            )

        if self.log_diag is None:
            return GaussianProcess(kernel, X_train, diag=jnp.exp(params["log_diag"])), params
        else:
            return GaussianProcess(kernel, X_train, diag=jnp.exp(self.log_diag)), params

    # ============================================================
    # PREDICT & SAMPLE
    # ============================================================
    def predict(self, X_test, return_std=False):
        """Compute predictive mean and (optionally) standard deviation for new test inputs."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before calling predict().")
    
        X_test = np.asarray(X_test)
        if self.standardise_X:
            X_test = self.X_scaler.transform(X_test)
    
        # Compute GP conditional distribution
        gp_cond = self.gp.condition(self.y_train, X_test).gp
        mean = np.array(gp_cond.loc)
        var = np.array(gp_cond.variance)
    
        # Undo standardization
        if self.standardise_y:
            mean = self.y_scaler.inverse_transform(mean.reshape(-1, 1))[:, 0]
            var = var * (self.y_scaler.scale_[0] ** 2)
    
        if return_std:
            std = np.sqrt(var)
            return mean, std
        else:
            return mean


    def sample(self, X_test, n_samples, prngkey=None):
        """Draw samples from the predictive distribution.
        output shape of samples is (X_test.shape[0], n_samples)"""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before calling sample().")

        if prngkey is None:
            prngkey = np.random.randint(100000)
        
        X_test = np.asarray(X_test)
        if self.standardise_X:
            X_test = self.X_scaler.transform(X_test)

        gp_cond = self.gp.condition(self.y_train, X_test).gp
        samples = np.array(gp_cond.sample(jax.random.PRNGKey(prngkey), (n_samples,))).T
        
        # Undo standardization
        if self.standardise_y:
            samples = self.y_scaler.inverse_transform(samples.reshape(-1, 1)).reshape(samples.shape)

        return samples

    # ============================================================
    # SAVE & LOAD
    # ============================================================
    def save(self, path):
        """Save the fitted model to a file."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before saving.")

        data = {
            "best_params": self.best_params,
            'log_diag': self.log_diag,
            "X_train": self.X_train,
            "y_train": self.y_train,
            "kernel_fn": self.kernel_fn,
            "standardise_X": self.standardise_X,
            "standardise_y": self.standardise_y,
            "X_scaler": self.X_scaler,
            "y_scaler": self.y_scaler,
        }
        with open(path, "wb") as f:
            pickle.dump(data, f)

    @classmethod
    def load(cls, path):
        """Load a previously fitted model from a file."""
        with open(path, "rb") as f:
            data = pickle.load(f)

        model = cls(
            kernel_fn=data["kernel_fn"],
            standardise_X=data["standardise_X"],
            standardise_y=data["standardise_y"],
        )
        model.best_params = data["best_params"]
        if 'log_diag' in data:
            model.log_diag = data["log_diag"]
        else:
            model.log_diag = None
        model.X_train = data["X_train"]
        model.y_train = data["y_train"]
        model.X_scaler = data["X_scaler"]
        model.y_scaler = data["y_scaler"]
        model.gp, _ = model.build_gp(model.best_params, model.X_train)
        model.is_fitted = True

        return model