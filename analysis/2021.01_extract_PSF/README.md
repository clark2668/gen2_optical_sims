
## About
We need a script to extract the PSF function from the hdf5 file. We need to have the Gen2 tool installed. We run like:

`python extract_PSF.py summary_of_recos.hdf5`

## Results

Tabulate angular error
![](angular_error_standard.png)

Tabulated angular error with the King/Moffat fits
![](angular_error_with_fits_standard.png)

The fit parameters
![](fit_params_standard.png )

Comparisons of the fits to what we get when we load the fits into the Gen2 framework and then get them back out again.
![](compare_orig_to_framework_standard.png)