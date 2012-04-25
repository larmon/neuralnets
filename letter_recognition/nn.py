#!/usr/bin/env python

"""
nn.py -- implement artifical neural networks.

work module for hw2.
"""

import math

import random

def sigmoid(dblX):
    """The sigmoid function.  Given input dblX, sigmoid(dblX).

    >>> sigmoid(0.0)
    0.5
    >>> sigmoid(100.0)
    1.0
    >>> sigmoid(-100.0) < 1.0e-10
    True
    """
    return 1 / (1 + math.exp(-dblX))

class Perceptron(object):
    """Implements a node in a feed-forward neural network."""
    def __init__(self, listDblW, dblW0, ix):
        """Arguments:
        listDblW
            a list of weights, corresponding to w_1 to w_m in the notes.
        dblW0
            the constant-input weight referred to as w_0 in the notes.
        ix
            the index of this perceptron in it's layer (for computing
            the error of hidden nodes).
        """
        self.listDblW = map(float,listDblW)
        self.dblW0 = float(dblW0)
        self.ix = int(ix)
    def __repr__(self):
        tplSFormat = (list(self.listDblW), self.dblW0, self.ix)
        return "Perceptron(%r, %r, %r)" % tplSFormat
    def input_size(self):
        return len(self.listDblW)

class NeuralNetLayer(object):
    """Encapsulates a single layer of a neural network in which the layers
    are completely connected to their adjacent layers."""
    def __init__(self, cInputs, listPcpt):
        """Arguments:
        cInputs
            The number of inputs each perceptron in the layer receives.
            Because the layers are completely connected, each perceptron
            in the layer must receive the same number of inputs.
        listPcpt
            A list of perceptrons in the layer. The index of each perceptron
            must match its zero-indexed position in this list. That is,
            the following must hold:

                listPcpt[0].ix == 0.
        """
        self.check_consistency(cInputs, listPcpt)
        self.cInputs = int(cInputs)
        self.listPcpt = listPcpt
    def layer_input_size(self):
        """Returns the number of inputs connected to each unit in this layer."""
        return self.cInputs
    def layer_output_size(self):
        """Returns the number of units in this layer."""
        return len(self.listPcpt)
    @classmethod
    def check_consistency(cls, cInputs, listPcpt):
        for ix,pcpt in enumerate(listPcpt):
            if not isinstance(pcpt, Perceptron):
                raise TypeError("Expected Perceptron")
            if pcpt.input_size() != cInputs:
                raise TypeError("Input size mismatch")
            if pcpt.ix != ix:
                raise ValueError("Index mismatch. Expected %d but found %d"
                                 % (ix, pcpt.ix))

def dot(listDbl1, listDbl2):
    """Takes the dot product of two equal-length lists of floats.

    >>> dot([1.0, 2.0, 3.0], [-1.0, 0.25, 4.0])
    11.5"""
    if len(listDbl1) != len(listDbl2):
        raise ValueError("Incompatible lengths")
    return sum([dbl1*dbl2 for dbl1,dbl2 in zip(listDbl1,listDbl2)])

def output_error(dblActivation,dblTarget):
    """Computes the output error for perceptron activation level
    dblActivation and target value dblTarget.

    This is err_k in the lecture notes.

    Getting the sign of the return value of this function incorrect
    will cause you no end of headaches.  Make sure the order of the variables is
    correct when you are computing the error.

    >>> output_error(0.75, -1.0) # yes, it's this simple.
    -1.75"""
    return(dblTarget - dblActivation)

def hidden_error(listDblDownstreamDelta, pcpt, layerNext):
    """Determines the error on a hidden node from, its downstream deltas,
    and the weights of its out-edges.

    The output of this function corresponds to err_j in the lecture
    notes.
    
    >>> pcpt = Perceptron([], 0.0, 0)
    >>> listPcpt = [Perceptron([1.5],0,0), Perceptron([2.0],0,1)]
    >>> layer = NeuralNetLayer(1, listPcpt)
    >>> hidden_error([1.0, 0.75], pcpt, layer)
    3.0"""

    # zip the two lists together so that each delta is tupled with a Perceptron
    zipped = zip(listDblDownstreamDelta, layerNext.listPcpt)
    
    # sum the weights in each perceptron
    # del_wt = map ((lambda (a,b): (a, sum(b.listDblW))), zipped)
    del_wt = map ((lambda (a,b): (a, b.listDblW[pcpt.ix])), zipped)
    
    # multiply each delta times the summed list of weights for each Perceptron
    multiplied = map ((lambda (c,d): c*d), del_wt)
    
    # add the whole list together to get the weighted total sum
    return sum(multiplied)
    
def compute_delta(dblActivation, dblError):
    """Computes a delta value from activation and error.

    These values are referred to as \delta_j and \delta_k in the
    lecture notes.
    >>> compute_delta(0.5,0.5)
    0.125"""
    return dblError * dblActivation * (1 - dblActivation)

def update_weight(dblW, dblLearningRate, dblInput, dblDelta):
    """Compute the updated weight from the original weight `dblW`, the
    learning rate `dblLearningRate`, the input `dblInput` from an upstream
    node, and the current node's delta `dblDelta`.

    >>> update_weight(3.0, 0.1, 1.25, 2.0)
    3.25"""
    return(dblW + dblLearningRate * dblInput * dblDelta)

def update_pcpt(pcpt, listDblInputs, dblDelta, dblLearningRate):
    """Update the perceptron's weights according to the update rule
    given by equation 15 in the lecture notes.

    In this case, pcpt.listDblW correponds to the w_j's, dblLearningRate
    corresponds to lpha, listDblInputs corresponds to the x_j's, and
    dblDelta corresponds to \delta.

    Don't forget to update the perceptron's fixed-input weight (w_0 in
    the notes)!

    This function updates the perceptron's weights in place and does not
    return anything.

    >>> pcpt = Perceptron([1.0,2.0,3.0], 4.0, 0)
    >>> print pcpt
    Perceptron([1.0, 2.0, 3.0], 4.0, 0)
    >>> update_pcpt(pcpt, [0.5,0.5,0.5], 0.25, 2.0)
    >>> print pcpt
    Perceptron([1.25, 2.25, 3.25], 4.5, 0)"""

    #multiplies each element in listDblInputs by the dblDelta
    new_weights = []
    for dblW, dblInput in zip(pcpt.listDblW, listDblInputs):
        updt_wt = update_weight(dblW, dblLearningRate, dblInput, dblDelta)
        new_weights.append(updt_wt)

    #adds each element in new_weights with the perceptron's original weights
    new_dblW0 = pcpt.dblW0 + (dblDelta * dblLearningRate)
    
    pcpt.listDblW = new_weights
    pcpt.dblW0 = new_dblW0    

def pcpt_activation(pcpt, listDblInput):
    """Compute a perceptron's activation function.
    >>> pcpt = Perceptron([0.5,0.5,-1.5], 0.75, 0)
    >>> pcpt_activation(pcpt, [0.5,1.0,1.0])
    0.5"""

    print(pcpt.listDblW)
    print(listDblInput)
    
    return sigmoid(dot(pcpt.listDblW, listDblInput) + pcpt.dblW0)

def feed_forward_layer(layer, listDblInput):
    """Build a list of activation levels for the perceptrons
    in the layer recieving input listDblInput.

    >>> pcpt1 = Perceptron([-1.0,2.0], 0.0, 0)
    >>> pcpt2 = Perceptron([-2.0,4.0], 0.0, 1)
    >>> layer = NeuralNetLayer(2, [pcpt1, pcpt2])
    >>> listDblInput = [0.5, 0.25]
    >>> feed_forward_layer(layer, listDblInput)
    [0.5, 0.5]"""

    list_act_fun = []
    #returns a list of activation functions for every pcpt in the layer
    for pcpt in layer.listPcpt:
        act_level = pcpt_activation(pcpt, listDblInput)
        list_act_fun.append(act_level)
    return list_act_fun

class NeuralNet(object):
    """An artificial neural network."""
    def __init__(self, cInputs, listLayer):
        """Assemble the network from layers listLayer. cInputs specifies
        the number of inputs to each node in the first hidden layer of the
        network."""
        if not self.check_layers(cInputs, listLayer):
            raise TypeError("Incompatible neural network layers.")
        self.cInputs = cInputs
        for layer in listLayer:
            if not isinstance(layer, NeuralNetLayer):
                raise TypeError("NeuralNet layers must be of type "
                                "NeuralNetLayer.")
        self.listLayer = listLayer
    @classmethod
    def check_layers(cls, cInputs, listLayer):
        if not listLayer:
            return False
        if cInputs != listLayer[0].layer_input_size():
            return False
        for layerFst,layerSnd in zip(listLayer[:-1], listLayer[1:]):
            if layerFst.layer_output_size() != layerSnd.layer_input_size():
                return False
        return True
    def input_layer(self):
        return self.listLayer[0]
    def output_layer(self):
        return self.listLayer[-1]

def build_layer_inputs_and_outputs(net, listDblInput):
    """Build a pair of lists containing first the a list of the input
    to each layer in the neural network, and second, a list of output
    from each layer in the network.

    The list of inputs should contain as its first element listDblInput,
    the inputs to the first layer of the network.

    The list of outputs should contain as its last element the output of the
    output layer.
    >>> listCLayerSize = [2,2,1]
    >>> net = init_net(listCLayerSize)
    >>> build_layer_inputs_and_outputs(net, [-1.0, 1.0]) # doctest: +ELLIPSIS
    ([[...], [...]], [[...], [...]])"""
    lstInputs = []
    lstOutputs = []
    list_new_inputs = listDblInput
    for i in net.listLayer:
        lstInputs.append(list_new_inputs)
        layerOutputs = feed_forward_layer(i, list_new_inputs)
        lstOutputs.append(layerOutputs)
        list_new_inputs = layerOutputs
    return (lstInputs, lstOutputs)

def feed_forward(net, listDblInput):
    """Compute the neural net's output on input listDblInput."""
    return build_layer_inputs_and_outputs(net, listDblInput)[-1][-1]

def layer_deltas(listDblActivation, listDblError):
    """Compute the delta values for a layer which generated activation levels
    listDblActivation, resulting in error listDblError.

    >>> layer_deltas([0.5, 0.25], [0.125, 0.0625])
    [0.03125, 0.01171875]"""

    zipped = zip(listDblActivation, listDblError)
    deltas = map((lambda (a,b): compute_delta(a,b)), zipped)
    return deltas

def update_layer(layer, listDblInputs, listDblDelta,  dblLearningRate):
    """Update all perceptrons in the neural net layer.

    The function updates the perceptrons in the layer in place, and does
    not return anything.

    >>> listPcpt = [Perceptron([1.0,-1.0],0.0,0), Perceptron([-1.0,1.0],0.0,1)]
    >>> layer = NeuralNetLayer(2, listPcpt)
    >>> print layer.listPcpt
    [Perceptron([1.0, -1.0], 0.0, 0), Perceptron([-1.0, 1.0], 0.0, 1)]
    >>> update_layer(layer, [0.5,-0.5], [2.0,2.0], 0.5) # do the update
    >>> print layer.listPcpt
    [Perceptron([1.5, -1.5], 1.0, 0), Perceptron([-0.5, 0.5], 1.0, 1)]"""
    
    zipped = zip(layer.listPcpt,listDblDelta)
    updated_pcpts = map((lambda (pcpt,dblDelta): \
    update_pcpt(pcpt, listDblInputs, dblDelta, dblLearningRate)), zipped)   


def hidden_layer_error(layer, listDblDownstreamDelta, layerDownstream):
    """Determine the error produced by each node in a hidden layer, given the
    next layer downstream and the deltas produced by that layer.

    >>> layer = NeuralNetLayer(0, [Perceptron([], 0.0, 0),
    ...                            Perceptron([], 0.0, 1)])
    >>> layerDownstream = NeuralNetLayer(2, [Perceptron([0.75,0.25], 0.0, 0)])
    >>> hidden_layer_error(layer, [2.0], layerDownstream)
    [1.5, 0.5]"""
    
    return map((lambda x: \
    hidden_error(listDblDownstreamDelta, x, layerDownstream)), layer.listPcpt)
    

class Instance(object):
    def __init__(self, iLabel, listDblFeatures):
        self.iLabel = iLabel
        self.listDblFeatures = listDblFeatures

class ImageInstance(Instance):
    """Implements an instance composed of 2D data.

    A 1D representation of the data is available as in the Instance class
    through the data member listDblFeatures."""
    def __init__(self, iLabel, listListImage):
        listDblFeatures = []
        self.cRow = len(listListImage)
        self.cCol = None
        for listDblRow in listListImage:
            self.cCol = max(len(listDblRow), self.cCol)
            for dblCol in listDblRow:
                listDblFeatures.append(dblCol)
        super(ImageInstance,self).__init__(iLabel,listDblFeatures)
    def reconstruct_image(self):
        pass

def distributed_encode_label(iLabel):
    """Generate a distributed encoding of the integer label iLabel.
    The label will always be between 0 and 25, inclusive.

    >>> listDblEncoding = distributed_encode_label(2)
    >>> print listDblEncoding # doctest: +ELLIPSIS
    [...]
    >>> print " ".join("%.2f" % dbl for dbl in listDblEncoding)
    0.05 0.05 0.95 0.05 0.05 0.05 0.05 0.05 0.05 0.05"""
    
    # make a list of 10 0.05's
    lst = [0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05,0.05]
    
    # change the box with the index = iLabel to 0.95
    lst[iLabel] = 0.95
    
    return lst

def binary_encode_label(iLabel):
    """Generate a binary encoding of the integer label iLabel.
    The label will always be between 0 and 9, inclusive.

    The test suite assumes a little-endian arrangement, where the first
    number in your binary encoding should represent the least significant
    bit. This choice was arbitrary and there is in general no reason to prefer
    one endianness to another.

    >>> print " ".join("%.2f" % dbl for dbl in binary_encode_label(6))
    0.05 0.95 0.95 0.05"""
    
    num = iLabel
    #find the number of sixteens left in the ilabel
    sixteens = num/16
    #update number
    num = num - 16*sixteens
    #find the number of eights left in ilabel
    eights = num/8
    #update number
    num = num - 8*eights
    #find the number of fours left in iLabel
    fours = num/8
    #update number
    num = num - 4*fours
    #find the number of twos left in iLabel
    twos = num/2
    #update number
    num = num - 2*twos
    #find the number of ones left in iLabel
    ones = num
    
    binary = [ones, twos, fours, eights, sixteens]
    for i in binary:
        if i == 1: 
            i = 0.95
        else:
            i = 0.05
    return binary

def distributed_decode_net_output(listDblOutput):
    """Decode the output of a neural network with distributed-encoded outputs.

    >>> listDblOutput = [0.23, 0.4, 0.01, 0.2, 0.3, 0.78, 0.51, 0.15, 0.2, 0.1]
    >>> distributed_decode_net_output(listDblOutput)
    5"""
    
    # find the maximum number in the list
    max_num = max(listDblOutput)
    
    # return its index
    return listDblOutput.index(max_num)

def binary_decode_net_output(listDblOutput):
    """Decode the output of a neural network with binary-encoded outputs.

    You should implement this function assuming a little-endian encoding
    (see binary_encode_label for detail).

    >>> binary_decode_net_output([0.95, 0.44, 0.01, 0.51, 0.06])
    """
    lst = listDblOutput
    
    for i in range(0,5):
    
        if (lst[i] < 0.50):
            lst[i] = 0
        else:
            lst[i] = 1 * (2 ** i)
    
    return sum(lst)

def get_weight(net, layer_id, perceptron_id, input_id):
    if input_id == -1:
        return net.listLayer[layer_id].listPcpt[perceptron_id].dblW0
    return net.listLayer[layer_id].listPcpt[perceptron_id].listDblW[input_id]

def update_net(net, inst, dblLearningRate, listTargetOutputs):
    """Update the weights of a neural network using the data in instance inst
    and the target values in listTargetOutputs.

    This is the big one. It requires three steps:

    1. Feed the instance data forward to generate the inputs and
       outputs for every layer.
    2. Compute the delta values for each node.
    3. Update the weights for each node.

    This function returns the list of outputs after feeding forward.  Weight
    updates are done in place.
    """

    l_ins, l_outs = build_layer_inputs_and_outputs(net, inst.listDblFeatures)
    l_errs = []
    l_acts = []
    l_delts = []

    #builds the errors for the last layer (l_errs NOT COMPLETE AT THIS POINT)
    errs = []
    for i in range(len(l_outs[-1])):
        errs.append(output_error(l_outs[-1][i], listTargetOutputs[i]))
    l_errs.append(errs)

    #calculates deltas for the last layer based on output error info
    l_delts.append(layer_deltas(l_outs[-1], l_errs[-1]))

    #calculates hidden errors for the rest of the layers and deltas
    for i in range(2, len(net.listLayer)+1): 
        cur_layer = net.listLayer[-i] 
        dwn_layr = net.listLayer[-i+1] 
        l_errs.insert(0, hidden_layer_error(cur_layer, l_delts[-i+1], dwn_layr))
        l_delts.insert(0, layer_deltas(l_outs[-i], l_errs[-i]))

    #Finally, uses layers, inputs, deltas, and learning rate to update the net
    for i in range(len(net.listLayer)):
        update_layer(net.listLayer[i], l_ins[i], l_delts[i], dblLearningRate)

    return l_outs[-1]

def init_net(listCLayerSize, dblScale=0.01):
    """Build an artificial neural network and initialize its weights
    to random values in the interval (-dblScale,dblScale).

    The structure of the network is specified in listCLayerSize. The
    elements of this list correspond to

    [<number of inputs>, <number of nodes in the first hidden layer>,
    ..., <number of nodes in the last hidden layer>, <number of outputs>].

    There may be zero or more hidden layers. Each layer should be completely
    connected to the next.

    This function should return the network."""

    num_inputs = listCLayerSize[0]
    list_layers = []

    #if there are zero hidden layers
    if len(listCLayerSize) == 2:
        return NeuralNet(num_inputs, list_layers)

    #creates n-2 hidden layers, because input and output doesn't need layers
    for nn_counter in range(1, len(listCLayerSize)):

        #list of perceptrons to be passed into the neural net layer
        list_pcpts = []

        #creates a Perceptron for each node in the layer
        nodes_in_cur_layer = range(0, listCLayerSize[nn_counter])
        for pcpt_counter in nodes_in_cur_layer:
            const_inp_wt = random.uniform(-dblScale, dblScale)
            list_wts = []

            #creates list of weights, from 0 to the # of nodes in prev layer
            for wt_counter in range(listCLayerSize[nn_counter-1]):
                list_wts.append(random.uniform(-dblScale, dblScale))

            list_pcpts.append(Perceptron(list_wts, const_inp_wt, pcpt_counter))

        list_layers.append(NeuralNetLayer(listCLayerSize[nn_counter-1], list_pcpts))

    return NeuralNet(num_inputs, list_layers)

def load_data(sFilename, cMaxInstances=None):
	"""Load at most cMaxInstances instances from sFilename, or all instance if 
	cMaxInstances is None."""
	listInst = []
	infile = open(sFilename)
	try:
		listInputs = []
		iLabel = None
		for sLine in infile:
			if (sLine[0].isalpha()): 
				iLabel = ord(sLine[0]) - ord('A')
				listInputs.append([float(s)/16 for s in sLine[2:].split(',')])
				listInst.append(ImageInstance(iLabel, listInputs))
				if (cMaxInstances is not None and len(listInst) >= cMaxInstances):
					break
				listIntputs =[]
			else:
				break
	finally:
		infile.close()
	return listInst

def print_net(net):
    """Convenience routine for printing a network to standard out."""
    for layer in net.listLayer:
        print ""
        for pcpt in layer.listPcpt:
            print pcpt

class XorWrapper(object):
    XOR_INSTANCES = [Instance(0.1, [-1.0,-1.0]), Instance(0.9, [-1.0,1.0]),
                     Instance(0.9, [1.0,-1.0]), Instance(0.1, [1.0,1.0])]

def learn_xor():
    """Build a neural network which solves XOR."""
    net = init_net([2,2,1],0.5)
    for _ in xrange(5000):
        for inst in XorWrapper.XOR_INSTANCES:
            update_net(net,inst, 0.5, [inst.iLabel])
    for inst in XorWrapper.XOR_INSTANCES:
        print inst.iLabel, feed_forward(net,inst.listDblFeatures)

def num_correct(net, listInst):
  cCorrect = 0
  for inst in listInst:
    listDblOut = feed_forward(net,inst.listDblFeatures)
    iGuess = distributed_decode_net_output(listDblOut)
    #if opts.fShowGuesses:
    #print inst.iLabel, iGuess
    cCorrect += int(inst.iLabel == iGuess)
  return cCorrect

def experiment(opts):
    """Conduct a neural net performance experiment.

    Construct a neural network, then train it for cRounds on the data
    in sTrainFile. Then, test the resulting network on the instances in
    sTestFile.

    Finally, print out the accuracy achieved by the neural network.

    You may want to play with this function in order to run experiments
    of interest to you."""
    dictSeen = {}
    def load(sFilename):
        if sFilename in dictSeen:
            return dictSeen[sFilename]
        sys.stderr.write("Loading %s..." % sFilename)
        listInst = load_data(sFilename,opts.max_inst)
        sys.stderr.write("done.\n")
        dictSeen[sFilename] = listInst
        return listInst
    listInstTrain = load(opts.train)
    listInstVal = load(opts.validation)
    listInstTest = load(opts.test)
    config = [opts.num_inputs]
    if opts.hidden_units:
      print 'Adding a hidden layer with %d units' % opts.hidden_units
      config.append(opts.hidden_units)
    config.append(10)
    net = init_net(config)
    dblAlpha = opts.learning_rate
    print 'Learning rate: %f' % dblAlpha
    for ixRound in xrange(opts.rounds):
        # Compute the error
        errors = 0
        for inst in listInstTrain:
            listDblOut = update_net(net,inst,dblAlpha,distributed_encode_label(inst.iLabel))
            iGuess = distributed_decode_net_output(listDblOut)
            #print inst.iLabel, iGuess
            if iGuess != inst.iLabel:
              errors += 1
        # Get validation error
        validation_correct = num_correct(net, listInstVal)
        sys.stderr.write(
        "Round %d complete.  Training Accuracy: %f, Validation Accuracy: %f\n" % (
          ixRound + 1,
          1 - errors * 1.0 / len(listInstTrain),
          validation_correct * 1.0 / len(listInstVal)))
        if opts.stopping_condition:
            # TODO(CS181 Student): implement your stopping condition
            # as described in part 3.4 of the homework instructions.
            # Don't forget to use --enable-stopping on the command
            # line to activate the functionality you implement here.
            print "Implement me!"
    cCorrect = 0
    for inst in listInstTest:
        listDblOut = feed_forward(net,inst.listDblFeatures)
        iGuess = distributed_decode_net_output(listDblOut)
        #if opts.fShowGuesses:
        #print inst.iLabel, iGuess
        cCorrect += int(inst.iLabel == iGuess)
    print "correct:",cCorrect, "out of", len(listInstTest),
    print "(%.1f%%)" % (100.0*float(cCorrect)/float(len(listInstTest)))

def main(argv):
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("-d", "--doc-test", action="store_true", dest="doctest",
                      help="run doctests in nn.py")
    parser.add_option("-x", "--learn-xor", action="store_true", dest="xor",
                      help="run learn_xor")
    parser.add_option("-r", "--train", action="store", dest="train",
                      help="file containing training instances",
                      default="training-2000.txt")
    parser.add_option("-t", "--test", action="store", dest="test",
                      default="test-1000.txt",
                      help="file containing test instances")
    parser.add_option("-v", "--validation", action="store", dest="validation",
                      default="validation-1000.txt",
                      help="file containing test instances")
    parser.add_option("-n", "--rounds", action="store", dest="rounds",
                      default=10, type=int, help="number of training rounds")
    parser.add_option("-m", "--max-instances", action="store", dest="max_inst",
                      default=None, type=int,
                      help="maximum number of instances to load")
    parser.add_option("-l", "--learning_rate", action="store",
                      dest="learning_rate",
                      default=1.0, type=float,
                      help="the learning rate to use")
    parser.add_option("--hidden", action="store",
                      dest="hidden_units",
                      default=None, type=int,
                      help="number of hidden units to use.")
    parser.add_option("--num_inputs", action="store",
                      dest="num_inputs",
                      default=(10*12), type=int,
                      help="number of hidden units to use.")
    parser.add_option("--enable-stopping", action="store_true",
                      dest="stopping_condition", default=False,
                      help="detect when to stop training early (TODO)")
    opts,args = parser.parse_args(argv)
    if opts.doctest:
        import doctest
        doctest.testmod()
        return 0
    if opts.xor:
        learn_xor()
        return 0
    experiment(opts)
    return 0



if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
