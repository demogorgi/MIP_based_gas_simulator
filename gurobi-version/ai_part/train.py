#File contains class to train NN using MCTS
from .mcts import *
from .evaluate import *
from .neural_network_architecture import *
from .gas_network import *

class Train(object):

    def __init__(self, gas_network, nnet):
        self.gas_network = gas_network
        self.net = nnet
        self.eval_net = NeuralNetworkWrapper(gas_network)

    def start(self):
        #Main training function

        training_data = []

        for i in range(configs.num_self_plays):
        #Self plays to collect data to train the NN
            print("Start Self-play training", i+1)
            gas_network = deepcopy(self.gas_network)
            self.self_play(gas_network, training_data)

        self.net.save_model() #Current model saved

        self.eval_net.load_model() # current model is loaded

        self.net.train(training_data) # Train the current model

        #Initialize MCTS for both networks
        current_mcts =  MCTS(self.net)
        eval_mcts = MCTS(self.eval_net)
        #Evaluating the Model
        evaluator = Evaluate(current_mcts = current_mcts,
                             eval_mcts = eval_mcts,
                             gas_network = self.gas_network)
        wins, losses = evaluator.evaluate()

        if wins >= losses:
            print("New model saved as the best model")
            self.net.save_model("best_model")
        else:
            print("New model is not the best model.")
            self.net.load_model()
        new_agent_decision = self.get_decision()

        return new_agent_decision

    def self_play(self, gas_network, training_data):
        self_play_data = []
        mcts = MCTS(self.net)
        decisions = deepcopy(gas_network.decisions_dict)
        node = TreeNode()

        best_child = mcts.search(gas_network, node, configs.temperature)

        self_play_data.append([deepcopy(gas_network.state), deepcopy(best_child.parent.child_psas), 0])

        action = best_child.action

        decisions = gas_network.generate_decision_dict(action, decisions)

        value = gas_network.get_value(decisions)

        # Update v as the value of the game result
        for state_value in self_play_data:
            state_value[2] =  value
            state = deepcopy(state_value[0])
            psa_vector = deepcopy(state_value[1])
            training_data.append([state, psa_vector, state_value[2]])

    def get_decision(self):
        mcts = MCTS(self.net)
        node = TreeNode()
        gas_network = deepcopy(self.gas_network)

        gas_network.possible_decisions = gas_network.ex_dec_pool
        decisions = deepcopy(gas_network.decisions_dict)

        best_child = mcts.search(self.gas_network, node, configs.temperature)
        action = best_child.action
        decisions = self.gas_network.generate_decision_dict(action, decisions)
        value = self.gas_network.get_value(decisions)

        return decisions
