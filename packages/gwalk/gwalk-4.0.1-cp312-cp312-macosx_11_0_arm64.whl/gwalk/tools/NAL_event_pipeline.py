#!/usr/bin/env python3
'''\
Fit a whole catalog
'''
######## Imports ########
#### Standard Library ####
import argparse
from contextlib import contextmanager
import sys
from os.path import join, isfile, isdir
import os
import time
from contextlib import redirect_stdout
import concurrent.futures
import multiprocessing as mp
#### Third Party ####
import tqdm
import numpy as np
#### Homemade ####
from xdata import Database
#### Local ####
from gwalk.catalog.catalog import CATALOGS
from gwalk.catalog.catalog import WAVEFORMS_BEST
from gwalk.catalog.catalog import EVENTS
from gwalk.data.registry import GwalkFileRegistry as Registry
from gwalk.tools.fit_event_loop import fit_event_pipeline

######## Setup ########

######## Argparse ########
def arg():
    parser = argparse.ArgumentParser()
    # Required arguments
    parser.add_argument("--threads", default=1, type=int,
        help="Number of events to run at once")
    parser.add_argument("--catalog", required=True, type=str,
        help="[GWTC-1, GWTC-2, GWTC-2p1, ..., NRSurCat-1]")
    parser.add_argument("--wkdir", required=True, type=str,
        help="Where to save fit? E.g. GW150914")
    # Optional arguments
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
    # Check the directory
    if not isdir(opts.wkdir):
        os.mkdir(opts.wkdir)
    return opts

######## Nal event pipeline ########
def NAL_event_pipeline(
        catalog,
        wkdir,
        threads=1,
        **kwargs
    ):
    """Step through NAL_event_fits up to three times"""
    # Get event wkdirs
    event_wkdirs = {}
    event_apprx = {}
    skip = False
    for event in EVENTS[catalog]:
        if event == "GW190706_222641":
            skip = False
        if skip:
            continue
        event_wkdirs[event] = f"{wkdir}/{event}"
        event_obj = CATALOGS[catalog](event)
        try:
            event_obj.save()
        except:
            event_obj.download()
        best = None
        for wav in WAVEFORMS_BEST:
            if wav in event_obj.waveforms:
                best = wav
                break
        if best is None:
            print(f"Best waveform not found for {catalog}/{event}; waveforms:")
            print(event_obj.waveforms)
        else:
            print(f"Best waveform for {catalog}/{event}: {best}")
        event_apprx[event]=best
        
    ## Event Loop
    if threads <= 1:
        # tqdm bar
        with tqdm.tqdm (
            total=len(list(event_wkdirs.keys())),
            desc="Fitting events in {catalog}...",
            ) as pbar:
            # Loop the Epochs of cosmological histroy
            for event in event_wkdirs:
                fit_event_pipeline(
                    catalog=catalog,
                    event=event,
                    wkdir=event_wkdirs[event],
                    approximant=event_apprx[event],
                    **kwargs
                )
                pbar.update(1)
    else:
        with tqdm.tqdm (
            total=len(list(event_wkdirs.keys())),
            desc="Fitting events in {catalog}...",
            ) as pbar:
            with concurrent.futures.ProcessPoolExecutor(max_workers=threads) as executor:
                futures = {executor.submit(
                    fit_event_pipeline,
                    catalog=catalog,
                    event=event,
                    wkdir=event_wkdirs[event],
                    approximant=event_apprx[event],
                    **kwargs
                ): event for event in event_wkdirs}
            # Check through futures
            for future in concurrent.futures.as_completed(futures):
                try:
                    print(futures[future])
                except Exception as exc:
                    raise exc
                pbar.update(1)




######## Execution ########
if __name__ == "__main__":
    opts = arg()
    NAL_event_pipeline(**opts.__dict__)
