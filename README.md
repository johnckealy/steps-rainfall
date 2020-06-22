# Steps Rainfall

This project concerns the extrapolation of rainfall radar for accurate short-scale rain forecasts. 



## Lessons learned so far

Some trouble installing with both conda and pip. It seems that the problem was in naming my files "pysteps" – this caused a clash with the package directories.

To get the Met Eireann h5 files to work, I had to hack the source to set RATE to DZDB in the importers module. I'll need to find a less hacky fix for this that doesnt mess with the source.

You must place Met Eireann's h5 files in ./radar/<date>/