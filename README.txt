Author: Todor Ivanov
Name: wpsp.py
Version: 1.5

I. Requirements

    I.1.  Python version 2.7

II. How it works

    II.1.  The script downloads the latest version of wp-cli.phar from the official repo
    II.2.  The script then installs the profiler module to the local wp-cli.phar file
    II.3.  The script then runs tests on the website within the cwd taking the cli parameters into consideration (the -s and -n flags).
        II.3.A.  First the script runs a test on all stages and prints the stages that take more than N seconds to load and prints them
        II.3.B.  Then it runs a test on all hooks within the stages that qualify and again prints only results above N seconds
        II.3.C.  Next the plugin gets a list of the active plugins on the website
        II.3.D.  For each plugin it runs a test on all stages three times by not loading the plugin in question
        II.3.E.  It then saves the results for each plugin in a dictionary
        II.3.F.  Prints the results from dictionaries if they are above N seconds

III. Known issues

    III.1. The script may malfunction in cases there's something blocking the WP Cli. These may be:
        III.1.A.  Rules within the wp-config.php file
        III.1.B.  Plugin
        III.1.C.  Theme
        III.1.D.  Malware


IV. How to use

    IV.1.  Start the script using the python 2.7 binary
        IV.1.A.  For Site Tools use:
                    python2.7 wpsp.py
        IV.1.B.  For cPanel use:
                    /usr/bin/python2.7 wpsp.py

    IV.2.  Additional options:
        IV.1.A.  Set the seconds limit - only results above N seconds will be shown
                    -s <float> or --seconds <float>
        IV.1.B.  Set the count limit - only N number of results will be shown
                    -c <integer> or --count <integer>

V. How to download

   V.1.  Download directly:
            curl -O http://todorivanov.eu/resources/wpsp/wpsp.py -u support:n4hfeVO2nKk8M7j
   V.2.  Clone with git:
            git