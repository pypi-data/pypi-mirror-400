#AAI

def aai_setup():
    print(
        '''
    conda create -n tf-env python=3.10
    conda activate tf-env
    pip install tensorflow spyder
    spyder
        '''
    )

def aai_help():
    print(
        '''
    Welcome to the AAI Practicals CLI! 🧠

    This tool allows you to print the code for various AAI practicals.
    Run any command from your terminal or call its function in Python.

    =========================
    == General Commands    ==
    =========================
    
    Command: aai-help
    Function: aai_help()
    Description: Shows this help message.
    
    Command: aai-setup
    Function: aai_setup()
    Description: Shows the setup commands

    Command: aai-index
    Function: aai_index()
    Description: Displays the full list of AAI practicals.

    =========================
    == Practical Commands  ==
    =========================

    --- Practical 1: Deep Learning Algorithms ---
    aai-prac-1a      (aai_prac_1a)
    aai-prac-1b      (aai_prac_1b)
    aai-prac-1c      (aai_prac_1c)

    --- Practical 2: Natural Language Processing ---
    aai-prac-2a      (aai_prac_2a)
    aai-prac-2b      (aai_prac_2b)

    --- Practical 3: Chatbots ---
    aai-prac-3a      (aai_prac_3a)
    
    --- Practical 4: Recommendation Systems ---
    aai-prac-4a      (aai_prac_4a)

    --- Practical 5: Generative Models ---
    aai-prac-5a      (aai_prac_5a)

    --- Practical 6: Transfer Learning ---
    aai-prac-6a      (aai_prac_6a)

    --- Practical 7: Time Series Analysis ---
    aai-prac-7a      (aai_prac_7a)

    --- Practical 8: Hyperparameter Tuning ---
    aai-prac-8a      (aai_prac_8a)
        '''
    )

def aai_index():
    print(
        '''
Advanced Artificial Intelligence (AAI) Practicals:

1.  Advanced Deep Learning Algorithms
    A. Implement CNN using TensorFlow.
    B. Implement RNN.
    C. Implement CNN using PyTorch.

2.  Natural Language Processing (NLP)
    A. Build an NLP model for sentiment analysis.
    B. Build an NLP model for text classification.

3.  Chatbots
    A. Create a chatbot using advanced techniques like transformer models.

4.  Recommendation Systems
    A. Develop a recommendation system using collaborative filtering.

5.  Generative Models
    A. Train a GAN for generating realistic images.

6.  Transfer Learning
    A. Utilizing transfer learning to improve model performance on limited datasets.

7.  Time Series Analysis
    A. Building a deep learning model for time series forecasting or anomaly detection.

8.  Hyperparameter Tuning
    A. Using advanced optimization techniques like evolutionary algorithms or Bayesian optimization for hyperparameter tuning.
        '''
    )

def aai_prac_1a():
    print(
        '''
import tensorflow as tf
from tensorflow.keras import layers, models
import matplotlib.pyplot as plt
import numpy as np

(x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()

x_train, x_test = x_train / 255.0, x_test / 255.0

class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

plt.figure(figsize=(10,10))
for i in range(25):
    plt.subplot(5, 5, i + 1)
    plt.xticks([])
    plt.yticks([])
    plt.grid(False)
    plt.imshow(x_train[i])
    plt.xlabel(class_names[y_train[i][0]])
plt.show()

model = models.Sequential([
    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(32, 32, 3)),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dense(10, activation='softmax')
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

model.fit(x_train, y_train, epochs=8, batch_size=64, validation_split=0.2)

test_loss, test_acc = model.evaluate(x_test, y_test)
print(f"Test accuracy: {test_acc:.4f}")

img = x_test[2]
img_batch = np.expand_dims(img, axis=0)
pred_probs = model.predict(img_batch)
predicted_class = np.argmax(pred_probs)

plt.imshow(img)
plt.title(f"Predicted: {class_names[predicted_class]}")
plt.axis('off')
plt.show()
        '''
    )

def aai_prac_1b():
    print(
        '''
import torch
import torch.nn as nn
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader, TensorDataset
from collections import Counter
import re

reviews = [
    "I loved the movie, it was fantastic!",
    "Absolutely terrible, worst film ever.",
    "Great acting and wonderful story.",
    "The movie was boring and too long.",
    "An excellent and emotional performance.",
    "I hated it, very disappointing."
]
labels = [1, 0, 1, 0, 1, 0]

def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^\\w\\s]", "", text)
    return text.split()

tokenized_reviews = [preprocess(review) for review in reviews]

all_words = [word for review in tokenized_reviews for word in review]
word_counts = Counter(all_words)
vocab = {word: i + 1 for i, (word, _) in enumerate(word_counts.most_common())}
vocab['<PAD>'] = 0
vocab['<UNK>'] = len(vocab)

encoded_reviews = [[vocab.get(word, vocab['<UNK>']) for word in review] for review in tokenized_reviews]

padded_reviews = pad_sequence([torch.tensor(seq) for seq in encoded_reviews], batch_first=True)

labels_tensor = torch.tensor(labels)
dataset = TensorDataset(padded_reviews, labels_tensor)
dataloader = DataLoader(dataset, batch_size=2, shuffle=True)

class ReviewRNN(nn.Module):
    def __init__(self, vocab_size, embed_size, hidden_size, num_classes):
        super(ReviewRNN, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_size, padding_idx=0)
        self.rnn = nn.RNN(embed_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        x = self.embedding(x)
        output, _ = self.rnn(x)
        out = self.fc(output[:, -1, :])
        return out

vocab_size = len(vocab)
embed_size = 32
hidden_size = 64
num_classes = 2

model = ReviewRNN(vocab_size, embed_size, hidden_size, num_classes)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

num_epochs = 8
for epoch in range(num_epochs):
    for batch_x, batch_y in dataloader:
        outputs = model(batch_x)
        loss = criterion(outputs, batch_y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    print(f"Epoch [{epoch + 1}/{num_epochs}], Loss: {loss.item():.4f}")

def predict_sentiment(text):
    model.eval()
    with torch.no_grad():
        tokens = preprocess(text)
        encoded = [vocab.get(word, vocab['<UNK>']) for word in tokens]
        tensor = torch.tensor(encoded).unsqueeze(0)
        tensor = pad_sequence([tensor.squeeze()], batch_first=True, padding_value=vocab['<PAD>'])
        output = model(tensor)
        pred = torch.argmax(output, dim=1).item()
        return "Positive" if pred == 1 else "Negative"

print(predict_sentiment("I really enjoyed the movie"))
print(predict_sentiment("It was the worst movie ever"))
print(predict_sentiment("An excellent and emotional performance."))
print(predict_sentiment("Amazing movie!."))
        '''
    )

def aai_prac_1c():
    print(
        '''
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt

# --- Load Data ---
transform = transforms.ToTensor()
trainset = torchvision.datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
testset = torchvision.datasets.CIFAR10(root='./data', train=False, download=True, transform=transform)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=64, shuffle=True)
testloader = torch.utils.data.DataLoader(testset, batch_size=64, shuffle=False)
classes = ['plane','car','bird','cat','deer','dog','frog','horse','ship','truck']

# --- Build Model Sequentially (No class) ---
model = nn.Sequential(
    nn.Conv2d(3, 16, 3, padding=1),
    nn.ReLU(),
    nn.MaxPool2d(2, 2),
    nn.Flatten(),
    nn.Linear(16 * 16 * 16, 10)
)

# --- Setup Training ---
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# --- Training Loop ---
for epoch in range(3):
    for images, labels in trainloader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        loss = criterion(model(images), labels)
        loss.backward()
        optimizer.step()
    print(f"Epoch {epoch+1} completed")

# --- Evaluation ---
correct, total = 0, 0
with torch.no_grad():
    for images, labels in testloader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        _, preds = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (preds == labels).sum().item()
print(f"Accuracy: {100 * correct / total:.2f}%")

# --- Show One Prediction ---
images, labels = next(iter(testloader))
with torch.no_grad():
    output = model(images[0].unsqueeze(0).to(device))
pred = torch.argmax(output, 1).item()

plt.imshow(images[0].permute(1, 2, 0))
plt.title(f"Predicted: {classes[pred]}, Actual: {classes[labels[0]]}")
plt.axis("off")
plt.show()
        '''
    )

def aai_prac_2a():
    print(
        '''
import tensorflow as tf
from tensorflow.keras.datasets import imdb
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense

num_words = 10000
max_len = 200
(x_train, y_train), (x_test, y_test) = imdb.load_data(num_words=num_words)
x_train = pad_sequences(x_train, maxlen=max_len)
x_test = pad_sequences(x_test, maxlen=max_len)

model = Sequential([
    Embedding(num_words, 128, input_length=max_len),
    LSTM(64, dropout=0.2, recurrent_dropout=0.2),
    Dense(1, activation='sigmoid')
])

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

model.fit(x_train, y_train, epochs=3, batch_size=64, validation_split=0.2)
print("Test Accuracy:", model.evaluate(x_test, y_test, verbose=0)[1])

word_index = imdb.get_word_index()
word_index = {k: (v + 3) for k, v in word_index.items()}
word_index.update({"<PAD>": 0, "<START>": 1, "<UNK>": 2})
reverse_word_index = {v: k for k, v in word_index.items()}

def encode_review(text):
    return pad_sequences([[1] + [word_index.get(w, 2) for w in text.lower().split()]], maxlen=max_len)

def predict(text):
    score = model.predict(encode_review(text), verbose=0)[0][0]
    print(f"'{text}' → {'Positive' if score > 0.5 else 'Negative'} ({score:.2f})")

predict("The movie was fantastic and full of surprises")
predict("I hated this movie, it was a waste of time")
        '''
    )

def aai_prac_2b():
    print(
        '''
import re
import numpy as np
from sklearn.datasets import fetch_20newsgroups
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping

categories = ["sci.space", "comp.graphics", "rec.sport.hockey", "talk.politics.mideast"]
newsgroups = fetch_20newsgroups(
    subset="all",
    categories=categories,
    remove=("headers", "footers", "quotes")
)
texts, labels = newsgroups.data, newsgroups.target
class_names = newsgroups.target_names
print("Classes:", class_names)

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z\\s]", " ", text)
    text = re.sub(r"\\s+", " ", text)
    return text.strip()

texts = [clean_text(t) for t in texts]

max_words = 10000
max_len = 200
tokenizer = Tokenizer(num_words=max_words, oov_token="<OOV>")
tokenizer.fit_on_texts(texts)
sequences = tokenizer.texts_to_sequences(texts)

X = pad_sequences(sequences, maxlen=max_len)

encoder = LabelEncoder()
y = encoder.fit_transform(labels)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = Sequential([
    Input(shape=(max_len,)),
    Embedding(input_dim=max_words, output_dim=128),
    LSTM(128, dropout=0.2, recurrent_dropout=0.2),
    Dense(64, activation="relu"),
    Dropout(0.5),
    Dense(len(class_names), activation="softmax")
])

model.compile(loss="sparse_categorical_crossentropy", optimizer="adam", metrics=["accuracy"])

early_stop = EarlyStopping(monitor="val_loss", patience=2, restore_best_weights=True)
model.fit(X_train, y_train, epochs=5, batch_size=64, validation_split=0.2, callbacks=[early_stop])

loss, acc = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {acc:.4f}")
        '''
    )

def aai_prac_3a():
    print(
        '''
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

model_name = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

model.eval()

def generate_response(prompt, max_length=50):
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    
    with torch.no_grad():
        output = model.generate(input_ids, max_length=max_length, num_return_sequences=1, pad_token_id=50256)
        
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    return response

print("Chatbot: Hi there! How can I help you? (Type 'exit' to quit)")

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Chatbot: Goodbye!")
        break
    response = generate_response(user_input)
    print("Chatbot:", response)
        '''
    )

def aai_prac_4a():
    print(
        '''
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

data = [
    (0, 0, 5.0), (0, 1, 3.0), (1, 0, 4.0),
    (1, 2, 2.0), (2, 1, 4.0), (2, 2, 5.0)
]
n_users = 3
n_items = 3

users = torch.tensor([d[0] for d in data])
items = torch.tensor([d[1] for d in data])
ratings = torch.tensor([d[2] for d in data])

class MF(nn.Module):
    def __init__(self, n_users, n_items, n_factors=8):
        super(MF, self).__init__()
        self.user_emb = nn.Embedding(n_users, n_factors)
        self.item_emb = nn.Embedding(n_items, n_factors)

    def forward(self, user, item):
        u = self.user_emb(user)
        v = self.item_emb(item)
        return (u * v).sum(1)

model = MF(n_users, n_items)
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

for epoch in range(50):
    optimizer.zero_grad()
    preds = model(users, items)
    loss = criterion(preds, ratings)
    loss.backward()
    optimizer.step()
    if (epoch + 1) % 10 == 0:
        print(f"Epoch {epoch + 1}, Loss: {loss.item():.4f}")

print("Predicted rating (user 0, item 2):", model(torch.tensor([0]), torch.tensor([2])).item())
        '''
    )

def aai_prac_5a():
    print(
        '''
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
from torchvision import datasets, transforms
import matplotlib.pyplot as plt

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])
train_dataset = datasets.MNIST(root="./data", train=True, download=True, transform=transform)
dataloader = torch.utils.data.DataLoader(train_dataset, batch_size=64, shuffle=True)

latent_dim = 64
lr = 0.0002
epochs = 30

class Generator(nn.Module):
    def __init__(self, latent_dim):
        super(Generator, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(latent_dim, 128),
            nn.ReLU(True),
            nn.Linear(128, 256),
            nn.ReLU(True),
            nn.Linear(256, 512),
            nn.ReLU(True),
            nn.Linear(512, 28 * 28),
            nn.Tanh()
        )

    def forward(self, z):
        img = self.model(z)
        return img.view(-1, 1, 28, 28)

class Discriminator(nn.Module):
    def __init__(self):
        super(Discriminator, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(28 * 28, 512),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )

    def forward(self, img):
        return self.model(img.view(-1, 28 * 28))

generator = Generator(latent_dim).to(device)
discriminator = Discriminator().to(device)

criterion = nn.BCELoss()
optimizer_G = optim.Adam(generator.parameters(), lr=lr)
optimizer_D = optim.Adam(discriminator.parameters(), lr=lr)

for epoch in range(epochs):
    for i, (imgs, _) in enumerate(dataloader):
        real = imgs.to(device)
        batch_size = real.size(0)

        valid = torch.ones(batch_size, 1, device=device)
        fake = torch.zeros(batch_size, 1, device=device)

        z = torch.randn(batch_size, latent_dim, device=device)
        gen_imgs = generator(z)
        real_loss = criterion(discriminator(real), valid)
        fake_loss = criterion(discriminator(gen_imgs.detach()), fake)
        d_loss = (real_loss + fake_loss) / 2

        optimizer_D.zero_grad()
        d_loss.backward()
        optimizer_D.step()

        z = torch.randn(batch_size, latent_dim, device=device)
        gen_imgs = generator(z)
        g_loss = criterion(discriminator(gen_imgs), valid)

        optimizer_G.zero_grad()
        g_loss.backward()
        optimizer_G.step()

    print(f"Epoch [{epoch + 1}/{epochs}] D_loss: {d_loss.item():.4f} G_loss: {g_loss.item():.4f}")

z = torch.randn(16, latent_dim, device=device)
gen_imgs = generator(z).cpu().detach()

grid = torchvision.utils.make_grid(gen_imgs, nrow=4, normalize=True)
plt.imshow(grid.permute(1, 2, 0))
plt.axis("off")
plt.show()
        '''
    )

def aai_prac_6a():
    print(
        '''
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.layers import GlobalAveragePooling2D, Flatten, Dense, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from zipfile import ZipFile
import os

from google.colab import files
files.upload()

!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

!kaggle datasets download -d mohamedhanyyy/chest-ctscan-images  

file_name = "chest-ctscan-images.zip"
with ZipFile(file_name, 'r') as zip_ref:
    zip_ref.extractall()
print('Dataset extracted.')

train_dir = '/content/Data/train'
test_dir = '/content/Data/test'

train_datagen = ImageDataGenerator(
    rescale=1./255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True
)

test_datagen = ImageDataGenerator(rescale=1./255)

training_set = train_datagen.flow_from_directory(
    train_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical'
)

test_set = test_datagen.flow_from_directory(
    test_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical'
)

base_model = tf.keras.applications.InceptionV3(
    weights='imagenet',
    include_top=False,
    input_shape=(224, 224, 3)
)

for layer in base_model.layers[:-15]:
    layer.trainable = False

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Flatten()(x)
x = Dense(512, activation='relu')(x)
x = Dropout(0.3)(x)
x = Dense(512, activation='relu')(x)
x = Dropout(0.3)(x)
output = Dense(4, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=output)

model.summary()

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

history = model.fit(
    training_set,
    validation_data=test_set,
    epochs=8,
    steps_per_epoch=len(training_set),
    validation_steps=len(test_set)
)

plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(history.history['loss'], label='train loss')
plt.plot(history.history['val_loss'], label='val loss')
plt.title('Loss')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['accuracy'], label='train accuracy')
plt.plot(history.history['val_accuracy'], label='val accuracy')
plt.title('Accuracy')
plt.legend()

plt.show()

model.save('chest_ctscan_inceptionv3.h5')
print("Model saved.")

        '''
    )

def aai_prac_7a():
    print(
        '''
import pandas as pd
import tensorflow as tf
from keras.layers import Input, Dense
from keras.models import Model
from sklearn.metrics import precision_recall_fscore_support
import matplotlib.pyplot as plt

data = pd.read_csv('ambient_temperature_system_failure.csv')

data_values = data.drop('timestamp', axis=1).values
data_values = data_values.astype('float32')
data_converted = pd.DataFrame(data_values, columns=data.columns[1:])
data_converted.insert(0, 'timestamp', data['timestamp'])
data_converted = data_converted.dropna()

data_tensor = tf.convert_to_tensor(
    data_converted.drop('timestamp', axis=1).values, dtype=tf.float32
)

input_dim = data_converted.shape[1] - 1
encoding_dim = 10

input_layer = Input(shape=(input_dim,))
encoder = Dense(encoding_dim, activation='relu')(input_layer)
decoder = Dense(input_dim, activation='relu')(encoder)
autoencoder = Model(inputs=input_layer, outputs=decoder)

autoencoder.compile(optimizer='adam', loss='mse')

autoencoder.fit(
    data_tensor,
    data_tensor,
    epochs=50,
    batch_size=32,
    shuffle=True
)

reconstructions = autoencoder.predict(data_tensor)
mse = tf.reduce_mean(tf.square(data_tensor - reconstructions), axis=1)
anomaly_scores = pd.Series(mse.numpy(), name='anomaly_scores')
anomaly_scores.index = data_converted.index

threshold = anomaly_scores.quantile(0.99)
anomalous = anomaly_scores > threshold
binary_labels = anomalous.astype(int)

precision, recall, f1_score, _ = precision_recall_fscore_support(
    binary_labels, anomalous, average='binary'
)

test = data_converted['value'].values
predictions = anomaly_scores.values

print("Precision: ", precision)
print("Recall: ", recall)
print("F1 Score: ", f1_score)

plt.figure(figsize=(16, 8))
plt.plot(data_converted['timestamp'], data_converted['value'], label='Normal Data')
plt.plot(
    data_converted['timestamp'][anomalous],
    data_converted['value'][anomalous],
    'ro',
    label='Anomalies'
)
plt.title('Anomaly Detection using Autoencoder')
plt.xlabel('Time')
plt.ylabel('Value')
plt.legend()
plt.show()
        '''
    )

def aai_prac_8a():
    print(
        '''
import random

POP_SIZE = 500
MUT_RATE = 0.1
TARGET = 'Keerthan Gubbala'
GENES = ' abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

def initialize_pop(TARGET):
    population = list()
    tar_len = len(TARGET)
    for i in range(POP_SIZE):
        temp = list()
        for j in range(tar_len):
            temp.append(random.choice(GENES))
        population.append(temp)
    return population

def crossover(selected_chromo, CHROMO_LEN, population):
    offspring_cross = []
    for i in range(int(POP_SIZE)):
        parent1 = random.choice(selected_chromo)
        parent2 = random.choice(population[:int(POP_SIZE * 0.5)])
        p1 = parent1[0]
        p2 = parent2[0]
        crossover_point = random.randint(1, CHROMO_LEN - 1)
        child = p1[:crossover_point] + p2[crossover_point:]
        offspring_cross.extend([child])
    return offspring_cross

def mutate(offspring, MUT_RATE):
    mutated_offspring = []
    for arr in offspring:
        for i in range(len(arr)):
            if random.random() < MUT_RATE:
                arr[i] = random.choice(GENES)
        mutated_offspring.append(arr)
    return mutated_offspring

def selection(population, TARGET):
    sorted_chromo_pop = sorted(population, key=lambda x: x[1])
    return sorted_chromo_pop[:int(0.5 * POP_SIZE)]

def fitness_cal(TARGET, chromo_from_pop):
    difference = 0
    for tar_char, chromo_char in zip(TARGET, chromo_from_pop):
        if tar_char != chromo_char:
            difference += 1
    return [chromo_from_pop, difference]

def replace(new_gen, population):
    for _ in range(len(population)):
        if population[_][1] > new_gen[_][1]:
            population[_][0] = new_gen[_][0]
            population[_][1] = new_gen[_][1]
    return population

def main(POP_SIZE, MUT_RATE, TARGET, GENES):
    initial_population = initialize_pop(TARGET)
    found = False
    population = []
    generation = 1
    for _ in range(len(initial_population)):
        population.append(fitness_cal(TARGET, initial_population[_]))
    while not found:
        selected = selection(population, TARGET)
        population = sorted(population, key=lambda x: x[1])
        crossovered = crossover(selected, len(TARGET), population)
        mutated = mutate(crossovered, MUT_RATE)
        new_gen = []
        for _ in mutated:
            new_gen.append(fitness_cal(TARGET, _))
        population = replace(new_gen, population)
        if population[0][1] == 0:
            print('Target found!')
            print('String: ' + ''.join(population[0][0]) +
                  ' | Generation: ' + str(generation) +
                  ' | Fitness: ' + str(population[0][1]))
            break
        print('String: ' + ''.join(population[0][0]) +
              ' | Generation: ' + str(generation) +
              ' | Fitness: ' + str(population[0][1]))
        generation += 1

main(POP_SIZE, MUT_RATE, TARGET, GENES)
        '''
    )
