from ast import arg, expr_context
from cmath import exp
from email.headerregistry import HeaderRegistry
from glob import glob
import os, sys
from tabnanny import verbose
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

def set_value(key, value):
    try: 
        if key == '--observation-file': globals()['filename_observation'] = value
        elif key == '--simulation-file':
            globals()['filename_prediction_summary'] = value
        elif key == '--output-file': globals()['filename_out'] = value
        elif key == '--nsample': globals()['samples_per_process'] = int(value)
        elif key == '--output-directory':  globals()['directory_out'] = value
        elif key == '--reference-period-start': 
            globals()['reference_period_start_year'] = int(value)
        elif key == '--reference-period-end': 
            globals()['reference_period_end_year'] = int(value)
        elif key == '--start-year': globals()['start_year'] = int(value)
        elif key == '--end-year': globals()['end_year'] = int(value)
        elif key == '--conversion-factor-sim': 
            globals()['conversion_factor_sim'] = float(value)
        elif key == '--conversion-factor-obs': 
            globals()['conversion_factor_obs'] = float(value)
        elif key == '--basin-id': globals()['basinid'] = int(value)
        elif key == '--compute-anomaly':
            if value.lower() in ['true', 't', 'yes', 'y', '1']: 
                globals()['compute_anomaly'] = True
            else:  globals()['compute_anomaly'] = False
        elif key == '--verbose':
            if value.lower() in ['true', 't', 'yes', 'y', '1']: 
                globals()['compute_anomaly'] = True
            else:  globals()['compute_anomaly'] = False
    except: pass
    
def main(argv):
    global filename_observation
    global filename_prediction_summary
    global filename_out
    #global samples_per_process
    global directory_out
    global fun, funnames
    global compute_anomaly
    global reference_period_start_year
    global reference_period_end_year
    global start_year, end_year
    global conversion_factor_sim
    global conversion_factor_obs
    global basinid

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
                 '--conversion-factor-obs', '--basin-id', '--verbose']
    
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
        obj_df = Glue.compute_objective(
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
                    conversion_factor_obs=conversion_factor_obs
        )
        temp = os.path.splitext(filename_out)
        filename_out = os.path.join(directory_out, 
                                    '%s_%d%s'%(temp[0], world_rank, temp[1]))
        obj_df.to_csv(filename_out, index=False, header=False, mode='w')
    else: return 201

    return os.EX_OK

def create_example_bashfile(filename_out):
    multiline_text = """
#!/usr/bin/bash
#SBATCH --job-name=GlueObjCom
#SBATCH --partition=qdefault
#SBATCH --ntasks=20
#SBATCH --cpus-per-task=1  
#SBATCH --mem-per-cpu=500  
#SBATCH --time=0-05:00:00
#SBATCH -e report/GlueObjectiveComputation.err
#SBATCH -o report/GlueObjectiveComputation.out

module load Python/Python-3.6.9
module load openmpi/openmpi-4.1.0


directory_out="objectives_1e5"
options=(
    --observation-file ../observations/q_km3pmon_calib_seine_6122100.csv
    --simulation-file output/discharge_km3.5.unf0
    --output-directory $directory_out
    --output-file discharge_fx.csv
    --nsample 5000
    --compute-anomaly false
    --reference-period-start 2003
    --reference-period-end 2014
    --start-year 2003
    --end-year 2014
    --conversion-factor-sim  1
    --conversion-factor-obs 1
    --basin-id 0
    --verbose true
)
funs=(nse kge rmse alpha beta)

mkdir -p $directory_out
rm -rf $directory_out/*

app="~/ProjectWGHM/glue_objective_computer_mpi.py"
mpirun ./wrapper python3 $app ${options[@]} "${funs[@]/#/--fun }"
#app="/mnt/d/mhasan/Code\&Script/ProjectWGHM/glue_objective_computer_mpi.py"
#mpirun -n 3 ./wrapper python3 "$app" ${options[@]} "${funs[@]/#/--fun }"

mkdir $directory_out/summary
cat $directory_out/*.* >> $directory_out/summary/combined.dat
rm $directory_out/*.*
    """

    try:
        f = open(filename_out, 'w')
        f.write(multiline_text)
        f.close
    except: return False

    return True



if __name__ == '__main__': main(sys.argv)