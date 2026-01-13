# EuclidEmulator2 (version 1.01. of the emulator, version 1.4.3 of the wrapper)
This repository contains the source code of EuclidEmulator2, a fast and accurate tool to estimate the non-linear correction to the matter power spectrum.
In contrast to its predecessor EuclidEmulator, EuclidEmulator2 allows for 8-parameter cosmological models including massive neutrinos (assuming a degenerate hierarchy) and dynamical dark energy. EuclidEmulator2 is written in C++. For more information on EuclidEmulator please visit https://github.com/miknab/EuclidEmulator.

Authors:   M. Knabenhans, Pedro Carrilho<br/>
Date of last update:      January 2026<br/>
Reference: Euclid Consortium: Knabenhans et al., <a>https://arxiv.org/abs/2010.11288</a><br/>

If you use EuclidEmulator2 in any way (for a publication or otherwise), please cite this paper.

<b>Contact information:</b> If you have any questions and/or remarks related to this wrapper, please do not hesitate to send an email to (pedromgcarrilhoATgmail.com).

## Currently implemented features in the wrapper
* emulation of the non-linear correction factor <i>B(k,z)</i>
* large allowed redshift interval: <i>z</i> in the interval [0.0,10.0]
* spatial scales spanning more than three orders of magnitude: 8.73 x 10<sup>-3</sup> <i>h</i> / Mpc ≤ <i>k</i> ≤ 9.41 <i>h</i> / Mpc.

* Cosmology defined via parameter dictionary
* Can output in custom k-range with extrapolation outside default range
* Interfaces with class to compute full non-linear matter power spectrum

See below for a tutorial on usage explaining these functionalities

## Quick start
### Prerequisites
In any case you need:
 * C++11 or later
 * GNU Scientific Library version 2.5 or higher (GSL; see https://www.gnu.org/software/gsl/)
 * g++ version 4.9.1 or higher
 * cython, numpy, scipy (essential)
 * classy (for computing non-linear power spectrum only)

#### GSL install
On most machines, building GSL is relatively simple. To install it locally, e.g. in `~/local/gsl`, use
```
mkdir -p $HOME/local/gsl && cd $HOME/local
wget -c ftp://ftp.gnu.org/gnu/gsl/gsl-latest.tar.gz -O - | tar zxv
```
The install procedure follows standard steps, but each one might take several minutes. Execute each command separately and only continue if there are no errors.
```
./configure --prefix=$HOME/local/gsl
make
make check
make install
```
 Once done, make sure to add the GSL library to your library path with
 ```
 export LD_LIBRARY_PATH=$HOME/local/gsl/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
 ```

If are able to use conda, you can also install gsl via `conda install gsl` and the Euclid Emulator 2 python installer should be able to find gsl automatically.

### Usage

To run the python wrapper, first import the package via
```
import euclidemu2
```
and create an instance of `PyEuclidEmulator` via
```
ee2 = euclidemu2.PyEuclidEmulator()
```
then create a python dictionary with the requested values of the cosmological parameters:
```
cosmo_par = {'As':2.1e-09, 'ns':0.966, 'Omb':0.04, 'Omm':0.3, 'h':0.68, 'mnu':0.15, 'w':-1.0, 'wa':0.0}
```
This can then be passed to the main function along with an array of redshifts
```
redshifts = [0,2,4,6,8,10]
k, b = ee2.get_boost(cosmo_par,redshifts)
```
resulting in an array `k` with the wavenumbers in units of <i>h</i> / Mpc and a dictionary `b` indexed with the same index as the redshift array, e.g. `b[1]` is an array corresponding to `redshifts[1]`, etc. This is always the case, even when only one redshift is requested, so accessing that array is always done via `b[0]`.

To calculate the boost for a custom range and sampling of k values, define an array with the requested values, e.g.
```
k_custom = np.geomspace(1e-4,100,1000)
```
and use
```
k, b = ee2.get_boost(cosmo_par,redshifts,k_custom)
```
where now `k=k_custom` and `b` gives the interpolated (extrapolated) boosts inside (outside) the default range.

If classy is installed, you can also get the full non-linear power spectrum via
```
k, pnl, plin, b = ee2.get_pnonlin(cosmo_par, redshifts, k_custom)
```
which will now output `pnl` in addition to the linear power spectrum `plin` and the boost `b`, which are all indexed in the same way as the boost from `get_boost`.

If classy is not installed, a warning will appear when loading `euclidemu2` and the `get_pnonlin` function will not work. The `get_boost` function will always work.

<b>Warning:</b> In the most recent versions of Python (e.g. 3.8) `classy` may not work unless it is the first package to be imported. This is taken into account when calling `euclidemu2`, but implies that `euclidemu2` must be the first package to be imported. This has been verified not to be a problem for older versions of python (e.g. 3.6).

See the python notebook (test_euclid_emu2.ipynb) for an example of a full run and more details.

## License
EuclidEmulator2 is free software, distributed under the GNU General Public License. This implies that you may freely distribute and copy the software. You may also modify it as you wish, and distribute these modified versions. You must always indicate prominently any changes you made in the original code and leave the copyright notices, and the no-warranty notice intact. Please read the General Public License for more details.
