import re
import os
import yaml
from loguru import logger
from networkx import DiGraph, all_pairs_lowest_common_ancestor
from pathlib import Path


def get_leaves(graph: DiGraph) -> list:
    """
    Args:
        graph: a graph
    Outputs:
        list_leaves: it's a list of the graph's leaves
    """

    list_leaves = [
        x for x in graph.nodes() if graph.out_degree(x) == 0 and graph.in_degree(x) == 1
    ]

    return list_leaves


def compute_rate(size: int, struct_nb: int, regexp_nb: int) -> float:
    """
    Formula to score the readability of a software,
    where the obtained score is between -inf and 10

    args:
        size: size of the routine, in number of lines
        struct_nb: number of structure errors in the routine
        regexp_nb: number of regexp errors in the routine

    output:
        rate: it's a score that is given to the routine in terms of respect of structure and regexp rules.
        10 is perfect, and the lower the worse.

    """

    if size == 0:
        rate = 0
    else:
        rate = (float(struct_nb * 5 + regexp_nb) / size) * 10
        rate = 10.0 - rate

    return rate


def get_routine_content(name: str, start: int, end: int) -> list:
    """
    returns the content of a routine

    Args:
        name: name of the routine
        start: the line where one wants to start reading
        end: the line where one wants to stop reading

    Outputs:
        content: a list where each element is a line of the routine
    """

    filename = name.split(":")[0]
    with open(filename, "r") as fin:
        content = fin.readlines()[start:end]
    return content


def chaining(rulesfolder: dict) -> dict:
    """
    Args:
        rulesfolder: dictionnary of the structure and regexp rules
    Outputs:
        syntax_dict: dictionnary where each key correspond to a syntax group taken from the yml flolder.
    Values are the different syntax elements of the group, separated with a pipe, in lowercase or uppercase characters.
    Chains are read in lower characters by default

    """

    syntax_dict = {}

    if "types" in rulesfolder.keys():
        chain_alltypes = "|".join(rulesfolder["types"]).lower()
        chain_alltypes_uplow = chain_alltypes.upper() + "|" + chain_alltypes
        syntax_dict["{alltypes}"] = chain_alltypes_uplow
        syntax_dict["{alltypes_upper}"] = chain_alltypes.upper()
        syntax_dict["{alltypes_lower}"] = chain_alltypes

    if "intrinsics" in rulesfolder.keys():
        chain_allintrinsics = "|".join(rulesfolder["intrinsics"]).lower()
        syntax_dict["{intrinsics_upper}"] = chain_allintrinsics.upper()
        syntax_dict["{intrinsics_lower}"] = chain_allintrinsics

    if "structs" in rulesfolder.keys():
        chain_allstructs = "|".join(rulesfolder["structs"]).lower()
        chain_allstructs_uplow = chain_allstructs.upper() + "|" + chain_allstructs
        syntax_dict["{structs}"] = chain_allstructs_uplow
        syntax_dict["{structs_upper}"] = chain_allstructs.upper()
        syntax_dict["{structs_lower}"] = chain_allstructs

    if "named-args" in rulesfolder.keys():
        chain_allnamedargs = "|".join(rulesfolder["named-args"]).lower()
        syntax_dict["{named-args}"] = chain_allnamedargs
        syntax_dict["{named-args_upper}"] = chain_allnamedargs.upper()
        syntax_dict["{named-args_lower}"] = chain_allnamedargs

    if (
        "namespace_blocks" in rulesfolder.keys()
        and "context_blocks" in rulesfolder.keys()
    ):
        list_allblocks = rulesfolder["namespace_blocks"] + rulesfolder["context_blocks"]
        chain_allblocks = "|".join(list_allblocks).lower()
        chain_allblocks_uplow = chain_allblocks.upper() + "|" + chain_allblocks
        syntax_dict["{blocks}"] = chain_allblocks_uplow
        syntax_dict["{blocks_upper}"] = chain_allblocks.upper()
        syntax_dict["{blocks_lower}"] = chain_allblocks

    if "punctuations" in rulesfolder.keys():
        chain_allpunctuations = "|".join(rulesfolder["punctuations"])
        syntax_dict["{punctuations}"] = chain_allpunctuations

    if "operators" in rulesfolder.keys():
        chain_alloperators = "|".join(rulesfolder["operators"])
        syntax_dict["{operators}"] = chain_alloperators

    return syntax_dict


def compute_struct_items(
        routine_content: list, 
    ) -> dict:
    """
    Evaluate several figures from the content of the routine
    
    Args :
        routine_content : list of the lines of the routine
        structrules : dictionnary of the regexp rules
        var_declaration_regexp: pattern to detect the variables
      
    Output : dictionnary containing each structure error as a key,
    and its number of occurences in this routine as a value.

    """

    size = len(routine_content) # Would be better if we avoid comments

    list_vars = find_list_vars(
        routine_content,
    )    

    nesting_level = find_nesting_level(
        routine_content,
    )

    # finds the arguments, puts them in a list
    list_args = []
    for line in routine_content:
        if "(" in line:
            list_args = line.split("(")[1].split(")")[0].split(",")
            list_args = [arg.strip() for arg in list_args]
            break

    struct_items = {
        "size": size,
        "list_args": list_args,
        "list_vars": list_vars,
        "nesting_level": nesting_level
    }
    return struct_items



def compute_struct_errors(
    routine_content: list, nameroutine: str, structrules: dict
) -> dict:
    
    struct_items =  compute_struct_items(routine_content)
    # COMPUTE ERRORS 

    dic_err_struct = rate_structure_errors(struct_items,structrules)
    
    return dic_err_struct

def rate_structure_errors(struct_items: dict,structrules:dict) -> dict:
    error_size = round(
        struct_items["size"]
        /structrules["max-statements-in-context"]
    )

    error_args = round(
        len(struct_items["list_args"])
        /structrules["max-arguments"]
    )

    error_locals = round(
        len(struct_items["list_vars"])
        /structrules["max-declared-locals"])

    error_nesting = max(0,struct_items["nesting_level"]-structrules["max-nesting-levels"])

    # error for argument size > max or < min
    error_argsizeovermax=0
    error_argsizebelowmin=0
    for arg in struct_items["list_args"]:
        if len(arg) > structrules["max-arglen"]:
            error_argsizeovermax += 1
        if len(arg) < structrules["min-arglen"]:
            error_argsizebelowmin += 1
    # error for var size > max or <min
    error_varlenovermax = 0
    error_varlenbelowmin = 0
    for var in struct_items["list_vars"]:
        if len(var.strip())> structrules["max-varlen"]:
            error_varlenovermax += 1
        if len(var.strip()) < structrules["min-varlen"]:
            error_varlenbelowmin += 1
    
    dic_err_struct = {
        "size": error_size,
        "locals": error_locals,
        "nesting": error_nesting,
        "argsize_belowmin": error_argsizebelowmin,
        "argsize_overmax": error_argsizeovermax,
        "args": error_args,
        "varlen_belowmin": error_varlenbelowmin,
        "varlen_overmax": error_varlenovermax,
    }
    return dic_err_struct



def find_list_vars(routine_content: list)-> list:
    """Return a list of all assigned variables
    
    """
    # LOCAL VARS assigned
    regexp_assign = "^(?!.*(?:==|!=|\+=|\-=|<=|>=|:=).*).*?(.*?)\s*="
    list_vars = []
    def remove_leading_spaces_and_do(string):
        string = string.strip()
        if string.startswith("do ") or string.startswith("DO ") :    # FORTRAN CAVEAT
            string = string[3:]
        return string

    for line in routine_content:
        
        matches = re.findall(regexp_assign, remove_leading_spaces_and_do(line))

        if matches:
            matches = matches[0].split(",") # split if several entries are found in lhs
            matches = [item.strip("() ") for item in matches]
            list_vars.extend(matches)
    
    #list_vars = [item for item in list_vars if item.lower() not in structs]
        
    return sorted(set(list_vars))


def find_nesting_level(routine_content: list)-> int:
    """Determine nesting level upon indentation"""
    # NESTING LEVEL 
    if routine_content == []:
        return 0
    def count_leading_spaces(line):
        count = 0
        for char in line:
            if char == ' ':
                count += 1
            else:
                break
        return count

    lead_spaces= [count_leading_spaces(line) for line in routine_content]
    lead_spaces= list(sorted(set(lead_spaces)))
    if lead_spaces[0] == 0:
        lead_spaces = lead_spaces[1:]
    
    nesting_level = 0
    if lead_spaces:
        nesting_level= int(lead_spaces[-1]/lead_spaces[0])
    return nesting_level

def compute_regexp_errors(
    routine_content: list, nameroutine: str, regexprules: dict, syntax_dict: dict
) -> dict:
    """
    Args :
        routine_content = list of the lines of the routine
        nameroutine = name of the routine, in str
        regexprules = dictionnary of the regexp rules
        syntax_dict = dictionnary of the syntax groups with their elements in lowercase or uppercase characters

    Output : dictionnary containing each regexp error as a key,
    and its number of occurences in this routine as a value.

    """

    dic_err_regexp = {}

    for rule in regexprules.values():
        error_pattern = 0
        pattern = rule["regexp"]
        rulemessage = rule["message"]
        for synt_element, synt_val in syntax_dict.items():
            if synt_element in pattern:
                pattern = pattern.replace(synt_element, synt_val)

        for line in routine_content:
            if re.search(pattern, line):
                error_pattern += len(re.findall(pattern, line))

        dic_err_regexp[f"{rulemessage}"] = error_pattern

    return dic_err_regexp


def rec_get_score(graph: DiGraph, name: str) -> list:
    """
    Recursive function that searches, for each routine of the graph,
    its successors to calculate the size and score with a weighted
    average of the successors' size and score.

    Args:
        graph: the graph
        name: it's the name of the routine

    Output:
        size: size of the routine
        score: score of the routine, calculated with the regexp and structure rules
    """
    size = 0
    score = 0
    successors = list(graph.successors(name))
    if successors:
        for childname in graph.successors(name):
            sizec, scorec = rec_get_score(graph, childname)
            size += sizec
            score += scorec * sizec
        score /= size

        graph.nodes[name]["size"] = size
        graph.nodes[name]["score"] = score

    else:
        size = graph.nodes[name]["size"]
        score = graph.nodes[name]["score"]

    return size, score


def flinter_score(
    path:str, graph: DiGraph, regexprules: dict, structrules: dict, syntax_dict: dict
) -> DiGraph:
    """
    Args :
        graph : a graph
        regexprules : a dictionnary of regexp rules
    Output :
        graph : the same graph, with the size and score of all the nodes in the data.
    """
    repo_path = Path(path)
    main_folder = repo_path.parents[0].as_posix()

    # Création des dictionnaires "résumés sur toutes les fonctions"
    struct_dic_total = {}
    regexp_dic_total = {}

    for routine in get_leaves(graph):
        # adds a score to each leave of the graph
        node = graph.nodes[routine]
        node["score"] = 0
        if node.get("analyzed", True) and not node.get("empty_folder", False):
            #node_path = repo_path.as_posix() + "/"+ node["path"]
            node_path = os.path.join(main_folder,node["path"])
            
            routine_content = get_routine_content(
                node_path, node["line_start"], node["line_end"]
            )

            # Calculation : total number of structure errors in the routine (sum)
            struct_dic = compute_struct_errors(
                routine_content,
                routine,
                structrules,
            )
            struct_nb = sum(
                [struct_dic[pattern_st] for pattern_st in struct_dic.keys()]
            )

            # Calculation : total number of regexp errors in the routine (sum)
            regexp_dic = compute_regexp_errors(
                routine_content,
                routine,
                regexprules,
                syntax_dict,
            )
            regexp_nb = sum(
                [regexp_dic[pattern_re] for pattern_re in regexp_dic.keys()]
            )

            # node["score"] = adim_rate(node["size"], struct_nb, regexp_nb)
            node["score"] = max(compute_rate(node["size"], struct_nb, regexp_nb), 0)

            # logger : score total de la routine
            logger.info(f"\n\t{routine}: score = {node['score']}  (0:bad, 10:perfect)")
            # logger : résumé détaillé pour chaque routine

            struct_dic_short = {}
            regexp_dic_short = {}

            for error_s, occurence_s in struct_dic.items():
                if occurence_s != 0:
                    struct_dic_short[error_s] = occurence_s

            for error_r, occurence_r in regexp_dic.items():
                if occurence_r != 0:
                    regexp_dic_short[error_r] = occurence_r

            if struct_dic_short:
                logger.debug(
                    f"\n\tStructure errors: \n"
                    + flat_dict_as_str(struct_dic_short)
                )

            if regexp_dic_short:
                logger.debug(
                    f"\n\t Regexp errors: \n"
                    + flat_dict_as_str(regexp_dic_short)
                )

            for error_s, occurrence_s in struct_dic_short.items():
                if error_s not in struct_dic_total.keys():
                    struct_dic_total[error_s] = occurrence_s
                else:
                    struct_dic_total[error_s] += occurrence_s

            for error_r, occurence_r in regexp_dic_short.items():
                if error_r not in regexp_dic_total:
                    regexp_dic_total[error_r] = occurence_r
                else:
                    regexp_dic_total[error_r] += occurence_r

    
    logger.info("   Regexp errors summary:")
    logger.info("\n"+flat_dict_as_str(regexp_dic_total))
    logger.info("   Structure errors summary:")
    logger.info("\n"+flat_dict_as_str(struct_dic_total))

    _, root = list(all_pairs_lowest_common_ancestor(graph, pairs=None))[0]
    # size and score of the root
    size, score = rec_get_score(graph, root)
    logger.info(f"\n=============\nGlobal score = {score}\n\t(0:bad, 10:perfect)\n=============\n")
    return graph


###########################################################


def get_score( path: str,graph: DiGraph, rulesfile: str) -> DiGraph:
    """
    Args:
        graph:
        rulesfile: .yml folder with the regexp and structure rules

    Output: graph with a score to each node of the graph

    """

    # initial configuration of the logger
    if not Path(rulesfile).exists():
        raise RuntimeError(f"{rulesfile} not found...")

    with open(rulesfile, "r") as fin:
        input_file = yaml.safe_load(fin)
        regexprules = input_file["regexp-rules"]
        structrules = input_file["structure-rules"]
        syntaxrules = input_file["syntax"]

    syntax_dict = chaining(syntaxrules)

    score_graph = flinter_score(
        path,
        graph,
        regexprules,
        structrules,
        syntax_dict,
    )

    return score_graph


def flat_dict_as_str(dict_:dict)-> str:
    """Return a string presentation of a flat dict, ordered by values"""
    str_=""
    key_order = sorted(dict_, key=lambda k: dict_[k], reverse=True)
    for key in key_order:
        str_+= f"\t{dict_[key]}\t{key}\n"
    return str_