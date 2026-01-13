#!/usr/env/bin python3
"""A fixed subclass of GMM for caching more things
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
######## Mixture base class ########
class FixedGaussianMixture(GaussianMixture):
    """A Mixture of Gaussians"""
    def __init__(
            self,
            component_list,
            weights=None,
        ):
        """Initialize a new Gaussian Mixture

        Parameters
        ----------
        component_list : list
            A list of NAL MultivariateNormal objects
        weights : array_like
            A list of all the component weights
        """
        ## Check inputs ##
        if not hasattr(component_list, "__len__"):
            raise ValueError("GaussianMixture was not properly initialized"
                " with a list of NAL MultivariateNormal objects")
        if len(component_list) == 0:
            raise ValueError(f"Cannot initialize empty {self.__class__}!")
        # Check for empty components
        for component_index in range(len(component_list)):
            if not isinstance(
                component_list[component_index],
                MultivariateNormal,
            ):
                raise ValueError("GaussianMixture was not properly initialized"
                    " with a list of NAL MultivariateNormal objects")
        if weights is not None:
            weights = np.asarray(weights)
            if len(weights) != len(component_list):
                raise ValueError(
                    f"Weights have length {len(weights)}, "
                    f"but component_list has length {len(component_list)}")
        ## Assign components ##
        self._components = component_list
        self._weights = weights
        # normalize mixture
        self.normalize()
        # Cache things
        self._weights_normal = None
        self._params = None
        self._mu = None
        self._std = None
        self._cor = None
        self._cov = None
        self._limits = None

    #### Properties ####
    @property
    def components(self):
        return self._components

    @property
    def nsystems(self):
        return len(self.components)

    @property
    def ndim(self):
        return self.components[0].ndim

    @property
    def nparams(self):
        return self.components[0].nparams

    @property
    def weights(self):
        return self._weights

    @property
    def weights_normal(self):
        if self._weights_normal is None:
            self._weights_normal = super().weights_normal
        return self._weights_normal

    @property
    def mu(self):
        """The mu value for each Gaussian"""
        if self._mu is None:
            self._mu = super().mu
        return self._mu

    @property
    def std(self):
        """The std value for each Gaussian"""
        if self._std is None:
            self._std = super().std
        return self._std

    @property
    def cor(self):
        """The cor value for each Gaussian"""
        if self._cor is None:
            self._cor = super().cor
        return self._cor

    @property
    def cov(self):
        """The cov value for each Gaussian"""
        if self._cov is None:
            self._cov = super().cov
        return self._cov

    @property
    def limits(self):
        """The limits value for each Gaussian"""
        if self._limits is None:
            self._limits = super().limits
        return self._limits

    #### Management ####
    def append(*args, **kwargs):
        raise NotImplementedError(f"Cannot append {self.__class__}")


######## Testing ######## 
def test_fixed():
    print("testing fixed...")
    offset = np.asarray([0., 0., 0.5])
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
    cor = np.asarray([
        [
            [1.,0.],
            [0.,1.],
        ],
        [
            [1.,0.],
            [0.,1.],
        ],
        [
            [1.,0.],
            [0.,1.],
        ],
    ])
    params = params_of_offset_mu_std_cor(
        offset, mu, std, cor,
    )
    # Set limits
    limits = np.asarray([
        [0.,8.],
        [-8.,8.],
    ])
    A = MultivariateNormal(params[0],limits=limits)
    B = MultivariateNormal(params[1],limits=limits)
    C = MultivariateNormal(params[2],limits=limits)
    # Test construction
    ABC = FixedGaussianMixture([A,B,C])
    # Test params
    assert np.all(params == ABC.params)
    # Test mu
    assert np.all(mu == ABC.mu)
    # test std
    assert np.all(std == ABC.std)
    # Test cor
    assert np.all(cor == ABC.cor)
    # Test cov
    assert np.all(cov_of_std_cor(std,cor) == ABC.cov)
    # test pdf
    logpdf = logsumexp(np.log(ABC.likelihood(np.vstack((mu,mu)))),axis=0)
    logpdf_logsumexp = ABC(np.vstack((mu,mu)),log_scale=True)
    assert np.allclose(logpdf, logpdf_logsumexp)
    for i in range(len(mu)):
        mix_L = ABC.likelihood(np.vstack((mu,mu)),log_scale=True)[i]
        cmp_L = ABC.components[i].likelihood(np.vstack((mu,mu)),log_scale=True)
        goodness = np.exp(mix_L - cmp_L)/ABC.weights_normal[i]
        assert np.allclose(goodness, 1.)
    # Test copy
    abc = ABC.copy()
    # Test from_properties
    Abc = ABC.from_properties(
        mu,
        std=std, cor=cor, offset=offset,
        limits=limits,
    )
    # Make a non-equal copy
    BCA = FixedGaussianMixture([B,C,A])
    # Test Eq.

    assert ABC == abc
    assert abc == ABC
    assert ABC == Abc
    assert Abc == ABC
    assert Abc == abc
    assert abc == Abc
    assert not (ABC == BCA)
    assert not (BCA == ABC)
    assert ABC != BCA
    assert BCA != ABC

    # Test add
    AB = FixedGaussianMixture([A,B])
    BA = FixedGaussianMixture([B,A])
    ABBA = AB + BA
    assert ABBA == FixedGaussianMixture([A,B,B,A])

    # Test downsample
    assert AB == ABBA.downsample([0,2])

    # Test marginalize
    ABBA_1d = ABBA.marginalize([0])
    assert np.all(ABBA_1d.mu.flatten() == ABBA.mu[:,0].flatten())
    # Just see if it works
    vals = ABBA_1d(ABBA_1d.mu)

    # Test save / load
    ABBA.save("test_fixed.hdf5", "ABBA")
    abba = FixedGaussianMixture.load("test_fixed.hdf5", "ABBA")
    assert ABBA == abba
    print("  pass!")


def cli_tests():
    test_fixed()
    return

######## Execution ########
if __name__ == "__main__":
    cli_tests()
