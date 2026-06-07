import pickle

# Load model
model = pickle.load(open("model.pkl", "rb"))
symptom_index = pickle.load(open("symptom_index.pkl", "rb"))

# User symptoms
user_symptoms = [
    "itching",
    "skin_rash"
]

# Create feature vector
input_vector = [0] * len(symptom_index)

for symptom in user_symptoms:
    if symptom in symptom_index:
        input_vector[symptom_index[symptom]] = 1

# Predict
prediction = model.predict([input_vector])

print("Predicted Disease:")
print(prediction[0])