#!/usr/env/bin python3
"""Test for new catalog.py module"""
######## Imports ########
#### Standard Library ####
import os
#### Third Party ####
import numpy as np
#### Local ####
from gwalk.catalog.catalog import CATALOGS, Local_EventCatalog
from gwalk.catalog.catalog import EVENTS
from gwalk.data.registry import GwalkFileRegistry as Registry
from gwalk.catalog.coordinates import coordinate_tags

######## Setup ########
ExampleEvents = {
    "GWTC-1"    : "GW170817",
    "GWTC-2"    : "GW190425",
    "GWTC-2p1"  : "GW190403_051519",
    "GWTC-3"    : "GW191103_012549",
    "GWTC-4"    : "GW231123_135430",
    "NRSurCat-1": "GW150914_095045",
}
######## Functions ########
######## Tests ########
def reset():
    Reg = Registry()
    for item in Reg.tracked_files:
        Reg.save_hash(item)


def test_download():
    for cat in CATALOGS:
        cls = CATALOGS[cat]
        event = ExampleEvents[cat]
        obj = cls(event)
        obj.download()

def test_urls():
    cleaned = False
    for cat in EVENTS:
        for i in range(len(EVENTS[cat])):
            event = EVENTS[cat][i]
            cls = CATALOGS[cat]
            obj = cls(event)
            if not cleaned:
                obj.registry.clean()
                cleaned = True
            obj.spider()
    
def test_aligned3d():
    for cat in CATALOGS:
        cls = CATALOGS[cat]
        event = ExampleEvents[cat]
        obj = cls(event)
        samples, prior = obj.coordinate_tag_samples(
            obj.waveforms[0],
            "aligned3d",
        )
        print(np.mean(samples,axis=1))
        # Also test local catalog
        local_cat = Local_EventCatalog(
            ExampleEvents[cat],
            obj.fname,
            obj.catalog,
            wav_group=cls.waveform_group,
            )

def test_coordinates():
    cat = "GWTC-2"
    event = "GW190425"
    obj = CATALOGS[cat](event)
    print(obj.waveforms)
    for tag in coordinate_tags:
        samples, prior = obj.coordinate_tag_samples(
            obj.waveforms[0],
            tag,
        )
        print(tag, np.mean(samples,axis=1))

def explore():
    for cat in CATALOGS:
        cls = CATALOGS[cat]
        event = ExampleEvents[cat]
        print(cat, event)
        obj = cls(event)
        print(obj.waveforms)
        print(obj.dset_addr(obj.waveforms[0]))
        print(obj.fields(obj.waveforms[0]))
        mass_1 = obj.find_samples(obj.waveforms[0],'mass_1')
        print(f"np.mean(mass_1): {np.mean(mass_1)}")
        mc = obj.find_samples(obj.waveforms[0],"chirp_mass")
        print(f"np.mean(mc): {np.mean(mc)}")
    


######## Main ########
def main():
    reset()
    test_download()
    test_aligned3d()
    test_coordinates()
    test_urls()
    #explore()
    return

######## Execution ########
if __name__ == "__main__":
    main()
