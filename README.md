# OPUS_OpenSpecy-Conversion-
Micro-FTIR Spectral data from BRUKER LUMOS II with 32 x 32 FPA detector. Indiviudal spectra are preprocessed (Baseline Correction, and Normalized to max intensity 1.000) before being analyzed through open source polymer identification OpenSPecy. 
This is a preliminary code that is subjected to change. Feel free to email at March322@d.umn.edu for further quesitons. 
https://github.com/wincowgerDEV/OpenSpecy-package/blob/main/README.md
This will be an open source conversion upon completion. 

The baseline correction algorithm iteratively refines the baseline by fitting a polynomial and comparing the standard deviation of the residuals (dev_curr) with the previous iteration (dev_prev). It stops when the change in the residual deviation is less than 5%.
