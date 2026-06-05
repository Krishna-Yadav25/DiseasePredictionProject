import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle

# Load dataset
df = pd.read_csv("dataset.csv")
df.fillna("None", inplace=True)

# Collect all symptoms
symptoms = set()

for col in df.columns[1:]:
    symptoms.update(df[col].unique())

symptoms.discard("None")
symptoms = sorted(list(symptoms))

# Symptom mapping
symptom_index = {
    symptom: idx
    for idx, symptom in enumerate(symptoms)
}

# Create features and labels
X = []
y = []

for _, row in df.iterrows():

    feature_vector = [0] * len(symptoms)

    for symptom in row[1:]:

        if symptom != "None":
            feature_vector[symptom_index[symptom]] = 1

    X.append(feature_vector)
    y.append(row["Disease"])

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Train model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# Prediction
y_pred = model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, y_pred)

print("Accuracy:", accuracy * 100)

# Save model
pickle.dump(model, open("model.pkl", "wb"))

# Save symptom index
pickle.dump(symptom_index, open("symptom_index.pkl", "wb"))

print("Model Saved Successfully!")