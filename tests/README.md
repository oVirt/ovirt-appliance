Integration testing
===================

his directory contains the testcases to test the integration between
Node and Engine.

Dedicated directories to test the sanity of each image independently are
kept in the respective appliance specific test directories.

To test:

    make clean-build-and-check

This will take a long time, because it will build the Engine and Node
appliance, once that is done it will perform the integration tests.
