#File contains class to train NN using MCTS

from .mcts import *
from .evaluate import *
from .neural_network_architecture import *
from .gas_network import *

training_data = []
class Train(object):

    def __init__(self, gas_network, nnet):
        self.gas_network = gas_network
        self.net = nnet
        #self.eval_net = NeuralNetworkWrapper(gas_network)

    def start(self):
        #Main training function

        #training_data = []

        for i in range(configs.num_self_plays):
        #Self plays to collect data to train the NN
            #print("Start Self-play training")
            gas_network = deepcopy(self.gas_network)
            self.self_play(gas_network, training_data)

        action = [v for k,v in get_dispatcher_dec().items()]

        new_agent_decision = gas_network.generate_decision_dict(action)

        self.net.save_model() #Current model saved

        self.net.train(training_data) # Train the current model

        #Evaluating the decisions
        if penalties:
            evaluator = Evaluate(self.net)
            evaluator.evaluate()

        return new_agent_decision

    def self_play(self, gas_network, training_data):

        mcts = MCTS(self.net)
        self_play_data = []

        node = TreeNode()

        best_child = mcts.search(gas_network, node, configs.temperature)

        self_play_data.append([deepcopy(gas_network.state), deepcopy(best_child.parent.child_psas), None, 0])

        action = best_child.action

        gas_network.apply_action(action)

        value = gas_network.get_reward(gas_network.n_penalty[0])

        # Update v as the value of the game result
        for state_value in self_play_data:
            state_value[2] = [v for k,v in get_dispatcher_dec().items()]
            state_value[3] =  value
            state = deepcopy(state_value[0])
            psa_vector = deepcopy(state_value[1])
            training_data.append([state, psa_vector, state_value[2], state_value[3]])
