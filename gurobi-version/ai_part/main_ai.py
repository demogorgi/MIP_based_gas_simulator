from .sol2state import *
from .gas_network import *
from .neural_network_architecture import *
from .train import *


def ai_input(solution, agent_decisions, config, compressors, dt):

    Gas_Network.decisions_dict = agent_decisions
    Gas_Network.config = config
    Gas_Network.compressors = compressors
    Gas_Network.dt = dt

    state = extract_from_solution(solution)
    Gas_Network.state = state
    Gas_Network.penalty = find_penalty(solution)

    gas_network = Gas_Network()

    net = NeuralNetworkWrapper(gas_network)

    if CFG.load_model:
        file_path = CFG.model_dir + "best_model.meta"
        if os.path.exists(file_path):
            net.load_model("best_model")
        else:
            print("Trained model does not exist. Starting from scratch")
    else:
        print("Trained model not loaded. Starting from scratch")

    train  = Train(gas_network, net)
    train.start()

    new_agent_decision = Gas_Network.decisions_dict

    return new_agent_decision
