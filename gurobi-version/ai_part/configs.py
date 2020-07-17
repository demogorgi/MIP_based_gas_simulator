from .utils import *

configs = dotdict({
    'model_dir': "./ai_part/models/", #Directory to save models
    'load_model': True, #Flag value for loading a saved model

    'c_puct': 4, #level of exploration (1-6) used in MCTS
    'num_mcts_sims': 5,#10 #Number of MCTS simulations 800
    'dirichlet_alpha': 0.5,
    'epsilon':0.25,


    'num_self_plays' : 10, #Number of self-play games
    'temperature': 1, #Temperature for MCTS search

    'num_evaluation_plays' : 5, # Number of evaluation plays

})
