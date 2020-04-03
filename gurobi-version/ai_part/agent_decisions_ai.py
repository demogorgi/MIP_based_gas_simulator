

class Agent_Decision(object):

    def __init__(self):
        pass

    def trader_decisions(self, agent_decisions):
        trader_dec = {}

        for key, value in agent_decisions["exit_nom"]["X"].items():
            trader_dec[key] = value
        for key, value in agent_decisions["entry_nom"]["S"].items():
            trader_dec[key.split("^")[1]] = value
        return trader_dec

    def dispatcher_decisions(self, agent_decisions):

        dispatcher_dec = {}

        for key, value in agent_decisions["va"]["VA"].items():
            dispatcher_dec[key] = value
        for key, value in agent_decisions["zeta"]["VA"].items():
            dispatcher_dec[key] = value
