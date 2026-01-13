# Import necessary libraries
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from layerlearn.baseLightC import LightForestClassifier, LightSupportClassifier, LightDecisionClassifier, LightKNNClassifier, LightXGBClassifier, LightCatClassifier, LightGradientClassifier, LightAdaClassifier, LightLogisticClassifier
import warnings

warnings.filterwarnings("ignore")

# --- 1. Generate or Load Dataset ---
# This creates a sample dataset for classification tasks.
X, y = make_classification(n_samples=10000, n_features=10, n_informative=5, n_redundant=2, n_classes=2, random_state=42)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# --- 3. Initialize All Models ---
# Create a dictionary to hold all the models you want to compare.
models = {
    "Light Forest Classifier": LightForestClassifier(),
    "Light Support Classifier": LightSupportClassifier(),
    "Light Decision Classifier": LightDecisionClassifier(),
    "Light KNN Classifier": LightKNNClassifier(),
    "Light XGBoost Classifier": LightXGBClassifier(),
    "Light CatBoost Classifier": LightCatClassifier(),
    "Light Gradient Boosting Classifier": LightGradientClassifier(),
    "Light AdaBoost Classifier": LightAdaClassifier(),
    "Light Logistic Classifier": LightLogisticClassifier(),
}

# --- 4. Train Models and Evaluate ---
results = {}
confusion_matrices = {}
classification_reports = {}
warnings.filterwarnings("ignore")
print("Training and evaluating models...")
for name, model in models.items():
    # Train the model on the training data
    model.fit(X_train, y_train)

    # Make predictions on the test data
    y_pred = model.predict(X_test)

    # Calculate the accuracy score and store it
    score = accuracy_score(y_test, y_pred)
    results[name] = score
    confusion_matrices[name] = confusion_matrix(y_test, y_pred)
    classification_reports[name] = classification_report(y_test, y_pred)
    print(f"- {name}: Accuracy score = {score:.4f}")
    print(f"Confusion Matrix:\n{confusion_matrices[name]}")
    print(f"Classification Report:\n{classification_reports[name]}\n")

# --- 5. Create Comparison Graph ---
# Prepare data for plotting
model_names = list(results.keys())
accuracy_scores = list(results.values())

# Create the bar chart
plt.style.use('seaborn-v0_8-darkgrid')
fig, ax = plt.subplots(figsize=(10, 7))

# Create bars with different colors
colors = ['#4C72B0', '#55A868', '#C44E52', '#8172B2', '#CCB974', '#64B5CD', '#8C8C8C']
bars = ax.barh(model_names, accuracy_scores, color=colors)

# Add title and labels
ax.set_title('Comparison of KNN Model Classifier Performance', fontsize=18, fontweight='bold')
ax.set_xlabel('Accuracy Score', fontsize=12)
ax.set_ylabel('Algorithm', fontsize=12)
ax.set_xlim(0, 1.0) # Accuracy score ranges from 0 to 1

# Add the score value on each bar
for bar in bars:
    width = bar.get_width()
    # Position text slightly outside the bar
    label_x_pos = width + 0.01
    ax.text(label_x_pos, bar.get_y() + bar.get_height()/2, f'{width:.3f}',
            va='center', ha='left', fontsize=11, color='black')

# Invert y-axis to have the best-performing model on top
ax.invert_yaxis()

# Show the plot
plt.show()