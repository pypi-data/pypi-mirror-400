# ABC GP IPM

The integration of Gaussian Process (GP) models with Approximate Bayesian Computation (ABC) has been explored as a flexible framework for constructing Integral Projection Models (IPMs), enabling non-parametric modelling of demographic relationships and the incorporation of population-level information without explicit likelihoods. However, the practical implementation of this framework - particularly the selection of ABC summary statistics and the execution of ABC-PMC samplers - remains non-trivial and can limit its broader adoption.

To address this gap, we introduce ABC_GP_IPM, a Python package that provides a streamlined and user-friendly interface for constructing GP- and ABC-based IPMs.