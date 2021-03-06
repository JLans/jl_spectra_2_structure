#/usr/bin/env python

from __future__ import absolute_import, division, print_function
import os
from jl_spectra_2_structure.cross_validation import  CROSS_VALIDATION
import numpy as np
import uuid

from mpi4py import MPI
from mpi4py.futures import MPICommExecutor
#x=1
#print('running this script')
#wasserstein_loss
#kl_div_loss
#Use 3350 max for C2H4, 2200 for CO, and 2000 for NO. Use 750 points for C2H4 and 500 for CO and 450 for NO.
#coverage is 'low', 'high' or a float <= 1
#assert TARGET in ['binding_type','GCN','combine_hollow_sites']
#if __name__ == "__main__":
#if x==1:
def fun(x):
    print("on %s print %g" % (MPI.COMM_WORLD.rank,x))
    seed = uuid.uuid4()
    run_number = str(seed) 
    print('run_number: ' + run_number)
    #try:
    #    run_number = sys.argv[1]
    #except:
    #    "requires an input argument"
    #    raise
    
    L1orL2 = 'L1'
    TRAINING_ERROR = 'gaussian'
    hidden_layer1 = 100
    hidden_layer2 = 100
    hidden_layer_3 = 100
    hidden_layers = (hidden_layer1, hidden_layer2, hidden_layer_3)
    
    setup_list = np.repeat([('CO','low','GCN'),('CO','high','binding_type'),('CO',1,'GCN')\
                                    ,('CO','high','combine_hollow_sites'),('CO','high','GCN')\
                                    ,('NO','low','GCN'),('NO','high','binding_type')\
                                    ,('NO','high','combine_hollow_sites')\
                                    ,('NO',1,'binding_type'),('NO',1,'combine_hollow_sites'),('NO',1,'GCN')\
                                    ,('C2H4','low','binding_type'),('C2H4','low','GCN')\
                                    ,('CO','low','binding_type'),('CO','low','combine_hollow_sites')\
                                    ,('CO',1,'binding_type'),('CO',1,'combine_hollow_sites')\
                                    ,('NO','low','binding_type'),('NO','low','combine_hollow_sites')],5,axis=0).tolist()
    
    which_setup = setup_list[x]
    ADSORBATE = which_setup[0]
    COVERAGE = which_setup[1]
    try:
        COVERAGE = float(COVERAGE)
    except:
        COVERAGE=COVERAGE
    TARGET = which_setup[2]
    epsilon = 10**-12
    alpha = 10**-3
    learning_rate = 0.0004
    if COVERAGE == 'high' and TARGET in ['binding_type','combine_hollow_sites']:
        NUM_TRAIN = 500
        training_sets = 100
        batch_size=5
        epochs = 20
        
    else:
        NUM_TRAIN = 5000
        training_sets = 200
        batch_size=50
        epochs=10
        
    print('batch_size: '+str(batch_size))
    print('learning_rate: '+str(learning_rate))
    print('epsilon: '+str(epsilon))
    print('alpha: '+str(alpha))
    print('NUM_TRAIN: '+str(NUM_TRAIN))
    print('training_sets: '+str(training_sets))
    print('epochs: '+str(epochs))
    print('hidden layers: '+str(hidden_layers))
    #batch_size: 2297
    #learning_rate = 0.06651629336077657
    #epsilon = 0.02872678693613251
    #alpha = 0.001931666535492889
    #NUM_TRAIN = 100000
    #epochs=2
    #training_sets = 2
    if ADSORBATE == 'CO':
        INCLUDED_BINDING_TYPES=[1,2,3,4]
        MAX_COVERAGES = [1, 0.7, 0.2, 0.2]
        BINDING_TYPE_FOR_GCN=[1]
        HIGH_FREQUENCY = 2200
        ENERGY_POINTS=500
        GCN_ALL = False
    elif ADSORBATE == 'NO':
        INCLUDED_BINDING_TYPES=[1,2,3,4]
        MAX_COVERAGES = [1, 1, 1, 1]
        BINDING_TYPE_FOR_GCN=[1]
        HIGH_FREQUENCY = 2000
        ENERGY_POINTS=450
        GCN_ALL = False
    elif ADSORBATE == 'C2H4':
        INCLUDED_BINDING_TYPES=[1,2]
        MAX_COVERAGES = [1, 1]
        BINDING_TYPE_FOR_GCN=[2]
        HIGH_FREQUENCY = 2000
        ENERGY_POINTS=450
        if TARGET == 'GCN':
            GCN_ALL = True
        else:
            GCN_ALL = False
    print('ADSORBATE: '+ADSORBATE)
    print('TARGET: ' + str(TARGET))
    print('COVERAGE: ' + str(COVERAGE))
    print('GCN_ALL: ' + str(GCN_ALL))
    
    work_dir = os.getcwd()
    cross_validation_path = os.path.join(work_dir,'cross_validation_'+ADSORBATE+'_'+TARGET+'_'+str(COVERAGE))
    print(cross_validation_path) 
    CV_class = CROSS_VALIDATION(ADSORBATE=ADSORBATE,INCLUDED_BINDING_TYPES=INCLUDED_BINDING_TYPES\
                                ,cross_validation_path=cross_validation_path, VERBOSE=False)
    CV_SPLITS = 3
    CV_class.generate_test_cv_indices(CV_SPLITS=CV_SPLITS, BINDING_TYPE_FOR_GCN=BINDING_TYPE_FOR_GCN\
        , test_fraction=0.25, random_state=x, read_file=False, write_file=False)
    properties_dictionary = {'batch_size':batch_size, 'learning_rate_init':learning_rate\
    , 'epsilon':epsilon,'hidden_layer_sizes':hidden_layers,'regularization':L1orL2\
    ,'alpha':alpha, 'epochs_per_training_set':epochs,'training_sets':training_sets,'loss': 'wasserstein_loss'}
    CV_class.set_model_parameters(TARGET=TARGET, COVERAGE=COVERAGE\
    , MAX_COVERAGES = MAX_COVERAGES, NN_PROPERTIES=properties_dictionary\
    , NUM_TRAIN=NUM_TRAIN, NUM_VAL=10000, NUM_TEST=10000\
    , MIN_GCN_PER_LABEL=12, NUM_GCN_LABELS=10, GCN_ALL = GCN_ALL, TRAINING_ERROR = TRAINING_ERROR\
    , LOW_FREQUENCY=200, HIGH_FREQUENCY=HIGH_FREQUENCY, ENERGY_POINTS=ENERGY_POINTS)
    CV_RESULTS_FILE = ADSORBATE+'_'+TARGET+'_'+str(COVERAGE)+'_'+ run_number
    CV_class.run_CV_multiprocess(write_file=True, CV_RESULTS_FILE = CV_RESULTS_FILE, num_procs=CV_SPLITS+1)
    #CV_class.run_CV(write_file=True, CV_RESULTS_FILE = CV_RESULTS_FILE)

if __name__ == "__main__":
    with MPICommExecutor(MPI.COMM_WORLD, root=0) as executor:
        jobs = range(95)
        if executor is not None:
            executor.map(fun, jobs)
