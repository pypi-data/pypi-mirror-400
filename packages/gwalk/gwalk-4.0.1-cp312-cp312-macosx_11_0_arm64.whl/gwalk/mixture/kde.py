#!/usr/env/bin python3
"""A fixed subclass of GaussianMixture for Kernel Density Estimation
"""
######## Imports ########
#### Standard Library ####
from os.path import join
import warnings
#### Third Party ####
import numpy as np
from scipy.special import logsumexp
#### Homemade ####
from xdata import Database
from basil_core.random.pcg64 import seed_parser
#### Local ####
## Decomposition
from gwalk.multivariate_normal.decomposition import cov_of_std_cor
from gwalk.multivariate_normal.decomposition import std_of_cov
from gwalk.multivariate_normal.decomposition import cor_of_cov
from gwalk.multivariate_normal.decomposition import cor_of_std_cov
from gwalk.multivariate_normal.decomposition import offset_of_params
from gwalk.multivariate_normal.decomposition import mu_of_params
from gwalk.multivariate_normal.decomposition import std_of_params
from gwalk.multivariate_normal.decomposition import cor_of_params
from gwalk.multivariate_normal.decomposition import cov_of_params
from gwalk.multivariate_normal.decomposition import mu_cov_of_params
from gwalk.multivariate_normal.decomposition import params_of_offset_mu_cov
from gwalk.multivariate_normal.decomposition import params_of_offset_mu_std_cor
from gwalk.multivariate_normal.decomposition import cov_rescale
from gwalk.multivariate_normal.decomposition import params_reduce
from gwalk.multivariate_normal.decomposition import params_of_mu_cov
from gwalk.multivariate_normal.decomposition import nparams_of_ndim
from gwalk.multivariate_normal.decomposition import ndim_of_nparams
## Object
from gwalk.multivariate_normal import MultivariateNormal
## Mixture
from gwalk.mixture.mixture import GaussianMixture
from gwalk.mixture.fixed import FixedGaussianMixture
######## Mixture base class ########
class KernelDensityEstimator(FixedGaussianMixture):
    """A Kernel Density Estimator

    The point of this one is that it's initialized differently
    """
    def __init__(
            self,
            mu,
            limits,
            std = None,
            cor = None,
            cov = None,
            weights = None,
            rule = "scott",
            factor = None,
            **kwargs
        ):
        """Initialize a new Kernel Density Estimator

        Parameters
        ----------
        mu : array_like
            sample locations
        limits : array_like
            limits for each dimension (ndim, 2)
        std : array_like
            Array of standard deviation values for each sample
        cor : array_like
            Correlation matrix for each sample
        cov : array_like
            Covariance matrix for each sample
        weights : array_like
            A list of all the component weights
        rule : str
            Method of construction for KDE
        factor : float
            Multiplication factor for automatic std
        **kwargs : dict
            Keyword Arguments for MultivariateNormal object
            (sig_max, scale_max, etc...)
        """
        ## Check inputs ##
        if not isinstance(mu, np.ndarray):
            raise ValueError(f"mu should be an ndarray")
        if (len(mu.shape) == 2) and (mu.shape[1] > mu.shape[0]):
            raise ValueError(f"Tried to build a KDE with more dimensions"
                "than samples!")
        # Check for overconstrained data
        if (cov is not None) and ((std is not None) or (cor is not None)):
            raise RuntimeError(f"Covariance is overconstrained")

        ## Setup ##
        if len(mu.shape) == 1:
            ndim = 1
            nsample = np.size(mu)
        else:
            nsample = mu.shape[0]
            ndim = mu.shape[1]
        # Reshape mu
        mu = mu.reshape((nsample,ndim))

        ## KDE methods ##
        # Check for minimum amount of information
        if (cov is None) and (std is None):
            # Get sample std
            std_samples = np.std(mu, axis=0)
            # Check rule
            if rule == "scott":
                std = np.power(nsample,-1./(ndim + 4)) * std_samples
                pass
            else:
                raise NotImplementedError(f"Unknown KDE rule: {rule}")
            # Check factor
            if factor is not None:
                std = std * factor

        ## Construct covariance ##
        # Reshape std
        if std is not None:
            if np.size(std) == ndim:
                std = np.tile(std.flatten(),(nsample,1))
            else:
                std = std.reshape((nsample,ndim))
        # Reshape cor
        if cor is not None:
            if np.size(cor) == ndim**2:
                cor = np.tile(cor.reshape(ndim,ndim),(nsample,1,1))
            else:
                cor = cor.reshape((nsample,ndim,ndim))
        else:
            cor = np.tile(np.eye(ndim),(nsample,1,1))
        # Reshape cov
        if cov is not None:
            if np.size(cov) == ndim**2:
                cov = np.tile(cov.reshape(ndim,ndim),(nsample,1,1))
            else:
                cov = cov.reshape((nsample,ndim,ndim))
        else:
            cov = cov_of_std_cor(std,cor)
        # Generate params
        params = params_of_mu_cov(mu,cov)

        ## Generate components ##
        components = []
        for i in np.arange(nsample):
            components.append(MultivariateNormal(
                params[i],
                limits=limits,
                **kwargs
            ))
        ## Initialize Mixture
        super().__init__(components, weights=weights)

    #### Management ####
    def append(*args, **kwargs):
        raise NotImplementedError(f"Cannot append {self.__class__}")

    @classmethod
    def from_data(
            cls,
            params,
            scale=None,
            limits=None,
            weights=None,
            **kwargs
        ):
        ## Check inputs
        ngauss, nparams = np.shape(params)
        ndim = ndim_of_nparams(nparams)
        # Check limits
        if len(limits.shape) == 3:
            # Initialize new limits
            _limits = np.empty((ndim,2))
            # Loop dimensions
            for i in np.arange(ndim):
                # Find the highest high
                _limits[i,1] = np.max(limits[:,i,1])
                # ... and the lowest low
                _limits[i,0] = np.min(limits[:,i,0])
            # "Correct" limits
            limits = _limits
        # Initialize new KDE
        return KernelDensityEstimator(
            mu_of_params(params),
            limits,
            cov=cov_of_params(params),
            weights=weights,
            **kwargs
        )



######## Testing ######## 
def test_kde():
    print("testing kde...")
    mu = np.asarray([
        [1.,0.],
        [0.,1.],
        [0.5,0.5],
    ])
    std = np.asarray([
        [0.1,0.1],
        [0.1,0.1],
        [0.1,0.1],
    ])
    # Set limits
    limits = np.asarray([
        [0.,8.],
        [-8.,8.],
    ])

    kde_obj_0 = KernelDensityEstimator(
        mu,
        limits,
    )

    # Test save / load
    kde_obj_0.save("test_kde.hdf5", "kde_obj_0")
    kde_obj_1 = KernelDensityEstimator.load("test_kde.hdf5", "kde_obj_0")
    assert kde_obj_0 == kde_obj_1
    print("  pass!")


def cli_tests():
    test_kde()
    return

######## Execution ########
if __name__ == "__main__":
    cli_tests()
