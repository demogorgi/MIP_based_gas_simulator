import importlib
import sys
import re

wd = sys.argv[1].replace("/",".")
wd = re.sub(r'\.$', '', wd)

no = importlib.import_module(wd + ".nodes") #Nodes of the network(entry + exit +inner nodes)
co = importlib.import_module(wd + ".connections") #Connections of the network

special_pipes = []
for i in co.special:
    special_pipes.append(re.sub("\('(\S*)',\s'(\S*)'\)", r'\1,\2', str(i)))

class dotdict(dict):
    def __getattr__(self, name):
        return self[name]

#Function to remove duplicate entries from fixed_decisions.yml file
def remove_duplicate_decision(prev_agent_decisions, new_agent_decisions, step):
    for (k1,v1), (k2,v2) in zip(prev_agent_decisions.items(), new_agent_decisions.items()):
        if not re.search('(entry|exit)_nom',k1):
            for (l1,v_1),(l2,v_2) in zip(v1.items(),v2.items()):
                for (label1, value1), (label2, value2) in zip(v_1.items(), v_2.items()):
                    for i in range(step, -1, -1):
                        if i in value1:
                            break
                    if value1[i] == value2[step]:
                        del value2[step]
    return new_agent_decisions

#Create csv to store agent decisions, boundary flows, pressures and agent penalty values
def create_dict_for_csv(agent_decisions, step = 0, timestamp = '', penalty = [], bn_pr_flows = {}):

    extracted_ = {}
    extracted_['Time'] = timestamp
    for i, j in agent_decisions.items():
        for k,l in j.items():
            for m,n in l.items():
                key = i+"["+m+"]"
                for p in range(step,-1,-1):
                    if p in n:
                        extracted_[key] = n[p]
                        break
    if not bn_pr_flows:
        for i in no.exits:
            extracted_[f"var_node_p[{i}]"] = None
        for i in no.exits:
            extracted_[f"var_node_Qo_in[{i}]"] = None
        for i in special_pipes:
            extracted_[f"var_pipe_Qo_in[{i}]"] = None
    else:
        for i, j in bn_pr_flows.items():
            extracted_[i] = round(j,3)
    if penalty:
        extracted_['Dispatcher Penalty'] = penalty[0]
        extracted_['Trader Penalty'] = penalty[1]
    else:
        extracted_['Dispatcher Penalty'] = None
        extracted_['Trader Penalty'] = None

    fieldnames = reordered_headers(list(extracted_.keys()))
    # fieldnames = list(extracted_.keys())

    return fieldnames, extracted_

def reordered_headers(fieldnames):
    order = [0,1,12,2,13,3,15,4,14,5,6,7,8,9,10,11,16,17]
    fieldnames = [fieldnames[i] for i in order]
    return fieldnames

def get_bn_pressures_flows(solution):
    exit_pr_flows = {}
    for k,v in solution.items():
        if re.findall(r"var_node_p\[("+'|'.join(no.exits)+r")]",k):
            exit_pr_flows[k] = v
        elif re.findall(r"var_node_Qo_in\[("+'|'.join(no.exits)+r")]",k):
            exit_pr_flows[k] = v
        elif re.findall(r"var_pipe_Qo_in\[("+'|'.join(special_pipes)+r")]",k):
            exit_pr_flows[k] = v
    return exit_pr_flows
