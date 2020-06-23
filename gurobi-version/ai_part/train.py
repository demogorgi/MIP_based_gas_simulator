#File contains class to train NN using MCTS
from .configs import *
from .mcts import *
from .evaluate import *
from .neural_network_architecture import *

class Train(object):

    def __init__(self, gas_network, nnet):
        self.gas_network = gas_network
        self.net = nnet
        self.eval_net = NeuralNetworkWrapper(gas_network)

    def start(self):
        #Main training function

        training_data = []

        for i in range(CFG.num_self_plays):
            print("Start Self-play training", i+1)
            gas_network = self.gas_network.clone()
            self.self_play(gas_network, training_data)

        self.net.save_model() #Current model saved

        self.eval_net.load_model() #Current model is loaded

        self.net.train(training_data)

        eval_mcts = MCTS(self.net)

        evaluator = Evaluate(eval_mcts = eval_mcts, gas_network = self.gas_network)

        win_ratio = evaluator.evaluate()

        print("Win rate: ", win_ratio)
        if win_ratio > 0.55:
            print("New model saved as the best model")
            self.net.save_model("best_model")
        else:
            print("New model is not the best model.")
            self.net.load_model()

    def self_play(self, gas_network, training_data):

        mcts = MCTS(self.net)
        self_play_data = []

        node = TreeNode()

        iteration_over = False

        while not iteration_over:

            best_child = mcts.search(gas_network, node, CFG.temperature)

            self_play_data.append([deepcopy(gas_network.state), deepcopy(best_child.parent.child_psas), 0])

            action = best_child.action

            gas_network.take_action(action)

            iteration_over, value = gas_network.get_reward(gas_network.penalty)

            best_child.parent = None
            node = best_child    #Make the child node the root node

        # Update v as the value of the game result
        for state_value in self_play_data:
            value = -value
            state_value[2] =  value
            state = deepcopy(state_value[0])
            psa_vector = deepcopy(state_value[1])
            training_data.append([state, psa_vector, state_value[2]])

    def get_decision(self, net):
        mcts = MCTS(net)
        gas_network = self.gas_network.clone()
        feasible = False
        node = TreeNode()

        if not feasible:
            best_child = mcts.search(gas_network, node, CFG.temperature)
            best_action = best_child.action

            feasible = gas_network.check_feasibility(best_action)
            if feasible:
                gas_network.take_action(best_action)

        return gas_network.decisions_dict
