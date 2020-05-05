#Class contains configuration parameters

class CFG(object):

    dispatcher = 1 #Dispatcher agent
    trader = -1 #Trader agent

    model_dir = "./ai_part/models/" #Directory to save models

    c_puct = 4 #level of exploration (1-6) used in MCTS
    num_mcts_sims = 10 #Number of MCTS simulations 800
    dirichlet_alpha = 0.5
    epsilon = 0.25

    resnet_blocks = 5 #For Residual tower in NN
    learning_rate = 0.01 #0.001
    momentum = 0.9 #Momentum parameter for SGD optimizer

    epochs = 10 #Number of epochs for NN training
    batch_size = 128 #Batch size for NN training

    num_self_plays = 10 #Number of self-play games
    temp_threshold = 10
    temp_initial = 1
    temp_final = 0.001

    num_steps = 2 #Number of steps for self-play

    pressure_wt_factor = 2
    flow_wt_factor = 1

    load_model = 1 #Flag value for loading a saved model
