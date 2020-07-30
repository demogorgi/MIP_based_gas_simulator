#File contains class to train NN using MCTS

from .mcts import *
from .evaluate import *
from .neural_network_architecture import *
from .gas_network import *

class Train(object):

    def __init__(self, gas_network, nnet):
        self.gas_network = gas_network
        self.net = nnet
        #self.eval_net = NeuralNetworkWrapper(gas_network)

    def start(self):
        #Main training function

        training_data = []

        for i in range(configs.num_self_plays):
        #Self plays to collect data to train the NN
            print("Start Self-play training", i+1)
            gas_network = deepcopy(self.gas_network)
            self.self_play(gas_network, training_data)

        new_agent_decision = self.get_decision()

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

        self_play_data.append([deepcopy(gas_network.state), deepcopy(best_child.parent.child_psas), 0])

        action = best_child.action

        gas_network.take_action(action)

        value = gas_network.get_reward(gas_network.n_penalty[0])

        # Update v as the value of the game result
        for state_value in self_play_data:
            state_value[2] =  value
            state = deepcopy(state_value[0])
            psa_vector = deepcopy(state_value[1])
            training_data.append([state, psa_vector, state_value[2]])


    def get_decision(self):
        mcts = MCTS(self.net)
        gas_network = deepcopy(self.gas_network)
        node = TreeNode()

        best_child = mcts.search(gas_network, node, configs.temperature)
        action = best_child.action
        #gas_network.take_action(action)
        #penalty = gas_network.n_penalty[0]
        gas_network.apply_action(action)
        new_action_c_p = gas_network.cum_sum_penalty

        old_action = get_old_action()
        gas_network.apply_action(old_action)
        old_action_c_p = gas_network.cum_sum_penalty

        if new_action_c_p < old_action_c_p:
            decision = gas_network.generate_decision_dict(action)
            return decision
