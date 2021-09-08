from collections import OrderedDict

class WaterGapConfig:
    def __init__(self, execution_mode='OL'):
        self.option_filename = 'OPTIONS.DAT'
        self.output_option_filename = 'OUTPUT_OPTIONS.DAT'
        self.routing_option_filename = 'ROUTING.DAT'
        self.station_filename = 'STATIONS.DAT'
        self.singlecell_output_option_filename = 'SINGLECELL_OUTPUT_OPTIONS.DAT'
        self.singlecell_number_filename = 'SINGLECELLS.DAT'

        self.input_directory = ''
        self.climate_forcing_data_directory = ''
        self.routing_data_directory = ''
        self.water_use_data_directory = ''
        self.glacier_data_directory = ''
        self.output_directory = ''

        self.parameter_filename = ''

        self.start_year = 1901
        self.start_month = 1
        self.end_year = 2016
        self.end_month = 12
        self.time_step_in_years = 1
        self.intial_year_count = 0

        self.mean_state_filename = ''
        self.lastday_state_filename = ''
        self.day_state_filename = ''
        self.lastday_snowinelevation_filename = ''
        self.lastday_additional_variables_filename = ''

        self.wghm_state_filename = ''
        self.calibration_parameters_filename = ''
        self.snowinelevation_startvalue_filename = ''
        self.startvalues_additional_variable_filename = ''

        self.execution_mode = execution_mode
        #self.descriptions = OrderedDict()

    def is_okay(self):
        if (not (self.option_filename and self.output_option_filename and
                 self.routing_option_filename and self.station_filename and
                 self.input_directory and self.climate_forcing_data_directory and
                 self.routing_data_directory and self.water_use_data_directory
                 and self.glacier_data_directory and self.output_directory and
                 self.parameter_filename)): return False
        elif not (1901 <= self.start_year <= self.end_year): return False
        elif not (1 <= self.start_month <= 12): return False
        elif not (1 <= self.end_month <= 12): return False
        elif not (1 <= self.time_step_in_years <=
                  (self.end_year - self.start_year +1)): return False
        elif not self.intial_year_count >= 0: return False

        if self.execution_mode != 'OL':
            if not (self.mean_state_filename and self.lastday_state_filename and
                    self.day_state_filename and
                    self.lastday_snowinelevation_filename and
                    self.lastday_additional_variables_filename and
                    self.wghm_state_filename and
                    self.calibration_parameters_filename and
                    self.snowinelevation_startvalue_filename and
                    self.startvalues_additional_variable_filename):
                return False

        return True

    @staticmethod
    def read_watergap_config_file(filename_in, execution_mode='OL'):
        config = WaterGapConfig(execution_mode=execution_mode)

        f = None
        try:
            f = open(filename_in, 'r')
            for line in f:
                line = line.strip()
                if line and line[0] != '#':
                    temp = line.split()

                    if len(temp) > 2:
                        key, value = temp[0].strip(), temp[1].strip()
                        if key != '' and value != '':
                            if key == 'runtime_options':
                                config.option_filename = value
                            elif key == 'output_options':
                                config.output_option_filename = value
                            elif key == 'routing':
                                config.routing_option_filename = value
                            elif key == 'stations':
                                config.station_filename = value
                            elif key == 'scell_options':
                                config.singlecell_output_option_filename = value
                            elif key == 'scells':
                                config.singlecell_number_filename = value
                            elif key == 'input_dir':
                                config.input_directory = value
                            elif key == 'climate_dir':
                                config.climate_forcing_data_directory = value
                            elif key == 'routing_dir':
                                config.routing_data_directory = value
                            elif key == 'water_use_dir':
                                config.water_use_data_directory = value
                            elif key == 'param_json':
                                config.parameter_filename = value
                            elif key == 'glacier_dir':
                                config.glacier_data_directory = value
                            elif key == 'output_dir':
                                config.output_directory = value
                            elif key == 'start_year':
                                year = 1900
                                try: year = int(value)
                                except: pass

                                if year > 1900: config.start_year = year
                            elif key == 'start_month':
                                month = 0
                                try: month = int(value)
                                except: pass

                                if month > 0: config.start_month = month
                            elif key == 'end_year':
                                year = 1900
                                try: year = int(value)
                                except: pass

                                if year > 1900: config.end_year = year
                            elif key == 'end_month':
                                month = 0
                                try: month = int(value)
                                except: pass

                                if month > 0: config.end_month = month
                            elif key == 'time_step':
                                step = 0
                                try: step = int(value)
                                except: pass

                                if step > 0: config.time_step_in_years = step
                            elif key == 'num_init_years':
                                nyear = -1
                                try: nyear = int(value)
                                except: pass

                                if nyear > -1: config.intial_year_count = nyear
                            elif key == 'output_state_mean':
                                config.mean_state_filename = value
                            elif key == 'output_state_lastday':
                                config.lastday_state_filename = value
                            elif key == 'output_state_day':
                                config.day_state_filename = value
                            elif key == 'output_snowInElevation_lastday':
                                config.lastday_snowinelevation_filename = value
                            elif key == 'additionalOutIn_lastday':
                                config.lastday_additional_variables_filename = value
                            elif key == 'wghm_state':
                                config.wghm_state_filename = value
                            elif key == 'calibration_parameters':
                                config.calibration_parameters_filename = value
                            elif key == 'snowInElevation_startvalues':
                                config.snowinelevation_startvalue_filename = value
                            elif key == 'additionalOutIn_startvalues':
                                config.startvalues_additional_variable_filename \
                                = value
        except: config = None
        finally:
            try: f.close()
            except: pass

        return config

    def text_max_length(self, section_name):
        max_length = 0
        if section_name == 'option_files':
            max_length = max(len(self.option_filename),
                             len(self.output_option_filename),
                             len(self.routing_option_filename),
                             len(self.station_filename),
                             len(self.singlecell_output_option_filename),
                             len(self.singlecell_number_filename))
        elif section_name == 'data_directory':
            max_length = max(len(self.input_directory),
                             len(self.climate_forcing_data_directory),
                             len(self.routing_data_directory),
                             len(self.water_use_data_directory),
                             len(self.glacier_data_directory),
                             len(self.output_directory),
                             len(self.parameter_filename))

        elif section_name == 'time_info':
            max_length = max(len(str(self.start_year)),
                             len(str(self.start_month)),
                             len(str(self.end_year)),
                             len(str(self.end_month)),
                             len(str(self.time_step_in_years)),
                             len(str(self.intial_year_count)))

        elif section_name == 'state_output':
            max_length = max(len(self.mean_state_filename),
                             len(self.lastday_state_filename),
                             len(self.day_state_filename),
                             len(self.lastday_snowinelevation_filename),
                             len(self.lastday_additional_variables_filename))

        elif section_name == 'state_input':
            max_length = max(len(self.wghm_state_filename),
                             len(self.calibration_parameters_filename),
                             len(self.snowinelevation_startvalue_filename),
                             len(self.startvalues_additional_variable_filename))

        return max_length

    def write_wgapConfig_file(self, filename_out):
        succeed = True

        f = None
        try:
            f = open(filename_out, 'w')

            # info text
            f.write("# This is the central configuration file to run WGHM\n" +
                    "### Search advice: WGHM_howtorun_manual.md should be part of " +
                    "the internal wiki\n")\

            # section headings: section - 1
            max_length = 20 * self.text_max_length('option_files')//20 + 20
            f.write('\n' + '#' * 120 + '\n')

            f.write("# Section 1 - General option files and paths - used for " +
                    "closed  and open loop\n" +
                    "## Filenames of additional config files\n")

            # section variables
            f.write("runtime_options".ljust(40, ' ') +
                    self.option_filename.ljust(max_length, ' ') +
                    "WaterGAP option file for choice of algorithms\n")

            f.write("output_options".ljust(40, ' ') +
                    self.output_option_filename.ljust(max_length, ' ') +
                    "WaterGAP configuration for output variable " +
                    "and file format\n")

            f.write("routing".ljust(40, ' ') +
                    self.routing_option_filename.ljust(max_length, ' ') +
                    "River routing dataset\n")

            f.write("stations".ljust(40, ' ') +
                    self.station_filename.ljust(max_length, ' ') +
                    "River gauging virtual stations and their locations\n")

            f.write("scell_options".ljust(40, ' ') +
                    self.singlecell_output_option_filename.ljust(max_length, ' ') +
                    "Single cell output configuration\n")

            f.write("scells".ljust(40, ' ') +
                    self.singlecell_number_filename.ljust(max_length, ' ') +
                    "Single cell numbers\n")

            # info about next subsection
            f.write("\n\n## Paths to input data and output directory\n")
            max_length = 20 * self.text_max_length('data_directory') // 20 + 20

            f.write("input_dir".ljust(40, ' ') +
                    self.input_directory.ljust(max_length, ' ') +
                    "WaterGAP input directory\n")

            f.write("climate_dir".ljust(40, ' ') +
                    self.climate_forcing_data_directory.ljust(max_length, ' ') +
                    "Climate data directory\n")

            f.write("routing_dir".ljust(40, ' ') +
                    self.routing_data_directory.ljust(max_length, ' ') +
                    "River routing data directory\n")

            f.write("water_use_dir".ljust(40, ' ') +
                    self.water_use_data_directory.ljust(max_length, ' ') +
                    "Wateruse data directory\n")

            f.write("param_json".ljust(40, ' ') +
                    self.parameter_filename.ljust(max_length, ' ') +
                    "Model parameter filename\n")

            f.write("glacier_dir".ljust(40, ' ') +
                    self.glacier_data_directory.ljust(max_length, ' ') +
                    "Glacier data directory\n")

            f.write("output_dir".ljust(40, ' ') +
                    self.output_directory.ljust(max_length, ' ') +
                    "WaterGAP output directory\n")

            # section headings: section - 2
            f.write( '\n' + '#'.ljust(120, '#') + '\n')
            f.write("# Section 2 - Temporal configuration - used for " +
                    "closed and open loop\n" + "## Time data\n")

            max_length = 20 * self.text_max_length('time_info') // 20 + 30
            # section variables
            f.write("start_month".ljust(40, ' ') +
                    str(self.start_month).ljust(max_length, ' ') +
                    "Start month of simulation\n")

            f.write("start_year".ljust(40, ' ') +
                    str(self.start_year).ljust(max_length, ' ') +
                    "Start year of simulation\n")

            f.write("end_month".ljust(40, ' ') +
                    str(self.end_month).ljust(max_length, ' ') +
                    "End month of simulation\n")

            f.write("end_year".ljust(40, ' ') +
                    str(self.end_year).ljust(max_length, ' ') +
                    "End year of simulation\n")

            f.write("time_step".ljust(40, ' ') +
                    str(self.time_step_in_years).ljust(max_length, ' ') +
                    "Time step of simulation in year\n")

            f.write("num_init_years".ljust(40, ' ') +
                    str(self.end_year).ljust(max_length, ' ') +
                    'number of years for initial simulation runs')


            # headings for section 3
            f.write('\n' + '#'.ljust(120, '#')  + '\n' +
                    '#'.ljust(120, '#') + '\n' +
                    '#'.ljust(120, '#') + '\n')

            f.write("# THE FOLLOWING SECTIONS ARE ONLY NEEDED FOR USING " +
                    "LOOP FUNCTIONALITIES\n" +
                    "# Comment every line out for Closed Loop (aka " +
                    "standard way to run the model), but keep \"end_of_head\"" +
                    "-line (last line)\n" +
                    "# Commenting out is done by adding a \"#\" add the "+
                    "first position of the code line\n")

            # section - 3
            f.write('\n' + '#'.ljust(120, '#') + '\n')
            f.write("# Section 3 - used for Open Loop and to initialize the " +
                    "txt-file structure for open loop runs\n" +
                    "## Open Loop output files\n")

            max_length = 20 * self.text_max_length('state_output') // 20 + 20
            is_open_loop = (self.execution_mode == 'OL')

            if is_open_loop: f.write('#')
            temp = self.mean_state_filename
            if len(temp) == 0: temp = 'NA'
            f.write("output_state_mean".ljust(40, ' ') +
                    temp.ljust(max_length, ' ') +
                    "states of water compartments (monthly mean)\n")

            if is_open_loop: f.write('#')
            temp = self.lastday_state_filename
            if len(temp) == 0: temp = 'NA'
            f.write("output_state_lastday".ljust(40, ' ') +
                    temp.ljust(max_length, ' ') +
                    "states of water compartments (last day of month)\n")

            if is_open_loop: f.write('#')
            temp = self.day_state_filename
            if len(temp) == 0: temp = 'NA'
            f.write("output_state_day".ljust(40, ' ') +
                    temp.ljust(max_length, ' ') +
                    "states of water compartments (daily)\n")

            if is_open_loop: f.write('#')
            temp = self.lastday_snowinelevation_filename
            if len(temp) == 0: temp = 'NA'
            f.write("output_snowInElevation_lastday".ljust(40, ' ') +
                    temp.ljust(max_length, ' ') +
                    "states of snow in elevation layers\n")

            if is_open_loop: f.write('#')
            temp = self.lastday_additional_variables_filename
            if len(temp) == 0: temp = 'NA'
            f.write("additionalOutIn_lastday".ljust(40, ' ') +
                    temp.ljust(max_length, ' ') +
                    "additional output\n")

            # section 4:
            f.write('\n' + '#'.ljust(120, '#') + '\n')
            f.write("# Section 4 - used for Open Loop\n" +
                    "## Open Loop input files\n")
            max_length = 20 * self.text_max_length('state_input') // 20 + 20

            if is_open_loop: f.write('#')
            temp = self.wghm_state_filename
            if len(temp) == 0: temp = 'NA'
            f.write("wghm_state".ljust(40, ' ') +
                    temp.ljust(max_length, ' ') +
                    "states of water compartments in each grid cell\n")

            if is_open_loop: f.write('#')
            temp = self.calibration_parameters_filename
            if len(temp) == 0: temp = 'NA'
            f.write("calibration_parameters".ljust(40, ' ') +
                    temp.ljust(max_length, ' ') +
                    "calibration parameter\n")

            if is_open_loop: f.write('#')
            temp = self.snowinelevation_startvalue_filename
            if len(temp) == 0: temp = 'NA'
            f.write("snowInElevation_startvalues".ljust(40, ' ') +
                    temp.ljust(max_length, ' ') +
                    "states of snow in elevation layers\n")

            if is_open_loop: f.write('#')
            temp = self.startvalues_additional_variable_filename
            if len(temp) == 0: temp = 'NA'
            f.write("additionalOutIn_startvalues".ljust(40, ' ') +
                    temp.ljust(max_length, ' ') +
                    "additional input\n")

            f.write('\n' + '#'.ljust(120, '#') + '\n')
            f.write("end_of_head")
        except Exception as ex:
            print(str(ex))
            succeed = False
        finally:
            try: f.close()
            except: pass # do nothing

        return succeed
