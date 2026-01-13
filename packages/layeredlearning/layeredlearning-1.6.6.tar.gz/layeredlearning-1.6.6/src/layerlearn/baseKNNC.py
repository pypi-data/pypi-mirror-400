import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
import xgboost as XGBoost
import catboost as CatBoost
import lightgbm as LightGBM
from sklearn.model_selection import cross_val_predict

class KNNForestClassifier(BaseEstimator, ClassifierMixin):

    def __init__(self, base_model=None, meta_model=None, cv=5):
        self.base_model = base_model
        self.meta_model = meta_model
        self.cv = cv # Number of cross-validation folds

    def fit(self, X, y):
        # 1. Initialize defaults
        if self.base_model is None:
            self.base_model_ = KNeighborsClassifier(n_neighbors=5, weights='distance', algorithm='auto', leaf_size=30, p=2, metric='minkowski', n_jobs=-1)
        else:
            self.base_model_ = clone(self.base_model)
            
        if self.meta_model is None:
            self.meta_model_ = RandomForestClassifier(random_state=42, n_estimators=100, max_depth=10, min_samples_split=5, min_samples_leaf=2, bootstrap=True, n_jobs=-1)
        else:
            self.meta_model_ = clone(self.meta_model)

        # 2. Generate "out-of-sample" predictions for the meta model
        # We use cross_val_predict ensures that for every point in X, 
        # the prediction comes from a model that didn't see that point during training.
        base_predictions = cross_val_predict(self.base_model_, X, y, cv=self.cv)
        
        # 3. Stack features (Out-of-sample predictions + Original features)
        # Reshape base_predictions to be 2D (n_samples, 1)
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)
        X_meta = np.hstack((X, base_predictions))
        
        # 4. Train the Meta Model on these "honest" features
        self.meta_model_.fit(X_meta, y)
        
        # 5. Refit the Base Model on the FULL dataset 
        # (So it is ready for future .predict() calls on new data)
        self.base_model_.fit(X, y)
        
        return self

    def predict(self, X):
        if not hasattr(self, 'base_model_') or not hasattr(self, 'meta_model_'):
             raise RuntimeError("You must train the model before predicting!")

        # 1. Get base predictions (Normal predict, since we are now live)
        base_predictions = self.base_model_.predict(X)
        
        # Ensure 2D shape for concatenation
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)

        # 2. Stack features
        X_meta = np.hstack((X, base_predictions))
        
        # 3. Final prediction
        return self.meta_model_.predict(X_meta)
    
class KNNSupportClassifier(BaseEstimator, ClassifierMixin):

    def __init__(self, base_model=None, meta_model=None, cv=5):
        self.base_model = base_model
        self.meta_model = meta_model
        self.cv = cv # Number of cross-validation folds

    def fit(self, X, y):
        # 1. Initialize defaults
        if self.base_model is None:
            self.base_model_ = KNeighborsClassifier(n_neighbors=5, weights='distance', algorithm='auto', leaf_size=30, p=2, metric='minkowski', n_jobs=-1)
        else:
            self.base_model_ = clone(self.base_model)
            
        if self.meta_model is None:
            self.meta_model_ = SVC(kernel='rbf', gamma='scale', C=1.0, max_iter=-1, tol=1e-3, cache_size=200, verbose=False)
        else:
            self.meta_model_ = clone(self.meta_model)

        # 2. Generate "out-of-sample" predictions for the meta model
        # We use cross_val_predict ensures that for every point in X, 
        # the prediction comes from a model that didn't see that point during training.
        base_predictions = cross_val_predict(self.base_model_, X, y, cv=self.cv)
        
        # 3. Stack features (Out-of-sample predictions + Original features)
        # Reshape base_predictions to be 2D (n_samples, 1)
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)
        X_meta = np.hstack((X, base_predictions))
        
        # 4. Train the Meta Model on these "honest" features
        self.meta_model_.fit(X_meta, y)
        
        # 5. Refit the Base Model on the FULL dataset 
        # (So it is ready for future .predict() calls on new data)
        self.base_model_.fit(X, y)
        
        return self

    def predict(self, X):
        if not hasattr(self, 'base_model_') or not hasattr(self, 'meta_model_'):
             raise RuntimeError("You must train the model before predicting!")

        # 1. Get base predictions (Normal predict, since we are now live)
        base_predictions = self.base_model_.predict(X)
        
        # Ensure 2D shape for concatenation
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)

        # 2. Stack features
        X_meta = np.hstack((X, base_predictions))
        
        # 3. Final prediction
        return self.meta_model_.predict(X_meta)
    
class KNNDecisionClassifier(BaseEstimator, ClassifierMixin):

    def __init__(self, base_model=None, meta_model=None, cv=5):
        self.base_model = base_model
        self.meta_model = meta_model
        self.cv = cv # Number of cross-validation folds

    def fit(self, X, y):
        # 1. Initialize defaults
        if self.base_model is None:
            self.base_model_ = KNeighborsClassifier(n_neighbors=5, weights='distance', algorithm='auto', leaf_size=30, p=2, metric='minkowski', n_jobs=-1)
        else:
            self.base_model_ = clone(self.base_model)
            
        if self.meta_model is None:
            self.meta_model_ = DecisionTreeClassifier(random_state=42, max_depth=10, min_samples_split=5, min_samples_leaf=2, max_features='sqrt')
        else:
            self.meta_model_ = clone(self.meta_model)

        # 2. Generate "out-of-sample" predictions for the meta model
        # We use cross_val_predict ensures that for every point in X, 
        # the prediction comes from a model that didn't see that point during training.
        base_predictions = cross_val_predict(self.base_model_, X, y, cv=self.cv)
        
        # 3. Stack features (Out-of-sample predictions + Original features)
        # Reshape base_predictions to be 2D (n_samples, 1)
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)
        X_meta = np.hstack((X, base_predictions))
        
        # 4. Train the Meta Model on these "honest" features
        self.meta_model_.fit(X_meta, y)
        
        # 5. Refit the Base Model on the FULL dataset 
        # (So it is ready for future .predict() calls on new data)
        self.base_model_.fit(X, y)
        
        return self

    def predict(self, X):
        if not hasattr(self, 'base_model_') or not hasattr(self, 'meta_model_'):
             raise RuntimeError("You must train the model before predicting!")

        # 1. Get base predictions (Normal predict, since we are now live)
        base_predictions = self.base_model_.predict(X)
        
        # Ensure 2D shape for concatenation
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)

        # 2. Stack features
        X_meta = np.hstack((X, base_predictions))
        
        # 3. Final prediction
        return self.meta_model_.predict(X_meta)
    
class KNNLogisticClassifier(BaseEstimator, ClassifierMixin):

    def __init__(self, base_model=None, meta_model=None, cv=5):
        self.base_model = base_model
        self.meta_model = meta_model
        self.cv = cv # Number of cross-validation folds

    def fit(self, X, y):
        # 1. Initialize defaults
        if self.base_model is None:
            self.base_model_ = KNeighborsClassifier(n_neighbors=5, weights='distance', algorithm='auto', leaf_size=30, p=2, metric='minkowski', n_jobs=-1)
        else:
            self.base_model_ = clone(self.base_model)

        if self.meta_model is None:
            self.meta_model_ = LogisticRegression(n_jobs=-1, fit_intercept=True)
        else:
            self.meta_model_ = clone(self.meta_model)

        # 2. Generate "out-of-sample" predictions for the meta model
        # We use cross_val_predict ensures that for every point in X,
        # the prediction comes from a model that didn't see that point during training.
        base_predictions = cross_val_predict(self.base_model_, X, y, cv=self.cv)

        # 3. Stack features (Out-of-sample predictions + Original features)
        # Reshape base_predictions to be 2D (n_samples, 1)
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)
        
        X_meta = np.hstack((X, base_predictions))
        # 4. Train the Meta Model on these "honest" features
        self.meta_model_.fit(X_meta, y)
        # 5. Refit the Base Model on the FULL dataset
        # (So it is ready for future .predict() calls on new data)
        self.base_model_.fit(X, y)
        return self
    def predict(self, X):
        # 1. Get predictions from the base model
        base_predictions = self.base_model_.predict(X)

        # 2. Stack features (Original features + Base predictions)
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)
        X_meta = np.hstack((X, base_predictions))

        # 3. Get predictions from the meta model
        return self.meta_model_.predict(X_meta)
            
class KNNXGBClassifier(BaseEstimator, ClassifierMixin):

    def __init__(self, base_model=None, meta_model=None, cv=5):
        self.base_model = base_model
        self.meta_model = meta_model
        self.cv = cv # Number of cross-validation folds

    def fit(self, X, y):
        # 1. Initialize defaults
        if self.base_model is None:
            self.base_model_ = KNeighborsClassifier(n_neighbors=5, weights='distance', algorithm='auto', leaf_size=30, p=2, metric='minkowski', n_jobs=-1)
        else:
            self.base_model_ = clone(self.base_model)

        if self.meta_model is None:
            self.meta_model_ = XGBoost.XGBClassifier()
        else:
            self.meta_model_ = clone(self.meta_model)

        # 2. Generate "out-of-sample" predictions for the meta model
        # We use cross_val_predict ensures that for every point in X,
        # the prediction comes from a model that didn't see that point during training.
        base_predictions = cross_val_predict(self.base_model_, X, y, cv=self.cv)

        # 3. Stack features (Out-of-sample predictions + Original features)
        # Reshape base_predictions to be 2D (n_samples, 1)
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)
        X_meta = np.hstack((X, base_predictions))

        # 4. Train the Meta Model on these "honest" features
        self.meta_model_.fit(X_meta, y)

        # 5. Refit the Base Model on the FULL dataset 
        # (So it is ready for future .predict() calls on new data)
        self.base_model_.fit(X, y)

        return self

    def predict(self, X):
        # 1. Get predictions from the base model
        base_predictions = self.base_model_.predict(X)

        # 2. Stack features (Original features + Base predictions)
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)
        X_meta = np.hstack((X, base_predictions))

        # 3. Get predictions from the meta model
        return self.meta_model_.predict(X_meta).reshape(-1, 1)
    
    def predict(self, X):
        if not hasattr(self, 'base_model_') or not hasattr(self, 'meta_model_'):
             raise RuntimeError("You must train the model before predicting!")

        # 1. Get base predictions (Normal predict, since we are now live)
        base_predictions = self.base_model_.predict(X)
        
        # Ensure 2D shape for concatenation
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)

        # 2. Stack features
        X_meta = np.hstack((X, base_predictions))
        
        # 3. Final prediction
        return self.meta_model_.predict(X_meta)
    
class KNNCatClassifier(BaseEstimator, ClassifierMixin):

    def __init__(self, base_model=None, meta_model=None, cv=5):
        self.base_model = base_model
        self.meta_model = meta_model
        self.cv = cv # Number of cross-validation folds

    def fit(self, X, y):
        # 1. Initialize defaults
        if self.base_model is None:
            self.base_model_ = KNeighborsClassifier(n_neighbors=5, weights='distance', algorithm='auto', leaf_size=30, p=2, metric='minkowski', n_jobs=-1)
        else:
            self.base_model_ = clone(self.base_model)

        if self.meta_model is None:
            self.meta_model_ = CatBoost.CatBoostClassifier(verbose=0, random_state=42, iterations=1000, learning_rate=0.1, depth=10, l2_leaf_reg=3, bagging_temperature=1)
        else:
            self.meta_model_ = clone(self.meta_model)

        # 2. Generate "out-of-sample" predictions for the meta model
        # We use cross_val_predict ensures that for every point in X,
        # the prediction comes from a model that didn't see that point during training.
        base_predictions = cross_val_predict(self.base_model_, X, y, cv=self.cv)

        # 3. Stack features (Out-of-sample predictions + Original features)
        # Reshape base_predictions to be 2D (n_samples, 1)
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)
        X_meta = np.hstack((X, base_predictions))

        # 4. Train the Meta Model on these "honest" features
        self.meta_model_.fit(X_meta, y)

        # 5. Refit the Base Model on the FULL dataset 
        # (So it is ready for future .predict() calls on new data)
        self.base_model_.fit(X, y)

        return self
    
    def predict(self, X):
        if not hasattr(self, 'base_model_') or not hasattr(self, 'meta_model_'):
             raise RuntimeError("You must train the model before predicting!")

        # 1. Get base predictions (Normal predict, since we are now live)
        base_predictions = self.base_model_.predict(X)

        # Ensure 2D shape for concatenation
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)

        # 2. Stack features
        X_meta = np.hstack((X, base_predictions))

        # 3. Final prediction
        return self.meta_model_.predict(X_meta)

class KNNGradientClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, base_model=None, meta_model=None, cv=5):
        self.base_model = base_model
        self.meta_model = meta_model
        self.cv = cv # Number of cross-validation folds

    def fit(self, X, y):
        # 1. Initialize defaults
        if self.base_model is None:
            self.base_model_ = KNeighborsClassifier(n_neighbors=5, weights='distance', algorithm='auto', leaf_size=30, p=2, metric='minkowski', n_jobs=-1)
        else:
            self.base_model_ = clone(self.base_model)

        if self.meta_model is None:
            self.meta_model_ = GradientBoostingClassifier(n_estimators=100, random_state=42, learning_rate=0.1, max_depth=10, min_samples_split=5, min_samples_leaf=2)
        else:
            self.meta_model_ = clone(self.meta_model)

        # 2. Generate "out-of-sample" predictions for the meta model
        # We use cross_val_predict ensures that for every point in X,
        # the prediction comes from a model that didn't see that point during training.
        base_predictions = cross_val_predict(self.base_model_, X, y, cv=self.cv)

        # 3. Stack features (Out-of-sample predictions + Original features)
        # Reshape base_predictions to be 2D (n_samples, 1)
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)
        X_meta = np.hstack((X, base_predictions))

        # 4. Train the Meta Model on these "honest" features
        self.meta_model_.fit(X_meta, y)

        # 5. Refit the Base Model on the FULL dataset 
        # (So it is ready for future .predict() calls on new data)
        self.base_model_.fit(X, y)

        return self 

    def predict(self, X):
        if not hasattr(self, 'base_model_') or not hasattr(self, 'meta_model_'):
             raise RuntimeError("You must train the model before predicting!")

        # 1. Get base predictions (Normal predict, since we are now live)
        base_predictions = self.base_model_.predict(X)

        # Ensure 2D shape for concatenation
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)

        # 2. Stack features
        X_meta = np.hstack((X, base_predictions))

        # 3. Final prediction
        return self.meta_model_.predict(X_meta)
    
class KNNAdaClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, base_model=None, meta_model=None, cv=5):
        self.base_model = base_model
        self.meta_model = meta_model
        self.cv = cv # Number of cross-validation folds

    def fit(self, X, y):
        # 1. Initialize defaults
        if self.base_model is None:
            self.base_model_ = KNeighborsClassifier(n_neighbors=5, weights='distance', algorithm='auto', leaf_size=30, p=2, metric='minkowski', n_jobs=-1)
        else:
            self.base_model_ = clone(self.base_model)

        if self.meta_model is None:
            self.meta_model_ = AdaBoostClassifier(n_estimators=100, random_state=42, learning_rate=0.1, loss='linear')
        else:
            self.meta_model_ = clone(self.meta_model)

        # 2. Generate "out-of-sample" predictions for the meta model
        # We use cross_val_predict ensures that for every point in X,
        # the prediction comes from a model that didn't see that point during training.
        base_predictions = cross_val_predict(self.base_model_, X, y, cv=self.cv)

        # 3. Stack features (Out-of-sample predictions + Original features)
        # Reshape base_predictions to be 2D (n_samples, 1)
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)
        X_meta = np.hstack((X, base_predictions))

        # 4. Train the Meta Model on these "honest" features
        self.meta_model_.fit(X_meta, y)

        # 5. Refit the Base Model on the FULL dataset 
        # (So it is ready for future .predict() calls on new data)
        self.base_model_.fit(X, y)

        return self 

    def predict(self, X):
        if not hasattr(self, 'base_model_') or not hasattr(self, 'meta_model_'):
             raise RuntimeError("You must train the model before predicting!")

        # 1. Get base predictions (Normal predict, since we are now live)
        base_predictions = self.base_model_.predict(X)

        # Ensure 2D shape for concatenation
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)

        # 2. Stack features
        X_meta = np.hstack((X, base_predictions))

        # 3. Final prediction
        return self.meta_model_.predict(X_meta)
    
class KNNLightClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, base_model=None, meta_model=None, cv=5):
        self.base_model = base_model
        self.meta_model = meta_model
        self.cv = cv # Number of cross-validation folds

    def fit(self, X, y):
        # 1. Initialize defaults
        if self.base_model is None:
            self.base_model_ = KNeighborsClassifier(n_neighbors=5, weights='distance', algorithm='auto', leaf_size=30, p=2, metric='minkowski', n_jobs=-1)
        else:
            self.base_model_ = clone(self.base_model)

        if self.meta_model is None:
            self.meta_model_ = LightGBM.LGBMClassifier(random_state=42, n_estimators=100, learning_rate=0.1, max_depth=10, num_leaves=31, subsample=0.8)
        else:
            self.meta_model_ = clone(self.meta_model)

        # 2. Generate "out-of-sample" predictions for the meta model
        # We use cross_val_predict ensures that for every point in X,
        # the prediction comes from a model that didn't see that point during training.
        base_predictions = cross_val_predict(self.base_model_, X, y, cv=self.cv)

        # 3. Stack features (Out-of-sample predictions + Original features)
        # Reshape base_predictions to be 2D (n_samples, 1)
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)
        X_meta = np.hstack((X, base_predictions))

        # 4. Train the Meta Model on these "honest" features
        self.meta_model_.fit(X_meta, y)

        # 5. Refit the Base Model on the FULL dataset 
        # (So it is ready for future .predict() calls on new data)
        self.base_model_.fit(X, y)

        return self 

    def predict(self, X):
        if not hasattr(self, 'base_model_') or not hasattr(self, 'meta_model_'):
             raise RuntimeError("You must train the model before predicting!")

        # 1. Get base predictions (Normal predict, since we are now live)
        base_predictions = self.base_model_.predict(X)

        # Ensure 2D shape for concatenation
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)

        # 2. Stack features
        X_meta = np.hstack((X, base_predictions))

        # 3. Final prediction
        return self.meta_model_.predict(X_meta)