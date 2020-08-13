
import tensorflow as tf
import os
import numpy as np
from .configs import *

args = dotdict({
    'learning_rate':0.001,
    'epochs':10,
    'batch_size':64,
    'num_channels':512,
    'momentum': 0.9,
    'resnet_blocks': 5,
})

class NeuralNetwork(object):
    #Represent Policy and value head

    def __init__(self, gas_network):
        self.row, self.cols = gas_network.get_state_dimension()
        self.action_size = gas_network.get_action_size()

        self.pi = None
        self.v = None

        self.graph = tf.Graph()
        with self.graph.as_default():
            self.states = tf.placeholder(tf.float32,
                                         shape = [None,self.row])
            self.training = tf.placeholder(tf.bool)

            #Input_Layer
            input_layer = tf.reshape(self.states,
                                     [-1, self.row, 1, 1])

            #Convolutional Block
            conv1 = tf.layers.conv2d(
                inputs = input_layer,
                filters = 256,
                kernel_size = [3,3],
                padding = "same",
                strides = 1
                )
            #Batch Normalization
            batch_norm1 = tf.layers.batch_normalization(
                inputs = conv1,
                training = self.training)
            relu1 = tf.nn.relu(batch_norm1)

            resnet_in_out = relu1

            #Residual Tower
            for i in range(args.resnet_blocks):
                #Residual Block
                conv2 = tf.layers.conv2d(
                    inputs = resnet_in_out,
                    filters = 256,
                    kernel_size = [3,3],
                    padding = "same",
                    strides = 1)
                batch_norm2 = tf.layers.batch_normalization(
                    inputs = conv2,
                    training = self.training)
                relu2 = tf.nn.relu(batch_norm2)

                conv3 = tf.layers.conv2d(
                    inputs = relu2,
                    filters = 256,
                    kernel_size = [3, 3],
                    padding = "same",
                    strides = 1)
                batch_norm3 = tf.layers.batch_normalization(
                    inputs = conv3,
                    training = self.training)
                resnet_skip = tf.add(batch_norm3, resnet_in_out)
                resnet_in_out = tf.nn.relu(resnet_skip)

            #Policy Head
            conv4 = tf.layers.conv2d(
                inputs = resnet_in_out,
                filters = 2,
                kernel_size = [1, 1],
                padding = "same",
                strides = 1)
            batch_norm4 = tf.layers.batch_normalization(
                inputs = conv4,
                training = self.training)
            relu4 = tf.nn.relu(batch_norm4)

            relu4_flat = tf.reshape(relu4, [-1, self.row * 2])

            dense_pi = tf.layers.dense(
                inputs = relu4_flat,
                units = self.action_size)

            self.pi = tf.nn.softmax(dense_pi)

            #value Head
            conv5 = tf.layers.conv2d(
                inputs = resnet_in_out,
                filters = 1,
                kernel_size = [1,1],
                padding = "same",
                strides = 1)
            batch_norm5 = tf.layers.batch_normalization(
                inputs = conv5,
                training = self.training)
            relu5 = tf.nn.relu(batch_norm5)

            relu5_flat = tf.reshape(relu5, [-1, self.action_size])

            dense1 = tf.layers.dense(
                inputs = relu5_flat,
                units = 256)
            relu6 = tf.nn.relu(dense1)

            dense2 = tf.layers.dense(
                inputs = relu6,
                units = 1)

            self.v = tf.nn.tanh(dense2)

            #Loss Function
            self.train_pis = tf.placeholder(tf.float32,
                                            shape = [None, self.action_size])
            self.train_vs = tf.placeholder(tf.float32, shape = [None])

            self.loss_pi = tf.losses.softmax_cross_entropy(self.train_pis, self.pi)
            self.loss_v = tf.losses.mean_squared_error(self.train_vs,
                                                       tf.reshape(self.v, shape = [-1, ]))

            self.total_loss = self.loss_pi + self.loss_v

            #Stochastic gradient descent with momentum
            optimizer = tf.train.MomentumOptimizer(
                learning_rate = args.learning_rate,
                momentum = args.momentum,
                use_nesterov = False)
            self.train_op = optimizer.minimize(self.total_loss)

            #Saver for writing training checkpoints
            self.saver = tf.train.Saver()

            #Session for running operations on Graph
            self.sess = tf.Session()

            self.sess.run(tf.global_variables_initializer()) #Session Initialization


class NeuralNetworkWrapper(object):

    def __init__(self, gas_network):
        self.gas_network = gas_network
        self.net = NeuralNetwork(self.gas_network)
        self.sess = self.net.sess

    def policy_value(self, state):

        state = state[np.newaxis, :]
        pi,v = self.sess.run([self.net.pi, self.net.v],
                             feed_dict = {self.net.states: state,
                                          self.net.training: False})
        return pi[0], v[0][0]


    def train(self, training_data):
        #Trains network using states, pis and vs from self-play games

        print("\nTraining the network\n")

        for epoch in range(args.epochs):

            print("Epoch", epoch+1)
            examples_num = len(training_data)

            for i in range(0, examples_num, args.batch_size):
                states, pis, action, vs = map(list,
                                      zip(*training_data[i:i+args.batch_size]))
                
                feed_dict = {self.net.states: states,
                             self.net.train_pis: pis,
                             self.net.train_vs: vs,
                             self.net.training: True}

                self.sess.run(self.net.train_op,
                              feed_dict = feed_dict)

                pi_loss, v_loss = self.sess.run(
                    [self.net.loss_pi, self.net.loss_v],
                    feed_dict = feed_dict)

              # Record pi and v loss to a file.
                if configs.record_loss:
                    # Create directory if it doesn't exist.
                    if not os.path.exists(configs.model_dir):
                        os.mkdir(configs.model_dir)

                    file_path = configs.model_dir + configs.loss_file

                    with open(file_path, 'a') as loss_file:
                        loss_file.write('%f|%f\n' % (pi_loss, v_loss))

    def save_model(self, filename = "current_model"):
        if not os.path.exists(configs.model_dir):
            os.mkdir(configs.model_dir)

        file_path = configs.model_dir + filename
        #print("Saving model:", filename, "to", configs.model_dir)
        self.net.saver.save(self.sess, file_path)

    def load_model(self, filename = "current_model"):
        file_path = configs.model_dir + filename
        #print("Loading model:", filename, "from", configs.model_dir)
        self.net.saver.restore(self.sess, file_path)
