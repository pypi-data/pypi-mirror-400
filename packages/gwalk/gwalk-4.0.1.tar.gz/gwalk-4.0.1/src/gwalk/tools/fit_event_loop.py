#!/usr/bin/env python3
'''\
Test the Multivariate Normal object and methods
'''
######## Imports ########
#### Standard Library ####
import argparse
from contextlib import contextmanager
import sys
from os.path import join, isfile, isdir
import os
import time
from contextlib import redirect_stdout, redirect_stderr
#### Third Party ####
import numpy as np
#### Homemade ####
from xdata import Database
#### Local ####
from gwalk.catalog.catalog import CATALOGS
from gwalk.catalog.catalog import EVENTS
from gwalk.data.registry import GwalkFileRegistry as Registry
from gwalk.catalog.coordinates import coordinate_tags
from gwalk.tools.fit_catalog_samples import fit_real_event
from gwalk.tools.plot_nal_fit import plot_nal_corner
from gwalk.utils.tee import TeeWriter

######## Setup ########

######## Argparse ########
def arg():
    parser = argparse.ArgumentParser()
    # Required arguments
    parser.add_argument("--catalog", required=True, type=str,
        help="[GWTC-1, GWTC-2, GWTC-2p1, ..., NRSurCat-1]")
    parser.add_argument("--event", required=True, type=str,
        help="Must always match PE catalog name for event; E.g. GW150914")
    parser.add_argument("--wkdir", required=True, type=str,
        help="Where to save fit? E.g. GW150914")
    # Optional arguments
    parser.add_argument("--approximant", default=None, type=str,
        help=f"Waveform approximant; E.g. IMRPhenomPv2, NRSur7dq4, ...")
    parser.add_argument("--coordinates", default=None, type=str,
        help=f"{list(coordinate_tags.keys())}")
    parser.add_argument("--min-bins", default=10, type=int,
        help="Minimum histogram bins")
    parser.add_argument("--max-bins1d", default=100, type=int,
        help="Maximum 1d histogram bins")
    parser.add_argument("--max-bins2d", default=31, type=int,
        help="Maximum 2d histogram bins")
    parser.add_argument("--whitenoise", default=1.e-3, type=float,
        help="GP kernel whitenoise")
    parser.add_argument("--nwalk", default=1000, type=int,
        help="Number of random walkers")
    parser.add_argument("--nstep", default=1000, type=int,
        help="Random walker steps")
    parser.add_argument("--sig-factor", default=0.5, type=float,
        help="MCMC jump parameters")
    parser.add_argument("--carryover", default=0.03, type=float,
        help="Genetic carryover fraction")
    parser.add_argument("--make-plots", action='store_true',
        help="Make plots for this run?")
    parser.add_argument("--verbosity", default=1, type=int)
    # Parse args
    opts = parser.parse_args()
    # Check catalog
    if opts.catalog not in CATALOGS:
        raise ValueError(f"Unknown catalog {opts.catalog};"
            f"avaliable: {list(CATALOGS.keys())}")
    # Check event
    if opts.event not in CATALOGS[opts.catalog].events:
        raise ValueError(f"Unknown event {opts.event}; "
            f"available in {opts.catalog}: "
            f"{list(CATALOGS[opts.catalog].events)}")
    # Initialize event object
    event_obj = CATALOGS[opts.catalog](opts.event)
    # Check event again
    if opts.event not in event_obj.catalog_events:
        raise ValueError(f"Unknown event {opts.event}; "
            f"available: {list(event_obj.catalog_events)}")
    # Check approximant
    if (opts.approximant is not None) and \
            (opts.approximant not in event_obj.waveforms):
        raise ValueError(f"Unknown approximant {opts.approximant}; "
            f"available: {event_obj.waveforms}")
    # Check corodinate tag
    if (opts.coordinates is not None) and \
            (opts.coordinates in coordinate_tags):
        raise ValueError(f"Unknown coordinate tag: {opts.coordinate_tag}; "
            f"available in {opts.catalog} for "
            f"{opts.event}/{opts.approximant}: "
            f"{event_obj.waveform_tags(opts.approximant)}")
    elif (opts.coordinates is not None) and \
            (opts.approximant is not None) and \
            (not event_obj.has_coordinate_tag(
                opts.approximant,opts.coordinates
            )):
        raise ValueError(f"Known, but unavailable coordinate tag: "
            f"{opts.coordinate_tag}; available in {opts.catalog} for "
            f"{opts.event}/{opts.approximant}: "
            f"{event_obj.waveform_tags(opts.approximant)}")
    return opts

######## Event fit loop ########
def fit_event_loop(
        catalog,
        event,
        wkdir,
        approximant=None,
        coordinates=None,
        make_plots=False,
        **kwargs
    ):
    """Run the GWALK pipeline for an event"""
    # Get event object
    event_obj = CATALOGS[catalog](event)
    try:
        event_obj.save()
    except:
        event_obj.download()
    # Check the directory
    if not isdir(wkdir):
        os.mkdir(wkdir)
    # Identify fname NAL
    fname_nal = join(wkdir,f"{event_obj.catalog}_{event}.nal.hdf5")
    db = Database(fname_nal, event)
    # Figure out all the coordinate tags we want to loop through
    if coordinates is None:
      include_coordinates = list(coordinate_tags.keys())
    else:
      include_coordinates = [coordinates]

    ## Loop 1 ##
    # Loop the coordinate tags
    for coord_tag in include_coordinates:
      # Figure out all the waveforms that have this coordinate tag
      if approximant is None:
        include_approximants = []
        for wav in event_obj.waveforms:
          if not event_obj.has_coordinate_tag(wav,coord_tag):
            continue
          else:
            include_approximants.append(wav)
      else:
        include_approximants = [approximant]

      ## Loop 2 ##
      for apprx in include_approximants:
        # Skip if bad coordinates
        if not event_obj.has_coordinate_tag(apprx,coord_tag):
          continue
        print(f"coord_tag {coord_tag} for {event} with {apprx}...")
        if not event_obj.samples_nonsingular(apprx,coord_tag):
          continue
        print(f"Nonsingular!")
        ## Identify info
        fname_log = join(wkdir,f"{event_obj.catalog}_{event}_{coord_tag}:{apprx}.out")
        ## Context manager ##
        with open(fname_log, 'w') as logfile:
          with redirect_stdout(logfile), redirect_stderr(TeeWriter(logfile, sys.stderr)):
            ## fit real_event ##
            fit_real_event(
              catalog,
              event,
              apprx,
              coord_tag,
              fname_nal,
              **kwargs
            )
            ## Plot loop ##
            if not make_plots:
              continue
            # Find matching fits
            for tag in db.list_items():
              _coord_tag, _apprx, _nal_method = tag.split(":")
              if not (_coord_tag == coord_tag):
                continue
              if not (_apprx == apprx):
                continue

              # Check if it's got the coord tag
              # Label
              # fname_simple
              fname_plot = join(
                wkdir,
                f"{event_obj.catalog}_{event}_{tag}.png",
              )
              # Plot the fit
              try:
                plot_nal_corner(
                  catalog,
                  event,
                  apprx,
                  coord_tag,
                  fname_nal,
                  fname_plot,
                  nal_method = _nal_method,
                )
              except:
                pass

######## Nal event pipeline ########
def fit_event_pipeline(
        nwalk=1000,
        nstep=1000,
        max_bins2d=31,
        make_plots=False,
        **kwargs
    ):
    """Step through fit_event_loop up to three times"""
    # First with 100x100x20
    if max_bins2d > 20:
        fit_event_loop(
            nwalk=100,
            nstep=100,
            max_bins2d=20,
            make_plots=False,
            **kwargs
        )
    # Second true run
    fit_event_loop(
        nwalk=nwalk,
        nstep=nstep,
        max_bins2d=max_bins2d,
        make_plots=make_plots,
        **kwargs
    )





######## Execution ########
if __name__ == "__main__":
    opts = arg()
    fit_event_pipeline(**opts.__dict__)
