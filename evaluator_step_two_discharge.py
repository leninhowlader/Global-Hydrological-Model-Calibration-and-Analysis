import os, sys, numpy as np
sys.path.append('F:/mhasan/Code&Script/ProjectWGHM')
from calibration.configuration import Configuration
from calibration.wgapoutput import WGapOutput
from evaluator_step_two import compute_rmsd, construct_time_series
from utilities.fileio import write_flat_file
from datetime import datetime

r = 400
M = 24
working_directory = 'F:/mhasan/experiments/GlobalCDA/SA_mississippi/replication_one/'
# config_filename = 'config/configuration_eet_sample_evaluation_mississippi_step_one.txt' 
output_filename = 'output_step_two/discharge2_km3_rmsd.csv'

def main():
    global working_directory, config_filename, r, M, output_filename
    
    # step: set working directory
    os.chdir(working_directory)
    # config = Configuration.read_configuration_file(config_filename)
    
    # step: compute the total number of samples
    nsamples = r * (M + 1)
    
    d_discharge = WGapOutput.read_unf('output_R1/Discharge_km3.15.unf0')


    results_rmsd = []

    time_series_ref_b5 = None
    time_series_ref_b6 = None
    time_series_ref_b7 = None
    for sid in range(nsamples):
        t = datetime.now()

        # step: construct component time-series and sum them to form total sws time-series
        ts_b7 = construct_time_series(d_discharge, sid, 38760)
        # if ts_b7.shape[0] == 360:
        #     ts_tmp = np.array([])
        #     for i in range(30):
        #         if i%2 == 0:
        #             ts_tmp = np.append(ts_tmp, ts_b7[:12])
        #             ts_b7 = ts_b7[12:]
        #         else: ts_b7 = ts_b7[12:]
        #     ts_b7 = ts_tmp
        ts_b1 = construct_time_series(d_discharge, sid, 34526)
        ts_b2 = construct_time_series(d_discharge, sid, 34191)
        ts_b3 = construct_time_series(d_discharge, sid, 35523)
        ts_b4 = construct_time_series(d_discharge, sid, 37185)

        if not (ts_b1.shape == ts_b2.shape == ts_b3.shape == ts_b4.shape == ts_b7.shape): return False

        ts_b6 = ts_b7 - ts_b1 - ts_b2 - ts_b3
        ts_b5 = ts_b6 - ts_b4

        # testing purpose only
        testing = False
        if testing:
            ts = np.concatenate((ts_b1.reshape(180, 1), ts_b2.reshape(180, 1), ts_b3.reshape(180, 1), ts_b4.reshape(180, 1),
                                 ts_b5.reshape(180, 1), ts_b6.reshape(180, 1), ts_b7.reshape(180, 1)), axis=1)
            write_flat_file('recharge_sid%d.csv'%sid, ts)

        # step: find whether or not the current sample is a reference sample. if it is a reference
        # sample, assign the current time-series as the reference time-series and set the rmsd (root
        # mean squared difference) to zero. Otherwise, compute rmsd with the reference time-series
        # and the current time-series
        if sid%(M+1) == 0:
            rmsd_b5 = 0
            rmsd_b6 = 0
            rmsd_b7 = 0
            time_series_ref_b5 = ts_b5
            time_series_ref_b6 = ts_b6
            time_series_ref_b7 = ts_b7
        else:
            rmsd_b5 = compute_rmsd(time_series_ref_b5, ts_b5)
            rmsd_b6 = compute_rmsd(time_series_ref_b6, ts_b6)
            rmsd_b7 = compute_rmsd(time_series_ref_b7, ts_b7)

        # step: store result into result storage
        results_rmsd.append([5, sid, rmsd_b5])
        results_rmsd.append([6, sid, rmsd_b6])
        results_rmsd.append([7, sid, rmsd_b7])

        t = datetime.now() - t
        print('sample no.: %d [%0.3f sec]' % (sid+1, t.seconds+t.microseconds/10**6))
    # step: store the results into a file
    succeed = write_flat_file(output_filename, results_rmsd, separator=',')
    
    # step: return
    return succeed
    
if __name__ == '__main__': 
    succeed = main()
    if succeed: print('The program exits with success.')
    else: print('Error!! The process is aborted!')
