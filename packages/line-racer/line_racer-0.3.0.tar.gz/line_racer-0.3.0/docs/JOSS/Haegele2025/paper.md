---
title: 'line racer: Rapid Calculation of Exoplanetary Radiative Opacities'
tags:
  - Python
  - astronomy
  - exoplanets
  - brown dwarfs
  - atmospheres
  - opacities
  - spectroscopy
languages:
  - Python
  - Fortran
authors:
  - name: David Hägele
    orcid: 0009-0009-7667-7003
    corresponding: true
    affiliation: "1, 2"  # (Multiple affiliations must be quoted)
  - name: Paul Mollière
    orcid: 0000-0003-4096-7067
    affiliation: 1
affiliations:
 - name: Max Planck Institut für Astronomie, Königstuhl 17 D-69117 Heidelberg, Germany
   index: 1
 - name: Ruprecht-Karls-Universität Heidelberg, Fakultät für Physik und Astronomie, Im Neuenheimer Feld 226, 69120 Heidelberg, Germany
   index: 2
   
submitted_at: '2025-12-16'
software_repository_url: "https://gitlab.com/David_Haegele/line_racer"
bibliography: paper.bib

# Optional fields if submitting to an AAS journal too, see this blog post:
# https://blog.joss.theoj.org/2018/12/a-new-collaboration-with-aas-publishing
# aas-doi: 10.3847/xxxxx <- update this with the DOI from AAS once you know it.
# aas-journal: Astrophysical Journal <- The name of the AAS journal.
---

# Summary

# Statement of need
With the expected revolution in high-resolution spectroscopy of exoplanet and brown dwarf atmospheres in the coming years, very accurate knowledge of the opacities of various molecular and atomic species is crucial.
Because of that, the line lists, which contain the information about the transitions between different energy levels of the molecules and atoms, are growing rapidly in size.
Databases like ExoMol [@Tennyson2024] now have line lists for multiple molecules with billions of lines. For example, the latest ExoMol methane line list MM [@Yurchenko2024] contains 50 billion lines.
Therefore, it is very challenging to compute the opacities accurately from these line lists in a reasonable time. 
`line racer` is explicitly designed to calculate high-resolution opacities from large line lists in a very efficient manner.
To achieve this, it uses a combination of two different algorithms for the line calculation:

1. A line profile calculation based on the algorithm by @Humlicek1982 with a speedup proposed by @Molliere2015.
2. A sampling technique of the line profiles based on the algorithm proposed by @Min2017.

This combination allows for a very fast calculation while maintaining a high accuracy. 
Compared to existing tools, `line racer` has a calculation time per line that is dependent on the importance of the line, which is a significant advantage for the largest line lists.
Moreover, it is automatically parallelized to be used on multiple nodes and cores, dependent on the user's needs and available hardware.

Due to the increasing resolution of observations, it is also becoming relevant how exactly the line profiles are treated in the opacity calculations. 
In particular, the line wings treatment can have a significant impact on the resulting opacities at high resolution. 
Therefore, `line racer` includes different options for the line wing treatment, such as a simple cutoff at a user-specified distance from the line center or a sub-Lorentzian treatment following @Hartmann2002.

The opacities calculated with `line racer` can be used for various applications in the field of exoplanet and brown dwarf atmospheres.
To be directly compatible with one of the most used atmospheric modeling and retrieval codes, `line racer` can output the opacities in petitRADTRANS [@Molliere2019] format in addition to a simple standard format.

# Line profile calculation
As already mentioned, the line profile calculation in `line racer` is split up into two different algorithms. The decision of which algorithm to use for the lines is decided based on their strength and the size of the line list.
For the strongest lines of a large line list, or for small line lists, the line profiles are calculated with the Humlicek algorithm [@Humlicek1982] combined with a speed-up proposed by @Molliere2015.
The speedup is achieved by calculating the line wings on a coarser grid and interpolating them to the fine grid. 

To do that, the wavelength grid is divided into sub-grids. For every sub-grid, the lines with their center inside the sub-grid are calculated on the fine grid. 
The lines outside the sub-grid are calculated on a coarser grid if certain criteria are met. Otherwise, they are also calculated on the fine grid.

The weaker lines of large line lists are calculated with a modified version of the line profile sampling technique proposed by @Min2017.
This technique is not calculating the line profiles on every grid point but instead samples them to a precision that is determined by the importance of the line. 
For example, if the line is only contributing to the continuum background of the opacity, it is sampled with just a few or one sample. 
By that, it still contributes as much as it is supposed to, but the time spent to calculate the line is minimized. 

The simplest way of sampling works as follows: 
The line profile we assume is a Voigt profile, which is a convolution of a Gaussian and a Lorentzian. 
When sampling a convolution from random numbers, it is sufficient to sample random numbers from the individual distributions and add them.
Therefore, for every sample of a line, a random number is drawn from a Gaussian distribution with a width corresponding to the Doppler width of the line. 
Another random number is drawn from a Lorentzian distribution with a width $\gamma$ corresponding to the natural and pressure broadening of the line.
The sum of these two random numbers is added to the line center to get the position of the sample. 
In the corresponding bin of the wavenumber grid, a constant contribution is added.
To construct the line profile, this procedure is repeated for a number of samples. 
This method works well, but it requires many samples, especially for high-resolution wavenumber grids.
Therefore, @Min2017 proposed a speedup, where the information of the sample is used more efficiently. 
The Lorentzian sample $\Delta\nu_\mathrm{press}$ is not just added to the Gaussian sample and the line center but spread out over an interval defined by the Lorentzian sample. 
For that, the sample is added and subtracted from the line center plus the Gaussian sample to define the interval. In this interval, a weight $w$ is distributed to the corresponding bins of the wavenumber grid. 
@Min2017 defined the weight, which is now not constant anymore but dependent on the sample as:
$$
w = \frac{\Delta\nu_\mathrm{press}^2}{\Delta\nu_\mathrm{press}^2 + \gamma^2}
$$
However, with this weight, the line is not normalized to the correct integrated area. The normalization afterward is very time-consuming. 
Therefore, we introduced a new weight definition that preserves the integrated area of the line directly, without the need for a normalization step afterward:
$$
w = \frac{2\Delta\nu_\mathrm{press}^2}{\Delta\nu_\mathrm{press}^2 + \gamma^2}\frac{S}{\mathrm{N_{samples}}}\frac{R}{\nu_\mathrm{eff}}
$$
The first term is adapted from @Min2017 to preserve the shape of the line; however, with an additional factor of two, which originates from the derivation of this factor.
The second term represents the intensity $S$ of the line divided by the number of samples $\mathrm{N_{samples}}$ used to sample the line, to ensure that the total line strength is preserved.
The third term accounts for the bin width of the logarithmic grid with a resolution $R$ and location of the line with effective wavenumber $\nu_\mathrm{eff}$.
With this definition of the weight, it is possible to calculate up to five million lines per second. 
However, this is very dependent on the pressure and temperature, and it is important to mention that the lines are not calculated on every grid point but rather reproduce the overall opacity.
This direct normalization is introducing a small uncertainty in the integrated intensity because the weight is dependent on the random samples. 
But since it scales inversely with the number of lines and samples and the technique is only used for huge line lists, it is negligible.

An additional speed-up implemented is the use of a coarser grid for large lines. For these lines, the profile does not change rapidly over the grid spacing, which allows for a coarser grid. 
Such an adaptive grid was previously used in Hedges and @Hedges2016 and @deRegt2025.

We note that there are other tools to compute opacities for exoplanet atmospheres, such as [`HELIOS-K`](https://helios-k2.readthedocs.io/en/latest/) [@Grimm2021], [`Cthulhu`](https://cthulhu.readthedocs.io/en/latest/) [@Agrawal2024], [`ExoCross`](https://exocross.readthedocs.io/en/latest/) [@Yurchenko2018], and [`pyROX`](https://py-rox.readthedocs.io/en/latest/) [@deRegt2025].

# Acknowledgements
We thank M. Min for helpful discussions about the sampling technique of the line profiles.

# References


