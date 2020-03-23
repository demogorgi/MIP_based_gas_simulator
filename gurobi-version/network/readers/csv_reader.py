"""
 csv reader reads eingabedat*.csv files and converts their content into net data.
"""

import pandas as pandas
import re, os
import gurobipy as gp

TMP_CSV_PATH = ".temp_csv"
NODE_PRESSURE = "P"

def read_csv(net, content):
    data = generate_data(content)
    add_nodes(net, data)
    

def generate_data(content):
    content = format_content(content)
    file = open(TMP_CSV_PATH, "w")
    file.write(content)
    file.close()
    data = pandas.read_csv(TMP_CSV_PATH, header=0, index_col=0, sep=";")
    os.remove(TMP_CSV_PATH)
    return data

def format_content(content):
    content = re.sub("(\\r*\\n\\r*\\[)", "[", content) # remove newline + [ (bug from simone)
    content = re.sub("\"", "", content) # remove quotes
    content = re.sub("(?<=\\d),(?=\\d+)", ".", content) # replace commas by dots
    content = re.sub(r"(\[.+?\])", "", content) # remove units
    return content

def add_nodes(net, data):
    nodes = data.loc[(data.Type == "NO") | (data.Type == "NS")]
    net.nodes = list(nodes.index)
    net.var_node_p_old_old = nodes[NODE_PRESSURE].to_dict()
    net.var_node_p_old = nodes[NODE_PRESSURE].to_dict()
    net.pressure = nodes[NODE_PRESSURE].to_dict()
