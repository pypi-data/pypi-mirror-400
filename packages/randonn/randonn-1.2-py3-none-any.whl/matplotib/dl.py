# dl.py

def dl_help():
    print(
        '''
    Welcome to the Deep Learning Practicals CLI! 🧠

    This tool allows you to print the code for various deep learning practicals.
    Run any command from your terminal or call its function in Python.

    =========================
    == General Commands    ==
    =========================
    
    Command: dl-help
    Function: dl_help()
    Description: Shows this help message.

    Command: dl-index
    Function: dl_index()
    Description: Displays the full list of deep learning practicals.

    =========================
    == Practical Commands  ==
    =========================

    --- Practical 1: TensorFlow Fundamentals ---
    dl-prac-1a      (dl_prac_1a)
    dl-prac-1b      (dl_prac_1b)

    --- Practical 2: Linear Regression ---
    dl-prac-2       (dl_prac_2)

    --- Practical 3: CNN Classification ---
    dl-prac-3       (dl_prac_3)

    --- Practical 4: Multi-class Classification ---
    dl-prac-4       (dl_prac_4)
        '''
    )

def dl_index():
    print(
        '''
Deep Learning Practicals:

1.  TensorFlow Fundamentals
    A. Tensor Operations and Basic TensorFlow
    B. XOR Problem with Deep Neural Network

2.  Linear Regression
    Implement linear regression using TensorFlow/Keras

3.  CNN Classification
    Binary classification using Convolutional Neural Networks

4.  Multi-class Classification
    Iris dataset classification with neural networks
        '''
    )

def dl_prac_1a():
    print(
        '''
# Tensor Operations and Basic TensorFlow

import tensorflow as tf

# a. Create tensors with different shapes and data types
# Scalar
scalar = tf.constant(10)
print("Scalar:", scalar)

# Vector
vector = tf.constant([1, 2, 3], dtype=tf.int32)
print("Vector:", vector)

# Matrix
matrix = tf.constant([[1, 2], [3, 4]], dtype=tf.float32)
print("Matrix:\\n", matrix)

# 3D Tensor
tensor_3d = tf.constant([
    [[1, 2], [3, 4]],
    [[5, 6], [7, 8]]
], dtype=tf.float64)
print("3D Tensor:\\n", tensor_3d)

# b. Basic operations on tensors
a = tf.constant([10, 20, 30])
b = tf.constant([1, 2, 3])

print("Addition:", tf.add(a, b))
print("Subtraction:", tf.subtract(a, b))
print("Multiplication:", tf.multiply(a, b))
print("Division:", tf.divide(a, b))

# c. Reshape, slice, and index tensors
tensor = tf.constant([1, 2, 3, 4, 5, 6])

# Reshape
reshaped = tf.reshape(tensor, (2, 3))
print("Reshaped Tensor:\\n", reshaped)

# Indexing
print("Element at index 2:", tensor[2])

# Slicing
print("Slice (index 1 to 4):", tensor[1:5])

# d. Matrix multiplication and Eigenvalues/Eigenvectors
# Matrix multiplication
mat1 = tf.constant([[1, 2], [3, 4]], dtype=tf.float32)
mat2 = tf.constant([[5, 6], [7, 8]], dtype=tf.float32)

matmul_result = tf.matmul(mat1, mat2)
print("Matrix Multiplication Result:\\n", matmul_result)

# Eigenvalues and Eigenvectors
square_matrix = tf.constant([[4, -2], [1, 1]], dtype=tf.float32)

eigenvalues, eigenvectors = tf.linalg.eig(square_matrix)

print("Eigenvalues:\\n", eigenvalues)
print("Eigenvectors:\\n", eigenvectors)
        '''
    )

def dl_prac_1b():
    print(
        '''
# XOR Problem with Deep Neural Network

import numpy as np 
from tensorflow.keras import layers, models
from tensorflow.keras.optimizers import Adam 

# XOR dataset 
X = np.array([[0,0],[0,1],[1,0],[1,1]], dtype=np.float32) 
y = np.array([[0],[1],[1],[0]], dtype=np.float32) 

# Optimized deep forward network 
model = models.Sequential([ 
    layers.Dense(8, input_dim=2, activation='relu'),   #Hidden Layer 1 
    layers.Dense(8, activation='relu'),                #Hidden Layer 2 
    layers.Dense(1, activation='sigmoid')              #Output layer 
]) 

# Compile model  
model.compile(optimizer=Adam(learning_rate=0.01), loss='binary_crossentropy', metrics=['accuracy']) 

# Train the model 
model.fit(X, y, epochs=500, verbose=1) 

# Evaluate 
loss, accuracy = model.evaluate(X, y) 
print(f"Accuracy: {accuracy*100:.2f}%") 

# Predictions 
predictions = model.predict(X) 
print("Predictions:\\n", np.round(predictions).astype(int))
        '''
    )

def dl_prac_2():
    print(
        '''
# Linear Regression using TensorFlow/Keras

import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras import models, layers
from tensorflow.keras.optimizers import Adam

# Data
X = np.array([5, 7, 9, 11, 13, 15], dtype=np.float32)
y = np.array([15, 21, 27, 33, 39, 45], dtype=np.float32)

# Model
model = models.Sequential([
    layers.Dense(1, input_shape=(1,))
])

model.compile(optimizer=Adam(0.01), loss="mse")

# Train
history = model.fit(X, y, epochs=300, verbose=0)

# Loss curve
plt.plot(history.history["loss"])
plt.xlabel("Epochs")
plt.ylabel("Loss")
plt.title("Training Loss")
plt.show()

# Regression line
pred = model.predict(X)

plt.scatter(X, y, label="Actual")
plt.plot(X, pred, color="red", label="Prediction")
plt.xlabel("Square Footage (100 sq.ft)")
plt.ylabel("Price (Lakhs)")
plt.legend()
plt.show()

# Predictions
new_X = np.array([8, 12, 16], dtype=np.float32)
new_pred = model.predict(new_X)

for x, p in zip(new_X, new_pred):
    print(f"{x*100:.0f} sq.ft → {p[0]:.2f} Lakhs")
        '''
    )

def dl_prac_3():
    print(
        '''
# Binary Classification using CNN

import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras import models, layers
from tensorflow.keras.datasets import cifar10

# Load data
(X_train, y_train), (X_test, y_test) = cifar10.load_data()

# Binary labels: Vehicle=0, Animal=1
vehicles = [0, 1, 8, 9]
y_train = np.array([0 if y in vehicles else 1 for y in y_train])
y_test  = np.array([0 if y in vehicles else 1 for y in y_test])

# Normalize images
X_train, X_test = X_train / 255.0, X_test / 255.0

# Model
model = models.Sequential([
    layers.Conv2D(32, 3, activation="relu", input_shape=(32,32,3)),
    layers.MaxPooling2D(),
    layers.Conv2D(64, 3, activation="relu"),
    layers.MaxPooling2D(),
    layers.Flatten(),
    layers.Dense(128, activation="relu"),
    layers.Dense(1, activation="sigmoid")
])

model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

# Train
model.fit(X_train, y_train, epochs=10, batch_size=64, validation_split=0.2)

# Evaluate
loss, acc = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {acc*100:.2f}%")

# Predictions
labels = ["Vehicle", "Animal"]
pred = (model.predict(X_test[:5]) > 0.5).astype(int)

plt.figure(figsize=(10,4))
for i in range(5):
    plt.subplot(1,5,i+1)
    plt.imshow(X_test[i])
    plt.title(labels[pred[i][0]])
    plt.axis("off")
plt.show()
        '''
    )

def dl_prac_4():
    print(
        '''
# Multi-class Classification with Iris Dataset

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from tensorflow.keras import models, layers

# Load data
iris = load_iris()
X, y = iris.data, iris.target

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

# Model
model = models.Sequential([
    layers.Dense(16, activation="relu", input_shape=(4,)),
    layers.Dense(16, activation="relu"),
    layers.Dense(3, activation="softmax")
])

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

# Train
model.fit(X_train, y_train, epochs=100, verbose=0)

# Evaluate
loss, acc = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {acc*100:.2f}%")

# Predict 
sample = np.array([[5.1, 3.5, 1.4, 0.2]])
probs = model.predict(sample)[0]

pred_class = np.argmax(probs)
print("Predicted Class:", iris.target_names[pred_class])

# Visualization
plt.bar(iris.target_names, probs)
plt.ylabel("Probability")
plt.title("Prediction Probabilities")
plt.ylim(0, 1)
plt.show()
        '''
    )