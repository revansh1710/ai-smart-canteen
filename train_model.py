import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

# Sample training data: meal popularity per day
data = pd.DataFrame({
    "day": [1, 2, 3, 4, 5, 6, 7],
    "meal_orders": [100, 120, 90, 150, 130, 80, 70]
})

X = data[["day"]]
y = data["meal_orders"]

model = LinearRegression()
model.fit(X, y)

joblib.dump(model, "meal_model.pkl")
print("✅ Model trained and saved as meal_model.pkl")
