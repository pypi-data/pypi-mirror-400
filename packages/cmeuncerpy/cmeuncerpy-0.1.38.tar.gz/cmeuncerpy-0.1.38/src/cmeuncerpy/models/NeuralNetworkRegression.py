# Author meta data:

__Name__ = "Syed Raza"
__Email__ = "sar0033@uah.edu"

# a PyTorch implemented Neural Network class for Regression 
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

# NOTE: keep working on this class :)

class NeuralNetworkRegression(nn.Module):
    """
    Docstring for NeuralNetworkRegression
    """

    def __init__(self, input_size: int, hidden_layers: list, output_size: int):
        """
        The constructor for NeuralNetworkRegression class

        Params:
            - input_size: number of input features
            - hidden_layers: list containing number of neurons in each hidden layer
            - output_size: number of outputs
        """
        super(NeuralNetworkRegression, self).__init__()

        # Define the layers
        layers = []
        in_features = input_size

        self.trained = False  # Variable to check if the model has been trained

        for hidden_units in hidden_layers:
            layers.append(nn.Linear(in_features, hidden_units))
            layers.append(nn.ReLU())
            in_features = hidden_units

        layers.append(nn.Linear(in_features, output_size))

        # Combine all layers into a sequential module
        self.network = nn.Sequential(*layers)

    def forward(self, x):
        """
        Forward pass through the network

        Params:
            - x: input tensor
        Returns:
            - output tensor
        """
        return self.network(x)
    
    def predict(self, x):
        """
        Predict method for the NeuralNetworkRegression class

        Params:
            - x: input tensor
        Returns:
            - predicted output tensor
        """
        self.eval()  # Set the model to evaluation mode
        with torch.no_grad():
            return self.forward(x)
        
    def fit(self, X_train: np.ndarray, y_train: np.ndarray, 
            learning_rate: float = 0.001, 
            max_epochs: int = 1000, 
            tolerance: float = 1e-6) -> 'NeuralNetworkRegression':
        """
        Fit method for training the NeuralNetworkRegression model

        Params:
            - X_train: training input data as a numpy array
            - y_train: training labels as a numpy array
            - learning_rate: learning rate for the optimizer (default: 0.001)
            - max_epochs: maximum number of epochs for training (default: 1000)
            - tolerance: tolerance for convergence (default: 1e-6)
        Returns:
            - self: trained NeuralNetworkRegression model
        """
        # Convert numpy arrays to torch tensors
        X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
        y_train_tensor = torch.tensor(y_train, dtype=torch.float32) 

        # Define loss function and optimizer
        loss_function = nn.MSELoss()
        optimizer = optim.Adam(self.parameters(), lr=learning_rate)

        prev_loss = float("inf")
        self.loss_history = []  
        # Training loop
        for epoch in range(max_epochs):
            self.train()  # Set the model to training mode
            optimizer.zero_grad()  # Reset gradients

            # Forward pass  
            predictions = self.forward(X_train_tensor)
            loss = loss_function(predictions, y_train_tensor)  # Compute loss

            loss.backward()  # Backward pass

            optimizer.step()  # Update model parameters

            current_loss = float(loss.detach().item())

            self.loss_history.append(current_loss)  # Store loss history
            
            # Convergence check
            if abs(prev_loss - current_loss) < tolerance:
                print(f"Converged after {epoch+1} epochs.")
                break

            prev_loss = current_loss

            self.trained = True

        return self
    
    def predict(self, X_test: np.ndarray) -> np.ndarray:
        """
        The predict function for Linear Regression

        Params:
            - X_test, is the test input data as a numpy array
        Returns:
            - the predicted labels as a numpy array
        """
        if not self.trained:
            raise ValueError("Model is not trained yet. Please call fit() before predict().")

        # convert to pytorch tensor
        X_test_tensor = torch.tensor(X_test, dtype=torch.float32)

        # get predictions
        with torch.no_grad():
            predictions = self.forward(X_test_tensor)

        return predictions.numpy()
    
    def predict(self, X_test: np.ndarray) -> np.ndarray:
        """
        The predict function for Neural Network Regression

        Params:
            - X_test, is the test input data as a numpy array
        Returns:
            - the predicted values as a numpy array
        """        
        if not self.trained:
            raise ValueError("Model is not trained yet. Please call fit() before predict().")

        # convert to pytorch tensor
        X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
        # get predictions
        with torch.no_grad():
            predictions = self.forward(X_test_tensor)

        return predictions.numpy()
    
if __name__ == "__main__":
    # Example usage
    model = NeuralNetworkRegression(input_size=3, hidden_layers=[5, 5], output_size=1)
    X_train = np.random.rand(100, 3)
    y_train = np.random.rand(100, 1)
    model.fit(X_train, y_train)
    X_test = np.random.rand(10, 3)
    predictions = model.predict(X_test)
    print(predictions)