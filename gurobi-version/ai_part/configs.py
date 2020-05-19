#Class contains configuration parameters

class CFG(object):

    dispatcher = 1 #Dispatcher agent
    trader = -1 #Trader agent

    model_dir = "./ai_part/models/" #Directory to save models
    load_model = True #Flag value for loading a saved model

    c_puct = 4 #level of exploration (1-6) used in MCTS
    num_mcts_sims = 50 #Number of MCTS simulations 800
    dirichlet_alpha = 0.5
    epsilon = 0.25

    resnet_blocks = 5 #For Residual tower in NN
    learning_rate = 0.01 #0.001 learning rate for optimizer
    momentum = 0.9 #Momentum parameter for SGD optimizer

    epochs = 10 #Number of epochs for NN training
    batch_size = 128 #Batch size for NN training

    num_self_plays = 10 #Number of self-play games
    temp_threshold = 10 #Threshold temperature
    temp_initial = 1 #Initial Temperature
    temp_final = 0.001 #Final temperature (temperature after threshold passes)

    #Weights to calculate penalty for both agents
    pressure_wt_factor = 1
    flow_wt_factor = 0.1

    num_evaluation_plays = 10 # Number of evaluation plays
