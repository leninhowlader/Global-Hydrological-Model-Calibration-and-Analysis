import os, sys, numpy as np, pandas as pd
from analyses.glue import Glue

## List of global variables
filename_observation = ''
filename_prediction_summary = ''
filename_out = ''
directory_out = ''
samples_per_process = -1
funs = []
funnames = []
compute_anomaly = False
reference_period_start_year = -1
reference_period_end_year = -1
start_year = -1
end_year = -1
conversion_factor_sim = 1
conversion_factor_obs = 1
basinid = 0
verbose = True
observation_series_count = 1

def set_value(key, value):
    try: 
        if key == '--observation-file': globals()['filename_observation'] = value
        elif key == '--simulation-file':
            globals()['filename_prediction_summary'] = value
        elif key == '--output-file': globals()['filename_out'] = value
        elif key == '--nsample': 
            try: globals()['samples_per_process'] = int(value)
            except: pass
        elif key == '--output-directory':  globals()['directory_out'] = value
        elif key == '--reference-period-start': 
            try: globals()['reference_period_start_year'] = int(value)
            except: pass
        elif key == '--reference-period-end': 
            try: globals()['reference_period_end_year'] = int(value)
            except: pass
        elif key == '--start-year': 
            try: globals()['start_year'] = int(value)
            except: pass 
        elif key == '--end-year': 
            try: globals()['end_year'] = int(value)
            except: pass
        elif key == '--conversion-factor-sim': 
            try: globals()['conversion_factor_sim'] = float(value)
            except: pass
        elif key == '--conversion-factor-obs': 
            try: globals()['conversion_factor_obs'] = float(value)
            except: pass
        elif key == '--basin-id': 
            try: globals()['basinid'] = int(value)
            except: pass
        elif key == '--compute-anomaly':
            if value.lower() in ['true', 't', 'yes', 'y', '1']: 
                globals()['compute_anomaly'] = True
            else:  globals()['compute_anomaly'] = False
        elif key == '--verbose':
            if value.lower() in ['true', 't', 'yes', 'y', '1']: 
                globals()['verbose'] = True
            else:  globals()['verbose'] = False
        elif key == '--observation-series-count':
            try: globals()['observation_series_count'] = int(value)
            except: pass
    except: pass
    
def main(argv):
    global filename_observation
    global filename_prediction_summary
    global filename_out
    global samples_per_process
    global directory_out
    global fun, funnames
    global compute_anomaly
    global reference_period_start_year
    global reference_period_end_year
    global start_year, end_year
    global conversion_factor_sim
    global conversion_factor_obs
    global basinid
    global observation_series_count

    if len(argv) < 3: exit(os.EX_NOINPUT)
    world_rank, world_size = -1, -1
    try:
        world_rank = int(argv[-1])
        world_size = int(argv[-2])
    except: return 100 

    ## read in the arguments
    # for i in range(len(argv)): argv[i] = argv[i].lower()

    argnames  = ['--observation-file', '--simulation-file', '--output-file',
                 '--nsample', '--output-directory', '--compute-anomaly',
                 '--reference-period-start', '--reference-period-end',
                 '--start-year', '--end-year', '--conversion-factor-sim', 
                 '--conversion-factor-obs', '--basin-id', '--verbose',
                 '--observation-series-count']
    
    ## read function names
    # note that multiple fun names can be provided as command line
    # argument
    while '--fun' in argv:
        ikey = argv.index('--fun')
        funnames.append(argv[ikey+1])

        argv = argv[:ikey] + argv[(ikey+2):]
        #for i in [ikey, (ikey+1)]: argv.pop(i)
    ##

    for key in argnames:
        if key in argv: 
            set_value(key=key, value=argv[argv.index(key) + 1])
    ##
    
    # alias
    nsamples = samples_per_process

    if nsamples <= 0: return 101
    if not (filename_observation and filename_prediction_summary): return 102
    if not (filename_out or directory_out): return 103
    if world_size <= 0: return 104
    if world_rank < -1 or world_rank >= world_size: return 105

    sample_id_start = world_rank * nsamples
    sample_id_end = sample_id_start + nsamples - 1
    print('Objectives of samples %d to %d will be computed on processor %d'%(
        sample_id_start, sample_id_end, world_rank
    ))

    period_ref_mean = ()
    if (reference_period_start_year > 1900 < reference_period_end_year and 
        reference_period_end_year > reference_period_start_year): 
        period_ref_mean = (reference_period_start_year, 
                           reference_period_end_year)
    
    if not (start_year > 1900 < end_year and end_year >= start_year):
            start_year = end_year = -1
    
    if not funnames: funnames = ['nse', 'rmse', 'kge']
    funs = Glue.map_objective_functions(funnames=funnames)
    
    if filename_out:
        fx = Glue.compute_objective(
                    filename_obs=filename_observation,
                    filename_simunf=filename_prediction_summary,
                    funs=funs,
                    funnames=tuple(funnames),
                    start_year=start_year, 
                    end_year=end_year,
                    compute_anomaly=compute_anomaly,
                    period_ref_mean=period_ref_mean,
                    basinid=basinid,
                    sample_id_start=sample_id_start,
                    sample_id_end=sample_id_end,
                    conversion_factor_sim=conversion_factor_sim,
                    conversion_factor_obs=conversion_factor_obs,
                    observation_series_count=observation_series_count
        )

        if fx.ndim == 2:
            obj_df = pd.DataFrame(data=fx, columns=None)
            obj_df.iloc[:, 0] = obj_df.iloc[:, 0].astype(int)
        
            temp = os.path.splitext(filename_out)
            filename_out = os.path.join(directory_out, 
                                        '%s_%d%s'%(temp[0], world_rank, temp[1]))
            obj_df.to_csv(filename_out, index=False, header=False, mode='w')
        elif fx.ndim == 3:
            if fx.shape[2] == len(funnames):
                for i in range(fx.shape[2]):
                    obj_df = pd.DataFrame(data=fx, columns=None)
                    obj_df.iloc[:, 0] = obj_df.iloc[:, 0].astype(int)
                
                    temp = os.path.splitext(filename_out)
                    filename_out = os.path.join(directory_out, 
                        '%s_%s_%d%s'%(temp[0], funnames[i], world_rank, temp[1])
                    )
                    
                    obj_df.to_csv(
                        filename_out, index=False, header=False, mode='w'
                    )

            else: return 203
        else: return 202
    else: return 201

    return os.EX_OK

def create_example_bashfile(filename_out):
    multiline_text = """
#!/usr/bin/bash
#SBATCH --job-name=GlueObjCom
#SBATCH --partition=qdefault
#SBATCH --ntasks=100
#SBATCH --cpus-per-task=1  
#SBATCH --mem-per-cpu=500  
#SBATCH --time=0-05:00:00
#SBATCH -e report/GlueObjectiveComputation_GWSA.err
#SBATCH -o report/GlueObjectiveComputation_GWSA.out

module load Python/Python-3.6.9
module load openmpi/openmpi-4.1.0


directory_out="objectives_1e5"
output_filename="objectives_gwsa_entirebasin"                     #without extension
options=(
    --observation-file ~/observations/poc_FGB/gwsa_mm_2003_2016_seine.csv
    --simulation-file output/groundwater_mm.5.unf0
    --output-directory $directory_out
    --output-file "$output_filename".csv
    --nsample 1000
    --compute-anomaly true
    --reference-period-start 2003
    --reference-period-end 2014
    --start-year 2003
    --end-year 2014
    --conversion-factor-sim  1
    --conversion-factor-obs 1
    --basin-id 0
    --verbose true
    --observation-series-count 1
)
funs=(nse kge rmse alpha beta gamma r ioa rsr mae sse)

mkdir -p $directory_out
#rm -rf $directory_out/*

app="~/ProjectWGHM/glue_objective_computer_mpi.py"
mpirun ./wrapper python3 $app ${options[@]} "${funs[@]/#/--fun }"
#app="/mnt/d/mhasan/Code\&Script/ProjectWGHM/glue_objective_computer_mpi.py"
#mpirun -n 3 ./wrapper python3 "$app" ${options[@]} "${funs[@]/#/--fun }"

echo sid "${funs[@]/#/, }" >> $directory_out/"$output_filename".csv
cat $directory_out/"$output_filename"_*.* >> $directory_out/"$output_filename".csv
rm $directory_out/"$output_filename"_*.*
    """

    try:
        f = open(filename_out, 'w')
        f.write(multiline_text)
        f.close
    except: return False

    return True



if __name__ == '__main__': main(sys.argv)