"""
This script runs the ABC experiment. It has two boolean variables, `run_presession` and `run_experiment`, which determine whether to run the presession or the main experiment. If `run_presession` is True, it runs the presession. If `run_experiment` is True, it runs the main experiment.
"""

run_presession = bool
run_experiment = bool

#run_presession = True
run_experiment = True
if run_presession == True:
    from experiments.abc.experiment_classes.ABC_Presession import ABCPresession
    ABCPresession().run()
if run_experiment:  
    from experiments.abc.experiment_classes.ABC_Experiment import ABCExperiment
    exp = ABCExperiment() 
    exp.prepare_experiment() 
    exp.run_experiment()
    
