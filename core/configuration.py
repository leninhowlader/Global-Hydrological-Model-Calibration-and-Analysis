__author__ = 'mhasan'

import sys, os, numpy as np
from collections import OrderedDict
from datetime import datetime
from copy import deepcopy

from core.variable import ObsVariable, SimVariable, DerivedVariable
from wgap.watergap import WaterGAP
from core.parameter import Parameter
from utilities.fileio import FileInputOutput as io
from utilities.station import Station
from utilities.upstream import Upstream
from utilities.globalgrid import GlobalGrid as gg
from wgap.paraminfo import ParameterInfo
from core.stats import stats

class Configuration:
    """
    The class describes the configuration object which provide all fundamental
    structures for storing data, objects related to the experiment
    at hand, and defines the interconnection among those object. At the same
    time, the class also describe the necessary functionality to describe and
    configure optimization as well as other analyses like sensitivity and 
    uncertainty analysis.
    
    Properties/attributes:
    experiment_type, __experiment_type: str
        Describes the type of experiment. Experiment types can be 'sensitivity',
        'glue', 'se' (acronym for 'solution evaluation'), 'simulation', or 
        'calibration'. The default value for this attribute is 'sensitivity'
    experiment_name, __experiment_name: str
        Gives the name of the experiment. A name is important when multiple 
        experiments are carried out in parallell. Many file names the are 
        generated automatically may contain experiment_name to distinguish
        among the experiments for which they are created.
    parallel_evaluation, __do_parallel_evaluation: bool
        The flag indicates whether the experiment does parallel evaluation in a
        a parallel computing framework or the evaluation is done sequentially 
        on a single processor. The falg is by default set 'true'
    parameter_info_filename, __parameter_info_input_filename: str
        Filename that contains information regarding the parameter objects (see
        the description of the Parameter class for details about parameter 
        objects). If this file is provided, the parameter objects will be 
        created from the description file. However, parameter info data file
        must contain specific information or columns.
    compute_upstream_from_station_file, __compute_upstream_from_station_file: 
        bool
        The flag indicates should the upstream basin extent be computed from the
        provide station file in the WaterGAP class/module or not.
    disjoint_basin_extent, __disjoint_basin_extent: bool
        The flag indicates whether or not the extent of the basin be disjoint (
        i.e. only inter-basin area to be considered) instead of the entire 
        upstream area. the flag is only valid if compute_upstream_from_station_file
        is set true.
    output_directory, __output_directory: str
        name of the directory to save output of the experiment or any temporary
        files created during the experiment
        
    (attributes only related to 'calibration' experiment)
    calibration_type, __calibration_type: str
        Describe the type of calibration experiment. Probable value for the 
        variable can be 'single' or 'one' to represent single-problem 
        calibration or 'multiple' or 'many' to represent a multi-problem 
        calibration experiment.
    maximum_iteration, __max_iterations: int
        no. of model evaluations during calibration. the default value is 20,000
    calibration_result_output_filename, __calibration_result_output_filename: 
        str
        name of the file where the final output (usually the member of pareto 
        front and their objectives) will be saved
    parameter_value_output_filename, __parameter_value_output_filename: str
        (optional) the name of the file where the parameter values of each 
        proposed solution (or proposed sample) will be saved
    objective_values_output_filename, __objective_values_output_filename: str
        (optional) the name of the file where the objective values of each 
        proposed solution will be stored
    runtime_dynamics_output_filename, __runtime_dynamics_output_filename: str
        name of the file where runtime dynamic from the optimization algoritm to 
        be stored. this attribute is only related to the BORG Algorithm
    runtime_dynamics_frequency, __runtime_dynamics_frequency: int
        the frequency at which the runtime dynamic information will be stored in 
        the runtime dynamic output file. That is, after how many model 
        evaluations, the algorithmic internal states to be saved.
    
    (attributes only connected to multi-calibration analysis)
    poc_problem_count, __problem_count: int
        Indicates how many calibration problem to be solved. the default value 
        is 1 indicating a single-problem calibration
    multiproblem_parameter_list_filename, __multiproblem_parameter_list_filename
        : str
        name of the file where the names of the parameters for all calibration 
        problems are described or listed
    multiproblem_objective_list_filename, __multiproblem_objective_list_filename
        : str
        name of the file where hte names of the objective or the observation 
        variables for all calibration problems are listed
    multiproblem_parameter_index_list, __multiproblem_parameter_index_list: 
        tuple
        the array stores the parameter indices of all calibration problems.
    multiproblem_objective_index_list, __multiproblem_objective_index_list: 
        tuple
        the data structure where all objective indices (or the indices of the 
        observation variables) are stored
        
    (attributes related to 'sensitivity' or 'glue' or 'se' or 'simulation' analysis)
    input_sample_filename, __input_sample_filename: str
        name of the sample file. this is usually a comma separated CSV file (
        probably without header)
    sensitivity_as_change_in_simulation, __sensivity_as_change_in_simulation: 
        bool
        The flag determines whether or not the sensivity measure is to be 
        measured as the change in the current simulation from the reference
        simulation. The values (time-series) of the reference simulation run is
        determined internally during sensitivity computation
    function_to_measure_the_change, __function_to_measure_change: function
        The function that is to be used to compute the change between the 
        reference simulation run and the current simulation during sensitivity
        analysis. the default function is the root mean squared difference
    dump_simulation_timeseries, __dump_simulation_timeseries: bool
        The flag determines whether or not the simulation time-series (usually 
        time-series of each grid cell) is stored in binary 2-d array. the flag
        must be set ture during 'glue' and 'se' or 'simulation' type experiment 
        and also can be used during 'sensitivity' experiment.
    
    (attributes that is rarely used)
    compute_simulation_performance, __compute_simulation_performance: bool
        The flag determines if the performance indicators to be computed or not.
        if the flag is set 'true', all predefined performance metrices will be 
        computed and stored. for computing the performance the observation data
        must be available. see also simulation_efficiency_metrices() function in 
        WaterGAP module.
    simulation_efficiency_output_filename, 
        __simulation_efficiency_output_filename: str
        name of the file where computed simulation efficiency indices will be 
        stored.
    compute_simulation_summary_statistics, 
        __compute_simulation_summary_statistics: bool
        the flag determines whether or not the summary statistics to be coputed
        or not. for computing summary statistics, observation data is not 
        required
    simulation_summary_monthly_output_filename, 
        __simulation_summary_monthly_output_filename: str
        Name of the file where the month summary of the simulation output will 
        be stored
    simulation_summary_annual_output_filename,
        __simulation_summary_annual_output_filename: str
        Name of the file where the annual summary of the simulation output will 
        be stored
    simulation_summary_output_filename, 
        __simulation_summary_output_filename: str
        Name of the file where simulation summary to be stored
    compute_seasonal_statistics, __compute_seasonal_statistics: bool
        A flag that describes whether to compute the seasonal summary statistics
        or not from the simulated output. observation data is not required to
        compute the seasonal summary statistics
    seasonal_statistics_output_filename, 
        __seasonal_statistics_output_filename: str
        Name of the file where seasonal summary statistics will be saved.
    
    (attribute to be deprecated soon)
    save_parameter_values, __save_parameter_values: bool
        The flag states whether or not the parameter values of the sample be 
        saved in a file
    
    (internal data structures)
    obs_variables: list 
        the list holds the observation variables. (see more in ObsVarialbe 
        class)
    sim_variables: list
        a placeholder for the simulation variables. (see detailed in SimVariable
        class)
    derived_variables: list
        the list hold the derieved variables (see more in the description of 
        DerivedVariable calss)
    parameters: list
        the list contains the parameters (see details in Parameter class)
    samples: list
        The list contains parameter samples.
    calunit_cellls: list (of list)
        the cell number of calibration units. 
    calunit_staioncells: list (of list)
        holds the station cell numbers (WaterGAP GCRC number) for each 
        calibration unit
    __optionnames: dict
        hold the keyword for the options and their alternative named used in the
        configuration file
    
    Methods:

    """
    __optionnames = {
        'experiment_type': (
        'experiment_type', 'experiment type', 'mode'
        ),
        'experiment_name': (
            'experiment_name', 'experiment name', 'experiment_id', 
            'experiment_id','calibration_id', 'calibration_name', 
            'calibration id', 'calibration name'
        ),
        'maximum_iteration': (
            'maximum_iteration', 'maximum iteration', 'max iter', 'max_iter'
        ),
        'parameter_description_filename': (
            'parameter_description_filename',
            'parameter_info', 'parameter_info_input_filename', 
            'parameter_info_filename'
        ),
        'parallel_computation': (
            'parallel_evaluation', 'do_parallel_evaluation', 
            'parallel_evaluations', 'parallel_evaluation', 
            'parallel evaluations', 'parallel evaluation', 'parallel', 
            'parallelization'
        ),
        'output_directory': ('output_directory'),
        'save_simulation_output': (
            'save_simulation_output', 'save simulation output', 
            'dump_model_prediction', 'save_model_prediction'
        ),
        'objective_outfile': (
            'objective_filename', 'objective_output_filename', 
            'save_function_values', 'save function values', 
            'save_function_value', 'save function value', 'funvalue_dumpfile', 
            'funvalue dumpfile'
        ),
        'parameter_outfile': (
            'parameter_output_filename',
            'save_param_values' , 'save param values' , 'save_param_value' , 
            'save param value', 'parameter_dumpfile', 'parameter dumpfile',
            'parameter_value_output_filename'
        ),
        'result_outfile': (
            'result_outfile', 'calibration_output_filename', 'output_filename',
            'result_filename', 'result_dumpfile', 'output_filename'
        ),
        'runtime_dynamics_outfile': (
            'runtime_dynamics_filename', 'runtime dynamics filename'
        ),
        'runtime_dynamics_frequency': (
            'runtime_dynamics_write_frequency', 'runtime_report_frequency', 
            'runtime report frequency', 'runtime dynamics write frequency'
        ),
        'replace_nan': (),
        'compute_upstream': (
            'compute_upstream_from_station_file', 'upstream_from_station_file',
            'target_cells_from_station_file', 'target_cell_from_station_file',
            'target cells from station file', 'target cell from station file'
        ),
        'disjoint_basins': (
            'disjoint_basin_extent', 'disjoint basin extent', 
            'non_overlapping_basin'
        ),
        'calibration_type': (
            'calibration_type', 'calibration type', 'calibration-type'
        ),
        'multiproblem_calibration_parameter_list': (
            'multiproblem_calibration_parameter_list_filename',
            'multiproblem_calibration_parameter_list',
            'multiproblem calibration parameter list'
        ),
        'multiproblem_calibration_objective_list': (
            'multiproblem_calibration_objective_list_filename',
            'multiproblem_calibration_objective_list',
            'multiproblem calibration objective list',
            'multiproblem_calibration_observation_list',
            'multiproblem calibration observation list'
        ),
        'parameter_info_filename': (
            'parameter_info_input_filename', 'parameter info input filename',
            'parameter_info_filename', 'parameter info filename'
        ),
        'report_outfile': (),
        'sleep_time': (),
        'sample_filename': (
            'input_sample_filename', 'sample_filename'
        ),
        'change_from_refsimulation': (),
        'function_to_compute_change': (),
        'calibration_unit_cells': (
            'filename_calibration_unit_cells',
            'cell_list_of_calibration_units', 'calibration_unit_cells'
        ),
        'calibration_unit_stationcells': (
            'filename_calibration_unit_stationcells',
            'station_cells_of_calibration_units', 'calibration_unit_stationcells'
        ),
        
        ## options related to sensitivity
        'measure_of_sensitivity' : (
            'measure_of_sensitivity', 'measure of sensitivity'
        )
    }

    def __init__(self, experiment_type='sensitivity'):
        self.__experiment_type = experiment_type
        self.__experiment_name = ''
        self.__do_parallel_evaluation = True
        self.__parameter_info_input_filename = ''
        self.__compute_upstream_from_station_file = False
        self.__disjoint_basin_extent = True
        self.__output_directory = 'output'
        
        # [ ] attributes connected to 'calibration' experiment only
        self.__calibration_type = 'single'  # 'single' or 'one' 
                                            # 'multiple' or 'many'
        self.__max_iterations = 20000
        self.__calibration_result_output_filename = ''
        self.__save_parameter_values = False
        self.__parameter_value_output_filename = ''
        self.__objective_values_output_filename = ''
        self.__runtime_dynamics_output_filename = ''
        self.__runtime_dynamics_frequency = -1
        # [.]

        # [ ] attributes and structures related to multi-problem calibration
        self.__multiproblem_parameter_list_filename = ''
        self.__multiproblem_objective_list_filename = ''
        self.__problem_count = 1

        self.__multiproblem_parameter_index_list = ()
        self.__multiproblem_objective_index_list = ()
        self.__multiproblem_constraints_list = []
        # [.]


        # [ ] attributes connected to 'sensitivity' or 'glue' or 'se' or 
        # 'simulation' experiment
        self.__input_sample_filename = ''
        self.__sensivity_as_change_in_simulation = True
        self.__function_to_measure_change = None
        self.__dump_simulation_timeseries = True
        # [.]

        # [ ] attribute that are rarely used (and can be deprecated in future)
        self.__compute_simulation_performance = False
        self.__simulation_efficiency_output_filename = 'efficiency.dat'
        self.__compute_simulation_summary_statistics = False
        self.__simulation_summary_monthly_output_filename = ''
        self.__simulation_summary_annual_output_filename = ''
        self.__simulation_summary_output_filename = ''
        self.__compute_seasonal_statistics = False
        self.__seasonal_statistics_output_filename = 'seasonal_statistics.csv'
        # [.]

        # [ ] internal data structures
        self.obs_variables = []
        self.sim_variables = []
        self.derived_variables = []
        self.parameters = []
        self.samples = []
        
        self.calunit_cells_filename = ''
        self.calunit_stationcell_filename = ''
        self.calunit_cellls = []
        self.calunit_staioncells = []
        # [.]

    @property
    def multiproblem_constraints_list(self): 
        return self.multiproblem_constraints_list
    @multiproblem_constraints_list.setter
    def multiproblem_constraints_list(self, array):
        if array: self.multiproblem_constraints_list = array
    
    @property
    def poc_problem_count(self): return self.__problem_count
    @poc_problem_count.setter
    def poc_problem_count(self, nproblem): self.__problem_count = nproblem

    # @property
    # def single_problem_mode(self): return self.__one_problem
    # @single_problem_mode.setter
    # def single_problem_mode(self, flag:bool): self.__one_problem = flag

    @property
    def calibration_type(self): return self.__calibration_type
    @calibration_type.setter
    def calibration_type(self, calib_type): self.__calibration_type = calib_type

    @property
    def multiproblem_parameter_list_filename(self):
        return self.__multiproblem_parameter_list_filename
    @multiproblem_parameter_list_filename.setter
    def multiproblem_parameter_list_filename(self, filename):
        self.__multiproblem_parameter_list_filename = filename

    @property
    def multiproblem_objective_list_filename(self):
        return self.__multiproblem_objective_list_filename
    @multiproblem_objective_list_filename.setter
    def multiproblem_objective_list_filename(self, filename):
        self.__multiproblem_objective_list_filename = filename

    @property
    def multiproblem_parameter_index_list(self):
        return self.__multiproblem_parameter_index_list
    @multiproblem_parameter_index_list.setter
    def multiproblem_parameter_index_list(self, param_list):
        self.__multiproblem_parameter_index_list = param_list
    
    @property
    def multiproblem_objective_index_list(self):
        return self.__multiproblem_objective_index_list
    @multiproblem_objective_index_list.setter
    def multiproblem_objective_index_list(self, objective_list):
        self.__multiproblem_objective_index_list = objective_list

    @property
    def experiment_name(self):
        return self.__experiment_name
    @experiment_name.setter
    def experiment_name(self, name):
        self.__experiment_name = name

    @property
    def sensitivity_as_change_in_simulation(self):
        return self.__sensivity_as_change_in_simulation
    @sensitivity_as_change_in_simulation.setter
    def sensitivity_as_change_in_simulation(self, flag:bool):
        self.__sensivity_as_change_in_simulation = bool(flag)

    @property
    def function_to_measure_the_change(self): 
        return self.__function_to_measure_change
    @function_to_measure_the_change.setter
    def function_to_measure_the_change(self, fun): 
        self.__function_to_measure_change = fun

    @property
    def experiment_type(self): return self.__experiment_type
    @experiment_type.setter
    def experiment_type(self, exper_type): self.__experiment_type = exper_type

    @property
    def parallel_evaluation(self):
        return self.__do_parallel_evaluation
    @parallel_evaluation.setter
    def parallel_evaluation(self, flag):
        self.__do_parallel_evaluation = flag

    @property
    def parameter_info_filename(self):
        return self.__parameter_info_input_filename
    @parameter_info_filename.setter
    def parameter_info_filename(self, filename):
        self.__parameter_info_input_filename = filename

    @property
    def input_sample_filename(self):
        return self.__input_sample_filename
    @input_sample_filename.setter
    def input_sample_filename(self, filename):
        self.__input_sample_filename = filename

    @property
    def save_parameter_values(self):
        return self.__save_parameter_values
    @save_parameter_values.setter
    def save_parameter_values(self, flag):
        self.__save_parameter_values = flag

    @property
    def parameter_value_output_filename(self):
        return self.__parameter_value_output_filename
    @parameter_value_output_filename.setter
    def parameter_value_output_filename(self, filename):
        self.__parameter_value_output_filename = filename


    @property
    def dump_simulation_timeseries(self):
        return self.__dump_simulation_timeseries
    @dump_simulation_timeseries.setter
    def dump_simulation_timeseries(self, flag):
        self.__dump_simulation_timeseries = flag

    @property
    def maximum_iteration(self): return self.__max_iterations
    @maximum_iteration.setter
    def maximum_iteration(self, max_itarations):
        self.__max_iterations = max_itarations

    @property
    def compute_upstream_from_station_file(self):
        return self.__compute_upstream_from_station_file
    @compute_upstream_from_station_file.setter
    def compute_upstream_from_station_file(self, flag:bool):
        self.__compute_upstream_from_station_file = flag

    @property
    def disjoint_basin_extent(self):
        return self.__disjoint_basin_extent
    @disjoint_basin_extent.setter
    def disjoint_basin_extent(self, flag):
        self.__disjoint_basin_extent = flag

    @property
    def output_directory(self):
        return self.__output_directory
    @output_directory.setter
    def output_directory(self, directory):
        self.__output_directory = directory

    @property
    def calibration_result_output_filename(self):
        return self.__calibration_result_output_filename
    @calibration_result_output_filename.setter
    def calibration_result_output_filename(self, filename):
        self.__calibration_result_output_filename = filename

    @property
    def objective_values_output_filename(self):
        return self.__objective_values_output_filename
    @objective_values_output_filename.setter
    def objective_values_output_filename(self, filename):
        self.__objective_values_output_filename = filename
    
    @property
    def runtime_dynamics_output_filename(self):
        return self.__runtime_dynamics_output_filename
    @runtime_dynamics_output_filename.setter
    def runtime_dynamics_output_filename(self, filename):
        self.__runtime_dynamics_output_filename = filename
    
    @property
    def runtime_dynamics_frequency(self):
        return self.__runtime_dynamics_frequency
    @runtime_dynamics_frequency.setter
    def runtime_dynamics_frequency(self, frequency:int):
        self.__runtime_dynamics_frequency = frequency

    @property
    def compute_simulation_performance(self):
        return self.__compute_simulation_performance
    @compute_simulation_performance.setter
    def compute_simulation_performance(self, flag):
        self.__compute_simulation_performance = flag

    @property
    def simulation_efficiency_output_filename(self):
        return os.path.join(self.__output_directory,
                            self.__simulation_efficiency_output_filename)
    @simulation_efficiency_output_filename.setter
    def simulation_efficiency_output_filename(self, filename):
        self.__simulation_efficiency_output_filename = filename

    @property
    def compute_seasonal_statistics(self):
        return self.__compute_seasonal_statistics
    @compute_seasonal_statistics.setter
    def compute_seasonal_statistics(self, flag):
        self.__compute_seasonal_statistics = flag

    @property
    def seasonal_statistics_output_filename(self):
        return os.path.join(self.__output_directory,
                            self.__seasonal_statistics_output_filename)
    @seasonal_statistics_output_filename.setter
    def seasonal_statistics_output_filename(self, filename):
        self.__seasonal_statistics_output_filename = filename

    @property
    def compute_simulation_summary_statistics(self):
        return self.__compute_simulation_summary_statistics
    @compute_simulation_summary_statistics.setter
    def compute_simulation_summary_statistics(self, flag):
        self.__compute_simulation_summary_statistics = flag

    @property
    def simulation_summary_output_filename(self):
        return os.path.join(self.__output_directory,
                            self.__simulation_summary_output_filename)
    @simulation_summary_output_filename.setter
    def simulation_summary_output_filename(self, filename):
        self.__simulation_summary_output_filename = filename

    @property
    def simulation_summary_annual_output_filename(self):
        return os.path.join(self.__output_directory,
                            self.__simulation_summary_annual_output_filename)
    @simulation_summary_annual_output_filename.setter
    def simulation_summary_annual_output_filename(self, filename):
        self.__simulation_summary_annual_output_filename = filename

    @property
    def simulation_summary_monthly_output_filename(self):
        return os.path.join(self.__output_directory,
                            self.__simulation_summary_monthly_output_filename)
    @simulation_summary_monthly_output_filename.setter
    def simulation_summary_monthly_output_filename(self, filename):
        self.__simulation_summary_monthly_output_filename = filename


    def obs_var_count(self): return len(self.obs_variables)
    def sim_var_count(self): return len(self.sim_variables)
    def get_parameter_count(self, problem_no:int=-1): 
        """
        The function count the no. of parameters to be considered in a 
        calibration problem. In case of multi-problem calibration case, the
        function returns the parameter count for the specified problem.
        
        Parameters:
        problem_no: int (optional, default value -1)
            problem number for which parameter count to be done. problem number
            must be positive integer (or zero) and less than total number of 
            problems. if problem no is given, it is assumed that the calibration
            type is multi-problem calibration

        Returns:
        int
            Parameter count for the specified problem
        """
        nparameters = 0
        if self.poc_problem_count == 1:
            for param in self.parameters:
                if param.cell_level_representation:
                    for el in param.cell_list:
                        if type(el) is list: nparameters += len(el)
                        else: nparameters += 1
                else: nparameters += 1
        
        else:
            if (self.poc_problem_count > 1 and problem_no >= 0 and
                problem_no < self.poc_problem_count):
                
                nparameters += len(
                    self.multiproblem_parameter_index_list[problem_no]
                )
                # Note that cell level representation is not implemented for
                # multi-problem calibration case
            
        return nparameters
            

    def get_objective_count(self, problem_no:int=-1):
        """
        The function returns count objectives for specified problem. if problem
        number is not provided, it is assumed that the calibration experiment 
        consists of only a single problem

        Parameter:
        problem_no: int (optional, default -1)
            problem number for which objective count has to performed, in the 
            case of multi-problem calibration. the parameter must have value
            between 0 and no. of problems (exclusive of the upper range).
        
        Returns:
        int
            number of objectives for the specified problem
        """
        nobjectives = 0
        
        if self.poc_problem_count == 1:
            for var in self.obs_variables:
                if type(var.data_cloud.data) is np.ndarray:
                    if var.data_cloud.data.ndim == 2:
                        nobjectives += var.data_cloud.data.shape[1]
                        # Note that when observation data has many columns, it 
                        # is expected that the counter simulation variable would
                        # also have the same number of columns. And thus,
                        # objectives will be computed comparing column-by-column
                        # observation data and simulation output resulting an
                        # objective count similar to the number of columns in
                        # the observation (or counter simulation) variable.
                    else: nobjectives += 1
                else: nobjectives += 1
        else:
            if (self.poc_problem_count > 1 and problem_no >= 0 and
                problem_no < self.poc_problem_count):

                varlist = self.multiproblem_objective_index_list[problem_no]
                nobjectives = np.unique(varlist).shape[0]

                # Note that cell-level calibration has not implemented in the
                # case of multi-problem calibration. this is why varlist length
                # would be sufficient for finding the number of objectives for
                # a cda unit. however, there could be same variable multiple
                # times for representing the same variable values in different 
                # location and for each location objectives will be computed
                # separately. however, objective for the same variable in 
                # different location will be averaged. this is why unique 
                # variable numbers should reflect the no. of objective for a
                # specific problem. 
                # 
                # Caution: it is expected that the number of columns in the
                # observation variables would be more than one but the columns
                # mostly would represent data for different problems, or in few
                # cases data from different locations in the same basin (e.g., 
                # the streamflow data in several stations) 

        return nobjectives

    def get_constraints_count(self, problem_no:int=-1): 
        """
        The function returns number of constraints in the calibration problem.

        Parameters:
        problem_no: int (optional, default -1)
            problem identification number that is used to specify the problem.
            this parameter will only be used for multi-problem calibration case.

        Returns:
        int
            number of constraints in the specified calibration problem
        """
        return 0

    def get_parameter_bounds(self, problem_no:int=-1):
        """
        The function generates two lists of upper and lower parameter bound for 
        a specified problem. If no problem is specified, it is assumed that the 
        calibration problem in single-problem calibration

        Parameters:
        problem_no: int (optional, default -1)
            problem identification number that is used to specify the problem.
            this parameter will only be used for multi-problem calibration case.
        
        Returns:
        list, list
            two list of parameter bounds. the first contains the lower limits 
            and the second list contains the upper limits of parameters for the
            specific problem
        """
        lower, upper = [], []

        if self.poc_problem_count == 1:
            for param in self.parameters:
                nunits = 0
                if param.cell_level_representation:
                    for el in param.cell_list:
                        if type(el) is list: nunits += len(el)
                        else: nunits += 1
                else: nunits += 1

                lower += [param.get_lower_bound()] * nunits
                upper += [param.get_upper_bound()] * nunits
        elif (self.poc_problem_count > 1 and problem_no >= 0 and
              problem_no < self.poc_problem_count):
            
            indexarray = self.multiproblem_parameter_index_list[problem_no]
            for num in indexarray:
                param = self.parameters[num]
                lower.append(param.get_lower_bound())
                upper.append(param.get_upper_bound())
            
            # Note that in multi-problem calibration, cell level calibration is 
            # not implemented. 
        else: pass

        return lower, upper
    
    def get_epsilons(self, problem_no:int=-1):
        """
        This function returns the list of epsilon values for all objectives 
        assiciated with a specified problem. If problem no is not provided, it 
        is assumed that the calibration experiment contains only a single 
        problem

        Parameters:
        problem_no: int (optional, default -1)
            the problem indentifier for which the epsilons should be returned. 
            the parameter is only used for multi-problem calibration case. the
            problem must be a positive number ranging from 0 till one less than
            the number of problems in experiment.
        
        Returns:
        list
            list of epsilon values for objective concerning the specified 
            problem
        """
        epsilons = []

        if self.poc_problem_count == 1:
            for var in self.obs_variables:
                if var.data_cloud.data.ndim == 2: 
                    nobjs = var.data_cloud.data.shape[1]
                    # see explanation in get_objective_count() function for 
                    # getting more than one objective from a single variable 
                else: nobjs = 1 

                epsilons += [var.get_epsilon()] * nobjs
        elif (self.poc_problem_count > 1 and problem_no >= 0 and
              problem_no < self.poc_problem_count):
            
            indexlist = self.multiproblem_objective_index_list[problem_no]
            
            temp = OrderedDict()
            for num in indexlist: temp[num] = None
            varnumlist = list(temp.keys())
            # Note that in multi-problem calibration case, in the objective list
            # or the observation variable index list, the same variable can 
            # occur multiple times; however, a average of the objectives 
            # concerning the variable will be computed. thus the total number 
            # of objectives would be the same as the length of the unique 
            # index number of the observation variables in the multi-problem
            # objective index list. However, order is very important here. The 
            # order of the epsilons must be the same as how the objectives are
            # computed and appears in the array of objectives when the 
            # objectives are computed in model evaluation. this is why, unique 
            # list of objective index (or obs. variable index) has been created
            # above with preserving the order of appreance of an observation
            # variable

            for num in varnumlist:
                var = self.obs_variables[num]
                epsilons.append(var.get_epsilon())
        else: pass

        return epsilons

    @staticmethod
    def read_configuration_file(filename):
        config = Configuration()

        try:
            fs = open(filename, 'r')
            lines = fs.readlines()
            try: fs.close()
            except: pass

            while lines:
                line = lines.pop(0).strip()
                if line:
                    temp = line.strip().split()
                    for i in range(len(temp)): temp[i] = temp[i].strip().lower()
                    if len(temp) == 2:
                        key, value = temp[0], temp[1]
                        if key == 'begin':
                            if value == 'settings':
                                Configuration.read_settings(lines, config)

                            elif value == 'model-options':
                                WaterGAP.read_model_settings(lines)

                            elif (value == 'parameter' and
                                  len(config.parameters) == 0):
                                param_list = Parameter.read_parameters(lines)
                                if param_list: config.parameters = param_list

                            elif value == 'obs-variable':
                                config.obs_variables \
                                = ObsVariable.read_variables(lines)

                            elif value == 'sim-variable':
                                config.sim_variables \
                                = SimVariable.read_variables(lines)

                            elif value == 'derived-variable':
                                config.derived_variables \
                                    = DerivedVariable.read_variables(lines)
        except: config = None

        return config

    @staticmethod
    def read_settings(lines, config):
        optionnames = Configuration.__optionnames

        while lines:
            line = lines.pop(0).strip()
            line = line.split('#')[0].strip()       # leave out hash comments
            
            if line:
                temp = line.strip().split()
                temp[0] = temp[0].strip().lower()

                if temp[0] == 'end': return True
                else:
                    temp = line.split('=')
                    for i in range(len(temp)): temp[i] = temp[i].strip()

                    if len(temp) == 2:
                        key, value = temp[0], temp[1]

                        while key.find('  ') != -1: key = key.replace('  ', ' ')
                        while key.find(' ') != -1: key = key.replace(' ', '_')

                        if not (key and value): continue

                        if key in optionnames['experiment_type']: 
                            config.experiment_type = value.lower()

                        elif key in optionnames['experiment_name']:
                            config.experiment_name = value

                        elif key in optionnames['parameter_description_filename']:
                            config.parameter_info_filename = value

                        elif key in optionnames['sample_filename']:
                            config.input_sample_filename = value

                        elif key in optionnames['parallel_computation']:

                            if value.lower() in ['y', 'yes', 'true', 't', '1']:
                                config.parallel_evaluation = True
                            else: config.parallel_evaluation = False

                        elif key in optionnames['maximum_iteration']:

                            try: max_iter = int(value)
                            except: max_iter = 0

                            config.maximum_iteration = max_iter

                        elif key in optionnames['compute_upstream']:

                            if value.lower() in ['y', 'yes', 'true', 't', '1']:
                                config.compute_upstream_from_station_file = True
                            else:
                                config.compute_upstream_from_station_file \
                                = False

                        elif key in optionnames['disjoint_basins']:
                            if value.lower() in ['y', 'yes', 'true', 't', '1']:
                                config.disjoint_basin_extent = True
                            else: config.disjoint_basin_extent = False
                        
                        elif key in optionnames['calibration_unit_cells']:
                            config.calunit_cellls \
                            = SimVariable.read_groupped_cell_attribute(
                                value, dtype=int
                            )
                            config.calunit_cells_filename = value

                        elif key in optionnames['calibration_unit_stationcells']:    
                            config.calunit_staioncells \
                            = SimVariable.read_groupped_cell_attribute(
                                value, dtype=int
                            )
                            config.caliunti_stationcell_filename = value
                        
                        elif key in optionnames['output_directory']:
                            config.output_directory = value

                        elif key in optionnames['result_outfile']:
                            config.calibration_result_output_filename = value

                        elif key in ['save_parameter_values']:
                            if value.lower() in ['y', 'yes', 'true', 't', '1']:
                                config.save_parameter_values = True
                            else: config.save_parameter_values = False

                        elif key in optionnames['parameter_outfile']:
                            config.parameter_value_output_filename = value
                            config.save_parameter_values = True

                        elif key in optionnames['save_simulation_output']:
                            if value.lower() in ['y', 'yes', 'true', 't', '1']:
                                config.dump_simulation_timeseries = True
                            else: config.dump_simulation_timeseries = False
                        
                        elif key in optionnames['objective_outfile']:
                            config.objective_values_output_filename = value
                        
                        elif key in optionnames['runtime_dynamics_outfile']:
                            config.runtime_dynamics_output_filename = value
                            
                        elif key in optionnames['runtime_dynamics_frequency']:
                            try: config.runtime_dynamics_frequency = int(value)
                            except: config.runtime_dynamics_frequency = -1
                        
                        elif key in optionnames['calibration_type']:
                            config.calibration_type = value.lower()
                            # if config.calibration_type in ['multiple', 'many']:
                            #     config.single_problem_mode = False
                            # else: config.single_problem_mode = True
                        
                        elif key in optionnames[
                            'multiproblem_calibration_parameter_list']:
                            config.multiproblem_parameter_list_filename = value
                        
                        elif key in optionnames[
                            'multiproblem_calibration_objective_list']:
                            config.multiproblem_objective_list_filename = value
                        
                        elif key in optionnames['parameter_info_filename']:
                            config.parameter_info_filename = value

                        elif key in ['compute_prediction_efficiency'
                                     'compute_model_efficiency']:
                            value = value.lower()
                            if value in ['true', 't', '1', 'yes', 'y']:
                                config.compute_prediction_efficiency = True
                            else: config.compute_prediction_efficiency = False

                        elif key in ['model_efficiency_output_filename'
                                     'prediction_efficiency_output_filename']:
                            config.prediction_efficiency_output_filename = value
                            config.compute_prediction_efficiency = True

                        elif key in ['compute_prediction_statistics'
                                     'prediction_statistics']:
                            if value.lower() in ['true', 't', '1', 'yes', 'y']:
                                config.compute_prediction_statistics = True
                            else: config.compute_prediction_statistics = False

                        elif key in ['prediction_summary_statistics_filename',
                                     'summary_statistics_output_filename']:
                            config.prediction_summary_output_filename = value
                            config.compute_prediction_statistics = True

                        elif key in ['annual_statistics_output_filename',
                                     'annual_statistics_filename']:
                            config.prediction_summary_annual_output_filename \
                            = value

                            config.compute_prediction_statistics = True

                        elif key in ['monthly_statistics_output_filename',
                                     'monthly_statistics_filename']:
                            config.prediction_summary_monthly_output_filename \
                            = value

                            config.compute_prediction_statistics = True

                        elif key in ['compute_seasonal_statistics',
                                     'seasonal_statistics']:
                            if value.lower() in ['true', 't', '1', 'yes', 'y']:
                                config.compute_seasonal_statistics = True
                            else: config.compute_seasonal_statistics = False

                        elif key in ['seasonal_statistics_output_filename']:
                            config.seasonal_statistics_output_filename = value
                            config.compute_seasonal_statistics = True
                        elif key in optionnames['measure_of_sensitivity']:
                            value = value.lower()
                            if value in ['rmsd', 'rmse','change_in_simulation']:
                                config.sensitivity_as_change_in_prediction = True

                        # elif key in ['as_change_in_prediction']:
                        #     if value.lower() in ['true', 't', '1', 'yes', 'y']:
                        #         config.sensitivity_as_change_in_prediction = True
                        #     else:
                        #         config.sensitivity_as_change_in_prediction = False
                        elif key in ['function']:
                            fun = None
                            value = value.lower()
                            if value == 'rmse': fun = stats.root_mean_square_error
                            # else: value = None
                            config.function = fun

        return False
    
    def is_okay(self, skip_observation=False, error_code=False):
        # if error_code: return self.is_okay_errcode(skip_observation=skip_observation)
        # else: return not bool(self.is_okay_errcode(skip_observation=skip_observation))

        err = self.is_okay_errcode(skip_observation=skip_observation)
        if error_code: return err
        else:
            if err == 0: return True
            else: return False

    def is_okay_errcode(self, skip_observation=False):
        '''
        This function checks the completeness of the configuration object. If
        the configuration object has observation variable(s), observation data
        will be read hear if skip observation flag is not set True. In case of
        sensitivity analysis, samples will be loaded.

        Parameters:
        skip_observation: bool (optional, default False)
            The flag indicates to neglect observation data varification while 
            consistency is checked if the flag is set true.
        
        Returns:
        int
            a number indicating the error code. Error code could be one of the 
            followings
                0	no error
                100 failed to create target cell list from stations in station file
                150 cell list consistency check for multi-problem calibration failed
                200 absence of sim-variable
                20x error in sim variable no. x
                300 failed to acquire observation dataset
                30x obs-variable no. x
                40x error in derived variable no. x
                501 Sample file not found
                502 Samples could not be read from sample file
                600 error in sensitivity method selection
                700 absence of parameters
                70x error in parameter no. x
                810 no multiproblem calibration parmeters file
                820 no multiproblem calibration objectives file
                830 length of objective list and length of paramter list
                    does not match.
        '''
        # step:
        # create parameter objects from parameter info file (if given)
        if self.parameter_info_filename:
            self.parameters = Parameter.read_parameter_list(
                self.parameter_info_filename
            )
        # end [step]

        # step-x:
        # check the parameter index for multi-problem optimization
        if self.calibration_type in ['multiple', 'many']:
            f = self.multiproblem_parameter_list_filename
            if not os.path.exists(f): return 810
            param_indicies = self.get_parameter_indices_for_manyPoc(f)
            if len(param_indicies) > 0:
                self.multiproblem_parameter_index_list = param_indicies
        # end [step]

        # step-x:
        # check the objective [or observaiton] indeices for multi-problem 
        # calibration
        if self.calibration_type in ['multiple', 'many']:
            f = self.multiproblem_objective_list_filename
            if not os.path.exists(f): return 820
            obj_indices = self.get_objective_indices_for_manyPoc(f)
            if len(obj_indices) > 0:
                self.multiproblem_objective_index_list = obj_indices
        # end [step-x]

        # step-x:
        # check number of problems in parameter index list and objective 
        # index list. the length of these two list should be equal.
        if self.calibration_type in ['multiple', 'many']:
            if (len(self.multiproblem_objective_index_list) 
                != len(self.multiproblem_parameter_index_list)):
                return 830
            else:
                self.poc_problem_count = \
                len(self.multiproblem_objective_index_list)
        # end [step]
        
        # step: 
        # check whether or not the station file is available when 
        # compute_upstream_from_station_file flag is set true
        if not (WaterGAP.station_filename and
                os.path.exists(os.path.join(WaterGAP.home_directory,
                                            WaterGAP.station_filename))):
            self.compute_upstream_from_station_file = False
            self.disjoint_basin_extent = False
        # end [step]

        # step: read the target cells from station file, if applicable
        if self.compute_upstream_from_station_file:
            succeed = self.generate_target_cells_from_station_file()
            if not succeed: return 100
        # end [step]
        
        # step: 
        # check completeness of parameters
        if not self.parameters: return 700
        else:
            pnum = 0
            for param in self.parameters:
                pnum += 1
                if not param.is_okey(): return (700 + pnum)
        # end [step]    
        
        # step:
        # distribute the cell list of calibration units into parameter 
        # cell list
        if self.calunit_cellls:
            # [+] clear existing cell list
            for param in self.parameters: 
                param.cell_list.clear()
            # [.] 
            
            if self.calibration_type in ['multiple', 'many']:
                param_indices = self.multiproblem_parameter_index_list
                
                # [+] map calunit to parameter by parameter index
                param_calunit = {}
                for i in range(len(param_indices)):
                    for ip in param_indices[i]:
                        try: param_calunit[ip].append(i)
                        except: param_calunit[ip] = [i]
                # [.]
                
                iparams = set(param_calunit.keys())
                for i in iparams:
                    iunits = param_calunit[i]
                    param = self.parameters[i] 
                    
                    for iu in iunits:
                        param.cell_list.append(
                            self.calunit_cellls[iu]
                        )
                
                if not self.multi_problem_celllist_consistency_test():
                    return 150
            else:
                for param in self.parameters:
                    param.cell_list = self.calunit_cellls
        # end [step]


        # step:
        # assign cell list to simulation variables (only if cell list of cal. 
        # units provided)
        #
        if self.calibration_type in ['multiple', 'many']:
            obj_indices = self.multiproblem_objective_index_list

            obj_calunit_map = OrderedDict()
            for i in range(len(obj_indices)):
                for iobj in obj_indices[i]:
                    try: obj_calunit_map[iobj].append(i)
                    except: obj_calunit_map[iobj] = [i]

            for i in obj_calunit_map.keys():
                iunits = obj_calunit_map[i]
                
                obs_var = self.obs_variables[i]
                sim_var = self.find_counter_variable(
                    obs_var.counter_variable
                )
                
                # basin cell list can be assigned by specifying values 
                # in variable declaration. thus, if a variable already
                # has cell list, re-assignment of cell list must be avoided
                if not sim_var.basin_cell_list:
                    if self.calunit_cellls and not sim_var.basin_outlets_only:
                        for iu in iunits:
                            sim_var.basin_cell_list.append(
                                self.calunit_cellls[iu]
                            )
                    
                    if self.calunit_staioncells and sim_var.basin_outlets_only:
                        for iu in iunits:
                            sim_var.basin_cell_list.append(
                                self.calunit_staioncells[iu]
                            )
        else:
            for sim_var in self.sim_variables:
                if not sim_var.basin_cell_list:
                    if self.calunit_cellls and not sim_var.basin_outlets_only:
                        sim_var.basin_cell_list = self.calunit_cellls
            
                    if self.calunit_staioncells and sim_var.basin_outlets_only:
                        sim_var.basin_cell_list = self.calunit_staioncells
        # end [step] 

        
        # step: 
        # check completeness of simulation variables. there must at least be one
        # simulation variable
        if not self.sim_variables: return 200
        else:
            varnum = 0
            for var in self.sim_variables:
                varnum += 1
                var.data_source.file_endian = WaterGAP.output_endian_type
                if not var.is_okay(): return (200 + varnum)
        # end [step]


        # step: 
        # check completeness of observation variables (if any). Try to load the 
        # observation data
        if not skip_observation:
            if len(self.obs_variables) > 0:
                # if not ObsVariable.data_collection(self.obs_variables): return 300
                if not ObsVariable.read_observations(self.obs_variables): 
                    return 300

                varnum = 0
                for var in self.obs_variables:
                    varnum += 1
                    if not var.is_okay(): return (300 + varnum)
                
                # for var in self.obs_variables:
                #     var.data_cloud.data = np.array(var.data_cloud.data)
                #     var.data_cloud.data_indices \
                #     = np.array(var.data_cloud.data_indices)
        # end [step]

        # step:
        # compute objective weighting factors from upstream area if the station
        # cell number (WaterGAP GCRC cell number) or the cell number of the most
        # downstream cell is provided in the observation variables. Usually this
        # weighting of objectives using the entire upstream area is applied for
        # streamflow objectives if multiple streamflow stations are present 
        # within the same CDA unit.
        #   
        # Caution: if objective weighting has to be used, it is necessary that 
        # if in a single unit, only one station is present, the station cell 
        # number must be provided. the weighting factor for that particular 
        # objective would become 1.0
        # 
        if len(self.obs_variables) > 0:
            for var in self.obs_variables:
                if len(var.GCRC_for_weighting_factor_based_on_upstream_area) > 0:
                    weights_allunits = np.array([])
                    
                    for stations_cellnum in var.GCRC_for_weighting_factor_based_on_upstream_area:
                        upstream_areas = np.array(
                            [Upstream.compute_entire_upstream_area(x)
                            for x in stations_cellnum]
                        )

                        weights = upstream_areas/upstream_areas.sum()
                        
                        weights_allunits = np.concatenate(
                            (weights_allunits, weights), axis=0
                        )
                    
                    var.weight_factors = weights_allunits.flatten().tolist()
                
                elif len(var.objective_weights) > 0:
                    weight_factors = []
                    for x in var.objective_weights:
                        weight_factors += (np.array(x)/np.sum(x)).tolist()
                    
                    var.weight_factors = weight_factors
        # end [step]

        # step: 
        # check completeness of derived variables (if any)
        if len(self.derived_variables) > 0:
            varnum = 0
            for var in self.derived_variables:
                varnum += 1
                if not var.is_okay(): return (400 + varnum)
                if not var.evaluate_equation(
                    simvars=self.sim_variables, obsvars=self.obs_variables):
                    return (400 + varnum)
        # end [step]

        # step: 
        # check if the samples can be gathered in the case of sensitivity 
        # analysis experiment. load the samples. note that 'se' stands for 
        # 'solution evaluation'
        if self.__experiment_type in ['sensitivity', 'glue', 'se', 'simulation']: 
            # check the sample file and load samples
            if not self.__input_sample_filename: return 501
            elif not self.samples:
                header, dt = io.read_flat_file(self.__input_sample_filename, separator=',')
                if dt:
                    for d in dt:
                        if len(d) != len(self.parameters): return 502
                    self.samples = dt
                else: return 502
            if not self.samples: return 502

            if self.__experiment_type == 'sensitivity':
                if not (self.sensitivity_as_change_in_simulation or
                        len(self.obs_variables) > 0): return 600
        # end [step]

        return 0

    def find_counter_variable(self, varname):
        for var in self.sim_variables:
            if var.varname == varname: return var
        
        for var in self.derived_variables:
            if var.varname == varname: return var
        
        return None

    def multi_problem_celllist_consistency_test(self):
        param_indices = self.multiproblem_parameter_index_list
        
        # [+] map calunit to parameter by parameter index
        param_calunit = {}
        for i in range(len(param_indices)):
            for ip in param_indices[i]:
                try: param_calunit[ip].append(i)
                except: param_calunit[ip] = [i]
        # [.]
        
        cunit_cells = [np.array(x) for x in self.calunit_cellls]
        
        iparams = set(param_calunit.keys())
        for i in iparams:
            iunits = param_calunit[i]
            param = self.parameters[i] 
            if len(param.cell_list) != len(iunits): 
                # return False
                print('False1')
            
            param_cells = [np.array(x) for x in param.cell_list]
            for j in range(len(param_cells)):
                iu = iunits[j]
                try:
                    if np.abs(param_cells[j]-cunit_cells[iu]).sum() != 0:
                        # return False
                        print('False2')
                except: 
                    print('False3')
                    # return False        
        
        return True

    
    def get_parameter_indices_for_manyPoc(self, parameter_index_filename):
        
        if len(self.parameters) == 0: return []
        
        paramnames_all = gg.read_cell_info(
            parameter_index_filename, data_type=str
        )
        

        # [+] find and remove those parameters that are not used in 
        # multi-problem calibration
        all = set([p.parameter_name for p in self.parameters])
        used = set(
            [y for x in paramnames_all for y in x]
        )
        not_used = list(all - used)

        for pname in not_used:
            for i in range(len(self.parameters)):
                if self.parameters[i].parameter_name == pname:
                    _ = self.parameters.pop(i)
                    break
        # [.]

        # [+] check whether or not all parameters in parameter_index_filename
        # are already available in self.parameters list
        all = set([p.parameter_name for p in self.parameters])
        if np.sum([(x not in all) for x in used]) > 0: 
            return []
        # [.]

        param_index = dict()
        for i in range(len(self.parameters)): 
            param_index[self.parameters[i].parameter_name] = i

        param_list = []
        for pnames in paramnames_all:
            ii = [param_index[x] for x in pnames]
            param_list.append(tuple(ii))
        
        return tuple(param_list) 
                    
    def get_objective_indices_for_manyPoc(self, objective_index_filename):
        if len(self.obs_variables) == 0: return []
        
        obj_index = dict()
        for i in range(len(self.obs_variables)):
            obj_index[self.obs_variables[i].varname] = i 

        varnames_all = gg.read_cell_info(
            objective_index_filename, data_type=str
        )
        
        objective_list = []
        for varnames in varnames_all:
            indices = []
            for i in range(len(varnames)):
                vname = varnames[i].strip()
                if vname != '': indices.append(obj_index[vname])
            if len(indices) > 0:
                # indices.sort()
                objective_list.append(tuple(indices))
        
        return tuple(objective_list)
    
    def generate_target_cells_from_station_file(self):
        '''
        This method generate basin cell list from given station file and then 
        assign them to variables and parameter. However, if target cell list 
        (either of a variable or of a parameter) is provided by another mean 
        (i.e., usign old method), the cell list will not be overwritten. This 
        will ensure explicit assignment of target cell if it is needed.

        Returns:
        bool
            True on success, False otherwise
        '''
        succeed = True

        # setp: 
        # get basin outlet cells
        filename = os.path.join(
            WaterGAP.home_directory, WaterGAP.station_filename
        )
        outlets = Station.get_stations(filename, rowcol_only=True)
        if len(outlets) == 0: return False
        # end [step]

        # step: 
        # compute entire upstream basin extents
        succeed = Upstream.read_flow_data(
            unf_input=True, model_version=WaterGAP.model_version
        )
        if not succeed: return False
        basins = Upstream.compute_basin_extent(outlets)
        if len(basins) != len(outlets): return False
        # end [step]

        # step: 
        # compute disjoint basins (if applicable) and discharge outlet cells
        # for all basins
        discharge_outlets, discharge_outlets_without_supbasin = [], []
        if self.disjoint_basin_extent:
            supbasins = Upstream.find_super_basin(outlets)

            discharge_outlets = Upstream.find_basin_discharge_cell(
                basins, supbasins
            )
            
            discharge_outlets_without_supbasin = \
            Upstream.find_basin_discharge_cell(basins, {})
            
            basins = Upstream.compute_nonoverlapping_basin_extent(basins, supbasins)
        else:
            for cell in outlets: discharge_outlets.append([cell])
        # end [step]

        # step: 
        # find wghm cell num and area for all basin cells
        basin_cellnum, basin_cellareas = [], []
        for key, value in basins.items():

            cnums, careas = [], []
            for cell in value:
                cnums.append(gg.get_wghm_cell_number(cell[0], cell[1]))
                careas.append(gg.find_wghm_cellarea(cell[0]))

            basin_cellnum.append(cnums)
            basin_cellareas.append(careas)
        # end [step]

        # step: 
        # find wghm cell num of discharge outlets
        cellnum_discharge, cellnum_discharge_without_supbasin = [], []
        for basin_outlets in discharge_outlets:
            cnums = []
            for cell in basin_outlets: 
                cnums.append(gg.get_wghm_cell_number(cell[0], cell[1]))
            cellnum_discharge.append(cnums)

        for basin_outlets in discharge_outlets_without_supbasin:
            cnums = []
            for cell in basin_outlets: 
                cnums.append(gg.get_wghm_cell_number(cell[0], cell[1]))
            cellnum_discharge_without_supbasin.append(cnums)
        # end [step]

        # step: 
        # assign target cells in simulation variables
        if self.calibration_type in ['multiple', 'many']:
            simvarmap = {}
            for var in self.sim_variables:
                simvarmap[var.varname] = var
            
            for var in self.derived_variables:
                simvarmap[var.varname] = var

            for prob_no in range(self.poc_problem_count):
                varindices = self.multiproblem_objective_index_list[prob_no]
                for num in varindices:
                    obsvar = self.obs_variables[num]
                    var = simvarmap[obsvar.counter_variable]

                    cl = basin_cellnum[prob_no]
                    if var.basin_outlets_only: cl = cellnum_discharge[prob_no]
                    var.add_unit_extent_cellnums(cl)
        else:
            for var in self.sim_variables:
                if not var.basin_cell_list:
                    if var.basin_outlets_only:
                        # if not var.boo_consider_super_basins:
                        #     var.basin_cell_list = cellnum_discharge_without_supbasin
                        # else: var.basin_cell_list = cellnum_discharge
                        var.basin_cell_list = cellnum_discharge
                    else: var.basin_cell_list = basin_cellnum

                if not var.cell_weights and var.cell_area_as_weight: 
                    var.cell_weights = basin_cellareas
        # end [step]

        # step: 
        # assign target cells in parameters
        if self.calibration_type in ['multiple', 'many']:
            for prob_no in range(self.poc_problem_count):
                paramindices = self.multiproblem_parameter_index_list[prob_no]
                cl = basin_cellnum[prob_no]

                for num in paramindices:
                    param = self.parameters[num]
                    param.add_unit_extent_cellnums(cl)
        else:
            unique_target_cells = []
            for basin in basin_cellnum: unique_target_cells += basin
            unique_target_cells = list(set(unique_target_cells))

            for param in self.parameters:
                if not param.cell_list: param.cell_list = unique_target_cells
        # end [step]

        return succeed

    def get_copies_of_single_unit_parameters(
        self, calunit_index, param_values=[]
    ):
        """
        This method creates a list of copies of parameter for a single basin/
        unit from the common parmeter sets in a multi-unit problem

        Parameters:
        :param calunit_index (int)
            index of experimental unit
        :param param_values (list of float; optional)
            list of parameter values; if provided, the current parameter value 
            will be updated by the values in this list. The values must be 
            provided in the same order as they are defined in the multi-problem
            parameter list file. in addition, the length of the parameter value
            list must match with the parameter list in the multi-problem 
            parameter file
        :return (list of Parameter)
            A list of Parameter for the target experimental unit
        """
        
        if not self.multiproblem_parameter_index_list or not self.parameters: 
            return [] 

        # [ ] listing parameter indices in the earlier basins which is used to 
        # determine index of the cell list for the current basin. Note that not 
        # all parameters get selected for all units that cause the length of the
        # the cell list of a parameter sometimes less than the no. of basins
        #  
        param_indices_earlier_units = []
        for i in range(calunit_index):
            param_indices_earlier_units \
            += self.multiproblem_parameter_index_list[i]
        param_indices_earlier_units = np.array(param_indices_earlier_units)
        
        param_indices_curr = self.multiproblem_parameter_index_list[calunit_index]
        # [.]

        
        # [ ] create (deep) copies of parameters for the target experimental 
        # unit
        param_count = len(param_indices_curr)
        
        parameter_list =[]
        for i in range(param_count):
            # deep copy the parameter instance
            i_param = param_indices_curr[i]
            param = deepcopy(self.parameters[i_param])
            
            # update the cell list of the parameter for the target experiemntal 
            # unit
            i_celllist = (param_indices_earlier_units==i_param).sum()
            param.cell_list=self.parameters[i_param].cell_list[i_celllist]
            
            parameter_list.append(param)
        # [.]

        # [ ] set parameter values, if provided 
        if len(param_values) == len(parameter_list):
            for i in range(len(parameter_list)):
                parameter_list[i].parameter_value = param_values[i]
        # [.]

        return parameter_list

    def write_general_experiment_settings(self, file):
        """
        The method writes the general configuration options i.e., the basic 
        experiment settings into a file.

        @param
        file (file descriptor): a open and functional writable file descriptor

        @return (bool)
        True on success, False otherwise
        """
        succeed = True

        text_lines = []
        text_lines.append('BEGIN SETTINGS')
        if self.experiment_type:
            keyword = 'experiment_type'
            value = self.experiment_type
            text_lines.append('%s = %s'%(keyword, value))

        if self.experiment_name:
            keyword = 'experiment_name'
            value = self.experiment_name
            text_lines.append('%s = %s'%(keyword, value))

        if self.experiment_type in ['calibration']: 
            keyword = 'calibration_type'
            value = self.calibration_type
            text_lines.append('%s = %s'%(keyword, value))

            keyword = 'maximum_iteration'
            value = self.maximum_iteration
            text_lines.append('%s = %d'%(keyword, value))

            keyword = 'objective_output_filename'
            value = self.objective_values_output_filename
            if value: text_lines.append('%s = %s'%(keyword, value))

            keyword = 'parameter_output_filename'
            value = self.parameter_value_output_filename
            if value: text_lines.append('%s = %s'%(keyword, value))

            keyword = 'result_filename'
            value = self.calibration_result_output_filename
            if not value: value = '[not provided]'
            text_lines.append('%s = %s'%(keyword, value))

            keyword = 'runtime_dynamics_filename'
            value = self.runtime_dynamics_output_filename
            if value: 
                text_lines.append('%s = %s'%(keyword, value))

                keyword = 'runtime_dynamics_write_frequency'
                value = self.runtime_dynamics_frequency
                text_lines.append('%s = %d'%(keyword, value))
            
            if self.calibration_type in ['many', 'multiple']:
                keyword = 'multiproblem_calibration_parameter_list_filename'
                value = self.multiproblem_parameter_list_filename
                if not value: value = '[not provided]'
                text_lines.append('%s = %s'%(keyword, value))

                keyword = 'multiproblem_calibration_objective_list_filename'
                value = self.multiproblem_objective_list_filename
                if not value: value = '[not provided]'
                text_lines.append('%s = %s'%(keyword, value))

        if self.experiment_type in ['sa', 'sensitivity', 'glue', 'se', 'simulation']:
            keyword = 'sample_filename'
            value = self.input_sample_filename
            if not value: value = '[not provided]'
            text_lines.append('%s = %s'%(keyword, value))
        
        keyword = 'parameter_description_filename'
        value = self.parameter_info_filename
        if value: text_lines.append('%s = %s'%(keyword, value))
    
        keyword = 'save_simulation_output'
        value = self.__dump_simulation_timeseries
        if value: 
            text_lines.append('%s = %s'%(keyword, 'true'))

            keyword = 'output_directory'
            value = self.output_directory
            if not value: value = '[not provided]'
            text_lines.append('%s = %s'%(keyword, value))
        
        if self.compute_upstream_from_station_file:
            keyword = 'compute_upstream_from_station_file'
            value = 'true'
            text_lines.append('%s = %s'%(keyword, value))
            
            keyword = 'non_overlapping_basin'
            value = 'true' if self.disjoint_basin_extent else 'false'
            text_lines.append('%s = %s'%(keyword, value))

        keyword = 'filename_calibration_unit_cells'
        value = self.calunit_cells_filename
        if value: text_lines.append('%s = %s'%(keyword, value))

        keyword = 'filename_calibration_unit_stationcells'
        value = self.calunit_stationcell_filename
        if value: text_lines.append('%s = %s'%(keyword, value))
        
        keyword = 'parallel_evaluation'
        value = 'true' if self.parallel_evaluation else 'false'
        if value: text_lines.append('%s = %s'%(keyword, value))
        
        text_lines.append('END SETTINGS')
        
        try:
            _ = file.write('\n'.join(text_lines))
        except: succeed = False

        return succeed 

    @staticmethod    
    def write_configuration_file(config, filename_out):
        config = Configuration()

        file = open(filename_out, 'w')
        succeed = config.write_general_experiment_settings(file)
        succeed &= WaterGAP.write_watergap_configurations(file)
        succeed &= Parameter.write_parameter_description(config.parameters, file)
        file.close()

        return True
    
    
    
    
    @staticmethod
    def runtime_report(
        filename_config:str,
        filename_out:str
    ):
        f = open(filename_out, 'a')

        today = datetime.now()
        text = """
_______________________________________________________________________________
                Runtime Configuration-Object Correctness Test
                         [Written by: H.M. Mehedi]
_______________________________________________________________________________
Date: %s
    
Name of the File: %s
\n\n\n""" % (str(today), filename_config)
        f.write(text)

        if not os.path.exists(filename_config):
            message = 'configuration file does not exist: %s\n'%filename_config
            f.write(message)
            f.close()
            return -1

        config = Configuration.read_configuration_file(filename_config)
        if not config:
            message = 'wrong file format: %s\n'%filename_config
            f.write(message)
            f.close()
            return -1

        err_code = config.is_okay(error_code=True)
        if err_code == 0:
            message = 'configuration overall check  [okay]\n'
        else: message = 'configuration overall check  [failed: error %d]\n' % \
                        err_code
        f.write(message)

        # report general setting
        message = '\n[SECTION] BASIC SETTINGS:\n'
        f.write(message)

        message = '\tMode:%s\n' % config.experiment_type
        f.write(message)

        message = '\tOuput directory: %s\n' % config.output_directory
        f.write(message)

        if not os.path.exists(config.output_directory):
            message = '\tOutput directory: [does not exist]\n'
        else: message = '\tOutput directory: [exists] \n'
        f.write(message)

        message = '\tSample filename: %s\n' % config.input_sample_filename
        f.write(message)

        message = '\tNumber of samples: %d\n'%len(config.samples)
        f.write(message)

        # report model settings
        message = '\n[SECTION] MODEL CONFIGURATION:\n'
        f.write(message)

        if WaterGAP.is_okay():
            message = '\tWaterGAP model overall check [okay]\n'
        else: message = '\tWaterGAP model overall check [failed]\n'
        f.write(message)

        if os.path.exists(WaterGAP.home_directory):
            message = '\tModel home directory: [exists]\n'
        else: message = '\tModel home directory: [does not exist]\n'
        f.write(message)

        message = '\tstart year: %d\n'%WaterGAP.start_year
        f.write(message)

        message = '\tend year: %d\n'%WaterGAP.end_year
        f.write(message)

        message = '\n[SECTION] PARAMETER:\n'
        f.write(message)

        message = '\tNumber of parameter: %d\n' % len(config.parameters)
        f.write(message)

        param_names = []
        for p in config.parameters: param_names.append(p.parameter_name)
        param_info = ParameterInfo.get_selected_paramter_info(param_names=param_names)

        param_acronyms = ','.join([param_info[p]['acronym'] for p in param_names])
        message = '\tparameter names: %s\n' % param_acronyms
        f.write(message)

        succeed = True
        for p in config.parameters:
            if (p.get_lower_bound() != param_info[p.parameter_name]['min'] or
                p.get_upper_bound() != param_info[p.parameter_name]['max']):
                succeed = False; break
        if succeed: message = '\tparameter range: [correct]\n'
        else: message = '\tparameter range: [not correct]\n'
        f.write(message)


        message = '\tnumber of grid cells: '
        temp = config.parameters[0].cell_list
        if len(temp) > 1:
            for p in config.parameters:
                counts =[len(x) for x in p.cell_list]

                f.write(message + '\n')

                message = '\t\t%s: %s [total = %d]'%(
                    p.parameter_name,
                    ', '.join([str(x) for x in counts]),
                    sum(counts)
                )
            f.write(message)
        else:
            for p in config.parameters:
                try: count = len(p.cell_list[0])
                except: count = 0
                message = '\n\t\t%s: total count = %d'%(
                    p.parameter_name, count
                )

                f.write(message)

        message = '\n[SECTION] VARIABLE:\n'
        f.write(message)

        message = '\tnumber of simulation variables: %d\n' % len(config.sim_variables)
        f.write(message)

        succeed = True
        for v in config.sim_variables:
            if not v.is_okay(): succeed = False; break
        if succeed:  message = '\tgeneral check for variables: [okay]\n'
        else: message = '\tgeneral check for variables: [not okay]\n'
        f.write(message)

        if False: # if succeed:
            # erroneous
            counts =[len(v.basin_cell_list) for v in config.sim_variables]
            if np.mean(counts) == counts[0]:
                message = '\tnumber of basin in variables: [consistent]\n'
                f.write(message)

                message='\tnumber of basin: %d\n'%counts[0]
            else: message = '\tnumber of basin in variables: [not consistent]\n'
            f.write(message)

            succeed = True
            varlist = [v for v in config.sim_variables if len(v.basin_cell_list[0]) > 1]

            counts =[[len(v.basin_cell_list[i]) for i in range(len(v.basin_cell_list))]
                     for v in varlist]
            if np.abs(np.array(counts).mean(axis=0)-np.array(counts[0])).sum() != 0:
                succeed = False

            if succeed:
                counts =[np.array(v.basin_cell_list).size for v in varlist]
                if np.mean(counts) != counts[0]: succeed = False

            if succeed: message = '\ttarget cell list: [consistent]\n'
            else: message = '\ttarget cell list: [not consistent]\n'
            f.write(message)

            succeed = True
            for v in config.sim_variables:
                if len(v.cell_weights) != 0:

                    weight_counts = [len(v.cell_weights[i]) for i in range(len(v.cell_weights))]
                    cell_counts = [len(v.basin_cell_list[i]) for i in range(len(v.basin_cell_list))]

                    if np.abs(np.array(weight_counts)-np.array(cell_counts)).sum() == 0:
                        f.write('\t[%s] cell counts: [consistent]\n' % v.varname)
                    else: f.write('\t[%s] cell counts: [not consistent]\n' % v.varname)

                    weight_sums = [np.sum(v.cell_weights[i]) for i in range(len(v.cell_weights))]

                    message = '\t[%s] area sum: %s\n' % (v.varname, ','.join([str(x) for x in weight_sums]))
                    f.write(message)

        message = '\n\nreport success!!\n'
        f.write(message)
        f.close()

        return True
    
    