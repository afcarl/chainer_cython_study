#!/usr/bin/env python
"""Chainer example: train a multi-layer perceptron on MNIST

This is a minimal example to write a feed-forward net.

"""
from __future__ import print_function

import numpy as np
import six

import chainer
from chainer import computational_graph
from chainer import cuda
import chainer.links as L
from chainer import optimizers
from chainer import serializers

import data
import net

batchsize = 100
n_epoch = 20
n_units = 1000

# Prepare dataset
print('load MNIST dataset')
mnist = data.load_mnist_data()
mnist['data'] = mnist['data'].astype(np.float32)
mnist['data'] /= 255
mnist['target'] = mnist['target'].astype(np.int32)

N = 60000
x_train, x_test = np.split(mnist['data'],   [N])
y_train, y_test = np.split(mnist['target'], [N])
N_test = y_test.size

# Prepare multi-layer perceptron model, defined in net.py
model = L.Classifier(net.MnistMLP(784, n_units, 10))
xp = np

# Setup optimizer
optimizer = optimizers.Adam()
optimizer.setup(model)

# Learning loop
def train():
    for epoch in six.moves.range(1, n_epoch + 1):
        print('epoch', epoch)

        # training
        perm = np.random.permutation(N)
        sum_accuracy = 0
        sum_loss = 0
        for i in six.moves.range(0, N, batchsize):
            x = chainer.Variable(xp.asarray(x_train[perm[i:i + batchsize]]))
            t = chainer.Variable(xp.asarray(y_train[perm[i:i + batchsize]]))

            # Pass the loss function (Classifier defines it) and its arguments
            optimizer.update(model, x, t)

            if epoch == 1 and i == 0:
                with open('graph.dot', 'w') as o:
                    g = computational_graph.build_computational_graph(
                        (model.loss, ), remove_split=True)
                    o.write(g.dump())
                print('graph generated')

            sum_loss += float(model.loss.data) * len(t.data)
            sum_accuracy += float(model.accuracy.data) * len(t.data)

        print('train mean loss={}, accuracy={}'.format(
            sum_loss / N, sum_accuracy / N))

        # evaluation
        sum_accuracy = 0
        sum_loss = 0
        for i in six.moves.range(0, N_test, batchsize):
            x = chainer.Variable(xp.asarray(x_test[i:i + batchsize]),
                                 volatile='on')
            t = chainer.Variable(xp.asarray(y_test[i:i + batchsize]),
                                 volatile='on')
            loss = model(x, t)
            sum_loss += float(loss.data) * len(t.data)
            sum_accuracy += float(model.accuracy.data) * len(t.data)

        print('test  mean loss={}, accuracy={}'.format(
            sum_loss / N_test, sum_accuracy / N_test))

    # Save the model and the optimizer
    print('save the model')
    serializers.save_hdf5('mlp.model', model)
    print('save the optimizer')
    serializers.save_hdf5('mlp.state', optimizer)
