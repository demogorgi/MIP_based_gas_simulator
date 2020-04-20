from .sol2state import *
from .gas_network import *
from .neural_network_architecture import *
from .train import *



def ai_input(solution, config, compressors, dt):

    state = sol2state(solution)
    gas_network = Gas_Network(state)

    #print(gas_network.get_dispatcher_moves(dispatcher_dec)[0])
    # action = gas_network.get_dispatcher_moves(dispatcher_dec)[0]
    # gas_network.take_action(action)
    # exit()
    #
    # net = NeuralNetworkWrapper(gas_network)
    #
    # train  = Train(gas_network, net)
    # train.start()
