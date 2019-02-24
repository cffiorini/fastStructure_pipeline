import subprocess
import os
from numpy import loadtxt

################################################################################
#modify according to your needs
analysis_name = "test" #string
input_ped = "/home/fiorini/test/test" #path to files ped, map and pop, without file extenxtion
               #(map and ped files must have the same name)
remove_inds = "/home/fiorini/test/test_remove_ind.txt" #path to file.txt
output_path = "/home/fiorini/test/" #path to folder
input_bed = "/home/fiorini/test/test"
final_lines_order = "/home/fiorini/test/test_reorder_lines.txt" #path to file.txt
path_plink = "/home/fiorini/Ceci/Professional/Software/plink" #path to plink
path_faststru = "/home/fiorini/bin/fastStructure/" #path to fastStructure folder
rep = range(2) #number of repetitions
k_range = range(1,3) #range of k = (k to k+1)
################################################################################

os.chdir(output_path)

#transform ped and map files in bed, bim and fam files required by fastStructure
subprocess.call([path_plink,
    "--file", input_ped,
    "--remove", remove_inds,
    "--out", input_bed, #output 1
    "--make-bed",
    "--allow-extra-chr", "0"
])

#perform fastStructure analysis, givin a range of Ks and the number of replicates
for r in rep:
    for k in k_range:
        subprocess.call(["python",
            path_faststru + "structure.py",
            "-K", "%d"%k,
            "--input=" + input_bed, #input=output 1
            "--output=" + output_path + "outr%d"%r #output folder
        ])
        # s = ''
        # for i in range(1, 209):
        #     s = s + str(i) + '\n'
        # subprocess.call(["echo", s, ">", output_path + "outr%d.%d.meanQ"%(r,k) #output
        # ])

#change line order so clumpak output will match desired order
ordering = loadtxt(final_lines_order, comments="#", delimiter=",", unpack=False)
for r in rep:
    for k in k_range:
        with open(output_path + "outr%d.%d.meanQ"%(r,k), "r") as infile:
            lines = [line for line in infile] # Read all input lines into a list
        with open(output_path + "outr%d.%d_reord.meanQ"%(r,k), "w") as outfile:
            for idx in ordering: # Write output lines in the desired order.
                outfile.write(lines[int(idx)-1])

with open(input_bed + ".pop", "r") as infile:
    lines = [line for line in infile] # Read all input lines into a list
with open(input_bed + "_reord.pop", "w") as outfile:
    for idx in ordering: # Write output lines in the desired order.
        outfile.write(lines[int(idx)-1])

#organize fastStructure output to create ADMIXTURE-like zip file to be processed
#by http://clumpak.tau.ac.il
for k in k_range:
    kdir = output_path + analysis_name + "/k%d"%k
    os.makedirs(kdir)
    for r in rep:
        subprocess.call(["mv",
            output_path + "outr%d.%d_reord.meanQ"%(r,k),
            kdir
        ])

subprocess.call(["zip",
    "-r",
    analysis_name + ".zip",
    analysis_name
])

#organize fastStructure output in files to be processed by chooseK.py
for r in rep:
    rdir = output_path + analysis_name + "_chooseK/r%d"%r
    os.makedirs(rdir)
    for k in k_range:
        subprocess.call(["mv",
            output_path + "outr%d.%d.meanQ"%(r,k),
            rdir
        ])
        subprocess.call(["mv",
            output_path + "outr%d.%d.meanP"%(r,k),
            rdir
        ])
        subprocess.call(["mv",
            output_path + "outr%d.%d.log"%(r,k),
            rdir
        ])

#clean folder
subprocess.call(["rm",
    "-r",
    "test",
    "test.bed",
    "test.bim",
    "test.fam",
    "test.log",
    "test.nosex",
])

#perform fastStructure chooseK analysis
with open(output_path + analysis_name + "_chooseK/chooseK.log", "w") as chooseK:
    for r in rep:
        rdir = output_path + analysis_name + "_chooseK/r%d"%r
        subprocess.call(["python",
                path_faststru + "chooseK.py",
                "--input=" + rdir + "/outr%d"%r,

        ], stdout=chooseK)
