from .gp_ipm import GP_IPM
from typing import Dict, Any, Callable, Tuple, Optional, List
import numpy as np
import pandas as pd
import ray
import inspect
import gpflow
f64 = gpflow.utilities.to_default_float
import sys, os
import time
import datetime
import pickle



class ABC_GP_IPM(GP_IPM):
    def __init__(self, GP_IPM_instance: GP_IPM, fun_ss: Callable, name_ss: List[str], ini_popu, 
                 fun_IBM_cache: Callable, fun_structure: Callable, fun_capture: Optional[Callable] = None, 
                 cache_path: str = None, fun_IBM_kwargs: Dict[str, Any] = None, 
                 fun_structure_kwargs: Dict[str, Any] = None, fun_capture_kwargs: Dict[str, Any] = None):
        """
        Initializes a new abc_gp_ipm instance which is specialized for Approximate Bayesian Computation
        using Gaussian Processes within an Individual-based Model framework.

        Args:
            GP_IPM_instance (GP_IPM): An instance of GP_IPM containing necessary population data and GP models.
            fun_ss (Callable): Function to calculate selected summary statistics. Takes two arguments:
                               exp_dataset (expected dataset), simu_dataset (simulated dataset).
            name_ss (List[str]): List of names for each summary statistic, used for referencing within analyses.
                                 The order and number of summary statistics calculated by fun_ss must match those in name_ss. 
            ini_popu: Initial population structure used for starting the IBM simulation in fun_IBM_cache.
            fun_IBM_cache (Callable): Function for performing a single step of IBM simulation through cached MCMC samples.
                                      Requires dataset and models dictionary as inputs.
            fun_structure (Callable): Function that returns the population structure from a given dataset.
                                      Requires data_simu (output from fun_IBM_cache) and time_step as inputs.
            fun_capture (Optional[Callable]): Optionally, a function to transform the simulation output into a format
                                              comparable with observed data sets. Takes data_simu and time_step as inputs.
            cache_path (str): Path to the directory where simulation results or data should be cached.
                              Defaults to a subdirectory 'true_popu/Lm' in the current working directory.
            fun_IBM_kwargs (Dict[str, Any]): Additional keyword arguments for fun_IBM_cache.
            fun_structure_kwargs (Dict[str, Any]): Additional keyword arguments for fun_structure.
            fun_capture_kwargs (Dict[str, Any]): Additional keyword arguments for fun_capture if used.
        """

        # Initialize with empty dictionaries if None is provided
        fun_IBM_kwargs = fun_IBM_kwargs or {}
        fun_structure_kwargs = fun_structure_kwargs or {}
        fun_capture_kwargs = fun_capture_kwargs or {}

        # Validate the existence of dynamically required attributes in GP_IPM_instance
        required_attributes = [f"XY_{name}_compu" for name in GP_IPM_instance._vitalrate_names]
        missing_attrs = [attr for attr in required_attributes if not hasattr(GP_IPM_instance, attr)]
        if missing_attrs:
            raise AttributeError(f"Missing attributes in GP_IPM instance: {', '.join(missing_attrs)}")
        
        # Ensure all previous validations and initializations are done
        super().__init__(GP_IPM_instance.popu_data, GP_IPM_instance.POPUdata_dict,
                         GP_IPM_instance.GPmodel_mle, GP_IPM_instance.GPmodel,
                         GP_IPM_instance.MCMC_samples)

        if not callable(fun_ss) or not callable(fun_IBM_cache) or not callable(fun_structure) or (fun_capture and not callable(fun_capture)):
            raise ValueError("All provided functions must be callable.")
        if not isinstance(name_ss, list) or not all(isinstance(name, str) for name in name_ss):
            raise ValueError("name_ss must be a list of strings.")

        if cache_path is None:
            cache_path = os.getcwd() + "/true_popu/Lm"

        # Validate and assign functions and attributes
        self.fun_ss = self.validate_function(fun_ss, ['exp_dataset', 'simu_dataset'], {})
        self.name_ss = name_ss
        self.ini_popu = ini_popu
        self.fun_IBM_cache = self.validate_function(fun_IBM_cache, ['dataset', 'models'], fun_IBM_kwargs)
        self.fun_IBM_kwargs = fun_IBM_kwargs if fun_IBM_kwargs is not None else {}
        self.cache_path = cache_path or os.getcwd() + "/true_popu/Lm"
        self.fun_structure = self.validate_function(fun_structure, ['data_simu', 'time_step'], fun_structure_kwargs)
        self.fun_structure_kwargs = fun_structure_kwargs if fun_structure_kwargs is not None else {}
        self.fun_capture = self.validate_function(fun_capture, ['data_simu', 'time_step'], fun_capture_kwargs) if fun_capture else None
        self.fun_capture_kwargs = fun_capture_kwargs if fun_capture_kwargs is not None else {}
        self.capture = self.fun_capture is not None
        self.n_samples = self.number_samples()
        


    def validate_function(self, func: Callable, required_args: List[str], additional_kwargs: Dict[str, Any] = None):

        """
        Validates the function's signature and ensures it can accept additional keyword arguments.

        Args:
            func: The function to validate.
            required_args: A list of required argument names.
            additional_kwargs: Additional keyword arguments to be used with the function.

        Returns:
            A function wrapper that incorporates additional keyword arguments.
        """
        actual_args = inspect.getfullargspec(func).args
        if not all(arg in actual_args for arg in required_args):
            raise ValueError(f"Function must have at least these arguments: {required_args}")

        def wrapper(*args, **kwargs):
            # Combine provided kwargs with additional kwargs and pass them to the function
            all_kwargs = {**additional_kwargs, **kwargs}
            return func(*args, **all_kwargs)

        return wrapper


    def number_samples(self):
        n_samples = [] 
        for key in self.MCMC_samples:
            n_samples.append(self.MCMC_samples[key][0].shape[0])
        return n_samples 


    # build IPM_whole by given random indeces for each vital rate's MCMC sample (in parallel computing)
    def random_IPM_whole_para(self, total_samples, num_cores, given_weight=False):
        # total_samples: Total number of simulated samples required.
        # num_cores: number of cores used for parallel computing. 
        result = []
        simulators = [para_ipmmcmc_whole.remote(self) for _ in range(num_cores)]
        if given_weight==False:
            for _ in np.arange(0, total_samples, num_cores):
                result.extend(ray.get([s.random_IPM_ABC.remote() for s in simulators])) 
        else:
            for _ in np.arange(0, total_samples, num_cores):
                result.extend(ray.get([s.random_IPM_ABC_weight.remote() for s in simulators]))

        return result
    

    # implement IPM ABC simulation by a random index of MCMC samples (same weights)
    def random_IPM_ABC(self):
        index = np.random.randint(low=0, high=self.n_samples)

        return self.IPM_whole_givenindex(index)

    # implement IPM ABC simulation by a random index of MCMC samples by a given weights
    def random_IPM_ABC_weight(self):
        # randomly select a particle from the previous step.
        index = self.p_index[np.random.choice(self.p_index.shape[0], p=self.weight)].copy()
        _vital_tobe_replaced = np.random.randint(0, len(self.n_samples))
        index[_vital_tobe_replaced] = np.random.randint(0, self.n_samples[_vital_tobe_replaced]) 

        return self.IPM_whole_givenindex(index) 



    def IPM_whole_givenindex(self, index):

        models_now2 = self.GPmodel.copy()

        # model set up.
        for k, key in enumerate(self.MCMC_samples):

            _hmc_helper = gpflow.optimizers.SamplingHelper(
                models_now2[key].log_posterior_density,
                models_now2[key].trainable_parameters
            )
            # assigning values to hyperparameters from MCMC samples
            for var, var_samples in zip(_hmc_helper.current_state, self.MCMC_samples[key]):
                var.assign(var_samples[index[k]])

            models_now2[key].cache = pickle.load(open(file = f"{self.cache_path}/{key}/{index[k]}", mode="rb")) 

        # Actually, we do not have to define s separately with c_s , just keep the format for easier use in latter steps.
        s = []
        # for range(1) just in case if want to modify the code to repeat the process serveal more times in a single simulation.
        for _ in range(1): 
            c_s = []
            data_simu = self.fun_IBM_cache(dataset=self.ini_popu, models=models_now2, **self.fun_IBM_kwargs)
            
            if (data_simu.shape[0] == 0) or (data_simu.shape[0] == 1):
                return (index, [[np.repeat(np.inf, ) for _ in range(len(self.POPUdata_dict))]])

            if self.capture == False: 
                current_s = self.fun_ss(exp_dataset=self.POPUdata_dict[0], simu_dataset=data_simu)
            else:
                simu_ob = self.fun_capture(data_simu = data_simu, time_step=0, **self.fun_capture_kwargs)
                current_s = self.fun_ss(exp_dataset=self.POPUdata_dict[0], simu_dataset=simu_ob)
            
            c_s.append(current_s)
                
            for t in range(1, len(self.POPUdata_dict)):

                wt = self.fun_structure(data_simu, time_step=t, **self.fun_structure_kwargs)
                data_simu = self.fun_IBM_cache(dataset=wt, models=models_now2, **self.fun_IBM_kwargs)
                    
                if (data_simu.shape[0] == 0) or (data_simu.shape[0] == 1):
                    return (index, [[np.repeat(np.inf, ) for _ in range(len(self.POPUdata_dict))]])

                if self.capture == False: 
                    current_s = self.fun_ss(exp_dataset=self.POPUdata_dict[t], simu_dataset=data_simu)
                else:
                    simu_ob = self.fun_capture(data_simu = data_simu, time_step=t, **self.fun_capture_kwargs)
                    current_s = self.fun_ss(exp_dataset=self.POPUdata_dict[t], simu_dataset=simu_ob)
                
                c_s.append(current_s)

            s.append(c_s)

        return (index, s)
    


    def ABC_PMC(self, quantiles, n_particles, num_cores, details=True, smallest_unit=10000, file_path2store=os.getcwd()+f"/ABC_details",
                algo_continue=False, hist_mad=None, hist_threshold=None, hist_index=None, hist_weight=None):
        # num_cores: number of cores used for parallel computing.
        # smallest_unit: smallest number of repeatations implenmented when conducting ABC-PMC.

        os.makedirs(f"{file_path2store}", exist_ok=True) 
        if isinstance(n_particles, int):
            sys.exit("n_particle should be an array or a list! ")

        if (len(quantiles)) != len(n_particles):
            sys.exit("len(quantiles) should equal to len(n_particles)")


        if (algo_continue==True) and ((hist_mad==None) or (hist_threshold==None) or (hist_index==None) or (hist_weight==None)):
            sys.exit("Please provide all the history files to continue th algorithm.")

        if algo_continue == False:
            # for SMC iteration c=0
            print('c=0 ' + time.strftime("%H:%M:%S", time.localtime()), flush=True)
            particles = np.array(self.random_IPM_whole_para(total_samples=n_particles[0], given_weight=False, num_cores=num_cores), dtype=object)
            particles_summary = np.array([item for sublist in particles[:, 1] for item in sublist])
            particles_index = np.array([sublist for sublist in particles[:, 0]]); del(particles) # reliease memory

            if details == True:
                np.save(open(file = os.getcwd()+"/ABC_details/p_index_ini.pkl", mode="wb"), particles_index)

            # reshape
            c_shape = particles_summary.shape
            particles_summary = particles_summary.reshape((c_shape[0], c_shape[1]*c_shape[2]))
            self.mad = np.nanmedian(np.absolute(particles_summary - np.nanmedian(particles_summary, axis=0)), axis=0)
            s_mean = np.nanmean(particles_summary, axis=0)
            s_median = np.nanmedian(particles_summary, axis=0)
            dis = np.sqrt(np.sum((particles_summary/self.mad)**2, axis=1))

            # dis = np.sum(particles_summary/self.baseline, axis=1)
            # we do NOT accept all the particles at c=0 in this version.
            self.threshold = np.nanquantile(dis, axis=0, q=quantiles[0])
            # we prefer particles with smaller value in distance.
            accepted = np.repeat(True, particles_index.shape[0]) #dis <= self.threshold

            self.p_index = particles_index[accepted]
            self.weight = np.repeat(1/np.sum(accepted), np.sum(accepted))

            print(f'Total: {particles_index.shape[0]}', flush=True)
            print(f'Left: {self.p_index.shape[0]}', flush=True)
            print(f'Unique: {np.unique(self.p_index , axis=0).shape[0]} \n', flush=True)

            if details == True:
                np.save(open(file = file_path2store+f"/particles_summary{0}.pkl", mode="wb"), particles_summary)
                np.save(open(file = file_path2store+f"/accepted{0}.pkl", mode="wb"), accepted)
                np.save(open(file = file_path2store+f"/p_index_{0}.pkl", mode="wb"), self.p_index)
                np.save(open(file = file_path2store+f"/threshold{0}.pkl", mode="wb"), self.threshold)
                np.save(open(file = file_path2store+f"/weight{0}.pkl", mode="wb"), self.weight)
                np.save(open(file = file_path2store+f"/mad{0}.pkl", mode="wb"), self.mad)
                np.save(open(file = file_path2store+f"/r_s_mean{0}.pkl", mode="wb"), s_mean)
                np.save(open(file = file_path2store+f"/r_s_median{0}.pkl", mode="wb"), s_median)
            del(particles_summary); del(particles_index); del(c_shape)

        else:
            self.p_index = np.load(open(file = hist_index, mode="rb"))
            self.weight = np.load(open(file = hist_weight, mode="rb"))
            self.mad = np.load(open(file = hist_mad, mode="rb"))
            self.threshold = np.load(open(file = hist_threshold, mode="rb"))

        # for SMC iteration c>0
        for c in range(1, len(quantiles)):
            print(f'c={c} ' + time.strftime("%H:%M:%S", time.localtime()), flush=True)

            n_alive_particles=0
            c_summary = []
            c_index = []
            total_summary = []

            while n_alive_particles<n_particles[c]:
                particles = np.array(self.random_IPM_whole_para(total_samples=smallest_unit, given_weight=True, num_cores=num_cores), dtype=object)
                particles_summary = np.array([item for sublist in particles[:, 1] for item in sublist])
                particles_index = np.array([sublist for sublist in particles[:, 0]]); del(particles)
                # reshape
                c_shape = particles_summary.shape
                particles_summary = particles_summary.reshape((c_shape[0], c_shape[1]*c_shape[2]))

                # dis = np.sum(particles_summary/self.baseline, axis=1)
                dis = np.sqrt(np.sum((particles_summary/self.mad)**2, axis=1))

                # accept or reject based on the thershold computed from the previous step.
                accepted = dis <= self.threshold
                # update
                c_summary.extend(particles_summary[accepted])
                total_summary.extend(particles_summary)
                c_index.extend(particles_index[accepted]); del(particles_summary); del(particles_index); del(c_shape); del(dis)
                n_alive_particles = n_alive_particles+accepted.sum(); del(accepted)
                print('  '+time.strftime("%H:%M:%S", time.localtime()) + f' Required: {n_particles[c]}, Now: {n_alive_particles}', flush=True)

            t_summary = np.array([ii for ii in total_summary]); del(total_summary)
            s_mean = np.nanmean(t_summary, axis=0)
            s_median = np.nanmedian(t_summary, axis=0)
            self.mad = np.nanmedian(np.absolute(t_summary - np.nanmedian(t_summary, axis=0)), axis=0); del(t_summary)

            c_index2 = np.array([ii for ii in c_index]); del(c_index) # just tranform it from a list to an np.array
            c_weight = []
            for kk in range(c_index2.shape[0]):
                neighbour = np.sum(self.p_index == c_index2[kk], axis=1) >= 3
                c_weight.append(1/np.sum(self.weight[neighbour]))

            self.weight = c_weight/np.sum(c_weight); del(c_weight)
            self.p_index = c_index2; del(c_index2)
            summary = np.array([ii for ii in c_summary]); del(c_summary)
            dis_now = np.sqrt(np.sum((summary/self.mad)**2, axis=1))
            self.threshold = np.nanquantile(dis_now, axis=0, q=quantiles[c])

            # print(f'Total: {particles_index.shape[0]}', flush=True)
            print(f'Left: {self.p_index.shape[0]}', flush=True)
            print(f'Unique: {np.unique(self.p_index , axis=0).shape[0]} \n', flush=True)

            if details == True:
                np.save(open(file = file_path2store+f"/particles_summary{c}.pkl", mode="wb"), summary)
                np.save(open(file = file_path2store+f"/p_index_{c}.pkl", mode="wb"), self.p_index)
                np.save(open(file = file_path2store+f"/threshold{c}.pkl", mode="wb"), self.threshold)
                np.save(open(file = file_path2store+f"/weight{c}.pkl", mode="wb"), self.weight)
                np.save(open(file = file_path2store+f"/mad{c}.pkl", mode="wb"), self.mad)
                np.save(open(file = file_path2store+f"/r_s_mean{c}.pkl", mode="wb"), s_mean)
                np.save(open(file = file_path2store+f"/r_s_median{c}.pkl", mode="wb"), s_median)
            del(summary)

        return (self.p_index, self.threshold)




    def simulate(self, abc_index: np.ndarray, abc_weight: np.ndarray, num_samples: int,
                 simu_length: int, fun_pop_metric: Callable, fun_IBM: Callable, 
                 fun_pop_metric_kwargs: Dict[str, Any] = None, fun_IBM_kwargs: Dict[str, Any] = None):
        """
        Run simulations based on sampled abc_index and abc_weight after ABC-PMC sampling.

        Args:
        - abc_index (np.ndarray): Sampled indices from the ABC process.
        - abc_weight (np.ndarray): Weights associated with each sampled index.
        - num_samples (int): The number of simulated samples to generate.
        - simu_length (int): The length of the simulation in time steps.
        - fun_pop_metric (Callable): Function to calculate population metrics based on the simulation output.
            Takes `data_simu` and `time_step` as inputs.
        - fun_pop_metric_kwargs (Dict[str, Any], optional): Additional keyword arguments for `fun_pop_metric`.
        - fun_IBM (Callable): Function for performing a single step of an IBM simulation.
            Takes `dataset` and `models` dictionary as inputs.
        - fun_IBM_kwargs (Dict[str, Any], optional): Additional keyword arguments for `fun_IBM`.
        
        Returns:
        - Simulated data or processed results depending on the provided functions.
        """

        # Args checks:
        # shape checks:
        if abc_weight.shape[0] != abc_index.shape[0]:
            raise ValueError("The shape of abc_weight and abc_index are inconsistent.")
        
        if len(self.n_samples) != abc_index.shape[1]:
            raise ValueError("The shape of abc_index is inconsistent with the number of vital rates.")
        

        if not callable(fun_pop_metric) or not callable(fun_IBM):
            raise ValueError("All provided functions must be callable.")
        
        # Initialize with empty dictionaries if None is provided
        fun_IBM_kwargs = fun_IBM_kwargs or {}
        fun_pop_metric_kwargs = fun_pop_metric_kwargs or {}
        fun_pop_metric = self.validate_function(fun_pop_metric, ['data_simu', 'time_step'], fun_pop_metric_kwargs)
        fun_pop_metric_kwargs = fun_pop_metric_kwargs if fun_pop_metric_kwargs is not None else {}
        fun_IBM = self.validate_function(fun_IBM, ['dataset', 'models'], fun_IBM_kwargs)
        fun_IBM_kwargs = fun_IBM_kwargs if fun_IBM_kwargs is not None else {}

        abc_pop_metric = []
        for i in range(num_samples):
            c_index = abc_index[np.random.choice(abc_weight.shape[0], p=abc_weight)]

            models_now = self.GPmodel.copy()

            # model set up.
            for k, key in enumerate(self.MCMC_samples):

                _hmc_helper = gpflow.optimizers.SamplingHelper(
                    models_now[key].log_posterior_density,
                    models_now[key].trainable_parameters
                )
                # assigning values to hyperparameters from MCMC samples
                for var, var_samples in zip(_hmc_helper.current_state, self.MCMC_samples[key]):
                    var.assign(var_samples[c_index[k]])

            ps = []
            simu_data = fun_IBM(dataset=self.ini_popu, models=models_now, **fun_IBM_kwargs)
            for t in range(1, simu_length):
                ps_0 = fun_pop_metric(simu_data, time_step=t, **fun_pop_metric_kwargs)
                ps.append(ps_0)
                wt = self.fun_structure(simu_data, time_step=t, **self.fun_structure_kwargs)
                simu_data = fun_IBM(dataset=wt, models=models_now, **fun_IBM_kwargs); del(wt) 
                
            ps_0 = fun_pop_metric(simu_data, time_step=simu_length, **fun_pop_metric_kwargs)
            ps.append(ps_0)  
            abc_pop_metric.append(ps)


        return abc_pop_metric 
                



@ray.remote
class para_ipmmcmc_whole():
    def __init__(self, ipmmcmc_whole):
        # m is an object belonging to ipmmcmc_whole
        self.ipmmcmc_whole = ipmmcmc_whole
    
    def random_IPM_ABC(self):
        return self.ipmmcmc_whole.random_IPM_ABC()

    def random_IPM_ABC_weight(self):
        return self.ipmmcmc_whole.random_IPM_ABC_weight()