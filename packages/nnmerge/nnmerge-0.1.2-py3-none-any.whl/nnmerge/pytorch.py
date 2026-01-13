import torch.nn as nn

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

def convert_to_multi_model(single_model_class, constants, hyperparameters_list):
    return MultiModel(single_model_class, constants, hyperparameters_list)