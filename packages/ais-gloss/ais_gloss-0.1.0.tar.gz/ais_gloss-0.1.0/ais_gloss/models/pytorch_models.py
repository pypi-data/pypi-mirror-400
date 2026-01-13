import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader


class TabularDataset(Dataset):
    """Dataset for tabular data"""

    def __init__(self, X, y):
        self.X = torch.FloatTensor(X)
        self.y = torch.FloatTensor(y) if len(y.shape) == 1 else torch.FloatTensor(y)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


class SimpleNN(nn.Module):
    """Simple Neural Network"""

    def __init__(self, input_dim, output_dim, hidden_dims=[64, 32], dropout=0.2):
        super(SimpleNN, self).__init__()

        layers = []
        prev_dim = input_dim

        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            prev_dim = hidden_dim

        layers.append(nn.Linear(prev_dim, output_dim))

        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)


class DeepNN(nn.Module):
    """Deep Neural Network"""

    def __init__(self, input_dim, output_dim, hidden_dims=[128, 64, 32, 16], dropout=0.3):
        super(DeepNN, self).__init__()

        layers = []
        prev_dim = input_dim

        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.BatchNorm1d(hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            prev_dim = hidden_dim

        layers.append(nn.Linear(prev_dim, output_dim))

        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)


class PyTorchModelWrapper:
    """Wrapper for PyTorch models to make them compatible with sklearn interface"""

    def __init__(self, model_class, input_dim, output_dim, task='regression',
                 hidden_dims=None, dropout=0.2, lr=0.001, epochs=100, batch_size=32):
        self.model_class = model_class
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.task = task
        self.hidden_dims = hidden_dims or [64, 32]
        self.dropout = dropout
        self.lr = lr
        self.epochs = epochs
        self.batch_size = batch_size
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None

    def fit(self, X, y):
        """Train the model"""
        # Prepare data
        if len(y.shape) == 1:
            y = y.reshape(-1, 1)

        dataset = TabularDataset(X, y)
        dataloader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        # Initialize model
        self.model = self.model_class(
            self.input_dim, self.output_dim,
            hidden_dims=self.hidden_dims, dropout=self.dropout
        ).to(self.device)

        # Loss and optimizer
        if self.task == 'regression':
            criterion = nn.MSELoss()
        else:
            criterion = nn.CrossEntropyLoss()

        optimizer = optim.Adam(self.model.parameters(), lr=self.lr)

        # Training loop
        self.model.train()
        for epoch in range(self.epochs):
            epoch_loss = 0
            for batch_X, batch_y in dataloader:
                batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)

                optimizer.zero_grad()
                outputs = self.model(batch_X)

                if self.task == 'classification':
                    batch_y = batch_y.long().squeeze()

                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()

                epoch_loss += loss.item()

        return self

    def predict(self, X):
        """Make predictions"""
        self.model.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X).to(self.device)
            outputs = self.model(X_tensor)

            if self.task == 'classification':
                predictions = torch.argmax(outputs, dim=1).cpu().numpy()
            else:
                predictions = outputs.cpu().numpy().squeeze()

        return predictions

    def predict_proba(self, X):
        """Predict probabilities (for classification)"""
        if self.task != 'classification':
            raise ValueError("predict_proba only available for classification tasks")

        self.model.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X).to(self.device)
            outputs = self.model(X_tensor)
            probabilities = torch.softmax(outputs, dim=1).cpu().numpy()

        return probabilities


def get_pytorch_models(input_dim, output_dim, task='regression'):
    """Get dictionary of PyTorch models"""
    models = {
        'PyTorch_SimpleNN': PyTorchModelWrapper(
            SimpleNN, input_dim, output_dim, task=task,
            hidden_dims=[64, 32], dropout=0.2, epochs=100
        ),
        'PyTorch_DeepNN': PyTorchModelWrapper(
            DeepNN, input_dim, output_dim, task=task,
            hidden_dims=[128, 64, 32, 16], dropout=0.3, epochs=100
        ),
    }
    return models
