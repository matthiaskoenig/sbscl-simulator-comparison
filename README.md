# Comparing SBSCL simulator

Comparison of SBSCL (https://github.com/draeger-lab/SBSCL) against other simulators
for correctness and performance.
Comparisons are performed for FBA simulations and ODE simulations.

## FBA
The BiGG model collections are compared against results from `cobrapy` (https://github.com/opencobra/cobrapy) 
and `cameo` (https://cameo.bio/index.html).

The bigg database is available from

https://github.com/SBRG/bigg_models

A dump of all models is available from

https://www.dropbox.com/sh/ye05djxrpxy37da/AAD6GrSRTt4MRfuIpprlnLYba?dl=0

The models for comparison are included in this repository in
```
models/bigg-v1.6
```
The results of the FBA simulations are available in 
``` 
results/fba
``` 
Objective values are compared between different simulators.
Model loading and optimization are benchmarked via repeated execution.

### ODE
ODE models are compared between different simulators:
- `roadrunner`
- `copasi`
- `AMICI`

## Installation
```
pip install -r requirements.txt
```


© 2017-2021 Matthias König
