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
            #print(training_data)
            self.self_play(gas_network, training_data)

        self.net.save_model() #Current model saved

        self.eval_net.load_model() #Current model is loaded

        self.net.train(training_data)

        eval_mcts = MCTS(self.eval_net)

        evaluator = Evaluate(eval_mcts = eval_mcts, gas_network = self.gas_network)

        wins, losses = evaluator.evaluate()

        print("Wins:", wins)
        print("Losses: ", losses)

        nums_ = wins + losses

        if nums_ == 0:
            win_rate = 0
        else:
            win_rate = wins / nums_

        print("Win rate: ", win_rate)
        if win_rate > 0.55:
            print("New model saved as the best model")
            self.net.save_model("best_model")
        else:
            print("New model discarded.")
            self.net.load_model()

    def self_play(self, gas_network, training_data):

        mcts = MCTS(self.net)
        self_play_data = []

        node = TreeNode()

        count = 0
        iteration_over = False

        while not iteration_over:

            if count < CFG.temp_threshold:
                best_child = mcts.search(gas_network, node, CFG.temp_initial)
            else:
                best_child = mcts.search(gas_network, node, CFG.temp_final)

            self_play_data.append([deepcopy(gas_network.state), deepcopy(best_child.parent.child_psas), 0])

            action = best_child.action

            gas_network.take_action(action)

            count += 1

            iteration_over, value = gas_network.get_reward()

            best_child.parent = None
            node = best_child    #Make the child node the root node

        # Update v as the value of the game result
        for state_value in self_play_data:
            value = -value
            state_value[2] =  value
            state = deepcopy(state_value[0])
            psa_vector = deepcopy(state_value[1])
            training_data.append([state, psa_vector, state_value[2]])
