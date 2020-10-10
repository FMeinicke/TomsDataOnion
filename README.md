# Tom's Data Onion
Solutions for Tom's Data Onion riddles from https://www.tomdalling.com/toms-data-onion/

The idea of making a standalone decoding script was "stolen" from [nharrer]'s [TomsDataOnion](https://github.com/nharrer/TomsDataOnion) repo.  
The other scripts for decoding the individual layers I have written myself.
I found [nharrer]'s repo just after I finished solving all the riddles.

### Prerequisites
Coincidentally, the prerequisites are quite similar:  
You'll need Python 3 as well as `pycryptdome`.
Simply install it with `pip`:

    $ pip install pycrptdome

### Running
Then you can easily decode the whole Onion by running

    $ python decode.py

> #### Note:
> I'd advise you to first solve the riddles yourself before running the decode script or having a look into the code.

The contents of each layer will be put into a separate file with the name of the corresponding layer.
The last file contains the *THE CORE* of the Onion.

**But be warned: The secret hidden inside the Onion is deeply shocking! Use at your own risk.**


[nharrer]: https://github.com/nharrer
