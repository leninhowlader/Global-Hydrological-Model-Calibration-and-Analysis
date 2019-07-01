import os, sys, numpy as np
sys.path.append('F:/mhasan/Code&Script/ProjectWGHM')
from calibration.wgapoutput import WGapOutput
from evaluator_step_two import compute_rmsd, construct_time_series
from utilities.fileio import write_flat_file
from datetime import datetime

r = 400
M = 24
working_directory = 'F:/mhasan/experiments/GlobalCDA/SA_mississippi/replication_three/'
# config_filename = 'config/configuration_eet_sample_evaluation_mississippi_step_one.txt' 
output_filename = 'output_step_two/twsv_km3_rmsd.csv'

def main():
    global working_directory, config_filename, r, M, output_filename
    
    # step: set working directory
    # os.chdir(working_directory)
    # config = Configuration.read_configuration_file(config_filename)
    
    # step: compute the total number of samples
    nsamples = r * (M + 1)
    
    # step: read all sws component storages i.e. local lake, global lake, local wetland, global wetland, 
    #       reservoir and river storages
    filename = os.path.join(working_directory, 'output_R3/TWS_km3.15.unf0')
    d_tws = WGapOutput.read_unf(filename)
    
    # step: find out the basin ids
    basins = np.unique(d_tws[:,1])
    
    results_rmsd = []
    for bid in basins:
        print('current basin no.: %d' %bid, end='', flush=True)
        t = datetime.now()
        
        time_series_ref = None
        
        for sid in range(nsamples):
            # step: construct component time-series and sum them to form total sws time-series
            ts_tws = construct_time_series(d_tws, sid, bid)
            time_series_curr = ts_tws - np.mean(ts_tws)
            
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
    filename = os.path.join(working_directory, output_filename)
    succeed = write_flat_file(filename, results_rmsd, separator=',')
    
    # step: return
    return succeed
    
if __name__ == '__main__': 
    succeed = main()
    if succeed: print('The program exits with success.')
    else: print('Error!! The process is aborted!')
    