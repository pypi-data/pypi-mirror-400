import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import time
from tqdm import tqdm

class MyModel(nn.Module):
    def __init__(self, constants, hyperparameters):
        super(MyModel, self).__init__()
        self.fc1 = nn.Linear(constants["input_size"], hyperparameters["hidden_size_l1"])
        self.fc2 = nn.Linear(hyperparameters["hidden_size_l1"], hyperparameters["hidden_size_l2"])
        self.fc3 = nn.Linear(hyperparameters["hidden_size_l2"], constants["num_classes"])
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return x

class MultiModel(nn.Module):
    def __init__(self, SingleModel, constants, hyperparameters_list):
        super(MultiModel, self).__init__()
        self.model_list = []
        for hyperparameters in hyperparameters_list:
            self.model_list.append(SingleModel(constants, hyperparameters))

    def forward(self, x):
        y_list = []
        for model in self.model_list:
            y_list.append(model(x))
        return y_list

    def to(self, device):
        for model in self.model_list:
            model.to(device)
        return self

if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    batch_size = 10_000

    constants = {
        "input_size": 10_000,
        "num_classes": 3
    }

    hyperparameters = {"hidden_size_l1": 10, "hidden_size_l2": 15}

    hyperparameters_list = [
        {"hidden_size_l1": 10, "hidden_size_l2": 10},
        {"hidden_size_l1": 10, "hidden_size_l2": 15},
        {"hidden_size_l1": 15, "hidden_size_l2": 10},
        {"hidden_size_l1": 15, "hidden_size_l2": 15},
        {"hidden_size_l1": 20, "hidden_size_l2": 10},
        {"hidden_size_l1": 20, "hidden_size_l2": 15},
        {"hidden_size_l1": 20, "hidden_size_l2": 20},
    ]

    x = torch.randn(batch_size, constants["input_size"]).to(device)

    # ======================================================
    # Sequential hyperparameter search
    # ======================================================
    print("Sequential hyperparameter search execution time:")
    start_time = time.time()
    
    for hyperparameters in tqdm(hyperparameters_list):
        model = MyModel(constants, hyperparameters)
        model.to(device)
        output = model(x)
        print("Model output shape: ", output.shape)
    
    end_time = time.time()
    elapsed_time_sequential = end_time - start_time
    
    print(f"\nExecution time: {elapsed_time_sequential}")
    # ======================================================

    # ======================================================
    # Parallel hyperparameter search
    # ======================================================
    print("Parallel hyperparameter search execution time:")
    start_time = time.time()

    model = MultiModel(MyModel, constants, hyperparameters_list)
    model.to(device)
    output = model(x)
    print("Model output length: ", len(output))
    
    end_time = time.time()
    elapsed_time_parallel = end_time - start_time
    print(f"\nExecution time: {elapsed_time_parallel}")

    print(f"Speedup: {elapsed_time_sequential/elapsed_time_parallel*100}%")    
    # ======================================================
    