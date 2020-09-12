from .utils import *

configs = dotdict({
    'model_dir': "./ai_part/models/", #Directory to save models
    'load_model': True, #Flag value for loading a saved model
    'record_loss': True,
    'loss_file':"loss.txt",

    'c_puct': 1, #level of exploration (1-6) used in MCTS
    'num_mcts_sims': 5,#10 #Number of MCTS simulations 800
    'dirichlet_alpha': 0.5,
    'epsilon':0.25,

    'num_self_plays' : 10, #Number of self-play games
    'temperature': 1, #Temperature for MCTS search

    'train_model': True,

    'nums_eval_plays':10, #Number of plays for the evaluation of the model

})

penalties = [] # store dispatcher and trader penalties
c_values = [] #To store cumulative sum of nomination flow difference
win_ratios = []

current_acc_c = 0
