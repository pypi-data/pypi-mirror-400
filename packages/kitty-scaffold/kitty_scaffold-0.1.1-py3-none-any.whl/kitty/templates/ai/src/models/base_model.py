"""Model architecture definitions."""


class BaseModel:
    """Base model class."""
    
    def __init__(self):
        pass
    
    def train(self):
        """Train the model."""
        raise NotImplementedError
    
    def predict(self, input_data):
        """Make predictions."""
        raise NotImplementedError
    
    def save(self, path):
        """Save model to disk."""
        raise NotImplementedError
    
    def load(self, path):
        """Load model from disk."""
        raise NotImplementedError
