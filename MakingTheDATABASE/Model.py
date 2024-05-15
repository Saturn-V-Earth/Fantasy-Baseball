from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, GridSearchCV
import xgboost as xgb
import pandas as pd

# Step 1: Prepare the data
data = pd.read_csv("baseball_game_data.csv")  # Load your data into a pandas DataFrame

# Step 2: Encode the target variable using Label Encoding
label_encoder = LabelEncoder()
data['At_Bat_Outcome_encoded'] = label_encoder.fit_transform(data['At_Bat_Outcome'])

# Features and target variable
X = data[['Inning', 'Batter_Avg', 'strike_percentage']]  # Features
y = data['At_Bat_Outcome_encoded']  # Encoded target variable

# Step 3: Train-Test Split (Optional for evaluation)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 4: Hyperparameter Tuning for XGBoost
# Define the parameters grid for hyperparameter tuning
params = {
    'learning_rate': [0.01, 0.1, 0.3],
    'max_depth': [3, 5, 7],
    'min_child_weight': [1, 3, 5],
    'subsample': [0.6, 0.8, 1.0],
    'colsample_bytree': [0.6, 0.8, 1.0],
    'n_estimators': [500, 1000, 1500]
}

grid_search = GridSearchCV(estimator=xgb.XGBClassifier(),
                           param_grid=params,
                           scoring='accuracy',
                           cv=5,
                           n_jobs=-1)

grid_search.fit(X_train, y_train)
best_params = grid_search.best_params_
best_model = grid_search.best_estimator_

# Step 5: Evaluate the XGBoost Model
y_pred = best_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print("Best XGBoost Accuracy: ", accuracy)


# Step 8: Function to predict outcome for a custom situation
def predict_outcome(inning, batter_avg, strike_percentage):
    # Create a DataFrame with the custom situation
    custom_data = pd.DataFrame({'Inning': [inning],
                                'Batter_Avg': [batter_avg],
                                'strike_percentage': [strike_percentage]})
    
    # Make predictions using the best model
    prediction = best_model.predict(custom_data)
    outcome = label_encoder.inverse_transform(prediction)[0]
    return outcome

# Example usage
print(predict_outcome(8, 0.300, 0.500))