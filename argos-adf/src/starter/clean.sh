ssh -f ping4 "pkill -f "PyroNameserver.py""
ssh -f ping6 "pkill -f "PyroNameserver.py""
ssh -f ping7 "pkill -f "PyroNameserver.py""
ssh -f ping4 "pkill -f "Dataserver.py""
ssh -f ping6 "pkill -f "Dataserver.py""
ssh -f ping7 "pkill -f "Dataserver.py""
ssh -f ping4 "pkill -f "feeder.py""
ssh -f ping6 "pkill -f "feeder.py""
ssh -f ping7 "pkill -f "feeder.py""
ssh -f ping4 "pkill -f "process.py""
ssh -f ping6 "pkill -f "process.py""
ssh -f ping7 "pkill -f "process.py""
ssh -f ping4 "pkill -f "action.py""
ssh -f ping6 "pkill -f "action.py""
ssh -f ping7 "pkill -f "action.py""
pkill -f "Dataserver.py"
pkill -f "PyroNameserver.py"
pkill -f "feeder.py"
pkill -f "process.py"
pkill -f "action.py"