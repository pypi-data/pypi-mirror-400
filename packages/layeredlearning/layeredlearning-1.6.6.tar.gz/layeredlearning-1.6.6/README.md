# LayerLearn — Flexible Model Library

layerlearn is a small Python package that makes it easy to build stacked estimators (regressors and classifiers) around scikit-learn models.
this library is designed to provide a flexible and easy-to-use interface for building stacked models, allowing users to combine multiple models to improve performance. with this library you can stack any scikit-learn compatible models and also you can use the default models provided by the library.

## Features

- **Flexible Stacking**: Easily stack any scikit-learn compatible models.
- **Regression and Classification**: Supports both regression and classification tasks.
- **Customizable**: Allows customization of the base and meta models.
- **Easy to Use**: Simple API for building and training stacked models.

## Requirements

- Python 3.8+
- scikit-learn
- numpy
- xgboost
- catboost
- lightgbm

## Installation

From PyPI:

```bash
pip install layeredlearning
```

From source (recommended for development):

```bash
git clone https://github.com/Mr-J12/newalgo.git
cd newalgo
pip install -e .
```

## Examples & tests

See example scripts in the repository:

- testing/regression_default_dataset.py  
- testing/classification_default_dataset.py  
- testing/instantiation_checking.py


## Quick examples

### Regression:

```python
from layerlearn.flexiblestacked import FlexibleStackedRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split

X, y = make_regression(n_samples=200, n_features=10, noise=10)
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)

base = LinearRegression()
meta = RandomForestRegressor(random_state=0)
stack = FlexibleStackedRegressor(base, meta)
stack.fit(X_train, y_train)
preds = stack.predict(X_test)
print(preds[:5])
```

### Classification:

```python
from layerlearn.flexiblestacked import FlexibleStackedClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

X, y = make_classification(n_samples=200, n_features=10, n_classes=2, random_state=0)
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)

base = LogisticRegression(max_iter=1000)
meta = RandomForestClassifier(random_state=0)
stack = FlexibleStackedClassifier(base, meta)
stack.fit(X_train, y_train)
preds = stack.predict(X_test)
print(preds[:5])
```

## Visualization

### Regression Default Dataset Report
![](/results/different_model_comparison_with_flexible/regression_default_dataset.png)
### Classification Default Dataset Report
![](/results/different_model_comparison_with_flexible/classification_default_dataset.png)

## Model-wise Testing Results

### Regression Model Performance

The regression testing uses a synthetic dataset with 200 samples and 10 features. The following models are evaluated:

- **baseLinear Regressor**: Baseline linear model providing initial predictions
- **baseForest Regressor**: Ensemble of trees capturing non-linear patterns and reducing variance
- **baseXGBR Regressor**: Regularized gradient boosting with strong performance on tabular data
- **baseLight Regressor**: Fast, memory-efficient gradient boosting suited for large datasets
- **baseCat Regressor**: Ordered boosting with robust handling of categorical features

Results and performance metrics are visualized in the regression default dataset report above, showing R² Score across all base models.


### Regression Model Visualizations

**Linear Regression Results**
![](/results/model_wise_on_default_dataset/Linear_Regression.png)

**Random Forest Regressor Results**
![](/results/model_wise_on_default_dataset/Forest_regression.png)

**XGBoost Regressor Results**
![](/results/model_wise_on_default_dataset/XGB_Regression.png)

**LightGBM Regressor Results**
![](/results/model_wise_on_default_dataset/Light_regression.png)

**CatBoost Regressor Results**
![](/results/model_wise_on_default_dataset/Cat_regression.png)

### Classification Model Performance

The classification testing uses a synthetic binary classification dataset with 200 samples and 10 features. The following models are evaluated:

- **Logistic Regression** : Standard logistic classification baseline
- **Random Forest Classifier** : Ensemble method for combining predictions
- **XGBoost Classifier**: Gradient boosting for improved classification accuracy
- **LightGBM Classifier**: Fast classification with categorical feature support
- **CatBoost Classifier**: Optimized for categorical data with robust performance

Results and performance metrics are displayed in the classification default dataset report above, showing Accuracy, Precision, Recall, and F1-Score across all base models.

#### Classification Model Visualizations

**Logistic Regression Results**
![](/results/classification_logistic_regression.png)

**Random Forest Classifier Results**
![](/results/classification_random_forest.png)

**XGBoost Classifier Results**
![](/results/classification_xgboost.png)

**LightGBM Classifier Results**
![](/results/classification_lightgbm.png)

**CatBoost Classifier Results**
![](/results/classification_catboost.png)

## Development

- Install development requirements (scikit-learn, numpy).
- Run example scripts to verify behavior:
  python testing/regression_default_dataset.py

## License

See LICENSE for details.
