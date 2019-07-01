import os, sys, numpy as np
sys.path.append('F:/mhasan/Code&Script/ProjectWGHM')
from calibration.configuration import Configuration
from calibration.wgapoutput import WGapOutput
from evaluator_step_two import compute_rmsd, construct_time_series
from utilities.fileio import write_flat_file
from datetime import datetime

r = 400
M = 24
working_directory = 'F:/mhasan/experiments/GlobalCDA/SA_mississippi/replication_three/'
# config_filename = 'config/configuration_eet_sample_evaluation_mississippi_step_one.txt' 
output_filename = 'output_step_two/sws_km3_rmsd.csv'

def main():
    global working_directory, config_filename, r, M, output_filename
    
    # step: set working directory
    os.chdir(working_directory)
    # config = Configuration.read_configuration_file(config_filename)
    
    # step: compute the total number of samples
    nsamples = r * (M + 1)
    
    # step: read all sws component storages i.e. local lake, global lake, local wetland, global wetland, 
    #       reservoir and river storages
    d_locallake = WGapOutput.read_unf('output_R3/LocalLake_km3.15.unf0')
    d_globallake = WGapOutput.read_unf('output_R3/GlobalLake_km3.15.unf0')
    d_localwetland = WGapOutput.read_unf('output_R3/LocalWetland_km3.15.unf0')
    d_globalwetland = WGapOutput.read_unf('output_R3/GlobalWetland_km3.15.unf0')
    d_reservoir = WGapOutput.read_unf('output_R3/Reservoir_km3.15.unf0')
    d_river = WGapOutput.read_unf('output_R3/River_km3.15.unf0')
    if not (type(d_locallake) is np.ndarray and type(d_globallake) is np.ndarray and type(d_localwetland) is np.ndarray
            and type(d_globalwetland) is np.ndarray and type(d_reservoir) is np.ndarray and type(d_river) is np.ndarray):
        return False
    if not (d_locallake.shape == d_globallake.shape == d_localwetland.shape == d_globalwetland.shape == d_reservoir.shape
              == d_river.shape): 
        return False
    
    # step: find out the basin ids
    basins = np.unique(d_locallake[:,1])
    
    results_rmsd = []
    for bid in basins:
        print('current basin no.: %d ' %bid, end='', flush=True)
        t = datetime.now()

        time_series_ref = None
        
        for sid in range(nsamples):
            # step: construct component time-series and sum them to form total sws time-series
            ts_ll = construct_time_series(d_locallake, sid, bid)
            ts_gl = construct_time_series(d_globallake, sid, bid)
            ts_lw = construct_time_series(d_localwetland, sid, bid)
            ts_gw = construct_time_series(d_globalwetland, sid, bid)
            ts_rs = construct_time_series(d_reservoir, sid, bid)
            ts_rv = construct_time_series(d_river, sid, bid)
            
            time_series_curr = ts_ll + ts_gl + ts_lw + ts_gw + ts_rs + ts_rv
            
            # step: find whether or not the current sample is a reference sample. if it is a reference
            # sample, assign the current time-series as the reference time-series and set the rmsd (root
            # mean squared difference) to zero. Otherwise, compute rmsd with the reference time-series
            # and the current time-series
            if sid%(M+1) == 0:
                rmsd = 0
                time_series_ref = time_series_curr
            else: rmsd = compute_rmsd(time_series_curr, time_series_ref)
            
            # step: store result into result storage
            results_rmsd.append([bid, sid, rmsd])
        
        # display how much time each sample takes to be processed. [this is just to show that the
        # work is in progress :)]
        tdif = datetime.now() - t
        total_t = tdif.seconds + tdif.microseconds / 10**6
        print('[time: %f seconds]' % (total_t))
    
    # step: store the results into a file
    succeed = write_flat_file(output_filename, results_rmsd, separator=',')
    
    # step: return
    return succeed
    
if __name__ == '__main__': 
    succeed = main()
    if succeed: print('The program exits with success.')
    else: print('Error!! The process is aborted!')
