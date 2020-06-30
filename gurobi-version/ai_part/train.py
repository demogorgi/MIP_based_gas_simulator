#File contains class to train NN using MCTS
from .configs import *
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

        for i in range(CFG.num_self_plays):
            print("Start Self-play training", i+1)
            gas_network = self.gas_network.clone()
            self.self_play(gas_network, training_data)

        self.net.save_model() #Current model saved

        self.net.train(training_data)

        new_agent_decision = self.get_decision()

        #Evaluating the decisions
        if Gas_Network.penalties:
            evaluator = Evaluate()
            win_ratio = evaluator.evaluate(Gas_Network.penalties)

            print("Win rate: ", win_ratio)
            if win_ratio > 0.55:
                print("New model saved as the best model")
                self.net.save_model("best_model")
            else:
                print("New model is not the best model.")
                self.net.load_model()

        return new_agent_decision

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

            value = gas_network.get_reward(gas_network.exp_penalty)
            iteration_over =True

            best_child.parent = None
            node = best_child    #Make the child node the root node

        # Update v as the value of the game result
        for state_value in self_play_data:
            value = -value
            state_value[2] =  value
            state = deepcopy(state_value[0])
            psa_vector = deepcopy(state_value[1])
            training_data.append([state, psa_vector, state_value[2]])

    def get_decision(self):
        mcts = MCTS(self.net)
        gas_network = self.gas_network.clone()
        feasible = False
        node = TreeNode()

        dec_penalty = {}

        for i in range(CFG.num_evaluation_plays):

            best_child = mcts.search(gas_network, node, CFG.temperature)
            best_action = best_child.action
            #print(best_action)
            gas_network.take_action(best_action)

            dec_penalty[i] = [best_action, gas_network.exp_penalty[0]]

        d = dec_penalty[min(dec_penalty, key=dec_penalty.get)]
        best_decision = gas_network.generate_decision_dict(d[0])
        #print(best_decision)
        if d[1] < gas_network.penalty[0]:
            return best_decision
        else:
            return None
