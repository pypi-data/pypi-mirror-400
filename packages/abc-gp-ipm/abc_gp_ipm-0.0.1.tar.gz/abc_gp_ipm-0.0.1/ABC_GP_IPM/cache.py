# Cache functions: faster predictions

from typing import Optional, Tuple
import tensorflow as tf
from check_shapes import check_shapes
import gpflow
from gpflow import posteriors
from gpflow.base import InputData, MeanAndVariance
from gpflow.posteriors import VGPPosterior
from gpflow.models.model import GPModel
from gpflow.models.gpr import GPR_deprecated

# @check_shapes(
#     "Xnew: [batch..., N, D]",
#     # "Cache[0]: [M, D]",
#     # "Cache[1]: [M, M]",
#     "return[0]: [batch..., N, P]",
#     "return[1]: [batch..., N, P, N, P] if full_cov and full_output_cov",
#     "return[1]: [batch..., P, N, N] if full_cov and (not full_output_cov)",
#     "return[1]: [batch..., N, P, P] if (not full_cov) and full_output_cov",
#     "return[1]: [batch..., N, P] if (not full_cov) and (not full_output_cov)",
# )
def predict_f_loaded_cache(
    model: GPModel, 
    Xnew: InputData,
    Cache: Optional[Tuple[tf.Tensor, ...]],
    full_cov: bool = False,
    full_output_cov: bool = False,
) -> MeanAndVariance:
    """
    For backwards compatibility, GPR's predict_f uses the fused (no-cache)
    computation, which is more efficient during training.

    For faster (cached) prediction, predict directly from the posterior object, i.e.,:
        model.posterior().predict_f(Xnew, ...)
    """

    if isinstance(model, gpflow.models.gpr.GPR):
        posterior = model.posterior(posteriors.PrecomputeCacheType.NOCACHE)
        posterior.cache = Cache
        return posterior.predict_f(Xnew, full_cov=full_cov, full_output_cov=full_output_cov)
    
    elif isinstance(model, gpflow.models.gpmc.GPMC):
        X_data, _Y_data = model.data
        posterior = VGPPosterior(
            kernel = model.kernel,
            X = X_data,
            q_mu = model.V,
            q_sqrt = None,
            white = True,
            precompute_cache=None,
        )
        posterior.cache = Cache
        return posterior.predict_f(Xnew, full_cov=full_cov, full_output_cov=full_output_cov)
        
    else:
        raise ValueError(f"{model} is not a supported GPmodel type for faster predictions.")
         


def predict_y_loaded_cache(
    model: GPModel, 
    Xnew: InputData,
    Cache: Optional[Tuple[tf.Tensor, ...]],
    full_cov: bool = False,
    full_output_cov: bool = False,
) -> MeanAndVariance:
    """
    For backwards compatibility, GPR's predict_f uses the fused (no-cache)
    computation, which is more efficient during training.

    For faster (cached) prediction, predict directly from the posterior object, i.e.,:
        model.posterior().predict_f(Xnew, ...)
    """

    f_mean, f_var = predict_f_loaded_cache(
        model=model, Xnew=Xnew, Cache=Cache, full_cov=full_cov, full_output_cov=full_output_cov
    )

    return model.likelihood.predict_mean_and_var(Xnew, f_mean, f_var)



def GPMC_posterior(
    model: gpflow.models.gpmc.GPMC,
    precompute_cache: posteriors.PrecomputeCacheType = posteriors.PrecomputeCacheType.TENSOR,
) -> posteriors.VGPPosterior:
    
    X_data, _Y_data = model.data
    return posteriors.VGPPosterior(
        kernel=model.kernel,
        X=X_data,
        q_mu=model.V,
        q_sqrt=None,
        white=True,
        precompute_cache=precompute_cache,
    )


