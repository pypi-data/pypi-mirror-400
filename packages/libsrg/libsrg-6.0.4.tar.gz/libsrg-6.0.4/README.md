## Name
libsrg -- count calls to python logging at each logging severity level

## Description
libsrg provides the following classes:
* libsrg.LoggingCounter
  * extends logging.Handler with count of logs at each severity level
  * counts on output, so logs suppressed by current logging level do not get counted
  * atexit hook used to print statistics on program exit
* libsrg.LoggingAppBase
  * application base class with LoggingCounter installed
  * argparse.ArgumentParser
    * --verbose sets logging level to DEBUG
    * --logfile <file> directs logging to a file
  * Derived classes can add application specific options to ArgumentParser
* libsrg.Runner
  * run command line in a subprocess
  * capture stdout, stderr
  * try catch block for exceptions
  * exceptions can optionally be raised back to calling program

I write a lot of smallish command line utilities for internal use, and factored out some common 
repetitive boilerplate code into this package. Published for my own installation convenience, 
but might be useful to others as well. 

## Example output

Library uses atexit hook to summarize logging activity counts and total execution time. 
Counts are also available to the program at runtime.
```
2022-02-22 12:46:22,568 INFO     (libsrg.LoggingCounter:61) __log_atexit 
Logging Summary:
Logging at Level INFO       occurred         13 times
Logging at Level DEBUG      occurred          1 times
Logging at Level WARNING    occurred          1 times
Logging at Level ERROR      occurred          2 times
Logging at Level CRITICAL   occurred          1 times
Elapsed time was 0.087 seconds
```

## Internal notes on updating

* /GNAS/PROJ/PycharmProjects/libsrg/publish.bash
```
#! /bin/bash

cd /GNAS/PROJ/PycharmProjects/libsrg
rm -rf dist
python3 -m build --wheel
python3 -m twine check dist/*
python3 -m twine upload dist/*
```

## Installation from pypi via pip
* pip3 install libsrg
* pip3 install libsrg --update

## Installation from Gitlab or local repository
* pip3 install git+ssh://git@gitlab.com/SRG_gitlab/libsrg.git
* pip3 install /GNAS/PROJ/PycharmProjects/libsrg

## Testing

Pytest performs its own logging setup before calling any user supplied tests, so it
doesn't work well testing these classes logging setup. Ad-hoc test code is supplied
at the end of the classes and executes if the class is loaded as __main__.


## Roadmap
My intention is to keep this library small. It is not expected to evolve into an all-purpose framework. 
Output is geared towards developers, not end users. 

## License
MIT

## Project status
Pulled extraneous applications out into libsrg_apps