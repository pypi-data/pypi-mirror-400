#!/usr/bin/env python3
"""Test gwalk.data module"""
######## Setup ########
fname_gw = "GW150914_GWTC-1.hdf5"
######## Imports ########
#### Standard Library #######
from importlib import resources
import os
#### Homemade ####
import xdata
from gwalk.data.registry import GwalkFileRegistry as FileRegistry

######## Functions ########
def test_import():
    Files = FileRegistry()
    Files.download(fname_gw)
    assert os.path.isfile(f"{Files.directory}/hash.dat")
    Files.report()
    Files.clean()
    Files.report()
    Files.validate_all()
    Files.report()
    pass

def test_cmd():
    from os import system as command
    from os import path
    from gwalk import data
    exe = f"python3 {path.join(resources.files(data),'registry.py')}"
    # list
    cmd = exe + " list"
    print(cmd)
    command(cmd)
    # validate 
    cmd = exe + " validate"
    print(cmd)
    command(cmd)
    # clean
    cmd = exe + " clean"
    print(cmd)
    command(cmd)
    # Delete all
    #cmd = exe + " clear --assume-yes"
    #print(cmd)
    #command(cmd)
    # Download
    cmd = exe + f" download {fname_gw} --assume-yes"
    print(cmd)
    command(cmd)
    # Update to md5
    cmd = f"{exe} save --enc md5"
    print(cmd)
    command(cmd)
    # Validate
    cmd = f"{exe} validate {fname_gw}"
    print(cmd)
    command(cmd)
    # Remove
    cmd = f"{exe} remove --assume-yes {fname_gw}"
    print(cmd)
    command(cmd)
    # Check spiider
    cmd = f"{exe} download {fname_gw} --spider"
    print(cmd)
    command(cmd)
    # Download
    cmd = f"{exe} download --assume-yes {fname_gw} --enc sha256 --retries 2 --verbose --buffer 131072"
    print(cmd)
    command(cmd)

######## Main ########
def main():
    test_import()
    test_cmd()

######## Execution ########
if __name__ == "__main__":
    main()
