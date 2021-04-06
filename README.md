This is a parallel branch and bound method simulator implemented 
on Python.

To run this project firstly you need to install all requirements listed in `requirements.txt`

Then you just need to run command\
`python3 Engine.py`

You must know, that there are parameters which must be set and could be set in the Engine class instance

These are all of them:
 - `proc_amount` - amount of simulated processes (**required=True**), 
 - `max_depth` - the max value of the depth of the binary tree (which is used in BnB method) (**required=True**),
 - `price_receive=1e-2` - how much model time system spends on simulating **receive** action,
 - `price_send=1e-2` - how much model time system spends on simulating **send** action,
 - `price_put=1e-2` - how much model time system spends on simulating **put subproblems** action,
 - `price_get=1e-3` - how much model time system spends on simulating **get subproblems** action,
 - `price_balance=1.0` - how much model time system spends on simulating **balance** action,
 - `price_solve=10.0` - how much model time system spends on simulating **solve one subproblem** action

To set these parameters you just need to add them here:

`eng = Engine(proc_amount=3, max_depth=6)` - at the end of the **Engine.py** file
   