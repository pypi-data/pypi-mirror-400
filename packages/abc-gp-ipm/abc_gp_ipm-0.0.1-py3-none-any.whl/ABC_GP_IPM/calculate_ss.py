from .gp_ipm import GP_IPM
from typing import Dict, Any, Callable, Tuple
import numpy as np
import pandas as pd
import ray
import inspect
from sklearn.metrics import roc_curve, auc
import copy  
import gpflow

class Perted_IPM(GP_IPM):
    def __init__(self, GP_IPM_instance: GP_IPM, target: str, fun_ss: Callable, name_ss: list, 
                 opt_percentage: float, fun_IBM: Callable, **fun_IBM_kwargs):

        # Initializes a Perted_IPM instance which performs perturbed individual-based modeling.
        
        # Args:
        #     GP_IPM_instance (GP_IPM): 
        #         An instance of GP_IPM containing necessary population data and GP models.
        #     target (str): 
        #         The key from GP_IPM_instance.GPmodels to which perturbation and simulations are targeted.
        #     fun_ss (Callable): 
        #         Function that calculates a list of candidate summary statistics.
        #         Must take exactly two arguments: 
        #         - exp_dataset: Expected (true) dataset.
        #         - simu_dataset: Simulated dataset.
        #     name_ss (List[str]): 
        #         List of names for each summary statistic, used for referencing within analyses.
        #     opt_percentage (float): 
        #         Percentage (0 to 100) of MCMC samples to consider around the optimum for analysis.
        #     fun_IBM (Callable): 
        #         Function for performing a single step of IBM simulation.
        #         Takes at least two arguments:
        #         - dataset: Initial population structure and environmental factors.
        #         - models: Dictionary of fitted GP models for Bayesian analysis, keyed by 'm_' plus vital rate names.
        #     **fun_IBM_kwargs:
        #         Additional keyword arguments to pass to fun_IBM, allowing for dynamic simulation adjustments.


        # Validate the existence of dynamically required attributes in GP_IPM_instance
        required_attributes = [formatted_name for name in GP_IPM_instance._vitalrate_names for formatted_name in (f"XY_{name}_compu", f"build_new_{name}")]
        missing_attrs = [attr for attr in required_attributes if not hasattr(GP_IPM_instance, attr)]
        if missing_attrs:
            raise AttributeError(f"Missing attributes in GP_IPM instance: {', '.join(missing_attrs)}")

        # Ensure all previous validations and initializations are done
        super().__init__(GP_IPM_instance.popu_data, GP_IPM_instance.POPUdata_dict,
                         GP_IPM_instance.GPmodel_mle, GP_IPM_instance.GPmodel,
                         GP_IPM_instance.MCMC_samples)

        # Validate other parameters 
        if target not in GP_IPM_instance.GPmodel:
            raise ValueError(f"Target '{target}' is not a valid key in GPmodel. Available keys: {list(GP_IPM_instance.GPmodel.keys())}")
        if not (0 <= opt_percentage <= 100):
            raise ValueError("opt_percentage must be a float between 0 and 100 inclusive.")
        if not callable(fun_ss) or not callable(fun_IBM):
            raise ValueError("Both fun_ss and fun_IBM must be callable functions.")
        if not isinstance(name_ss, list) or not all(isinstance(name, str) for name in name_ss):
            raise ValueError("name_ss must be a list of strings.")


        # Assign remaining class attributes
        self.target = target
        self.fun_ss = self.validate_fun_ss(fun_ss)
        self.name_ss = name_ss
        self.opt_percentage = opt_percentage
        self.fun_IBM = self.validate_fun_IBM(fun_IBM, fun_IBM_kwargs)
        self.fun_IBM_kwargs = fun_IBM_kwargs
        self.GP_IPM_instance = GP_IPM_instance



    def validate_fun_ss(self, func):
        expected_args = ['exp_dataset', 'simu_dataset']
        actual_args = inspect.getfullargspec(func).args

        if actual_args != expected_args:
            raise ValueError(f"Function: fun_ss must have exactly these arguments: {expected_args}")

        def wrapper(exp_dataset, simu_dataset):
            return func(exp_dataset, simu_dataset)

        return wrapper

    def validate_fun_IBM(self, func, func_kwargs):
        expected_args = ['dataset', 'models']
        actual_args = inspect.getfullargspec(func).args[:2]  # Only consider the first two expected arguments

        if actual_args[:2] != expected_args:
            raise ValueError(f"Function: fun_IBM must have exactly these first two arguments: {expected_args}")

        def wrapper(dataset, models):
            return func(dataset, models, **func_kwargs)  # Pass **kwargs to fun_IBM

        return wrapper

    # the function used to calculate log_posterior_density 
    def log_posterior_density(self):
        _lp = np.array([])
        _samples = self.MCMC_samples[self.target]
        _hmc_helper = getattr(self, f"hmm_helper_{self.target}", None)

        for i in range(_samples[0].shape[0]):
            for var, var_samples in zip(_hmc_helper.current_state, _samples):
                var.assign(var_samples[i])
            
            _lp = np.append(_lp, np.array(self.GPmodel[self.target].log_posterior_density()))

        return _lp 
    
##########################################################################################################################
#       we define a simulation function for calculating summary around optimum 
#      (simulated datasets generated by interested_models VS simulated datasets generated by the other given MCMC samples) 
#      (1 model VS M models)
#      (N datasets generated by 1 model VS N datasets generated by M model, where N is the value of repetition and M is decided by opt_percentage. 


    def ss_optVSmcmc(self, repetition, random_seed, log_posterior_density, test_data, num_cores):
        # test_data: a dataset can be directly fed to fun_IBM to performance simulation.
        # num_cores: number of cores used for parallel computing.

        if not isinstance(repetition, int) or repetition <= 0:
            raise ValueError("the total number of repetition must be a positive integer.")

        if not isinstance(random_seed, int) or random_seed <= 0:
            raise ValueError("random_seed must be a positive integer.")

        if not isinstance(num_cores, int) or num_cores <= 0:
            raise ValueError("num_cores must be a positive integer.")
        
        self.nlog_post = log_posterior_density
        self.test_data = test_data
        _MCMC_index_list = self.whether_around_opt_comp
        
        # set random seeds
        self.rep = repetition
        num_total_samples = self.MCMC_samples[self.target][0].shape[0]
        self._num_current_samples = np.sum(_MCMC_index_list)
        self.list_seed = self._list_seed_comp(rep=repetition, random_seed=random_seed, num_samples=num_total_samples)
        
        # set up: data sets
        summary_data = pd.DataFrame(data=0.0,  index=range(0, self._num_current_samples*repetition), 
                                    columns=np.append(self.name_ss,['i']))

        # set up: find the interested model.

        # _hmc_helper = getattr(self, f"hmm_helper_{self.target}", None)
        # # assigning values to hyperparameters from MCMC samples
        # for var, var_samples in zip(_hmc_helper.current_state, self.MCMC_samples[self.target]):
        #     var.assign(var_samples[self.opt_comp])
        # self.models_interested = self._build_models(self.GPmodel[self.target])

        m_new_opti = getattr(self.GP_IPM_instance, 'build_new_'+self.target)(self.popu_data)
        _hmc_helper = gpflow.optimizers.SamplingHelper(
            m_new_opti.log_posterior_density, m_new_opti.trainable_parameters
            )
        for var, var_samples in zip(_hmc_helper.current_state, self.MCMC_samples[self.target]):
            var.assign(var_samples[self.opt_comp])
        self.models_interested = self._build_models(m_new_opti)





        print(f"\n\n\n\n Parallel computing is starting \n with repeat time {repetition} and random seed {random_seed}.\n\n\n\n")
        
        i_list = np.arange(0, num_total_samples)[_MCMC_index_list]

        n_actor = num_cores
        result_s = []
        simulators = [para_Perted_IPM.remote(self) for _ in range(n_actor)]
        for i in np.arange(0, self._num_current_samples, n_actor):
            if i == (self._num_current_samples//n_actor * n_actor):
                remainder_p1 = self._num_current_samples%n_actor
                result_s.append(ray.get([s.simuVSsimu_fun.remote(i_list[k+i]) for k,s in enumerate(simulators[:remainder_p1])]))
            else: 
                result_s.append(ray.get([s.simuVSsimu_fun.remote(i_list[k+i]) for k,s in enumerate(simulators)]))

        K = len(result_s[0])
        for j in range(len(result_s)):
            for k, result in enumerate(result_s[j]):
                result.index = range(K*repetition*j+(k*repetition), K*repetition*j+(k+1)*repetition)
                summary_data.loc[(K*repetition*j+(k*repetition)):(K*repetition*j+(k+1)*repetition-1)] = result.copy()
                
        del(self.models_interested); del(self.rep); del(self.list_seed); del(self.nlog_post); del(self.test_data)
        
        return summary_data



    def simuVSsimu_fun(self, i):
        # i: a single index of MCMC sample you want to use to do the simulations.

        # model initialize
        # _samples = self.MCMC_samples[self.target]
        # _hmc_helper = getattr(self, f"hmm_helper_{self.target}", None)
        # # assigning values to hyperparameters from MCMC samples
        # for var, var_samples in zip(_hmc_helper.current_state, _samples):
        #     var.assign(var_samples[i])
        # models_2 = self._build_models(self.GPmodel[self.target])

        # model initialize
        m_new = getattr(self.GP_IPM_instance, 'build_new_'+self.target)(self.popu_data)
        # assigning values to hyperparameters from MCMC samples
        _hmc_helper = gpflow.optimizers.SamplingHelper(
            m_new.log_posterior_density, m_new.trainable_parameters
            )
        for var, var_samples in zip(_hmc_helper.current_state, self.MCMC_samples[self.target]):
            var.assign(var_samples[i])
        models_2 = self._build_models(m_new)


        np.random.seed(self.list_seed[i])
        summary_data = pd.DataFrame(data=0.0,  index=range(self.rep), columns=self.name_ss)

        for j in range(self.rep):
            # generating dataset with models1
            simu_1step_data1 = self.fun_IBM(dataset=self.test_data, models=self.models_interested, **self.fun_IBM_kwargs)
            # generating datasetwith models2
            simu_1step_data2 = self.fun_IBM(dataset=self.test_data, models=models_2, **self.fun_IBM_kwargs)
            # a list of summary stats at current time
            current_s = self.fun_ss(exp_dataset=simu_1step_data1, simu_dataset=simu_1step_data2)
            summary_data.iloc[j,:] = current_s        

        summary_data['i'] = np.array(i)

        return summary_data


##########################################################################################################################
# 2nd, now, we define a simulation function to compare populations generated by the same model.
#      (a simulated dataset generated by a model VS another simulated datasets generated the same model) 
#      (1 model VS 1 model)
#      (N VS N datasets generated by 1 model, where N is the value of repetition)

    def ss_optVSopt(self, repetition, random_seed, log_posterior_density, test_data, num_cores):

        if not isinstance(repetition, int) or repetition <= 0:
            raise ValueError("the total number of repetition must be a positive integer.")

        if not isinstance(random_seed, int) or random_seed <= 0:
            raise ValueError("random_seed must be a positive integer.")

        if not isinstance(num_cores, int) or num_cores <= 0:
            raise ValueError("num_cores must be a positive integer.")
        
        # set random seeds
        self.rep = repetition
        self.list_seed = self._list_seed_comp(rep=repetition, random_seed=random_seed, num_samples=repetition)
        self.nlog_post = log_posterior_density
        self.test_data = test_data


        summary_data = pd.DataFrame(data=0.0,  index=range(0, repetition), columns=self.name_ss)

        # set up: find the interested model.
        # _hmc_helper = getattr(self, f"hmm_helper_{self.target}", None)
        # # assigning values to hyperparameters from MCMC samples
        # for var, var_samples in zip(_hmc_helper.current_state, self.MCMC_samples[self.target]):
        #     var.assign(var_samples[self.opt_comp])
        # self.models_interested = self._build_models(self.GPmodel[self.target])
        m_new_opti = getattr(self.GP_IPM_instance, 'build_new_'+self.target)(self.popu_data)
        _hmc_helper = gpflow.optimizers.SamplingHelper(
            m_new_opti.log_posterior_density, m_new_opti.trainable_parameters
            )
        for var, var_samples in zip(_hmc_helper.current_state, self.MCMC_samples[self.target]):
            var.assign(var_samples[self.opt_comp])
        self.models_interested = self._build_models(m_new_opti)

        print(f"\n\n\n\n Parallel computing is starting \n with repeat time {self.rep} and random seed {random_seed}.\n\n\n\n")
        
        i_list = np.arange(0, repetition)

        n_actor =num_cores
        result_s = []
        simulators = [para_Perted_IPM.remote(self) for _ in range(n_actor)]
        for i in np.arange(0, repetition, n_actor):
            if i == (repetition//n_actor * n_actor):
                remainder_p1 = repetition%n_actor
                result_s.append(ray.get([s.simuVSsimu_singleModel_fun.remote(i_list[k+i]) for k,s in enumerate(simulators[:remainder_p1])]))
            else: 
                result_s.append(ray.get([s.simuVSsimu_singleModel_fun.remote(i_list[k+i]) for k,s in enumerate(simulators)]))

        K = len(result_s[0])
        for j in range(len(result_s)):
            for k, result in enumerate(result_s[j]):
                summary_data.loc[K*j+(k)] = result.copy()

        del(self.models_interested); del(self.rep); del(self.list_seed); del(self.nlog_post); del(self.test_data)        
        return summary_data

    def simuVSsimu_singleModel_fun(self, i):
        # i: a single index of MCMC sample you want to use to do the simulations.
        np.random.seed(self.list_seed[i])
        # generating dataset with models1
        simu_1step_data1 = self.fun_IBM(dataset=self.test_data, models=self.models_interested, **self.fun_IBM_kwargs)
        # generating datasetwith models2
        simu_1step_data2 = self.fun_IBM(dataset=self.test_data, models=self.models_interested, **self.fun_IBM_kwargs)
        # a list of summary stats at current time
        current_s = self.fun_ss(exp_dataset=simu_1step_data1, simu_dataset=simu_1step_data2)
                                    
        return current_s

    @property
    def opt_comp(self):
        assert self.nlog_post is not None, '\n log_posterior_density is needed! '
        # assert self.nlog_likeli is not None, '\n nlog_likeli is needed! '
        # return np.where(self.nlog_likeli == np.min(self.nlog_likeli))[0][0]
        return np.where(self.nlog_post == np.min(self.nlog_post))[0][0]

    @property
    def whether_around_opt_comp(self):
        assert self.nlog_post is not None, '\n log_posterior_density is needed for simulation! '
        assert self.opt_percentage is not None, '\n opt_percentage is needed for finding MCMC samples around the optimum!'

        # return self.nlog_likeli <= np.percentile(self.nlog_likeli, self.opt_percentage)
        return self.nlog_post <= np.percentile(self.nlog_post, self.opt_percentage)
    

 
    def _build_models(self, m_new):
        new_models = self.GPmodel_mle.copy() 
        new_models[self.target] = m_new

        return new_models
    
    def _list_seed_comp(self, rep, random_seed, num_samples):
        assert random_seed is not None, '\n random_seed is needed for simulation! '

        # np.random.seed(random_seed)
        # list_seed = np.random.choice(range(num_samples*rep*10), size=num_samples, replace=False)

        list_seed = np.arange(random_seed, random_seed+num_samples)

        return list_seed
    

    def top_ss(self, summary_opt, summary_around_opt, num_top_returned: int, threshold: float, return_full: bool = False):
        """
        Selects top summary statistics based on a given threshold.

        Parameters:
            summary_opt (Any): Summary statistics at the optimum.
            summary_around_opt (Any): Summary statistics around the optimum.
            num_top_returned (int): The total number of top summary statistics to return.
            threshold (float): A float threshold to filter statistics, must be between 0 and 1 exclusive.
            return_full (bool): If True, return full details.

        Returns:
            The filtered summary statistics based on the threshold, either full details or a summary.
        """
        if not (0 < threshold < 1):
            raise ValueError("threshold must be a float between 0 and 1 exclusive.")

        print('\n\n\n' + f'Calculating the top summary stats for: {self.target} ...' + '\n\n\n')
        rep_opt = summary_opt.shape[0]
        self._num_current_samples = np.sum(self.whether_around_opt_comp)
        rep_around_opt = summary_around_opt.shape[0] / self._num_current_samples 
        most_freq_summary_stats = pd.DataFrame(data=0.0, 
                                                index=range(self._num_current_samples), 
                                                columns=self.name_ss)

        for j in range(self._num_current_samples):
            d = summary_around_opt.loc[(0+j*rep_around_opt):(rep_around_opt-1+j*rep_around_opt)].reset_index(drop=True).copy()
            auc0 = np.zeros(len(self.name_ss))
            for i in range(len(self.name_ss)):        
                fpr0, tpr0, _ = roc_curve(y_true=np.append(np.repeat(1, rep_opt), np.repeat(0, rep_around_opt)), 
                                        y_score=np.append(summary_opt.iloc[:, i], d.iloc[:, i]), pos_label=1)
                auc0[i] = auc(fpr0, tpr0)
            
            most_freq_summary_stats.iloc[j, np.argsort(auc0)[np.sort(auc0) > threshold]] = most_freq_summary_stats.iloc[j, np.argsort(auc0)[np.sort(auc0) > threshold]]+ 1
            most_freq_summary_stats.iloc[j, np.argsort(auc0)[np.sort(auc0) < (1-threshold)]] = most_freq_summary_stats.iloc[j, np.argsort(auc0)[np.sort(auc0) < (1-threshold)]]+ 1


        print('Frequency exceeding the threshold: ', np.sort(most_freq_summary_stats.sum())[-num_top_returned:])
        most_columns = most_freq_summary_stats.columns[np.argsort(most_freq_summary_stats.sum())[-num_top_returned:]]
        print('name_ss: ', most_columns.values)

        if return_full == True:
            return most_freq_summary_stats
        else:
            return (np.sort(most_freq_summary_stats.sum())[-num_top_returned:], most_columns.values)

        # for j in range(self._num_current_samples):
        #     d = summary_around_opt.iloc[int(j*rep_around_opt):int((j+1)*rep_around_opt)].reset_index(drop=True)
        #     auc_scores = np.array([auc(*roc_curve(y_true=np.append(np.repeat(1, rep_opt), np.repeat(0, rep_around_opt)),
        #                                 y_score=np.append(summary_opt.iloc[:, i], d.iloc[:, i]), pos_label=1)[:2])
        #                            for i in range(len(self.name_ss))])
            
        #     high_threshold_indices = auc_scores > threshold
        #     low_threshold_indices = auc_scores < (1 - threshold)
        #     most_freq_summary_stats.iloc[j, high_threshold_indices] += 1
        #     most_freq_summary_stats.iloc[j, low_threshold_indices] += 1

        # top_indices = np.argsort(most_freq_summary_stats.sum().values)[-num_top_returned:]
        # print('Frequency exceeding the threshold:', most_freq_summary_stats.sum().values[top_indices])
        # print('name_ss:', self.name_ss[top_indices])

        # if return_full:
        #     return most_freq_summary_stats
        # else:
        #     return self.name_ss[top_indices].tolist()




@ray.remote
class para_Perted_IPM():
    def __init__(self, m):
        # m is an object belonging to Perted_IPM
        self.m = m
    
    def simuVSsimu_fun(self, i):
        return self.m.simuVSsimu_fun(i)
    
    def simuVSsimu_singleModel_fun(self, i):
        return self.m.simuVSsimu_singleModel_fun(i)