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

            print("Start Self-play training", i+1)
            gas_network = deepcopy(self.gas_network)
            self.self_play(gas_network, training_data)

        self.net.save_model() #Current model saved

        self.net.train(training_data)

        new_agent_decision = self.get_decision()


        #Evaluating the decisions
        if penalties: #and Gas_Network.step == numSteps-1
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

        value = gas_network.get_reward(gas_network.n_penalty)

            # best_child.parent = None
            # node = best_child    #Make the child node the root node

            # Update v as the value of the game result
        for state_value in self_play_data:
            #value = -value
            state_value[2] =  value
            state = deepcopy(state_value[0])
            psa_vector = deepcopy(state_value[1])
            training_data.append([state, psa_vector, state_value[2]])


    def get_decision(self):
        mcts = MCTS(self.net)
        gas_network = deepcopy(self.gas_network)
        node = TreeNode()
        cum_penalty = 0

        best_child = mcts.search(gas_network, node, configs.temperature)
        action = best_child.action

        for i in range(8):
            if gas_network.next_step < numSteps:
                gas_network.take_action(action)
                gas_network.decisions_dict = gas_network.generate_decision_dict(action)

                cum_penalty += gas_network.n_penalty[0]
                gas_network.next_step += 1
                gas_network.state = get_state(gas_network.next_step, gas_network.decisions_dict)

        if cum_penalty < 1000:
            return gas_network.decisions_dict

        # else:
        #     exit()
        #     next_action = next(child.action for child in best_child.parent.children)
        #     best_decision = gas_network.generate_decision_dict(next_action)
