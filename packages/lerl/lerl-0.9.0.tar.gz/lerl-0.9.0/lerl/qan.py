from .utils import format_snippet

def undercomplete_ae_code():
    code = '''
# UnderComplete Autoencoder

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt

transform = transforms.ToTensor()

train_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

class UndercompleteAE(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(784, 128),
            nn.ReLU(),
            nn.Linear(128, 9)
        )
        self.decoder = nn.Sequential(
            nn.Linear(9, 128),
            nn.ReLU(),
            nn.Linear(128, 784),
            nn.Sigmoid()
        )

    def forward(self, x):
        z = self.encoder(x)
        x_hat = self.decoder(z)
        return x_hat

model = UndercompleteAE()
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)

losses = []

for epoch in range(5):
    for images, _ in train_loader:
        images = images.view(images.size(0), -1)

        outputs = model(images)
        loss = criterion(outputs, images)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        losses.append(loss.item())

    print(f"Epoch {epoch+1}/5, Loss: {loss.item():.4f}")

plt.plot(losses)
plt.xlabel("Iterations")
plt.ylabel("MSE Loss")
plt.title("Undercomplete AE Training Loss")
plt.show()

# Visualization of Reconstruction

model.eval()
images, _ = next(iter(train_loader))
images = images.view(images.size(0), -1)

with torch.no_grad():
    recon = model(images)

plt.figure(figsize=(10, 4))
for i in range(10):
    # Original
    plt.subplot(2, 10, i+1)
    plt.imshow(images[i].view(28,28), cmap='gray')
    plt.axis('off')

    # Reconstructed
    plt.subplot(2, 10, i+11)
    plt.imshow(recon[i].view(28,28), cmap='gray')
    plt.axis('off')

plt.show()


'''
    return format_snippet(code)

def denoising_ae_code():
    code = '''
# Denoising Autoencoder
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt

transform = transforms.ToTensor()

train_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

class UndercompleteAE(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(784, 128),
            nn.ReLU(),
            nn.Linear(128, 9)
        )
        self.decoder = nn.Sequential(
            nn.Linear(9, 128),
            nn.ReLU(),
            nn.Linear(128, 784),
            nn.Sigmoid()
        )

    def forward(self, x):
        z = self.encoder(x)
        x_hat = self.decoder(z)
        return x_hat

model = UndercompleteAE()
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3)

dae_losses = []

for epoch in range(5):
    for images, _ in train_loader:
        images = images.view(images.size(0), -1)

        noisy = images + 0.5 * torch.randn_like(images)
        noisy = torch.clamp(noisy, 0., 1.)

        outputs = model(noisy)
        loss = criterion(outputs, images)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        dae_losses.append(loss.item())

    print(f"Epoch {epoch+1}/5, Loss: {loss.item():.4f}")

plt.plot(dae_losses)
plt.xlabel("Iterations")
plt.ylabel("MSE Loss")
plt.title("Denoising AE Loss")
plt.show()


# Visualize Original vs Noisy vs Denoised
model.eval()
images, _ = next(iter(train_loader))
images = images.view(images.size(0), -1)

noisy = images + 0.5 * torch.randn_like(images)
noisy = torch.clamp(noisy, 0., 1.)

with torch.no_grad():
    recon = model(noisy)

plt.figure(figsize=(12, 6))
for i in range(10):
    plt.subplot(3, 10, i+1)
    plt.imshow(images[i].view(28,28), cmap='gray')
    plt.axis('off')

    plt.subplot(3, 10, i+11)
    plt.imshow(noisy[i].view(28,28), cmap='gray')
    plt.axis('off')

    plt.subplot(3, 10, i+21)
    plt.imshow(recon[i].view(28,28), cmap='gray')
    plt.axis('off')

plt.show()


'''
    return format_snippet(code)

def convolutional_ae_code():
    code = '''
# Convolutional Autoencoder
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt

transform = transforms.ToTensor()

fashion_data = datasets.FashionMNIST(root='./data', train=True, download=True, transform=transform)
fashion_loader = DataLoader(fashion_data, batch_size=32, shuffle=True)

class ConvAE(nn.Module):
    def __init__(self):
        super().__init__()

        self.encoder = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 8, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )

        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(8, 16, 2, stride=2),
            nn.ReLU(),
            nn.ConvTranspose2d(16, 1, 2, stride=2),
            nn.Sigmoid()
        )

    def forward(self, x):
        z = self.encoder(x)
        x_hat = self.decoder(z)
        return x_hat

model = ConvAE()
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3)

cae_losses = []

for epoch in range(5):
    for images, _ in fashion_loader:
        outputs = model(images)
        loss = criterion(outputs, images)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        cae_losses.append(loss.item())

    print(f"Epoch {epoch+1}/5, Loss: {loss.item():.4f}")

plt.plot(cae_losses)
plt.xlabel("Iterations")
plt.ylabel("MSE Loss")
plt.title("CAE Training Loss")
plt.show()

model.eval()
images, _ = next(iter(fashion_loader))

with torch.no_grad():
    recon = model(images)

plt.figure(figsize=(10, 4))
for i in range(10):
    plt.subplot(2, 10, i+1)
    plt.imshow(images[i][0], cmap='gray')
    plt.axis('off')

    plt.subplot(2, 10, i+11)
    plt.imshow(recon[i][0], cmap='gray')
    plt.axis('off')

plt.show()


'''
    return format_snippet(code)

def simple_rnn_code():
    code = '''
# Simple RNN on QA Dataset
import pandas as pd
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, SimpleRNN, Dense

data = pd.read_csv("qa_dataset.csv")
print(data.head())

questions = data["question"].astype(str).tolist()
answers = data["answer"].astype(str).tolist()

tokenizer = Tokenizer(num_words=5000, oov_token="<OOV>")
tokenizer.fit_on_texts(questions)

seqs = tokenizer.texts_to_sequences(questions)
padded_q = pad_sequences(seqs, maxlen=20, padding="post")

# Encode answers as labels
label_tokenizer = Tokenizer()
label_tokenizer.fit_on_texts(answers)
y = label_tokenizer.texts_to_sequences(answers)
y = [i[0] for i in y]


model = Sequential([
    Embedding(input_dim=5000, output_dim=64, input_length=20),
    SimpleRNN(64),
    Dense(len(label_tokenizer.word_index) + 1, activation="softmax")
])

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()

model.fit(
    padded_q,
    y,
    epochs=10,
    batch_size=32,
    validation_split=0.2
)

loss, acc = model.evaluate(padded_q, y)
print("Accuracy:", acc)



'''
    return format_snippet(code)

def rnn_imdb_code():
    code = '''
# RNN - IMDB

import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report
import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, SimpleRNN, Dense
from tensorflow.keras.datasets import imdb
import matplotlib.pyplot as plt

vocab_size = 10000
(x_train, y_train), (x_test, y_test) = imdb.load_data(num_words=vocab_size)

max_len = 200

x_train = pad_sequences(x_train, maxlen=max_len)
x_test = pad_sequences(x_test, maxlen=max_len)

word_index = imdb.get_word_index()
reverse_word_index = {v: k for k, v in word_index.items()}

def decode(review):
    return " ".join([reverse_word_index.get(i-3, "?") for i in review])

print(decode(x_train[0]))
print("Label:", "Positive" if y_train[0] == 1 else "Negative")

model = Sequential([
    Embedding(vocab_size, 128, input_length=max_len),
    SimpleRNN(64),
    Dense(1, activation="sigmoid")
])

model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

model.build()
model.summary()

history = model.fit(
    x_train, y_train,
    epochs=2,
    batch_size=64,
    validation_split=0.2
)


plt.plot(history.history["accuracy"], label="Train Acc")
plt.plot(history.history["val_accuracy"], label="Val Acc")
plt.legend()
plt.title("Accuracy")
plt.show()

plt.plot(history.history["loss"], label="Train Loss")
plt.plot(history.history["val_loss"], label="Val Loss")
plt.legend()
plt.title("Loss")
plt.show()

test_loss, test_acc = model.evaluate(x_test, y_test)
print("Test Accuracy:", test_acc)

y_pred = (model.predict(x_test) > 0.5).astype(int)

print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))


'''
    return format_snippet(code)

def lstm_vs_rnn_code():
    code = '''
# LSTM vs RNN - IMBD
from tensorflow.keras.datasets import imdb
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, SimpleRNN, Dense

vocab_size = 10000
max_len = 200

(x_train, y_train), (x_test, y_test) = imdb.load_data(num_words=vocab_size)

x_train = pad_sequences(x_train, maxlen=max_len)
x_test = pad_sequences(x_test, maxlen=max_len)

#SIMPLE LSTM

lstm_model = Sequential([
    Embedding(vocab_size, 128, input_length=max_len),
    LSTM(64),
    Dense(1, activation="sigmoid")
])

lstm_model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

lstm_model.summary()

lstm_history = lstm_model.fit(
    x_train, y_train,
    epochs=2,
    batch_size=64,
    validation_split=0.2
)

#SIMPLE RNN

rnn_model = Sequential([
    Embedding(vocab_size, 128, input_length=max_len),
    SimpleRNN(64),
    Dense(1, activation="sigmoid")
])

rnn_model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

rnn_model.summary()

rnn_history = rnn_model.fit(
    x_train, y_train,
    epochs=2,
    batch_size=64,
    validation_split=0.2
)

# LSTM VS RNN
lstm_acc = lstm_model.evaluate(x_test, y_test)[1]
rnn_acc = rnn_model.evaluate(x_test, y_test)[1]

print("LSTM Test Accuracy:", lstm_acc)
print("SimpleRNN Test Accuracy:", rnn_acc)


'''
    return format_snippet(code)

def lstm_next_word_code():
    code = '''
# LSTM NEXT WORD
import re
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np

with open("document.txt", "r") as f:
    text = f.read().lower()

text = re.sub(r"[^a-z\s]", "", text)
text = text.replace("\n", " ")

tokenizer = Tokenizer()
tokenizer.fit_on_texts([text])

total_words = len(tokenizer.word_index) + 1

input_sequences = []
words = text.split()

for i in range(1, len(words)):
    seq = words[:i+1]
    token_seq = tokenizer.texts_to_sequences([" ".join(seq)])[0]
    input_sequences.append(token_seq)

max_len = max(len(seq) for seq in input_sequences)

input_sequences = pad_sequences(input_sequences, maxlen=max_len, padding="pre")

X = input_sequences[:, :-1]
y = input_sequences[:, -1]

y = np.array(y)

y = to_categorical(y, num_classes=total_words)

model = Sequential([
    Embedding(total_words, 64, input_length=max_len-1),
    LSTM(100),
    Dense(total_words, activation="softmax")
])

model.compile(
    loss="categorical_crossentropy",
    optimizer="adam"
)

model.summary()

model.fit(
    X, y,
    epochs=50,
    validation_split=0.1
)

def predict_next_word(text_input):
    seq = tokenizer.texts_to_sequences([text_input])[0]
    seq = pad_sequences([seq], maxlen=max_len-1, padding="pre")

    preds = model.predict(seq)[0]
    top_3 = preds.argsort()[-3:][::-1]

    for i in top_3:
        print(tokenizer.index_word[i])

predict_next_word("what is the")

#Sentiment Alalysis
reviews = [
    "This movie was fantastic and emotional",
    "Worst acting and boring story",
    "The movie was average",
]

for r in reviews:
    seq = tokenizer.texts_to_sequences([r])
    pad = pad_sequences(seq, maxlen=max_len)
    pred = lstm_model.predict(pad)[0][0]
    print(r, "→", "Positive" if pred > 0.5 else "Negative")


'''
    return format_snippet(code)

def gan_code():
    code = '''
# GAN on Mnist
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import os

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

dataset = datasets.MNIST(root="./data", train=True, download=True, transform=transform)
loader = DataLoader(dataset, batch_size=64, shuffle=True)

class Generator(nn.Module):
    def __init__(self, z_dim=100):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(z_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Linear(512, 784),
            nn.Tanh()
        )

    def forward(self, z):
        return self.net(z)

class Discriminator(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(784, 512),
            nn.LeakyReLU(0.2),
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.net(x)

z_dim = 100
G = Generator(z_dim)
D = Discriminator()

criterion = nn.BCELoss()
opt_G = optim.Adam(G.parameters(), lr=0.0002)
opt_D = optim.Adam(D.parameters(), lr=0.0002)

epochs = 5
os.makedirs("gan_samples", exist_ok=True)

for epoch in range(epochs):
    for images, _ in loader:
        batch_size = images.size(0)
        real = images.view(batch_size, -1)

        real_labels = torch.ones(batch_size, 1)
        fake_labels = torch.zeros(batch_size, 1)

        # Train Discriminator
        z = torch.randn(batch_size, z_dim)
        fake = G(z)

        D_real = D(real)
        D_fake = D(fake.detach())

        loss_D = criterion(D_real, real_labels) + criterion(D_fake, fake_labels)

        opt_D.zero_grad()
        loss_D.backward()
        opt_D.step()

        # Train Generator
        z = torch.randn(batch_size, z_dim)
        fake = G(z)
        D_fake = D(fake)

        loss_G = criterion(D_fake, real_labels)

        opt_G.zero_grad()
        loss_G.backward()
        opt_G.step()

    print(f"Epoch {epoch+1}/{epochs} | LossD: {loss_D:.4f} | LossG: {loss_G:.4f}")

with torch.no_grad():
    z = torch.randn(16, z_dim)
    fake = G(z).view(-1, 28, 28)

plt.figure(figsize=(4,4))
for i in range(16):
    plt.subplot(4,4,i+1)
    plt.imshow(fake[i], cmap="gray")
    plt.axis("off")
plt.show()

'''
    return format_snippet(code)

def dcgan_code():
    code = '''
# DCGAN
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import os

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

dataset = datasets.MNIST(root="./data", train=True, download=True, transform=transform)
loader = DataLoader(dataset, batch_size=64, shuffle=True)

class DCGAN_G(nn.Module):
    def __init__(self, nz=100):
        super().__init__()
        self.net = nn.Sequential(
            nn.ConvTranspose2d(nz, 128, 7, 1, 0),
            nn.BatchNorm2d(128),
            nn.ReLU(),

            nn.ConvTranspose2d(128, 64, 4, 2, 1),
            nn.BatchNorm2d(64),
            nn.ReLU(),

            nn.ConvTranspose2d(64, 1, 4, 2, 1),
            nn.Tanh()
        )

    def forward(self, z):
        return self.net(z)

class DCGAN_D(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(1, 64, 4, 2, 1),
            nn.LeakyReLU(0.2),

            nn.Conv2d(64, 128, 4, 2, 1),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2),

            nn.Flatten(),
            nn.Linear(128 * 7 * 7, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.net(x)

G = DCGAN_G()
D = DCGAN_D()

criterion = nn.BCELoss()
opt_G = optim.Adam(G.parameters(), lr=0.0002, betas=(0.5, 0.999))
opt_D = optim.Adam(D.parameters(), lr=0.0002, betas=(0.5, 0.999))

fixed_noise = torch.randn(16, 100, 1, 1)
os.makedirs("synthetic_pack", exist_ok=True)

epochs = 5

for epoch in range(epochs):
    for images, _ in loader:
        batch_size = images.size(0)
        real = images

        real_labels = torch.ones(batch_size, 1)
        fake_labels = torch.zeros(batch_size, 1)

        # Train D
        z = torch.randn(batch_size, 100, 1, 1)
        fake = G(z)

        loss_D = criterion(D(real), real_labels) + \
                 criterion(D(fake.detach()), fake_labels)

        opt_D.zero_grad()
        loss_D.backward()
        opt_D.step()

        # Train G
        loss_G = criterion(D(fake), real_labels)

        opt_G.zero_grad()
        loss_G.backward()
        opt_G.step()

    print(f"Epoch {epoch+1} | LossD: {loss_D:.4f} | LossG: {loss_G:.4f}")

    with torch.no_grad():
        fake = G(fixed_noise)
        plt.figure(figsize=(4,4))
        for i in range(16):
            plt.subplot(4,4,i+1)
            plt.imshow(fake[i][0], cmap="gray")
            plt.axis("off")
        plt.savefig(f"synthetic_pack/fake_epoch_{epoch+1}.png")
        plt.close()

plt.figure(figsize=(4,4))
plt.imshow(fake[0][0], cmap="gray")
plt.axis("off")
plt.savefig("synthetic_pack/final_grid.png")
plt.show()
'''
    return format_snippet(code)