#! /usr/env/bin python3
'''Plot a NAL fit against a KDE from the catalog samples
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
        help="Where to load fit? E.g. GW150914.nal.hdf5")
    parser.add_argument("--fname-out", required=True, type=str,
        help="Where to save plot? E.g. GW150914.png")
    parser.add_argument("--nal-method", type=str, default="genetic",
        help="What kind of fit to plot?")
    parser.add_argument("--verbosity", default=1, type=int)
    parser.add_argument("--resolution", default=100, type=int,
        help="Corner plot resolution")
    parser.add_argument("--figsize", default=8, type=int,
        help="Corner figure size")
    parser.add_argument("--fontscale", default=0.6, type=float,
        help="Corner plot font scaling")
    parser.add_argument("--cmap", default="terrain_r", type=str,
        help="Color for histograms")
    parser.add_argument("--resample", default=None, type=int,
        help="resample for contours.")
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

def plot_nal_corner(
        catalog,
        event,
        waveform,
        coord_tag,
        fname_nal,
        fname_out,
        nal_method = "genetic",
        rng=None,
        resolution=100,
        cmap="terrain_r",
        figsize=8,
        fontscale=0.6,
        verbosity=0,
        resample=1_000_000,
    ):
    '''\
    Fit some samples to a mesh
    '''
    from basil_core.random.pcg64 import seed_parser
    from basil_core.plots.corner import Corner
    from gwalk.catalog import CATALOGS
    from gwalk.catalog.coordinates import coordinate_tags, coord_labels
    from gwalk.density import Mesh
    from gwalk import MultivariateNormal
    from gwalk.optimize_likelihood_grid import optimize_likelihood_grid
    import numpy as np
    import time
    import warnings
    from matplotlib import pyplot as plt
    # Set fonts
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['DejaVu Serif']
    # Identify fit
    Event = CATALOGS[catalog](event)
    nal_label = f"{event}/{coord_tag}:{waveform}:{nal_method}"

    # Identify attributes
    attrs = {
             "event"    : event,
             "coord_tag": coord_tag,
             "coords"   : coordinate_tags[coord_tag],
             "group"    : waveform,
            }

    # Load fit
    MV = MultivariateNormal.load(
        fname_nal,
        nal_label,
    )
    # load KDE
    KDE = Event.coordinate_tag_kde(waveform, coord_tag)
    MV.limits = KDE.limits[0]

    if any(np.std(KDE.mu,axis=0) == 0.):
        raise ValueError(f"{coord_tag} is not suitable to {event} with {waveform}; some coordinates have delta functions")

    # Identify coordinate labels
    p_labels = []
    for i in range(KDE.ndim):
        p_labels.append(coord_labels[coordinate_tags[coord_tag][i]])

    # Print KL divergence
    print(f"Estimating KL divergence for {nal_label}")
    D_KL = KDE.KL(
        MV,
        nsample=1_001,
        verbose=True,
        debug=True,
    )
    print(f"KL Divergence for {nal_label}: {D_KL}")

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="divide by zero")
        warnings.filterwarnings("ignore", 
            message="The following kwargs were not used by contour")
        # Set title
        title = f"{event}:{coord_tag}\n{waveform}:{nal_method}\n" + \
            "$\mathrm{D}_{\mathrm{KL}}$: " + f"{D_KL:.4f}"
        # Create corner plot
        nal_corner = Corner(
            KDE.ndim,
            limits=KDE.limits[0],
            labels=p_labels,
            title=title,
            log_scale=True,
            figsize=figsize,
            fontscale=fontscale,
        )
        # Add histogram layer
        nal_corner.add_histogram_layer(
            KDE.mu,
            weights=KDE.weights,
            bins=resolution,
            imshow=True,
            cmap=cmap,
        )
        # Error bars
        if resample is None:
            nal_corner.add_scatter2d_layer(
                np.atleast_2d(MV.mu),
                np.atleast_2d(MV.std),
                s=40,
                elinewidth=2.0,
            )
        else:
            samples = MV.sample_normal(resample)
            nal_corner.add_histogram_layer(
                samples,
                bins=resolution,
                contour=True,
                cmap=cmap,
            )

        # Draw the plot
        nal_corner.save(fname_out)



######## Execution ########
if __name__ == "__main__":
    opts = arg()
    plot_nal_corner(
        opts.catalog,
        opts.event,
        opts.approximant,
        opts.coordinates,
        opts.fname_nal,
        opts.fname_out,
        nal_method = opts.nal_method,
        resolution=opts.resolution,
        verbosity=opts.verbosity,
        cmap=opts.cmap,
        figsize=opts.figsize,
        fontscale=opts.fontscale,
        resample=opts.resample,
       )
