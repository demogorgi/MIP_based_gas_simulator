def get_prescribed_nominations(agent_decisions,i):
    if i < 10:
        agent_decisions["entry_nom"]["S"]["EN_aux0^EN"] = [1100]
        agent_decisions["entry_nom"]["S"]["EH_aux0^EH"] = [0]
    else:
        agent_decisions["entry_nom"]["S"]["EN_aux0^EN"] = [0]
        agent_decisions["entry_nom"]["S"]["EH_aux0^EH"] = [1100]
