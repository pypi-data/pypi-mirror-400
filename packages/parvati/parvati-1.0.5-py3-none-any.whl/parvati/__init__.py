"""
PARVATI
Profiles Analysis and Radial Velocities using Astronomical Tools for Investigation
==============================================================================================

PARVATI is a Python package to compute and analyse stellar line profiles
Written by Monica Rainer

    PARVATI is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY. 
    See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

----------------------------------------------
Documentation
----------------------------------------------

Use the built-in ``help`` function to view a function's docstring::

  >>> help(pa.compute_ccf)
  ... # doctest: +SKIP
  
----------------------------------------------
Available Functions
----------------------------------------------

The functions available in PARVATI may be divided in categories
according to their use:
1. Spectra ingestion and preparation
2. Single line extraction or mean line profile computation
3. Line analysis
4. Auxiliary functions

1. Spectra ingestion and preparation
----------------------------------------------
read_spectrum(filename, unit='a', wavecol=1, fluxcol=2, \
              nfluxcol=0, snrcol=0, echcol=0, errcol=0):
    Read the spectrum from an ASCII or FITS file
    
norm_spectrum(wave, flux, snr=False, echelle=False, deg=2, \
              n_ord=False, refine=False, output=False)
    Automatically normalise a stellar spectrum

2. Single line extraction or mean line profile computation
----------------------------------------------
read_mask(maskname, unit='a', ele=False, no_ele=False, depths=(0.01,1),\
          balmer=True, tellurics=True, wmin=False, wmax=False, absorption=False)
    Read stellar mask (either binary mask, VALD file, or spectrum)

compute_lsd(spectrum, mask_data, vrange=(-200,200), \
           step=1., cosmic=False, sigma=10, clean=False, \
           verbose=False, output=False)
    Compute the mean line profile using the Least-Squares Deconvolution
    Donati J.-F., et al., 1997, MNRAS 291, 658
    Kochukhov O., et al., 2010, A&A 524, 5

compute_ccf(spectrum, mask_data, vrange=(-200,200), step=1., \
           mask_spectrum=False, cosmic=False, sigma=10, clean=False, \
           weights=False, verbose=False, output=False)
    Compute the mean line profile using  Cross-Correlation Function

extract_line(spectrum, unit='a', w0=6562.801, vrange=(-200,200), \
            step=1., verbose=False, output=False)
    Extract a single line from a spectrum at w0 as a mean line profile

3. Line analysis
----------------------------------------------

norm_profile(profiles, rvcol=1, prfcol=2, errcol=0, sfx='pfn', \
             std='line_mean_std', limits=False)
    Normalise the profiles to account for continuum problems.

fit_profile(vrad, flux, errs=0, gauss=True, lorentz=True, voigt=True, \
            rot=True, rv0=0, width=10, ld=0.6)
    Fit a line profile

moments(rvs, ccf, errs=0, limits=False, normalise=True)
    Compute the line moments
    Briquet M., Aerts C., 2003, A&A 398, 687
    errors: Teague R., 2019, Res. Notes AAS 3, 74

bisector(rv_range, flux, errs=0, limits=False)
    Compute the bisector of a stellar line profile
    Baştürk Ö., et al., 2011, A&A 535, 17

fourier(rv_range, flux, errs=False, limits=False, ld=0.6)
    Compute the Fourier transform of the line
    The vsini is derived using the empirical formula from
    Dravins, D., Lindegren, L., & Torkelsson, U. 1990, A&A, 237, 137

4. Auxiliary functions
----------------------------------------------
split_spectrum(spectrum)
     Auxiliary function for compute_lsd/compute_ccf

rebin_spectrum(o_wave, o_flux, o_nflux, o_snr, wave_step)
     Auxiliary function for compute_lsd

remove_cosmics(len_vrange, o_split_nflux, sigma)
     Auxiliary function for compute_lsd/compute_ccf

smooth_spectrum(new_wave, o_split_nflux, fine_step=10)
     Auxiliary function for compute_lsd/compute_ccf
     
show_ccf(rvs,ccfs)
    Auxiliary function
    Plot line profiles and define line limits

func_rot(x,a,x0,xl,LD=0.6)
    Fitting function
    Rotational broadening function, from:
    Gray, D. F. 2008, The Observation and Analysis of Stellar Photospheres

gaussian(x,x0,s,F0,K):
    Fitting function
    Gaussian function

lorentzian(x, x0, g, F0, K)
    Fitting function
    Lorentzian function

voigt_function(x, x0, g, s, F0, K)
    Fitting function
    Voigt function    

find_shift_fft(y1, y2)
    Auxiliary function for fourier

"""

from parvati.parvati import *
__version__ = '1.0.5'
