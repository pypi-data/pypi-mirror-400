#! /usr/env/bin python3
'''Fit samples using a bounded multivariate normal model with a mesh
'''
######## Argparse ########
def arg():
    import argparse
    import numpy as np
    from gwalk.catalog import CATALOGS
    from gwalk.catalog.coordinates import coordinate_tags, coord_labels

    parser = argparse.ArgumentParser()
    # Required arguments
    parser.add_argument("--catalog", required=True, type=str,
        help="[GWTC-1, GWTC-2, GWTC-2p1, ..., NRSurCat-1]")
    parser.add_argument("--event", required=True, type=str,
        help="Must always match PE catalog name for event; E.g. GW150914")
    parser.add_argument("--approximant", required=True, type=str,
        help="Waveform approximant; E.g. IMRPhenomPv2, NRSur7dq4, ...")
    parser.add_argument("--coordinates", required=True, type=str,
        help=f"{list(coordinate_tags.keys())}")
    parser.add_argument("--fname-nal", required=True, type=str,
        help="Where to save fit? E.g. GW150914.nal.hdf5")
    parser.add_argument("--min-bins", default=10, type=int,
        help="Minimum histogram bins")
    parser.add_argument("--max-bins1d", default=100, type=int,
        help="Maximum 1d histogram bins")
    parser.add_argument("--max-bins2d", default=20, type=int,
        help="Maximum 2d histogram bins")
    parser.add_argument("--whitenoise", default=1e-3, type=float,
        help="GP kernel whitenoise")
    parser.add_argument("--nwalk", default=100, type=int,
        help="Number of random walkers")
    parser.add_argument("--nstep", default=100, type=int,
        help="Random walker steps")
    parser.add_argument("--sig_factor", default=0.5, type=float,
        help="MCMC jump hyperparameter")
    parser.add_argument("--carryover", default=0.03, type=float,
        help="Genetic carryover fraction")
    parser.add_argument("--verbosity", default=1, type=int)
    opts = parser.parse_args()
    # Check catalog
    if opts.catalog not in CATALOGS:
        raise ValueError(f"Unknown catalog {opts.catalog}; available: {list(CATALOGS.keys())}")
    # Check event
    if opts.event not in CATALOGS[opts.catalog].events:
        raise ValueError(f"Unknown event {opts.event}; available in {opts.catalog}: {list(CATALOGS[opts.catalog].events)}")
    # Instantiate event object
    event_obj = CATALOGS[opts.catalog](opts.event)
    # Check event again
    assert opts.event in event_obj.catalog_events
    # Check waveform
    if opts.approximant not in event_obj.waveforms:
        raise ValueError(f"Unknown approximant {opts.approximant}; available: {event_obj.waveforms}")
    # Check coordinate tag
    if not opts.coordinates in coordinate_tags:
        raise ValueError(f"Unknown coordinate tag: {opts.coordinate_tag}; available in {opts.catalog} for {opts.event}/{opts.approximant}: {event_obj.waveform_tags(opts.approximant)}")
    elif not event_obj.has_coordinate_tag(opts.approximant,opts.coordinates):
        raise ValueError(f"Known, but unavailable coordinate tag: {opts.coordinate_tag}; available in {opts.catalog} for {opts.event}/{opts.approximant}: {event_obj.waveform_tags(opts.approximant)}")
    return opts
######## Functions ########

def model_guesses(
                  fname_nal,
                  event,
                  MV, X, coord_tag,
                  mesh=None,
                  verbosity=1,
                 ):
    '''Return model guesses for event
    fname_nal: str
        Input location of hdf5 file where fits are stored
    event: str
        Input GW name for gravitational wave event
    X: array like, shape = (nparam)
        Input some guess of fit parameters
    coord_tag: str
        Input coordinate group label
    '''
    from xdata import Database
    from gwalk import MultivariateNormal
    from gwalk.catalog.coordinates import coordinate_tags
    from os.path import join
    import numpy as np
    # Load coordinates
    coords = coordinate_tags[coord_tag][:-1]
    # Open the database
    db = Database(fname_nal,group=event)
    # Get all labels for event
    labels = db.list_items()
    # Initialize guess list
    Xg = []
    # Loop through the labels!
    for item in labels:
        if verbosity > 2:
            print(f"model_guesses: attempting to load {item}...")
        # try to load the fit
        try:
            MVi = MultivariateNormal.load(fname_nal,join(event,item))
        except:
            continue
        # Identify label information
        item_coord_tag, item_group, item_fit_method = item.split(":")
        # Load label coordinates
        item_coords = coordinate_tags[item_coord_tag][:-1]
        # Check for identical coordinate tag
        if item_coord_tag == coord_tag:
            item_X = MVi.params
        else:
            # Create a parameter map
            coord_map = {}
            for j, jtem in enumerate(coords):
                coord_map[j] = None
                for k, ktem in enumerate(item_coords):
                    if jtem == ktem:
                        coord_map[j] = k

            # Success! Identify label params
            item_guess = MVi.params
            # Initialize new guess
            item_X = X.copy()
            # Loop through each coordinate again
            for j in range(MV.ndim):
                # Do nothing if coordinate isn't in Visitor's coordinate system
                if coord_map[j] is None:
                    continue
                # Update mu and sigma parameters
                item_X[MV.p_map[f"mu_{j}"]] = item_guess[MVi.p_map[f"mu_{coord_map[j]}"]]
                item_X[MV.p_map[f"std_{j}"]] = item_guess[MVi.p_map[f"std_{coord_map[j]}"]]
                # Update correlation parameters
                for k in range(j):
                    if coord_map[k] is None:
                        continue
                    #Update factor
                    item_X[MV.p_map[f"cor_{j}_{k}"]] = \
                        item_guess[MVi.p_map[f"cor_{coord_map[j]}_{coord_map[k]}"]]

        # Print diagnostic info
        if (mesh is None):
            kl = None
        else:
            kl = mesh.nal_kl_div(MV,item_X,mode='mean')
        if verbosity > 1:
            print(f"{item} mean KL divergence: {kl}")
        # Append to guess list
        Xg.append(item_X.copy())
    Xg = np.asarray(Xg)
    #Return guesses!
    return Xg


def kl_div_optimization(mesh, MV):
    '''Return kl divergence based optimization functions

    Parameters
    ----------
    mesh: Mesh object
        Input mesh for sample evaluations
    MV: MultivariateNormal object
        Input truncated Gaussian we are fitting
    '''
    import numpy as np
    def f_opt(X):
        L = np.zeros(X.shape[0])
        k = MV.satisfies_constraints(X)
        L[k] = np.power(mesh.nal_kl_div(MV,X=X[k]),-1)
        return L

    def f_opt_param(X):
        L = np.zeros(X.shape)
        k = MV.satisfies_constraints(X)
        L[k] = np.power(mesh.nal_kl_div(MV,X=X[k],mode='parameter'),-1)
        return L

    return f_opt, f_opt_param

def fit_nal_with_mesh(
                      fname_nal,
                      label,
                      samples,
                      weights=None,
                      evaluation_res = 10,
                      nwalk=100,
                      nstep=100,
                      sig_factor=1.0,
                      carryover=0.03,
                      p_labels=None,
                      attrs=None,
                      event=None,
                      coord_tag=None,
                      verbosity=1,
                      fname_mesh=None,
                      mesh_label=None,
                      **mesh_kwargs
                     ):
    '''Fit samples to a truncated gaussian
    
    Note: this does not need to be a Gravitational Wave event

    Parameters
    ----------
    fname_nal: str
        Input name of the file where fits will be saved
    label: str
        Input label for saving fit within file
    samples: array like, shape = (npts,ndim)
        Input samples for fitting a truncated Gaussian to
    weights: array like, shape = (npts), optional
        Input weights for each sample
    evaluation_res: int, optional
        Input size of marginal evaluations on 1D and 2D marginals
    nwalk: int, optional
        Input number of random walkers to evolve
    nstep: int, optional
        Input number of steps for random walkers
    sig_factor: float, optional
        Input related to jump size for random walkers.
            Don't touch this unless you know what you are doing
    carryover: float, optional
        Input controls fraction of carryover for genetic algorithm
    p_labels: list, optional
        Input parameter labels for fits
    attrs: dict, optional
        Input attrs to save with fits
    event: str, optional
        Input If this is a Gravitational Wave event, we can make some smarter
            guesses in the beginning
    coord_tag: str, optional
        Input If this is a Gravitational Wave event,
            we may want information about the coordinates
    verbosity: int, optional
        Input print things
    '''
    from gwalk.density import Mesh
    import numpy as np
    import time
    # Identify fit
    # Identify ndim
    ndim = samples.shape[1]
    # Fit the mesh
    mesh = Mesh.fit(
                    samples,
                    ndim,
                    weights=weights,
                    verbose=verbosity > 2,
                    **mesh_kwargs
                   )
    # save the mesh
    if not (fname_mesh is None):
        try:
            mesh.save(fname_mesh, label=mesh_label)
        except:
            print("Failed to save new mesh %s %s"%(fname_mesh, mesh_label))
        
    # Generate an evaluation set
    mesh.generate_evaluation_set(evaluation_res)
    # Generate a multivariate normal object
    MV = mesh.construct_nal(labels=p_labels)
    # Do simple fit
    mesh.nal_fit_to_samples(MV,samples,weights=weights)
    # Recall simple fit
    Xs = MV.params
    # Generate additional guesses
    Xg = mesh.nal_mesh_guesses(MV)
    # Append guesses
    Xg = np.concatenate([Xg,Xs[None,:]])
    # Generate additional guesses
    if fname_nal is not None:
        if verbosity > 2:
            print("getting model guesses")
        Xm = model_guesses(
            fname_nal,
            event,
            MV, Xs.flatten(),
            coord_tag,
            mesh=mesh,
            verbosity=verbosity,
        )
        # Append guesses
        if not (Xm.size == 0):
            Xg = np.append(Xg,Xm,axis=0)
    # Initialize f_opt and f_opt_param
    if verbosity > 2:
        print("Initializing optimization functions")
    f_opt, f_opt_param = kl_div_optimization(mesh, MV)
    # Generate mesh guesses
    if verbosity > 2:
        print("Generating mesh guesses")
    Xg = mesh.nal_init_walkers(MV,nwalk=nwalk,Xg=Xg,f_opt=f_opt,f_opt_param=f_opt_param)
    if verbosity > 1:
        print("Beginning random walk")
    t0 = time.time()
    # Fit random walk
    mesh.nal_fit_random_walk(
                             MV,
                             Xg,
                             nstep=nstep,
                             nwalk=nwalk,
                             sig_factor=sig_factor,
                             carryover=carryover,
                             f_opt=f_opt,
                             f_opt_param=f_opt_param,
                            )
    t1 = time.time()
    # Save
    mesh.nal_save_kl(MV,fname_nal,label,attrs=attrs,better=True)
    if verbosity > 2:
        print(f"{label} mu:{MV.mu}")
        print(f"{label} std:{MV.std}")
        print(f"{label} cor:{MV.cor}")
        print(f"{label} KL:{mesh.nal_kl_div(MV,MV.params,mode='component')}")

def fit_real_event(
        catalog,
        event,
        waveform,
        coord_tag,
        fname_nal,
        random_state = None,
        **kwargs,
    ):
    '''\
    Fit some samples to a mesh
    '''
    from gwalk.catalog import CATALOGS
    from gwalk.catalog.coordinates import coordinate_tags, coord_labels
    from gwalk.density import Mesh
    from gwalk import MultivariateNormal
    from gwalk.optimize_likelihood_grid import optimize_likelihood_grid
    import numpy as np
    import time
    import warnings
    # Identify fit
    Event = CATALOGS[catalog](event)
    mesh_label = "%s/%s:%s"%(event,coord_tag,waveform)
    nal_label_simple = "%s/%s:%s:%s"%(event,coord_tag,waveform,"simple")
    nal_label_grid = "%s/%s:%s:%s"%(event,coord_tag,waveform,"grid")
    nal_label_genetic = "%s/%s:%s:%s"%(event,coord_tag,waveform,"genetic")

    # load samples
    samples, prior = Event.coordinate_tag_samples(waveform, coord_tag)
    inv_prior = prior**-1

    if any(np.std(samples,axis=0) == 0.):
        raise ValueError(f"{coord_tag} is not suitable to {event} with {waveform}; some coordinates have delta functions")

    # Identify ndim
    ndim = samples.shape[1]
    # Identify coordinate labels
    p_labels = []
    for i in range(ndim):
        p_labels.append(coord_labels[coordinate_tags[coord_tag][i]])

    # Identify attributes
    attrs = {
             "event"    : event,
             "coord_tag": coord_tag,
             "coords"   : coordinate_tags[coord_tag],
             "group"    : waveform,
            }

    # Fit simple
    MVsimple = MultivariateNormal.from_samples(
        samples,
        w=inv_prior,
        labels=p_labels,
    )
    MVsimple.save(fname_nal,nal_label_simple,attrs)

    # Find likelihood grid
    if Event.can_find_samples(waveform,"log_likelihood"):
        lnL_grid = Event.find_samples(waveform,"log_likelihood")
    else:
        lnL_grid = None
    # Fit grid
    if lnL_grid is not None:
        try:
            MVgrid  = optimize_likelihood_grid(
                samples,
                lnP=lnL_grid,
                labels=p_labels,
            )
            MVgrid.save(fname_nal,nal_label_grid,attrs)
        except:
            warnings.warn(f"Failed to optimize {nal_label_grid}")

    # No need to build mesh for zero steps
    if kwargs["nstep"] == 0:
        return

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="invalid value encountered in divide")
        warnings.filterwarnings("ignore", message="divide by zero")
        warnings.filterwarnings("ignore", message="pruning")
        # Generate mesh guesses
        fit_nal_with_mesh(
            fname_nal,
            nal_label_genetic,
            samples,
            weights=inv_prior,
            p_labels=p_labels,
            attrs=attrs,
            event=event,
            coord_tag=coord_tag,
            mesh_label=mesh_label,
            **kwargs
           )

######## Execution ########
if __name__ == "__main__":
    opts = arg()
    fit_real_event(
        opts.catalog,
        opts.event,
        opts.approximant,
        opts.coordinates,
        opts.fname_nal,
        min_bins=opts.min_bins,
        max_bins1d=opts.max_bins1d,
        max_bins2d=opts.max_bins2d,
        whitenoise=opts.whitenoise,
        nwalk=opts.nwalk,
        nstep=opts.nstep,
        sig_factor=opts.sig_factor,
        carryover=opts.carryover,
        verbosity=opts.verbosity,
       )
