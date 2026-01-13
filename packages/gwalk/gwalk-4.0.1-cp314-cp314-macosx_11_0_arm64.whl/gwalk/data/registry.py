#!/usr/bin/env python3
"""Use xdata to download stuff"""
######## Imports ########
#### Homemade ####
from xdata.registry import FileRegistry, main, arg
#### Local ####
from gwalk.data import files as FILE_DIRECTORY

######## objects ########
class GwalkFileRegistry(FileRegistry):
    """GWALK file registry"""
    def __init__(self):
        super().__init__(FILE_DIRECTORY)

######## Execution ########
if __name__ == "__main__":
    # Get command line arguments
    opts = arg()
    # Use command line arguments to call main
    main(
        FILE_DIRECTORY,
        "hash.dat",
        opts.action,
        opts.filename,
        verbose=opts.verbose,
        all_files=opts.all_files,
        assume_yes=opts.assume_yes,
        retries=opts.retries,
        spider=opts.spider,
        buffer=opts.buffer,
        enc=opts.enc,
    )
