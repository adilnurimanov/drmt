import sys
import math
import matplotlib
import importlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
if (len(sys.argv) != 4):
  print("Usage: ", sys.argv[0], " <result folder> <drmt latencies> <prmt latencies>")
  exit(1)
else:
  result_folder = sys.argv[1]
  drmt_latencies = importlib.import_module(sys.argv[2], "*")
  prmt_latencies = importlib.import_module(sys.argv[3], "*")

PROCESSORS=range(1, 51)

progs = ["switch_combined", "switch_combined_subset", "switch_egress",\
         "switch_egress_subset", "switch_ingress", "switch_ingress_subset"]
d_archs = ["drmt_ipc_1", "drmt_ipc_2"]
p_archs = ["prmt_coarse", "prmt_fine"]

pipeline_stages  = dict()
drmt_min_periods = dict()
drmt_thread_count= dict()

for prog in progs:
  for arch in d_archs + p_archs:
     fh = open(result_folder + "/" + arch + "_" + prog + ".txt", "r")
     for line in fh.readlines():
       if arch.startswith("prmt"):
         if "stages" in line:
           pipeline_stages[(prog, arch)] = float(line.split()[4])
       elif arch.startswith("drmt"):
         if "achieved throughput" in line:
           drmt_min_periods[(prog, arch)] = int(line.split()[7])
         if "thread count" in line:
           drmt_thread_count[(prog, arch)] = int(line.split()[5])
         if "Upper bound" in line:
           drmt_min_periods[(prog, "full_dagg")] = float(line.split()[5])
       else:
         print ("Unknown architecture")
         assert(False)

for prog in progs:
  plt.figure()
  plt.title("Throughput vs. number of processors: " + prog)
  plt.xlabel("Number of processors")
  plt.ylabel("Throughput in packets per cycle")
  for arch in p_archs:
    plt.plot(PROCESSORS, [min(1, 1/math.ceil(pipeline_stages[(prog, arch)]/n)) for n in PROCESSORS], label = arch)
  for arch in d_archs:
    plt.plot(PROCESSORS, [min(1, n / drmt_min_periods[(prog, arch)]) for n in PROCESSORS], label = arch)
  plt.plot(PROCESSORS, [min(1, n / drmt_min_periods[(prog, "full_dagg")]) for n in PROCESSORS], label = "full_dagg")
  plt.legend()
  plt.savefig(prog + ".pdf")

print("drmt thread count")
print("%26s %16s %16s %16s %16s"%("prog", "drmt_ipc_1", "drmt_ipc_2", "drmt:max(dM, dA)", "prmt:dM+dA"))
for prog in progs:
  print("%26s %16d %16d %16d %16d" %(prog,\
          int(math.ceil(drmt_thread_count[(prog, "drmt_ipc_1")] / drmt_min_periods[(prog, "drmt_ipc_1")])),\
          int(math.ceil(drmt_thread_count[(prog, "drmt_ipc_2")] / drmt_min_periods[(prog, "drmt_ipc_2")])),\
          max(drmt_latencies.dM, drmt_latencies.dA),
          prmt_latencies.dM + prmt_latencies.dA))