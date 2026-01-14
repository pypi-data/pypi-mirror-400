"""Model evaluation functions."""
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns


def evaluate_model(model, X_test, y_test):
    """
    Evaluate model performance.
    
    Args:
        model: Trained model
        X_test: Test features
        y_test: Test labels
    """
    y_pred = model.predict(X_test)
    
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.savefig('reports/figures/confusion_matrix.png')
    print("Confusion matrix saved to reports/figures/confusion_matrix.png")


def plot_feature_importance(model, feature_names):
    """Plot feature importance."""
    if hasattr(model, 'feature_importances_'):
        importance = model.feature_importances_
        
        plt.figure(figsize=(10, 6))
        plt.barh(feature_names, importance)
        plt.xlabel('Importance')
        plt.title('Feature Importance')
        plt.tight_layout()
        plt.savefig('reports/figures/feature_importance.png')
        print("Feature importance plot saved")
