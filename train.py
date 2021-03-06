import sys
import psutil
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

import convert
#from model import Net
from simple_model import Net

stored_data = []
stored_labels = []

def load_data(path_data, path_labels):
    datafile = open(path_data)
    labelfile = open(path_labels)
    
    data = datafile.readlines()
    labels = labelfile.readlines()

    datafile.close()
    labelfile.close()
    
    return [s.replace("\n", "").split(",") for s in data], [s.replace("\n", "") for s in labels]

def generate_batches(data, labels, batch_size):
    fill_mem = len(stored_data) == 0 and len(stored_labels) == 0
    mem_size = len(stored_data) if not fill_mem else 0

    r = int(len(data) / batch_size + 1) if len(data) % batch_size is not 0 else int(len(data) / batch_size) 
    
    if not fill_mem:
        yield stored_data, stored_labels

    for i in range(r - mem_size):
        #progress = (i+1) / int(len(data) / batch_size) * 100
        #sys.stdout.write('\rLoading data: [{0}] {1}%'.format("#"*int(progress / 5), int(progress)))
        
        end = len(data) if i + mem_size == int(len(data) / batch_size - mem_size) else (i + 1) * batch_size + mem_size
        inputs, targets = data[i * batch_size + mem_size : end], labels[i * batch_size + mem_size : end]
       
        shape = convert.bitboard(inputs[0]).shape
        data_batch = np.zeros((batch_size,) + shape)
        for idx, input in enumerate(inputs):
            data_batch[idx] = convert.bitboard(input)
        
        dir = {"1-0": 1, "1/2-1/2": 0, "0-1" : -1}
        labels_batch = np.zeros((batch_size, 1))
        for idx, label in enumerate(targets):
            labels_batch[idx] = dir[label]
        
        b1, b2 = torch.from_numpy(data_batch), torch.from_numpy(labels_batch)
        if psutil.virtual_memory().percent < 90 and fill_mem:
            stored_data.append(data_batch)
            stored_labels.append(labels_batch)

        yield b1, b2
    sys.stdout.write("\n")


def train(data, labels, batch_size=1, device="cpu", epochs=1):
    
    #train_batches = create_batches(data, labels, batch_size)

    #model = Net(batches[0][0].shape)
    model = Net([119, 8, 8])
    floss = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    if device == "cuda":
        model.cuda()
    
    model.train()
    for e in range(epochs):
        running_loss = 0.0
        for idx, batch in enumerate(generate_batches(data, labels, batch_size)):
            if isinstance(batch[0], list):
                for idx2, (inputs, targets) in enumerate(zip(batch[0], batch[1])):
                    optimizer.zero_grad()
                    outputs = model(inputs.to(device, torch.float))

                    loss = floss(outputs, targets.to(device, torch.float))
                    loss.backward()
                    optimizer.step()
                    
                    running_loss += abs(loss.item())

                    progress = (idx2 + 1) / int(len(data) / batch_size) * 100
                    sys.stdout.write('\rTraining: [{0}] {1}%'.format('#'*int(progress / 5), int(progress)))
                    idx += 1
            else:
                inputs, targets = batch
            
                optimizer.zero_grad()
                outputs = model(inputs.to(device, torch.float))
            
                loss = floss(outputs, targets.to(device, torch.float))
                loss.backward()
                optimizer.step()
            
                running_loss += loss.item()
            
                progress = (idx + 1) / int(len(data) / batch_size) * 100
                sys.stdout.write('\rTraining: [{0}] {1}%'.format("#"*int(progress / 5), int(progress)))
        sys.stdout.write("\n")
        print("epoch: %d, loss: %.3f" % (e, running_loss / int(len(dat) / batch_size)))
    
    scorecard = []
    
    model.eval()

    test_data, test_labels = load_data("data/dataset100K/test_data_25K", "data/dataset100K/test_labels_25K")
    #test_batches = create_batches(test_data, test_labels, 1)
    
    for idx, (inputs, labels) in enumerate(generate_batches(test_data, test_labels, 1)):
        outputs = model(inputs.to(device, torch.float))
        for i, val in enumerate(outputs.tolist()):
            if int(round(val[0])) == labels[i]:
                scorecard.append(1.0)
            else: 
                scorecard.append(0.0)
        progress = (idx + 1) / len(test_batches) * 100
        sys.stdout.write('\rTesting: [{0}] {1}%'.format("#" * int(progress / 5), int(progress)))
    sys.stdout.write("\n")
    print('performance: {:.2f}%'.format(np.sum(scorecard) / len(scorecard) * 100))

if __name__ == "__main__":
    data, labels = load_data("data/dataset100K/train_data_100K", "data/dataset100K/train_labels_100K")
    train(data, labels, batch_size=256, device="cuda", epochs=100)
