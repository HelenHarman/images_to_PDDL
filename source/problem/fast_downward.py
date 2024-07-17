import os
import re
import subprocess

#fd_path = "/home/helen/Desktop/fd/"
fd_planner = "/users/helen/images_to_pddl/fd/fast-downward.py" # <-- for virtual wall
#---fd_planner = "/home/helen/Desktop/fd-clean/fast-downward.py"
# --build release64#domain.pddl task.pddl --search \"astar(blind())\""
    # TODO: we should download a clean copy of FD <-- this has been done on virtual wall, where our experiments run


options = { # these have been copied from https://github.com/guicho271828/latplan/blob/master/fd-planner.py
    "lmcut" : "astar(lmcut())",
    "blind" : "astar(blind())",
    "hmax"  : "astar(hmax())",
    "mands" : "astar(merge_and_shrink(shrink_strategy=shrink_bisimulation(max_states=50000,greedy=false),merge_strategy=merge_dfp(),label_reduction=exact(before_shrinking=true,before_merging=false)))",
    "pdb"   : "astar(pdb())",
    "cpdb"  : "astar(cpdbs())",
    "ipdb"  : "astar(ipdb())",
    "zopdb" : "astar(zopdbs())",
}

#--- tmp files:
directory_for_tmp_files = "/tmp/img_to_pddl/"
problem_file = directory_for_tmp_files + "problem.pddl"
domain_file = directory_for_tmp_files + "domain.pddl"
plan_file = directory_for_tmp_files + "plan"


def run_planner(domain, problem, selected_option = "blind"): # latplan's default is FD's blind heuristic, so we are also using this
    if not os.path.exists(directory_for_tmp_files):
        os.makedirs(directory_for_tmp_files)
    write_file(problem_file, problem)
    write_file(domain_file, domain)
    cmd = [fd_planner, "--plan-file", plan_file, "--search-time-limit", "600s", problem_file, "--search", options[selected_option]] #--search-time-limit
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
    out, err = p.communicate()
    if os.path.exists(plan_file):
        f = open(plan_file, "r")
        plan = []
        for line in f.readlines():
            if ";" not in line:
                plan.append(line.strip())
        f.close()
    else:
        #print(out.decode("utf-8"))
        #print(err.decode("utf-8"))
        print("WARNING: failed to generate plan")
        plan = []
        #return [],-1
        #exit(1)

    results = out.decode("utf-8").splitlines()
 #   print(out.decode("utf-8"))
#    print(err.decode("utf-8"))
    for result in results:
        if ("Total time: " in result):
            time = float(re.findall("\d+\.\d+", result)[0])
            return plan, time
    return [], -1

def write_file(file_name, contents):
    f = open(file_name, "w")
    f.write(str(contents))
    f.close()



#=======================================================================
#=======================================================================

# current_dir = os.getcwd()
   # os.chdir(fd_path)
   # command = fd_planner + " " + problem_file + options[selected_option] + " \"" #+ domain_file + " "
    #result = os.popen(command)
    #print (out)
    #print (err)
    #os.chdir(current_dir)