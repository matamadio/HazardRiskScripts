---
title: 'HazardStats'
tags:
  - Python
  - spatial analysis
  - zonal statistics
  - natural hazards
  - risk
authors:
  - name: Mattia Amadio ^[co-first author] # note this makes a footnote saying 'co-first author'
    orcid: 0000-0003-0359-4230
    affiliation: "1" # (Multiple affiliations must be quoted)
  - name: Takuya Iwanaga ^[co-first author] # note this makes a footnote saying 'co-first author'
    orcid: 0000-0001-8173-0870
    affiliation: "2" # (Multiple affiliations must be quoted)
affiliations:
 - name: World Bank GFDRR
   index: 1
 - name: Australian National University
   index: 2
date: 18 November2021
bibliography: paper.bib

# Optional fields if submitting to a AAS journal too, see this blog post:
# https://blog.joss.theoj.org/2018/12/a-new-collaboration-with-aas-publishing
aas-doi: 10.3847/xxxxx <- update this with the DOI from AAS once you know it.
aas-journal: Astrophysical Journal <- The name of the AAS journal.
---

# Summary

`HazardStats` is a program written in Python to calculate zonal statistics over multiple rasters
using parallel (multi-core) processing and threshold filtering according to standard deviations or
percentile clip.

# Statement of need
Zonal statistic is one of the key functions for running spatial assessment of hazard and
risk. Popular desktop environments for spatial analysis, such as QGIS and ArcGIS, can perform
zonal statistics, either natively or by using plugins, allowing analyses to be conducted by
those otherwise unfamiliar with available programmatic approaches. Some degree of preprocessing
is necessary for their efficient computational application. Common implementations require users
to provide a vector dataset that defines the area of interest and that the extents are equal or
similar to the raster layers being analyzed. Naively conducting zonal statistics can result in
excessively long processing times. Manually preprocessing large datasets is often unrealistic or
not ideal, particularly for those unaccustomed or inexperienced with programming or
multi-processing.

`HazardStats` is designed for researchers and geoanalysts in the context of natural hazards and
risk assessments. It aims to improve "quality of life" by enabling the processing of large numbers
of layers while also allowing additional filtering of input data. It consists of six core
functions, use of which can be scripted, or directly applied via a command-line interface. The
primary method of use, however, is through a simple "Question and Answer" style user interface, the
final product of which is an Excel spreadsheet with the final result. `HazardStats` has been
successfully used in a number of academic studies and technical reports.

`HazardStats` is open-source (under the [something something] license) and leverages

rasterio (https://github.com/rasterio/rasterio)
geopandas (https://github.com/geopandas/geopandas)
openpyxl (https://foss.heptapod.net/openpyxl/openpyxl)


`Gala` is an Astropy-affiliated Python package for galactic dynamics. Python
enables wrapping low-level languages (e.g., C) for speed without losing
flexibility or ease-of-use in the user-interface. The API for `Gala` was
designed to provide a class-based and user-friendly interface to fast (C or
Cython-optimized) implementations of common operations such as gravitational
potential and force evaluation, orbit integration, dynamical transformations,
and chaos indicators for nonlinear dynamics. `Gala` also relies heavily on and
interfaces well with the implementations of physical units and astronomical
coordinate systems in the `Astropy` package [@astropy] (`astropy.units` and
`astropy.coordinates`).

# Mathematics

Single dollars ($) are required for inline mathematics e.g. $f(x) = e^{\pi/x}$

Double dollars make self-standing equations:

$$\Theta(x) = \left\{\begin{array}{l}
0\textrm{ if } x < 0\cr
1\textrm{ else}
\end{array}\right.$$

You can also use plain \LaTeX for equations
\begin{equation}\label{eq:fourier}
\hat f(\omega) = \int_{-\infty}^{\infty} f(x) e^{i\omega x} dx
\end{equation}
and refer to \autoref{eq:fourier} from text.

# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @fidgit.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }

# References

See paper.bib
