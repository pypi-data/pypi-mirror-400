import inspect, types, os, gpflow, pickle
from typing import Dict, Any, Callable, Tuple
import pandas as pd  
from .gp_cachebasic import GPMC_posterior
import numpy as np

class GP_IPM:
    def __init__(self, popu_data: pd.DataFrame, POPUdata_dict: Dict[int, pd.DataFrame], 
                 GPmodel_mle: Dict[str, gpflow.models.GPModel], GPmodel: Dict[str, gpflow.models.GPModel], 
                 MCMC_samples:  Dict[str, gpflow.models.GPModel]):
        """
        Initializes the GP_IPM class with population data and two sets of Gaussian Process models. Ensures all keys in both GPmodel_mle and GPmodel start with 'm_'.

        Parameters:
        - popu_data: A DataFrame containing population data across multiple years.
        - POPUdata_dict: A dictionary mapping years to DataFrames of population data slices.
        - GPmodel_mle: A dictionary of fitted MLE GP models (using GPflow) for each vital rate, keyed by "m_" plus vital rate names, for example "m_sur" for survival.
        - GPmodel: A dictionary of fitted GP models (using GPflow) for each vital rate for Bayesian analysis, also keyed by "m_" plus vital rate names.
        - MCMC_samples: A dictionary of MCMC samples for models in GPmodel, also keyed by "m_" plus vital rate names.

        
        Each key in POPUdata_dict corresponds to a specific year, and the value is a DataFrame for that year's data.
        This structure allows for easy access and manipulation of data from specific years.
        """
        self.popu_data = popu_data
        self.POPUdata_dict = POPUdata_dict
        self.GPmodel_mle = self.validate_keys(GPmodel_mle, 'GPmodel_mle')
        self.GPmodel = self.validate_keys(GPmodel, 'GPmodel')
        self.MCMC_samples = self.validate_keys(MCMC_samples, 'MCMC_samples')
        self._vitalrate_names = self.extract_names

        # reorder: to make the oeder of vital rates being consistent 
        self.GPmodel = {k : self.GPmodel[k] for k in self._vitalrate_names}
        self.MCMC_samples = {k : self.MCMC_samples[k] for k in self._vitalrate_names}

        # Additional check to ensure keys in GPmodel_mle, GPmodel, MCMC_samples are identical
        self.validate_identical_keys(self.GPmodel_mle, self.GPmodel)
        self.validate_identical_keys(self.MCMC_samples, self.GPmodel)
        self.hmc_helper_builder


    # functions for input validations
    @staticmethod
    def validate_keys(input_sict: Dict[str, Any], model_name: str) -> Dict[str, Any]:
        """
        Validates that all keys in a GP model dictionary start with 'm_'. Raises ValueError if not.

        Parameters:
        - input_sict: The dictionary to validate.
        - model_name: The name of the model dictionary for error messaging.

        Returns:
        - The validated dictionary.
        """
        if not all(key.startswith('m_') for key in input_sict):
            raise ValueError(f"All keys in {model_name} must start with 'm_'.")
        return input_sict


    @staticmethod
    def validate_identical_keys(dict1: Dict[str, Any], dict2: Dict[str, Any]):
        """
        Validates that two dictionaries have identical keys. Raises ValueError if not.

        Parameters:
        - dict1: First dictionary to compare.
        - dict2: Second dictionary to compare.
        """
        if set(dict1.keys()) != set(dict2.keys()):
            raise ValueError("Keys in GPmodel_mle and GPmodel must be identical.")


    # functions for pre-processing
    @property
    def extract_names(self):
        return [key for key in self.GPmodel_mle.keys()]
    
    @property
    def hmc_helper_builder(self):
        for key in self._vitalrate_names:
            # Construct the attribute name by prefixing 'hmm_helper_' to each key
            attr_name = f"hmm_helper_{key}"
            setattr(self, attr_name, gpflow.optimizers.SamplingHelper(
                self.GPmodel[key].log_posterior_density,
                self.GPmodel[key].trainable_parameters
            ))

    # def hmc_helper_builder(self):
    #     gpflow.optimizers.SamplingHelper(
    #             model.log_posterior_density,
    #             model.trainable_parameters
    #         )


    # functions used to calculate Caches.
    def calculate_cache(self, file_path=os.getcwd()+f"/true_popu/Lm"):
        print('Caching cholesky decomposition...')
        for key in self._vitalrate_names:
            os.makedirs(f"{file_path}/{key}", exist_ok=True)
            _mcmcsamples = self.MCMC_samples[key] 
            _num_mcmcsamples = _mcmcsamples[0].shape[0]

            # _x, _y = self.GPmodel[key].data 
            # _build_model = getattr(self, attribute_name = f"build_new_m_{key}", f"Attribute build_new_m_{key} does not exist.")   
            # _model = _build_model(X=_x, y=_y)
            # _model_type = type(_model)
            # _hmchelper = gpflow.optimizers.SamplingHelper(
            #     _model.log_posterior_density, _model.m_rec_new.trainable_parameters
            #     )

            _model = self.GPmodel[key]
            _hmchelper = getattr(self, f"hmm_helper_{key}", None)  
            if _hmchelper is None:
                raise AttributeError(f"Attribute hmm_helper_{key} does not exist.") 

            for i in range(_num_mcmcsamples):
                for var, var_samples in zip(_hmchelper.current_state, _mcmcsamples):
                    var.assign(var_samples[i])

                if isinstance(_model, gpflow.models.gpr.GPR):
                    pickle.dump(_model.posterior().cache, open(file = f"{file_path}/{key}/{i}", mode="wb"))
                elif isinstance(_model, gpflow.models.gpmc.GPMC):
                    pickle.dump(GPMC_posterior(_model).cache, open(file = f"{file_path}/{key}/{i}", mode="wb"))
                else:
                    raise ValueError(f"{key} is {type(_model)}, which is not a supported GPmodel type for faster predictions.")

        print('Done')




    # functions allowing users to add their own methods
    def add_XY_compu(self, method: Callable):
        """
        Adds a new method to this instance of the class. The method name must follow the pattern 'XY_' + valid_name + '_compu',
        where valid_name is an element from GPmodel_mle or GPmodel. 
        The method can only take a dataset as input, and return the desired X and Y for model training.
        The added methods are supposed to take popu_data as input, and return 2D arrays (X_, Y_).

        Parameters:
        - method: A function to be added as a method.

        Raises:
        - ValueError: If the method name does not follow the required naming pattern.
        """

        valid_names = [f"XY_{name}_compu" for name in self._vitalrate_names]
        if method.__name__ not in valid_names:
            raise ValueError(f"Method name must follow the pattern 'XY_' + vital rate + '_compu'. Valid names for vital rates are: {self._vitalrate_names}")
        
        # Check method parameter type
        sig = inspect.signature(method)
        params = list(sig.parameters.values())
        if len(params) != 1 or not isinstance(params[0].annotation, type(pd.DataFrame)):
            raise ValueError("Method must have exactly one parameter of type pd.DataFrame")

        # Attempt to execute the method and validate output
        name_part = method.__name__.split('_')[2]  # Extract the 'vita rate' part
        model_key = f"m_{name_part}"  # Construct the corresponding model key
        if model_key not in self.GPmodel_mle:
            raise ValueError(f"No model entry found for '{model_key}' in GPmodel_mle.")

        expected_x, expected_y = self.GPmodel_mle[model_key].data
        actual_x, actual_y = method(self.popu_data)

        if not np.array_equal(expected_x, actual_x) or not np.array_equal(expected_y, actual_y):
            raise ValueError(f"Method output does not match the expected values when trainging {model_key} in GPmodel_mle.")


        # Create a wrapper that includes 'self' and calls the function
        def method_wrapper(self, *args, **kwargs):
            return method(*args, **kwargs)

        # Add the method to the class
        setattr(self, method.__name__, types.MethodType(method_wrapper, self))
        # setattr(self, method.__name__, types.MethodType(method, self))



    def add_model_build(self, method: Callable):
        """
        Adds a new method to this instance of the class. The method name must follow the pattern 'build_new_m_' + vital rate.
        The method can only take two parameters as input (X and y), and return a moel with exactly the same setting as the corrspodning model in GPmodel.

        Parameters:
        - method: A function to be added as a method.

        Raises:
        - ValueError: If the method name does not follow the required naming pattern.
        """

        valid_names = [f"build_new_{name}" for name in self._vitalrate_names]
        if method.__name__ not in valid_names:
            raise ValueError(f"Method name must follow the pattern 'build_new_m_' + vital rate. Valid names for vital rates are: {self._vitalrate_names}")
        

        # Check return type and model settings
        model_key = method.__name__[10:]  # Stripping 'build_new_m_' to get the vital rate name
        if model_key not in self.GPmodel:
            raise ValueError(f"No existing model configuration found for '{model_key}' in GPmodel.")

        # Inspect the method signature
        sig = inspect.signature(method)
        params = list(sig.parameters.values())

        # Check method parameter type
        sig = inspect.signature(method)
        params = list(sig.parameters.values())
        if len(params) != 1 or not isinstance(params[0].annotation, type(pd.DataFrame)):
            raise ValueError("Method must have exactly one parameter of type pd.DataFrame")

        # Testing the method with a sample DataFrame to verify output type and configuration
        test_output = method(self.popu_data)
        if not isinstance(test_output, gpflow.models.GPModel):
            raise ValueError("Returned object must be an instance of a GPflow model.")

        # Example configuration check (e.g., kernel type, likelihood)
        existing_model = self.GPmodel[model_key]
        if type(test_output.kernel) != type(existing_model.kernel) or type(test_output.likelihood) != type(existing_model.likelihood):
            raise ValueError(f"Returned GP model does not match the existing model settings of {model_key} in GPmodel.")

        if not self.are_priors_identical(test_output, existing_model):
            raise ValueError("Returned GP model does not have identical priors to the existing model.")

        # Create a wrapper that includes 'self' and calls the function
        def method_wrapper(self, *args, **kwargs):
            return method(*args, **kwargs)

        # Add the method to the class
        setattr(self, method.__name__, types.MethodType(method_wrapper, self))
        # setattr(self, method.__name__, types.MethodType(method, self))


    def are_priors_identical(self, model1, model2):
        """
        Checks if the priors of two GPflow models are identical.

        Args:
        model1, model2: GPflow models to compare.

        Returns:
        True if all priors are identical, False otherwise.
        """
        for param1, param2 in zip(model1.trainable_parameters, model2.trainable_parameters):
            if not isinstance(param1.prior, type(param2.prior)):
                return False
            if param1.prior is not None and param2.prior is not None:
                if not isinstance(param1.prior, type(param2.prior)) or param1.prior.parameters != param2.prior.parameters:
                    return False
        return True
    

