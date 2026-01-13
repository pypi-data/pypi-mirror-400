#!/usr/env/bin python3
"""An object for managing mixtures of Gaussians (truncated)

Decision: FixedGaussianMixture will be a subclass with lots of caching

Decision: We're going to create a new mixture when we marginalize
    or downselect rather than modifying this one
"""
######## Imports ########
#### Standard Library ####
from os.path import join
import warnings
import time
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
from gwalk.multivariate_normal.pdf import maha, U_of_cov
from gwalk.multivariate_normal.pdf import maha_of_mu_cov_sample
from gwalk.multivariate_normal.pdf import mixture_pdf
######## Mixture base class ########
class GaussianMixture(object):
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
        ## Assign ndim ##
        self._ndim = None
        self._nparams = None
        # normalize mixture
        self.normalize()

    #### Properties ####
    @property
    def components(self):
        return self._components

    @property
    def nsystems(self):
        return len(self.components)

    @property
    def ndim(self):
        if (self._ndim is not None) and (self.nsystems == 0):
            return self._ndim
        else:
            self._ndim = self.components[0].ndim
            return self._ndim

    @property
    def nparams(self):
        if (self._nparams is not None) and (self.nsystems == 0):
            return self._nparams
        else:
            self._nparams = self.components[0].nparams
            return self._nparams

    @property
    def weights(self):
        return self._weights

    @weights.setter
    def weights(self, value):
        if (value is not None) and (not isinstance(value, np.ndarray)):
            raise ValueError(f"weights should be NoneType or ndarray")
        if np.any(value < 0):
            raise ValueError(f"weights should be positive semi-definite.")
        self._weights = value

    @property
    def weights_normal(self):
        if self.weights is None:
            return np.full(self.nsystems,1./self.nsystems)
        else:
            return self.weights / np.sum(self.weights)

    @property
    def params(self):
        """The params value for each Gaussian"""
        # Handle empty components
        if self.nsystems == 0:
            return np.asarray([])
        # Initialize output array
        _params = np.empty((self.nsystems,self.nparams),dtype=float)
        # Loop components
        for component_index in range(self.nsystems):
            _params[component_index] = self.components[component_index].params
        return _params

    @property
    def offset(self):
        """The log pdf of the normalization constant
        
        returns
        -------
        offset : np.ndarray
            PDF offset (E.g. normalization for truncated Gaussian)

        This one needs to be handled separately from params
            for caching reasons in the FixedGaussianMixture
        """
        # Handle empty components
        if self.nsystems == 0:
            return np.asarray([])
        # Initialize output array
        _offset = np.empty(self.nsystems,dtype=float)
        # Loop components
        for i in range(self.nsystems):
            _offset[i] = self.components[i].offset
        return _offset

    @property
    def mu(self):
        """The mu value for each Gaussian"""
        # Handle empty components
        if self.nsystems == 0:
            return np.asarray([])
        return mu_of_params(self.params)

    @property
    def std(self):
        """The std value for each Gaussian"""
        # Handle empty components
        if self.nsystems == 0:
            return np.asarray([])
        return std_of_params(self.params)

    @property
    def cor(self):
        """The cor value for each Gaussian"""
        # Handle empty components
        if self.nsystems == 0:
            return np.asarray([])
        return cor_of_params(self.params)

    @property
    def cov(self):
        """The cov value for each Gaussian"""
        # Handle empty components
        if self.nsystems == 0:
            return np.asarray([])
        return cov_of_params(self.params)


    @property
    def scale(self):
        """The scale value for each Gaussian"""
        # Handle empty components
        if self.nsystems == 0:
            return np.asarray([])
        # Initialize output array
        _scale = np.empty((self.nsystems,self.ndim),dtype=float)
        # Loop components
        for component_index in range(self.nsystems):
            _scale[component_index] = \
                self.components[component_index].scale
        return _scale

    @property
    def limits(self):
        """The limits value for each Gaussian"""
        # Handle empty components
        if self.nsystems == 0:
            return np.asarray([])
        # Initialize output array
        _limits = np.empty((self.nsystems,self.ndim,2),dtype=float)
        # Loop components
        for component_index in range(self.nsystems):
            _limits[component_index] = \
                self.components[component_index].limits
        return _limits

    @property
    def plimits(self):
        """The plimits value for each Gaussian"""
        # Handle empty components
        if self.nsystems == 0:
            return np.asarray([])
        # Initialize output array
        _plimits = np.empty((self.nsystems,self.nparams,2),dtype=float)
        # Loop components
        for component_index in range(self.nsystems):
            _plimits[component_index] = \
                self.components[component_index].plimits
        return plimits

    @property
    def data(self):
        """Fully constrained by params, scale, limits, and weights"""
        return self.params, self.scale, self.limits, self.weights


    #### Management ####
    @staticmethod
    def combine_data(
        params1, scale1, limits1, weights1,
        params2, scale2, limits2, weights2,
        ):
        """Combine the data to fully constrain a mixture"""
        ## Check inputs ##
        if not len(np.shape(params1)) > 1:
            raise ValueError(f"params1 should be shape (ngauss1,nparams1)"
                f" but has shape {np.shape(params1)}")
        if not len(np.shape(scale1)) > 1:
            raise ValueError(f"scale1 should be shape (ngauss1,ndim1)"
                f" but has shape {np.shape(scale1)}")
        if not len(np.shape(limits1)) > 1:
            raise ValueError(f"limits1 should be shape (ngauss1,ndim1,2)"
                f" but has shape {np.shape(limits1)}")
        if (weights1 is not None) and (not len(weights1.shape) > 1):
            raise ValueError(f"weights1 should be shape (ngauss1,)"
                f" but has shape {np.shape(weights1)}")
        if not len(np.shape(params2)) > 1:
            raise ValueError(f"params2 should be shape (ngauss2,nparams2)"
                f" but has shape {np.shape(params2)}")
        if not len(np.shape(scale2)) > 1:
            raise ValueError(f"scale2 should be shape (ngauss2,ndim2)"
                f" but has shape {np.shape(scale2)}")
        if not len(np.shape(limits2)) > 1:
            raise ValueError(f"limits2 should be shape (ngauss2,ndim2,2)"
                f" but has shape {np.shape(limits2)}")
        if (weights2 is not None) and (not len(weights2.shape) > 1):
            raise ValueError(f"weights2 should be shape (ngauss1,)"
                f" but has shape {np.shape(weights2)}")
        # Get shape quantities
        ngauss1, nparams1 = np.shape(params1)
        ngauss2, nparams2 = np.shape(params2)
        ndim1, ndim2 = ndim_of_nparams(nparams1), ndim_of_nparams(nparams2)
        # Check self-consistency of dimensions
        if not np.all(list(np.shape(scale1)) == np.asarray([ngauss1,ndim1])):
            raise ValueError(f"scale1 should be shape ({ngauss1},{ndim1})"
                f" but has shape {np.shape(scale1)}")
        if not np.all(list(np.shape(scale2)) == np.asarray([ngauss2,ndim2])):
            raise ValueError(f"scale2 should be shape ({ngauss2},{ndim2})"
                f" but has shape {np.shape(scale2)}")
        if not np.all(list(np.shape(limits1)) == \
                np.asarray([ngauss1,ndim1,2])):
            raise ValueError(f"limits1 should be shape ({ngauss1},{ndim1},2)"
                f" but has shape {np.shape(limits1)}")
        if not np.all(list(np.shape(limits2)) == \
                np.asarray([ngauss2,ndim2,2])):
            raise ValueError(f"limits2 should be shape ({ngauss2},{ndim2},2)"
                f" but has shape {np.shape(limits2)}")
        # Check cross-consistency of dimensions
        if nparams1 != nparams2:
            raise ValueError(f"Cannot combine mixtures with "
                f"different dimensions ({ndim1} and {ndim2})")
        
        ## Concatenate arrays ##
        ngauss = ngauss1 + ngauss2
        # params
        params = np.empty((ngauss,nparams1),dtype=float)
        params[:ngauss1] = params1
        params[ngauss1:] = params2
        # scale
        scale = np.empty((ngauss,ndim1),dtype=float)
        scale[:ngauss1] = scale1
        scale[ngauss1:] = scale2
        # Limits
        limits = np.empty((ngauss,ndim1,2),dtype=float)
        limits[:ngauss1] = limits1
        limits[ngauss1:] = limits2
        # Weights
        if (weights1 is None) and (weights2 is None):
            weights = None
        elif (weights1 is None) or (weights2 is None):
            raise ValueError(f"weights1 is type {type(weights1)}, but "
                f"weights2 is type {type(weights2)}!")
        else:
            weights = np.concatenate((weights1, weights2))
            if weights.shape[0] != ngauss:
                raise RuntimeError(f"Vera's math is wrong!")
        return params, scale, limits, weights

    def extend_data(
            self,
            new_params,
            new_scale,
            new_limits,
            new_weights,
        ):
        """Create a new params, limit, scale, etc... array for extended mixture"""
        return GaussianMixture.combine_data(
            self.params,
            self.scale,
            self.limits,
            self.weights,
            new_params,
            new_scale,
            new_limits,
            new_weights,
        )

    @classmethod
    def from_data(
            cls,
            params,
            scale=None,
            limits=None,
            weights=None,
            **kwargs
        ):
        """Generate from parameters"""
        ## Check inputs
        ngauss, nparams = np.shape(params)
        ndim = ndim_of_nparams(nparams)
        if scale is not None:
            if len(scale.shape) == 1:
                _scale = np.empty((ngauss,ndim),dtype=float)
                _scale[:,None] = scale
                print(scale)
                scale = _scale
                print(scale)
                raise RuntimeError(f"This block of code has never "
                    "been executed before. Please check that its inputs "
                    "and outputs make sense!")
            elif (len(scale.shape) != 2) or (scale.shape[0] != ngauss) or \
                    (scale.shape[1] != ndim):
                raise ValueError("scale should have shape "
                    f"{ngauss},{ndim}, but has shape {np.shape(scale)}")
        if limits is not None:
            if len(limits.shape) == 2 and (limits.shape[0] == ndim) and \
                (limits.shape[1] == 2):
                _limits = np.empty((ngauss,ndim,2),dtype=float)
                _limits[:,...] = limits
                limits = _limits
            if (len(limits.shape) != 3) or (limits.shape[0] != ngauss) or \
                    (limits.shape[1] != ndim):
                raise ValueError("scale should have shape "
                    f"{ngauss},{ndim}, but has shape {np.shape(scale)}")

        ## Construct objects
        # Initialize list of components
        cmpts = []
        # Loop components
        for cmpt_index in np.arange(ngauss):
            # Case 1: scale and limits are None
            if (scale is None) and (limits is None):
                cmpts.append(MultivariateNormal(
                    params[cmpt_index],
                    **kwargs
                ))
            elif limits is None:
                # Case 2: limits is None
                cmpts.append(MultivariateNormal(
                    params[cmpt_index],
                    scale=scale[cmpt_index],
                    **kwargs
                ))
            elif scale is None:
                # Case 3: scale is None
                cmpts.append(MultivariateNormal(
                    params[cmpt_index],
                    limits=limits[cmpt_index],
                    **kwargs
                ))
            else:
                # Case 4: All is specified
                cmpts.append(MultivariateNormal(
                    params[cmpt_index],
                    scale=scale[cmpt_index],
                    limits=limits[cmpt_index],
                    **kwargs
                ))

        # Return Mixture
        return cls(cmpts, weights=weights)

    @classmethod
    def from_properties(
            cls,
            mu,
            std=None,
            cor=None,
            cov=None,
            offset=None,
            **kwargs,
        ):
        """Construct from properties
        """
        ## Check inputs
        if not len(np.shape(mu)) == 2:
            raise ValueError(f"mu should have shape (ngauss, ndim) "
                f"but has shape {np.shape(mu)}!")
        # Load info
        ngauss, ndim = np.shape(mu)
        # Check for minimum amount of information
        if (cov is None) and (std is None):
            raise ValueError("Need some information about sigmas")
        # Check for overconstrained data
        if (not (cov is None)) and ((not (std is None)) or (not cor is None)):
            raise ValueError("Covariance is overconstrained!")

        ## Construct covariance
        if cov is None:
            # Case 1: Cor is None
            if cor is None:
                _cor = np.empty((ngauss,ndim,ndim),dtype=float)
                _cor[:,...] = np.diag(np.ones(ndim))
                print(_cor)
                cor = _cor
                print(cor)
                raise RuntimeError(f"This block of code has never "
                    "been executed before. Please check that its inputs "
                    "and outputs make sense!")
            # Case 2: cor is given
            else:
                # Check shape of cor
                if (len(np.shape(cor)) == 2) and \
                        (cor.shape[0] == ndim) and (cor.shape[1] == ndim):
                    _cor = np.empty((ngauss,ndim,ndim),dtype=float)
                    _cor[:,...] = cor
                    print(cor)
                    cor = _cor
                    print(cor)
                    raise RuntimeError(f"This block of code has never "
                        "been executed before. Please check that its inputs "
                        "and outputs make sense!")
                elif (len(np.shape(cor)) ==3) and (cor.shape[0] == ngauss) and\
                        (cor.shape[1] == ndim) and (cor.shape[2] == ndim):
                    pass
                else:
                    raise ValueError("cor should have shape "
                        f"({ngauss},{ndim},{ndim}), but has shape "
                        f"{np.shape(cor)}")

            # std should always be given; check shape
            if (len(np.shape(std)) == 1) and \
                    (std.shape[0] == ndim):
                # Initialize new std
                _std = np.empty((ngauss,ndim),dtype=float)
                _std[:,...] = std
                print(std)
                std = _std
                print(std)
                raise RuntimeError(f"This block of code has never "
                    "been executed before. Please check that its inputs "
                    "and outputs make sense!")
            elif (len(np.shape(std)) == 2) and \
                    (std.shape[0] == ngauss) and (std.shape[1] == ndim):
                # Great!
                pass
            else:
                raise ValueError("std should have shape "
                    f"({ngauss},{ndim}), but has shape {np.shape(std)}!")

            # Make cov from std and cor
            cov = cov_of_std_cor(std,cor)
        else:
            # Check shape of cov
            if (len(np.shape(cov)) == 2) and \
                    (cov.shape[0] == ndim) and (cov.shape[1] == ndim):
                _cov = np.empty((ngauss,ndim,ndim),dtype=float)
                _cov[:,...] = cov
                print(cov)
                cov = _cov
                print(cov)
                raise RuntimeError(f"This block of code has never "
                    "been executed before. Please check that its inputs "
                    "and outputs make sense!")
            elif (len(np.shape(cov)) ==3) and (cov.shape[0] == ngauss) and \
                    (cov.shape[1] == ndim) and (cov.shape[2] == ndim):
                pass
            else:
                raise ValueError("cov should have shape "
                    f"({ngauss},{ndim},{ndim}), but has shape "
                    f"{np.shape(cov)}")

        ## Get params ##
        if offset is None:
            params = params_of_mu_cov(mu,cov)
        else:
            params = params_of_offset_mu_cov(offset,mu,cov)
        ## Get mixture!
        return cls.from_data(params,**kwargs)

    def append(
            self, 
            new_params, 
            new_scale=None,
            new_limits=None,
            new_weights=None,
        ):
        """Add more components to Mixture"""
        # Load self.data
        cur_params, cur_scale, cur_limits, cur_weights = self.data
        # Check new_param dimensions
        ngauss_new, nparams_new = np.shape(new_params)
        ndim_new = ndim_of_nparams(nparams_new)
        # check scale
        if len(np.shape(new_scale)) == 1:
            _new_scale = np.empty((ngauss_new,ndim_new),dtype=float)
            _new_scale[:,...] = new_scale
            new_scale =_new_scale
        # Check limits
        if len(np.shape(new_limits)) == 2:
            _new_limits = np.empty((ngauss_new,ndim_new,2),dtype=float)
            _new_limits[:,...] = new_limits
            new_limits = _new_limits
        # Concatenate new and old
        params, scale, limits, weights = self.extend_data(
            new_params,
            new_scale,
            new_limits,
            new_weights,
        )
        # Return new instance
        return self.__class__.from_data(
            params,
            scale=scale,
            limits=limits,
            weights=weights,
            sig_max=self.components[0].sig_max,
            scale_max=self.components[0].scale_max,
        )

    def copy(self):
        """Make a copy of the mixture that we can mutate"""
        # Check weights
        if self.weights is None:
            new_weights = None
        else: new_weights = self.weights.copy()
        # Create new object
        new = self.__class__.from_data(
            self.params.copy(),
            scale=self.scale.copy(),
            limits=self.limits.copy(),
            weights=new_weights,
        )
        for i in range(self.nsystems):
            new.components[i].sig_max = self.components[i].sig_max
            new.components[i].scale_max = self.components[i].scale_max
        return new

    def save(self, fname, addr, separate=False):
        """Save to a database"""
        # Create the database pointer
        db = Database(fname)
        # Create the group
        if not db.exists(addr):
            db.create_group(addr)
        # Method 1: Separate
        if separate:
            # Name pad
            pad = int(np.log10(self.nsystems)) + 1
            # Loop the gaussians
            for i, component in enumerate(self.components):
                component_tag = join(addr, f"nal_{i:0{pad}d}")
                component.save(
                    fname,
                    component_tag,
                )
        # Method 2: Together
        else:
            db.dset_set(join(addr,"params"),self.params)
            db.dset_set(join(addr,"scale"),self.scale)
            db.dset_set(join(addr,"limits"),self.limits)
        # Save the weights
        if self.weights is not None:
            db.dset_set(join(addr,"weights"),self.weights)

    @classmethod
    def load(cls, fname, addr):
        """Load from a database"""
        # Create the database pointer
        db = Database(fname)
        # Get the list of tags
        tags = db.list_items(addr)

        # Load the weights
        if db.exists(join(addr,"weights")):
            weights = db.dset_value(join(addr,"weights"))
        else:
            weights = None
        
        # Case 1: Together
        if ("params" in tags) and ("scale" in tags) and ("limits" in tags):
            params = db.dset_value(join(addr,"params"))         
            scale = db.dset_value(join(addr,"scale"))         
            limits = db.dset_value(join(addr,"limits"))         
            return cls.from_data(
                params,
                scale=scale,
                limits=limits,
                weights=weights,
            )
        # Case 2: Separate
        else:
            # Initialize list of components
            components = []
            # Sort the tags
            tags.sort()
            # Loop the tags
            for tag in tags:
                if tag.startswith("nal_"):
                    components.append(MultivariateNormal.load(
                        fname,
                        join(addr,tag),
                    ))
            # Initialize object
            return cls(components,weights=weights)

    #### General Methods ####
    def inflate_covariance(
            self, 
            std=None,
            rule=None,
            factor=None,
        ):
        ## setup std
        # Case 0: bad inputs
        if (std is None) and (rule is None) and (factor is None):
            raise ValueError("inflate_covariance requires std, method, or"
                " factor.")
        # Case 1: construct std array
        elif std is None:
            # Get std of samples
            std_mix = np.std(self.mu, axis=0)
            # Check rule
            if (rule is None):
                std = std_mix * factor
            else:
                std = np.power(
                    self.nsystems,
                    -1./(self.ndim + 4)
                ) * std_mix
                # Check factor
                if factor is not None:
                    std = std * factor
        # Case 2: std given
        else:
            # Check rule and factor
            if (rule is not None) or (factor is not None):
                raise ValueError("rule and factor arguments are invalid "
                    "when std is provided")
        ## Loop Gaussians
        for i in range(self.nsystems):
            # Get object std
            _std = self.components[i].std
            # Loop dimensions
            for j in range(self.ndim):
                # Check value
                if _std[j] < std[j]:
                    _std[j] = std[j]
            # Get sig_max
            sig_max = self.components[i].sig_max
            # Get plims
            plims = self.components[i].plimits
            # Change plimits
            plims[self.ndim + 1:2*self.ndim + 1, 1] = _std*sig_max
            # Update plimits
            self._components[i].plimits = plims
            # Set std
            self._components[i].std = _std

    def marginalize(self, indices):
        """Downselect parameters
        """
        return self.__class__.from_data(
            params_reduce(self.params,indices),
            scale=self.scale[:,indices],
            limits=self.limits[:,indices],
            weights=self.weights,
            sig_max=self.components[0].sig_max,
            scale_max=self.components[0].scale_max,
        )

    def downsample(self, indices):
        """Downselect components"""
        # Check weights
        if self.weights is None:
            new_weights = None
        else:
            new_weights = self.weights[indices]
        # Return new object
        return self.__class__.from_data(
            self.params[indices],
            scale=self.scale[indices],
            limits=self.limits[indices],
            weights=new_weights,
            sig_max=self.components[0].sig_max,
            scale_max=self.components[0].scale_max,
        )

    def normalize(self):
        """Normalize each Gaussain"""
        for i in np.arange(self.nsystems):
            self.components[i].normalize()

    def sigma_to_closest(self, sample):
        """Find how many sigma some samples are from the closest component"""
        return np.min(
            maha_of_mu_cov_sample(
                self.mu,
                self.cov,
                sample,
            ),
            axis=0,
        )

    def likelihood(self, samples, log_scale=False, **kwargs):
        """Evaluate PDF

        Parameters
        ----------
        samples : array_like
            Input of MultivariateNormal object parameters (ngauss, nparams)
        """
        # Handle empty components
        if self.nsystems == 0:
            return np.asarray([])
        # Call MultivariateNormal.likelihood
        pdf = self.components[0].likelihood(
            samples,
            X=self.params,
            scale=self.scale,
            limits=self.limits,
            offset=self.offset,
            log_scale=log_scale,
            **kwargs
        )
        if log_scale:
            pdf = pdf + np.log(self.weights_normal)[:,None]
        else:
            pdf = pdf * self.weights_normal[:,None]
        return pdf

    def __call__(self, samples, debug=False, log_scale=False, **kwargs):
        """Evaluate PDF"""
        if log_scale:
            return mixture_pdf(
                self.mu,
                self.cov,
                samples,
                weights=self.weights_normal*np.exp(self.offset),
                log_scale=True,
                limits=self.limits,
                dynamic_rescale=True,
            )
        else:
            return mixture_pdf(
                self.mu,
                self.cov,
                samples,
                weights=self.weights_normal*np.exp(self.offset),
                log_scale=False,
                limits=self.limits,
                dynamic_rescale=True,
            )

    def resample(self, nsample, seed=None):
        """Resample mixture"""
        # Check nsample
        if nsample < 1:
            raise ValueError(f"nsample should be a natural number")
        # Get rng
        rng = seed_parser(seed)
        # This function is why we need separate weights and log_offset
        component_index = rng.choice(
            self.nsystems,
            size=nsample,
            p=self.weights_normal,
        )
        # Initialize empty array
        sample_values = np.full((nsample, self.ndim),np.inf,dtype=float)
        filled = 0
        for i, component in enumerate(self.components):
            # Identify the number of matches
            nmatch = np.count_nonzero(component_index == i)
            # Draw samples
            sample_values[filled:filled+nmatch] = \
                component.sample_normal(nmatch,seed=rng)
            # Inform filled
            filled += nmatch
        # Check filled
        if filled != nsample:
            raise RuntimeError("Vera's math was wrong!")
        # Check for zeros
        if not np.all(np.isfinite(sample_values)):
            warnings.warn(
                "Samples generated at infinity. "
                "There's probably a bug in resample function."
        )
        # Shuffle
        return rng.permutation(sample_values)

    #### Partner methods ####
    def __eq__(self, other):
        """Check if two mixtures are the same"""
        if not isinstance(other, self.__class__):
            return False
        if not self.nsystems == other.nsystems:
            return False
        if not self.ndim == other.ndim:
            return False
        if not np.allclose(self.params, other.params):
            return False
        if not np.allclose(self.limits, other.limits):
            return False
        if (self.weights is None) and (other.weights is not None):
            return False
        if (self.weights is not None) and (other.weights is None):
            return False
        if (self.weights is not None) and (other.weights is not None):
            if not np.allclose(self.weights, other.weights):
                return False
        return True

    def __add__(self, other):
        """Add two mixtures together (concatenate)"""
        if not isinstance(other, GaussianMixture):
            raise ValueError(f"other should be GaussianMixture, "
                f"but is type {type(other)}")
        params, scale, limits, weights = self.combine_data(
            self.params, self.scale, self.limits, self.weights,
            other.params, other.scale, other.limits, other.weights,
        )
        return self.__class__.from_data(
            params,
            scale=scale,
            limits=limits,
            weights=weights,
            sig_max=self.components[0].sig_max,
            scale_max=self.components[0].scale_max,
        )

    def KL(
            self, 
            other, 
            nsample=100_000, 
            logdiff_ceil = np.inf, 
            verbose=False,
            debug=False,
        ):
        """Estimate D_KL (P | Q) where P is self and Q is other

        D_KL(P|Q) is the information lost when using Q to approximate P
        """
        # Resample P
        if verbose: print("Sampling...")
        samples = self.resample(nsample)
        if verbose: print("Estimating lnP...")
        # Estimate lnP
        lnP = self.__call__(samples,log_scale=True)
        if verbose: print(f"lnP: {lnP}")

        if verbose: print(f"Estimating lnQ for {other}...")
        # Estimate lnQ
        # Case 1: other is KDE
        if isinstance(other, GaussianMixture):
            lnQ = other.__call__(samples,log_scale=True)
        # Case 2: MultivariateNormal
        elif isinstance(other, MultivariateNormal):
            other.normalize()
            lnQ = other.likelihood(samples,log_scale=True)
        # Case 3: Something else
        else:
            raise NotImplementedError(f"Unknown logpdf method for {other}")
        if verbose: print(f"lnQ: {lnQ}")

        # Estimate log difference
        logdiff = lnP - lnQ
        # Find where the ceiling is hit
        mask_ceil = logdiff > logdiff_ceil
        if debug:
            nceil = np.sum(mask_ceil)
            index_ceil = np.arange(mask_ceil.size)[mask_ceil]
            index_keep = np.arange(mask_ceil.size)[~mask_ceil]
        qt = [0.,0.01,0.05,0.32,0.5,0.66,0.95,0.99,1.0]
        if verbose:
            print(f"Quantiles: {qt}")
            print(f"logdiff[quantiles]: {np.quantile(logdiff,qt)}")
            print(f"log diff ceiling: {logdiff_ceil}")
            print(f"enforced: {np.sum(mask_ceil)}")
            print(f"logdiff[quantiles]: {np.quantile(logdiff,qt)}")
        # Debug ceiling values
        if debug and (np.sum(mask_ceil) > 0):
            print(f"other.mu: {other.mu}")
            print(f"other.std: {other.std}")
            print(f"self.limits: {self.limits}")
            print(f"other.limits: {other.limits}")
            print(f"Ceiling samples: {samples[mask_ceil]}")
            # Identify # sigma
            sigma_to_closest_component_self = \
                self.sigma_to_closest(samples[mask_ceil])
            print(f"  Sigma to closest [KL ceiling] (self): "
                f"{sigma_to_closest_component_self}")

            if isinstance(other, GaussianMixture):
                sigma_to_closest_component_other = \
                    other.sigma_to_closest(sample[mask_ceil])
            elif isinstance(other, MultivariateNormal):
                sigma_to_closest_component_other = \
                    other.mahalanobis_distance(samples[mask_ceil])
            else:
                raise NotImplementedError
            print(f"  Sigma to closest [KL ceiling] (other): "
                f"{sigma_to_closest_component_other}")

            # TODO
            # Find the largest logdiff point
            imax = np.argmax(logdiff)
            print(f"largest logdiff sample:")
            print(samples[imax])
            print(f"  Sample has logdiff {logdiff[imax]} "
                f"(ceiling: {logdiff_ceil})")
            sigma_to_closest_component_self = \
                self.sigma_to_closest(np.asarray([samples[imax]]))
            print(f"  Sigma to closest [imax] (self): "
                f"{sigma_to_closest_component_self}")

            if isinstance(other, GaussianMixture):
                sigma_to_closest_component_other = \
                    other.sigma_to_closest(np.asarray([samples[imax]]))
            elif isinstance(other, MultivariateNormal):
                sigma_to_closest_component_other = \
                    other.mahalanobis_distance(samples[imax])
            else:
                raise NotImplementedError
            print(f"  Sigma to closest [imax] (other): "
                f"{sigma_to_closest_component_other}")

            # Find the largest logdiff point which is not hitting the ceiling
            imax = index_keep[np.argmax(logdiff[index_keep])]
            print(f"largest non-ceiling logdiff sample:")
            print(samples[imax])
            print(f"  Sample has logdiff {logdiff[imax]} "
                f"(ceiling: {logdiff_ceil})")
            sigma_to_closest_component_self = \
                self.sigma_to_closest(np.asarray([samples[imax]]))
            print(f"  Sigma to closest [imax] (self): "
                f"{sigma_to_closest_component_self}")

            if isinstance(other, GaussianMixture):
                sigma_to_closest_component_other = \
                    other.sigma_to_closest(np.asarray([samples[imax]]))
            elif isinstance(other, MultivariateNormal):
                sigma_to_closest_component_other = \
                    other.mahalanobis_distance(samples[imax])
            else:
                raise NotImplementedError
            print(f"  Sigma to closest [imax] (other): "
                f"{sigma_to_closest_component_other}")

            # Find the largest sigma point which is not hitting the ceiling
            sigma_to_closest_component_self = \
                self.sigma_to_closest(samples)
            if isinstance(other, GaussianMixture):
                sigma_to_closest_component_other = \
                    other.sigma_to_closest(sample)
            elif isinstance(other, MultivariateNormal):
                sigma_to_closest_component_other = \
                    other.mahalanobis_distance(samples)
            else:
                raise NotImplementedError
            imax = index_keep[np.argmax(sigma_to_closest_component_other[index_keep])]
            print(f"largest sigma non-ceiling sample:")
            print(samples[imax])
            print(f"  Sample has logdiff {logdiff[imax]} "
                f"(ceiling: {logdiff_ceil})")
            print(f"  Sigma to closest [imax] (self): "
                f"{sigma_to_closest_component_self[imax]}")
            print(f"  Sigma to closest [imax] (other): "
                f"{sigma_to_closest_component_other[imax]}")

        # Check for perposterous ceiling values
        if np.sum(mask_ceil) > (nsample // 4):
            raise ValueError(f"More than 25% of samples are hitting KL ceiling")
        # Apply ceiling
        logdiff[mask_ceil] = logdiff_ceil

        # Estimate D_KL
        D_KL = np.mean(logdiff)
        if verbose:
            print(f"D_KL: {D_KL}")
        if debug and (np.sum(mask_ceil) > 0):
            #raise RuntimeError("KL Divergence debug exit")
            pass
        return D_KL

    def sig2_joint(self, other, nsample=100_000):
        """Estimate eq.39 of 1204.3117"""
        raise NotImplementedError


######## Testing ######## 
def test_mixture_pdf():
    print("testing mixture pdf...")
    # Setup simple problem
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
    cov = cov_of_std_cor(std, cor)
    params = params_of_offset_mu_std_cor(
        offset, mu, std, cor,
    )
    # Set limits
    limits = np.asarray([
        [-800.,800.],
        [-800.,800.],
    ])
    A = MultivariateNormal(params[0],limits=limits)
    B = MultivariateNormal(params[1],limits=limits)
    C = MultivariateNormal(params[2],limits=limits)
    # Draw some samples from each
    A_sample = A.sample_normal(1000)
    B_sample = B.sample_normal(1000)
    C_sample = C.sample_normal(1000)
    sample = np.concatenate((A_sample, B_sample, C_sample))
    
    # check to see how far away they are from centers
    closest_sigma = np.min(maha_of_mu_cov_sample(mu,cov,sample),axis=0)
    furthest_point = np.max(closest_sigma)
    assert furthest_point < 100

    #### Test 1: A likelihood by any other name ####
    L_large = A.likelihood(
        sample,
        X=params,
        scale=False,
        limits=limits,
        offset=offset,
        log_scale=False,
    )
    lnL_large = np.log(L_large)
    L_MV = np.sum(L_large, axis=0)
    lnL_MV =  logsumexp(lnL_large, axis=0)
    if not np.allclose(np.exp(lnL_MV), L_MV):
        raise RuntimeError("MultivariateNormal.likelihood failure")
    if not np.allclose(np.log(L_MV), lnL_MV):
        raise RuntimeError("MultivariateNormal.likelihood failure")
    # Alright, test the pdf methods
    L_mixture_1 = mixture_pdf(
        mu,
        cov,
        sample,
        weights=np.exp(offset),
        log_scale=False,
        dynamic_rescale=True,
    )
    lnL_mixture_1 = mixture_pdf(
        mu,
        cov,
        sample,
        weights=np.exp(offset),
        log_scale=True,
        dynamic_rescale=True,
    )
    assert np.allclose(lnL_MV, lnL_mixture_1)
    assert np.allclose(L_MV, L_mixture_1)
    L_mixture_2 = mixture_pdf(
        mu,
        cov,
        sample,
        weights=np.exp(offset),
        log_scale=False,
        dynamic_rescale=True,
        limits=limits,
    )
    lnL_mixture_2 = mixture_pdf(
        mu,
        cov,
        sample,
        weights=np.exp(offset),
        log_scale=True,
        dynamic_rescale=True,
        limits=limits,
    )
    assert np.allclose(lnL_MV, lnL_mixture_2)
    assert np.allclose(L_MV, L_mixture_2)
    L_mixture_3 = mixture_pdf(
        mu,
        cov,
        sample,
        weights=np.exp(offset),
        log_scale=False,
        dynamic_rescale=True,
        limits=np.tile(limits,(3,1,1)),
    )
    lnL_mixture_3 = mixture_pdf(
        mu,
        cov,
        sample,
        weights=np.exp(offset),
        log_scale=True,
        dynamic_rescale=True,
        limits=np.tile(limits,(3,1,1)),
    )
    assert np.allclose(lnL_MV, lnL_mixture_3)
    assert np.allclose(L_MV, L_mixture_3)

    #### Test 2: Global limits ####
    limits = np.asarray([
        [0.,800.],
        [-800.,1.],
    ])
    L_large = A.likelihood(
        sample,
        X=params,
        scale=False,
        limits=limits,
        offset=offset,
        log_scale=False,
    )
    lnL_large = np.log(L_large)
    L_MV = np.sum(L_large, axis=0)
    lnL_MV =  logsumexp(lnL_large, axis=0)
    # Check mixture
    L_mixture_4 = mixture_pdf(
        mu,
        cov,
        sample,
        weights=np.exp(offset),
        log_scale=False,
        dynamic_rescale=True,
        limits=limits,
    )
    lnL_mixture_4 = mixture_pdf(
        mu,
        cov,
        sample,
        weights=np.exp(offset),
        log_scale=True,
        dynamic_rescale=True,
        limits=limits,
    )
    assert np.allclose(L_MV, L_mixture_4)
    assert np.allclose(lnL_MV, lnL_mixture_4)
    #### Test 3: Local limits ####
    limits = np.asarray([
        [
            [0.,800.],
            [-800.,1.],
        ],
        [
            [0.,800.],
            [-800.,1.],
        ],
        [
            [0.,1.],
            [0.,1.],
        ],
    ])
    L_large = A.likelihood(
        sample,
        X=params,
        scale=False,
        limits=limits,
        offset=offset,
        log_scale=False,
    )
    lnL_large = np.log(L_large)
    L_MV = np.sum(L_large, axis=0)
    lnL_MV =  logsumexp(lnL_large, axis=0)
    # Check mixture
    L_mixture_5 = mixture_pdf(
        mu,
        cov,
        sample,
        weights=np.exp(offset),
        log_scale=False,
        dynamic_rescale=True,
        limits=limits,
    )
    lnL_mixture_5 = mixture_pdf(
        mu,
        cov,
        sample,
        weights=np.exp(offset),
        log_scale=True,
        dynamic_rescale=True,
        limits=limits,
    )
    assert np.allclose(L_MV, L_mixture_5)
    assert np.allclose(lnL_MV, lnL_mixture_5)
    print("  pass!")

def test_mixture():
    print("testing mixture...")
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
    ABC = GaussianMixture([A,B,C])
    # Test normalize
    ABC.normalize()
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
    BCA = GaussianMixture([B,C,A])
    # Test Eq.

    assert ABC == abc
    assert abc == ABC
    ABC.normalize()
    abc.normalize()
    Abc.normalize()
    assert ABC == Abc
    assert Abc == ABC
    assert Abc == abc
    assert abc == Abc
    assert not (ABC == BCA)
    assert not (BCA == ABC)
    assert ABC != BCA
    assert BCA != ABC

    # Test append
    AB = GaussianMixture([A,B])
    aBc = AB.append(
        np.atleast_2d(params[2]),
        new_limits=limits,
        new_scale=ABC.components[2].scale,
    )
    assert aBc == ABC

    # Test add
    AB = GaussianMixture([A,B])
    BA = GaussianMixture([B,A])
    ABBA = AB + BA
    assert ABBA == GaussianMixture([A,B,B,A])

    # Test downsample
    assert AB == ABBA.downsample([0,2])

    # Test marginalize
    ABBA_1d = ABBA.marginalize([0])
    assert np.all(ABBA_1d.mu.flatten() == ABBA.mu[:,0].flatten())
    # Just see if it works
    vals = ABBA_1d(ABBA_1d.mu)

    # Test KL
    D_KL_same = ABC.KL(abc)
    D_KL_diff = ABC.KL(ABBA)
    assert D_KL_same < D_KL_diff
    # Now something truly horrible
    D_KL_horrible = ABBA.KL(C,debug=True,verbose=True,logdiff_ceil=100.)

    # Test save / load
    ABBA.save("test_mixture.hdf5", "ABBA")
    abba = GaussianMixture.load("test_mixture.hdf5", "ABBA")
    # Check __eq__
    if not (ABBA == abba):
        if not isinstance(abba, GaussianMixture):
            print("Type failure")
        if not ABBA.nsystems == abba.nsystems:
            print("nsystems failure")
        if not ABBA.ndim == abba.ndim:
            print("ndim failure")
        if not np.allclose(ABBA.params, abba.params):
            print("params failure")
        if not np.allclose(ABBA.limits, abba.limits):
            print("limits failure")
        if (ABBA.weights is None) and (abba.weights is not None):
            print("weights failure 1")
        if (ABBA.weights is not None) and (abba.weights is None):
            print("weights failure2 ")
        if (ABBA.weights is not None) and (abba.weights is not None):
            if not np.allclose(ABBA.weights, abba.weights):
                print("weights failure 3")
        raise RuntimeError(f"Test failed: ABBA == abba")

    # Resample test
    x0 = ABBA.resample(1000)
    x1 = ABBA.resample(1)
    ABBA.weights = np.asarray([1.,4.,4.,1.])
    x2 = ABBA.resample(1000)
    assert not np.allclose(np.mean(x0,axis=0),np.mean(x2,axis=0))

    # Test save / load again
    ABBA.save("test_mixture.hdf5", "ABBA")
    abba = GaussianMixture.load("test_mixture.hdf5", "ABBA")
    assert ABBA == abba
    print("  pass!")


def cli_tests():
    test_mixture_pdf()
    test_mixture()
    return

######## Execution ########
if __name__ == "__main__":
    cli_tests()
