"""Lab workflow functions for ANN module"""

def flowlab1():
    """Complete Lab 1: PyTorch Tensor Operations"""
    code = '''import torch
print(f"PyTorch Version: {torch.__version__}")

if torch.cuda.is_available():
    print(f"PyTorch is using GPU: {torch.cuda.get_device_name(0)}")

else:
    print("PyTorch is using CPU")

# Scalar (0-D)
scalar = torch.tensor(1.5)
print(scalar)
print("\n\n")

# Vector (1-D)
vector = torch.tensor([1, 2, 3, 4, 5])
print(vector)
print("\n\n")

# 3x3 Matrix (2-D)
matrix = torch.rand(3, 3)
print(matrix)
print("\n\n")

# 2x3x4 3D Tensor
tensor3d = torch.rand(2, 3, 4)
print(tensor3d)
print("\n\n")

# Element-wise add
tensor_1 = torch.tensor([1, 2, 3])
tensor_2 = torch.tensor([4, 5, 6])
element_wise_add = tensor_1 + tensor_2

print(element_wise_add)
print("\n\n")

# Matrix multiplication
t1 = torch.rand(2, 3)
t2 = torch.rand(3, 4)
matrix_mul = torch.matmul(t1, t2)

print(matrix_mul.shape)
print("\n\n")

# Reductions
reduction_tensor = torch.rand(2, 3)
mean_rows_pt = torch.mean(reduction_tensor, dim=1)
sum_cols_pt = torch.sum(reduction_tensor, dim=0)

print(mean_rows_pt)
print("\n\n")
print(sum_cols_pt)

tensor1d = torch.arange(12)
print(tensor1d)
print("\n\n")

reshaped1_pt = tensor1d.reshape(3, 4)
print(reshaped1_pt)
print("\n\n")

reshaped2 = tensor1d.reshape(2, 6)
print(reshaped2)

x = torch.tensor(3.0, requires_grad=True)
y = x**2
y.backward()
print(f"x = {x.item()} y = {y.item()}")
print(x.grad.item())

image = torch.randint(0, 256, (5, 5), dtype=torch.float32)
print(image)

normalized_image = image / 255.0
print(normalized_image)

kernel = torch.tensor([[-1., -1., -1.], [-1., 1., -1.], [-1., -1., -1.]])
region_of_interest = normalized_image[1:4, 1:4]
filtered_region = region_of_interest * kernel
print(filtered_region)

average_brightness = torch.mean(normalized_image)
print(average_brightness.item())

sensor_data = torch.arange(30.)
print(sensor_data)

batched_data = sensor_data.reshape(6, 5)
print(batched_data)

batch_averages = torch.mean(batched_data, dim=1)
print(batch_averages)

sensor_type_data = sensor_data.reshape(6, 5)
print(sensor_type_data)

sensor_type_averages = torch.mean(sensor_type_data, dim=0)
print(sensor_type_averages)'''
    print(code)

def flowlab2():
    """Complete Lab 2: Perceptron"""
    code = '''from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Perceptron
from sklearn.inspection import DecisionBoundaryDisplay

from matplotlib import pyplot as plt
from mlxtend.plotting import plot_decision_regions
import seaborn as sns
import pandas as pd
import numpy as np

X_raw, y_raw = make_blobs(n_samples=300, centers=2, random_state=54)

scaler = StandardScaler()
X_prep = scaler.fit_transform(X_raw)

pd.DataFrame(X_prep).head()

pd.DataFrame(y_raw).head()

data = pd.DataFrame(X_prep, columns=['X1', 'X2'])
data['y'] = y_raw

sns.scatterplot(data=data, x='X1', y='X2', hue='y')
plt.show()

base_perceptron = Perceptron()
base_perceptron.fit(X_prep, y_raw)

plot = DecisionBoundaryDisplay.from_estimator(base_perceptron, X_prep, response_method='predict')
plot.ax_.scatter(X_prep[:, 0], X_prep[:, 1], c=y_raw, edgecolor='k')
plt.title("Perceptron Decision Boundary")
plt.show()

increased_max_iter_perceptron = Perceptron(random_state=53, max_iter=100)
decreased_max_iter_perceptron = Perceptron(random_state=42, max_iter=1)

increased_max_iter_perceptron.fit(X_prep, y_raw)
decreased_max_iter_perceptron.fit(X_prep, y_raw)

print("Increased max_iter:", increased_max_iter_perceptron.n_iter_)
print("Decreased max_iter:", decreased_max_iter_perceptron.n_iter_)

plot_decision_regions(X_prep, y_raw, clf=increased_max_iter_perceptron)
plt.show()

plot_decision_regions(X_prep, y_raw, clf=decreased_max_iter_perceptron)
plt.show()

raw_perceptron = Perceptron(random_state=53)
raw_perceptron.fit(X_raw, y_raw)

plot_decision_regions(X_raw, y_raw, clf=raw_perceptron)
plt.show()

prep_perceptron = Perceptron(random_state=53)
prep_perceptron.fit(X_prep, y_raw)

plot_decision_regions(X_prep, y_raw, clf=prep_perceptron)
plt.show()'''
    print(code)

def flowlab3():
    """Complete Lab 3: ADALINE Delta Rule"""
    code = '''from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Perceptron
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, f1_score

from torch.autograd import grad
import torch.nn as nn
import torch.functional as F
import torch

df = pd.DataFrame(data=load_iris().data, columns=['x1', 'x2', 'x3', 'x4'])
df['y'] = load_iris().target
df = df.iloc[50:150]
df['y'] = df['y'].apply(lambda x: 0 if x == 'Iris-versicolor' else 1)

df.head()

X = torch.tensor(df[['x2', 'x3']].values, dtype=torch.float32)
y = torch.tensor(df['y'].values, dtype=torch.int32)

torch.manual_seed(53)

shuffle_idx = torch.randperm(len(y), dtype=torch.int32)

X, y = X[shuffle_idx], y[shuffle_idx]
X_train, X_test = X[:int(len(shuffle_idx) * 0.7)], X[int(len(shuffle_idx) * 0.3):]
y_train, y_test = y[:int(len(shuffle_idx) * 0.7)], y[int(len(shuffle_idx) * 0.3):]

mu, sigma = torch.mean(X_train, dim=0), torch.std(X_train, dim=0)
X_train_prep = (X_train - mu) / sigma
X_test_prep = (X_test - mu) / sigma

class manual_ADALINE:
    def __init__(self, num_features):
        self.num_features = num_features
        self.weights = torch.zeros(num_features, 1, dtype=torch.float32)
        self.biases = torch.zeros(1, dtype=torch.float32)

    def forward(self, x):
        return torch.mm(x, self.weights) + self.biases

    def backward(self, x, yhat, y):
        grad_loss = (yhat.view(-1, 1) - y.view(-1, 1))
        grad_loss_weights = torch.mm(x.t(), grad_loss) / len(y)
        grad_loss_biases = torch.sum(grad_loss) / len(y)
        return grad_loss_weights, grad_loss_biases

def loss_function(yhat, y):
    return torch.mean((yhat - y) ** 2)

def train(model, x, y, total_epochs, lr=0.01, seed=53, batch_size=16):
    cost = []
    torch.manual_seed(seed)

    for epoch in range(total_epochs):
        shuffle_idx = torch.randperm(len(y))
        minibatches = torch.split(shuffle_idx, batch_size)

        for minibatch in minibatches:
            xb = x[minibatch]
            yb = y[minibatch].view(-1, 1)
            yhat = model.forward(xb)
            loss = loss_function(yhat, yb)
            gradient_W, gradient_B = model.backward(xb, yhat, yb)

            with torch.no_grad():
                model.weights -= lr * gradient_W
                model.biases -= lr * gradient_B

        with torch.no_grad():
            yhat_full = model.forward(x)
            curr_loss = loss_function(yhat_full, y.view(-1, 1))
            print(f'Epoch {epoch + 1} | MSE: {curr_loss.item():.6f}')
            cost.append(curr_loss.item())

    return cost

model = manual_ADALINE(num_features=X_train.size(1))

cost = train(model, X_train, y_train.float(), total_epochs=20, lr=0.01, seed=53, batch_size=16)

plt.plot(range(len(cost)), cost)
plt.ylabel('Mean Squared Error')
plt.xlabel('Epoch')
plt.show()

train_ones = torch.ones(y_train.size())
train_zeroes = torch.zeros(y_train.size())
train_predictions = model.forward(X_train)
train_accuracy = torch.mean((torch.where(train_predictions > 0.5, train_ones, train_zeroes).int() == y_train).float())

test_ones = torch.ones(y_test.size())
test_zeroes = torch.zeros(y_test.size())
test_predictions = model.forward(X_test)
test_accuracy = torch.mean((torch.where(test_predictions > 0.5, test_ones, test_zeroes).int() == y_test).float())

print(f'Training Accuracy: {train_accuracy * 100}')
print(f'Test Accuracy: {test_accuracy * 100}')

class semi_ADALINE:
    def __init__(self, num_features):
        self.num_features = num_features
        self.weights = torch.zeros(num_features, 1, dtype=torch.float32, requires_grad=True)
        self.bias = torch.zeros(1, dtype=torch.float32, requires_grad=True)

    def forward(self, x):
        return torch.mm(x, self.weights) + self.bias

def loss_function(yhat, y):
    return torch.mean((yhat - y) ** 2)

def train(model, x, y, total_epochs, lr=0.01, seed=53, batch_size=16):
    cost = []
    torch.manual_seed(seed)

    for epoch in range(total_epochs):
        shuffle_idx = torch.randperm(len(y))
        minibatches = torch.split(shuffle_idx, batch_size)

        for minibatch in minibatches:
            xb = x[minibatch]
            yb = y[minibatch]
            yhat = model.forward(xb)
            loss = loss_function(yhat, yb)

            gradient_W = grad(loss, model.weights, retain_graph=True)[0]
            gradient_B = grad(loss, model.bias)[0]

            with torch.no_grad():
                model.weights -= lr * gradient_W
                model.bias -= lr * gradient_B

        with torch.no_grad():
            yhat_full = model.forward(x)
            curr_loss = loss_function(yhat_full, y)
            print(f'Epoch {epoch + 1} | MSE: {curr_loss.item():.6f}')
            cost.append(curr_loss.item())

    return cost

model = semi_ADALINE(num_features=X_train.size(1))

cost = train(model, X_train, y_train.float(), total_epochs=20, lr=0.01, seed=53, batch_size=16)

plt.plot(range(len(cost)), cost)
plt.ylabel('Mean Squared Error')
plt.xlabel('Epoch')
plt.show()

train_ones = torch.ones(y_train.size())
train_zeroes = torch.zeros(y_train.size())
train_predictions = model.forward(X_train)
train_accuracy = torch.mean((torch.where(train_predictions > 0.5, train_ones, train_zeroes).int() == y_train).float())

test_ones = torch.ones(y_test.size())
test_zeroes = torch.zeros(y_test.size())
test_predictions = model.forward(X_test)
test_accuracy = torch.mean((torch.where(test_predictions > 0.5, test_ones, test_zeroes).int() == y_test).float())

print(f'Training Accuracy: {train_accuracy * 100}')
print(f'Test Accuracy: {test_accuracy * 100}')

class automatic_ADALINE(nn.Module):
    def __init__(self, num_features):
        super(automatic_ADALINE, self).__init__()
        self.linear = nn.Linear(num_features, 1)
        with torch.no_grad():
            self.linear.weight.zero_()
            self.linear.bias.zero_()

    def forward(self, x):
        return self.linear(x).view(-1)

def train(model, x, y, total_epochs, lr=0.01, seed=53, batch_size=16):
    cost = []
    torch.manual_seed(seed)
    optimizer = torch.optim.SGD(model.parameters(), lr=lr)

    for epoch in range(total_epochs):
        shuffle_idx = torch.randperm(len(y))
        minibatches = torch.split(shuffle_idx, batch_size)

        for minibatch in minibatches:
            xb = x[minibatch]
            yb = y[minibatch]
            yhat = model.forward(xb)
            loss = F.mse_loss(yhat, yb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        with torch.no_grad():
            yhat_full = model.forward(x)
            curr_loss = F.mse_loss(yhat_full, y)
            print(f'Epoch {epoch + 1} | MSE: {curr_loss.item():.6f}')
            cost.append(curr_loss.item())

    return cost

class automatic_ADALINE(nn.Module):
    def __init__(self, num_features):
        super(automatic_ADALINE, self).__init__()
        self.linear = nn.Linear(num_features, 1)
        with torch.no_grad():
            self.linear.weight.zero_()
            self.linear.bias.zero_()

    def forward(self, x):
        return self.linear(x).view(-1)

def train(model, x, y, total_epochs, lr=0.01, seed=53, batch_size=16):
    cost = []
    torch.manual_seed(seed)
    optimizer = torch.optim.SGD(model.parameters(), lr=lr)

    for epoch in range(total_epochs):
        shuffle_idx = torch.randperm(len(y))
        minibatches = torch.split(shuffle_idx, batch_size)

        for minibatch in minibatches:
            xb = x[minibatch]
            yb = y[minibatch]
            yhat = model.forward(xb)
            loss = torch.nn.functional.mse_loss(yhat, yb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        with torch.no_grad():
            yhat_full = model.forward(x)
            curr_loss = torch.nn.functional.mse_loss(yhat_full, y)
            print(f'Epoch {epoch + 1} | MSE: {curr_loss.item():.6f}')
            cost.append(curr_loss.item())

    return cost


model = automatic_ADALINE(num_features=X_train.size(1))

cost = train(model, X_train, y_train.float(), total_epochs=20, lr=0.01, seed=53, batch_size=16)

plt.plot(range(len(cost)), cost)
plt.ylabel('Mean Squared Error')
plt.xlabel('Epoch')
plt.show()

train_ones = torch.ones(y_train.size())
train_zeroes = torch.zeros(y_train.size())
train_predictions = model.forward(X_train)
train_accuracy = torch.mean((torch.where(train_predictions > 0.5, train_ones, train_zeroes).int() == y_train).float())

test_ones = torch.ones(y_test.size())
test_zeroes = torch.zeros(y_test.size())
test_predictions = model.forward(X_test)
test_accuracy = torch.mean((torch.where(test_predictions > 0.5, test_ones, test_zeroes).int() == y_test).float())

print(f'Training Accuracy: {train_accuracy * 100}')
print(f'Test Accuracy: {test_accuracy * 100}')

def to01(y_pm1):
    return ((np.asarray(y_pm1) + 1) // 2).astype(int)

def from01(y01):
    return (2*np.asarray(y01) - 1).astype(int)

class ADALINE:
    def __init__(self, lr=0.01, epochs=50):
        self.lr = lr
        self.epochs = epochs
        self.w = None
        self.b = 0
        self.sse_history_ = []

    def fit(self, X, y_pm1):
        X = np.asarray(X, dtype=float)
        y_pm1 = np.asarray(y_pm1, dtype=float).ravel()
        n_features = X.shape[1]

        self.w = np.random.randn(n_features) * 0.01
        self.b = 0
        self.sse_history_ = []

        for _ in range(self.epochs):
            sse = 0
            for xi, yi in zip(X, y_pm1):
                z = np.dot(self.w, xi) + self.b
                a = z
                e = yi - a
                self.w += self.lr * e * xi
                self.b += self.lr * e
                sse += e**2
            self.sse_history_.append(sse)
        return self

    def net_input(self, X):
        return np.dot(X, self.w) + self.b

    def predict_labels_pm1(self, X):
        return np.where(self.net_input(X) >= 0.0, 1, -1)

rng = np.random.default_rng(7)
n_per_class = 100

X0 = rng.multivariate_normal([0, 0], [[0.25, 0],[0, 0.25]], size=n_per_class)
X1 = rng.multivariate_normal([2, 2], [[0.25, 0],[0, 0.25]], size=n_per_class)
X = np.vstack([X0, X1])
y = np.hstack([np.zeros(n_per_class), np.ones(n_per_class)])
y_pm1 = from01(y)

X_train, X_test, y_train, y_test = train_test_split(X, y_pm1, test_size=0.3, stratify=y_pm1, random_state=42)

adaline = ADALINE(lr=0.05, epochs=50)
adaline.fit(X_train, y_train)

plt.plot(adaline.sse_history_)
plt.xlabel("Epochs")
plt.ylabel("SSE")
plt.title("ADALINE Training: SSE vs Epochs")
plt.show()

def print_metrics(y_true, y_pred, name="Test"):
    y_true01 = to01(y_true)
    y_pred01 = to01(y_pred)
    print(f"=== {name} Metrics ===")
    print("Accuracy :", accuracy_score(y_true01, y_pred01))
    print("Confusion:\n", confusion_matrix(y_true01, y_pred01))
    print("Precision:", precision_score(y_true01, y_pred01, zero_division=0))
    print("Recall   :", recall_score(y_true01, y_pred01, zero_division=0))
    print("F1-score :", f1_score(y_true01, y_pred01, zero_division=0))

# Predictions
y_train_pred = adaline.predict_labels_pm1(X_train)
y_test_pred  = adaline.predict_labels_pm1(X_test)

print_metrics(y_train, y_train_pred, "Train")
print_metrics(y_test, y_test_pred, "Test")

lrs = [0.001, 0.01, 0.1, 1.0]
epochs = 50

for lr in lrs:
    m = ADALINE(lr=lr, epochs=epochs).fit(X_train, y_train)
    plt.plot(m.sse_history_, label=f"lr={lr}")

plt.xlabel("Epochs")
plt.ylabel("SSE")
plt.title("Effect of Learning Rate")
plt.legend()
plt.show()

iris = load_iris()
X = iris.data[:, :2]
y = iris.target
mask = (y == 0) | (y == 1)
X, y = X[mask], y[mask]
y_pm1 = from01(y)

scaler = StandardScaler()
X_std = scaler.fit_transform(X)

Xi_train, Xi_test, yi_train, yi_test = train_test_split(
    X_std, y_pm1, test_size=0.3, stratify=y_pm1, random_state=42)

adaline_iris = ADALINE(lr=0.05, epochs=80).fit(Xi_train, yi_train)

print_metrics(yi_train, adaline_iris.predict_labels_pm1(Xi_train), "Iris Train")
print_metrics(yi_test, adaline_iris.predict_labels_pm1(Xi_test), "Iris Test")

X_full = iris.data[mask]
scaler = StandardScaler()
X_full_std = scaler.fit_transform(X_full)

Xf_train, Xf_test, yf_train, yf_test = train_test_split(
    X_full_std, y_pm1, test_size=0.3, stratify=y_pm1, random_state=42)

adaline_full = ADALINE(lr=0.05, epochs=100).fit(Xf_train, yf_train)

print_metrics(yf_train, adaline_full.predict_labels_pm1(Xf_train), "Iris (All Features) Train")
print_metrics(yf_test, adaline_full.predict_labels_pm1(Xf_test), "Iris (All Features) Test")


perc = Perceptron(max_iter=1000, tol=1e-3, random_state=0)
perc.fit(Xi_train, to01(yi_train))
y_pred_perc = perc.predict(Xi_test)

print("=== Perceptron (Iris Test) ===")
print("Accuracy :", accuracy_score(to01(yi_test), y_pred_perc))
print("Confusion:\n", confusion_matrix(to01(yi_test), y_pred_perc))
print("Precision:", precision_score(to01(yi_test), y_pred_perc, zero_division=0))
print("Recall   :", recall_score(to01(yi_test), y_pred_perc, zero_division=0))
print("F1-score :", f1_score(to01(yi_test), y_pred_perc, zero_division=0))'''
    print(code)

def flowlab4():
    """Complete Lab 4: Multi-Layer Perceptron"""
    code = '''from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from sklearn.metrics import RocCurveDisplay, mean_squared_error, mean_absolute_error, r2_score
from torch.utils.data import TensorDataset, random_split, DataLoader
import torch
import torch.nn as nn

X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([[0], [1], [1], [0]])

W1 = np.random.randn(2, 2) * 0.01
b1 = np.zeros((1, 2))
W2 = np.random.randn(2, 1) * 0.01
b2 = np.zeros((1, 1))
lr = 0.5
epochs = 10000

def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def sigmoid_derivative(x):
    return x * (1 - x)

for _ in range(epochs):
    z1 = np.dot(X, W1) + b1
    a1 = sigmoid(z1)
    z2 = np.dot(a1, W2) + b2
    y_pred = sigmoid(z2)
    loss = 0.5 * np.mean((y - y_pred) ** 2)

    delta2 = (y_pred - y) * sigmoid_derivative(y_pred)
    dW2 = np.dot(a1.T, delta2)
    db2 = np.sum(delta2, axis=0, keepdims=True)
    delta1 = np.dot(delta2, W2.T) * sigmoid_derivative(a1)
    dW1 = np.dot(X.T, delta1)
    db1 = np.sum(delta1, axis=0, keepdims=True)

    W2 -= lr * dW2
    b2 -= lr * db2
    W1 -= lr * dW1
    b1 -= lr * db1


print("Final predictions:")
for i in range(len(X)):
    print(f"Input: {X[i]}, Predicted: {y_pred[i][0]:.4f}, Actual: {y[i][0]}")

X = torch.tensor([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=torch.float32)
y = torch.tensor([[0], [1], [1], [0]], dtype=torch.float32)

model = nn.Sequential(
    nn.Linear(2, 2),
    nn.Sigmoid(),
    nn.Linear(2, 1),
    nn.Sigmoid()
)

criterion = nn.BCELoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.5)

losses = []
epochs = 1000
for epoch in range(epochs):
    outputs = model(X)
    loss = criterion(outputs, y)
    losses.append(loss.item())
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if epoch % 200 == 0:
        print(f"Epoch {epoch}, Loss: {loss.item():.4f}")

plt.plot(losses[-5:])
plt.title("Loss Curve (Last 5 Epochs)")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.show()

with torch.no_grad():
    predictions = model(X)
    print("Final predictions:")
    for i in range(len(X)):
        print(f"Input: {X[i].numpy()}, Predicted: {predictions[i][0]:.4f}, Actual: {y[i][0]}")

student_dataset = r'/content/student_dataset.csv'
df = pd.read_csv(student_dataset)

print(df.head())
print(df.info())

df = df.dropna()

numeric_columns = ['Age', 'distance to university (km)', 'Percent Attended']
df[numeric_columns] = (df[numeric_columns] - df[numeric_columns].mean()) / df[numeric_columns].std()

print(df.head())
print(df.info())

data_array = df.values
tensor_data = torch.from_numpy(data_array).float()
X, y = tensor_data[:, :-1], tensor_data[:, -1]
tensor_dataset = TensorDataset(X, y)

total_size = len(tensor_dataset)
train_size = int(0.8 * total_size)
test_size = total_size - train_size

batch_size = 32
epochs = 1200

train_dataset, test_dataset = random_split(
    tensor_dataset,
    [train_size, test_size],
    generator=torch.Generator().manual_seed(53)
)

print(f'Total dataset size: {total_size}, train size: {train_size}, test size: {test_size}')

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

model = nn.Sequential(
    nn.Linear(5, 4),
    nn.ReLU(),
    nn.Linear(4, 3),
    nn.ReLU(),
    nn.Linear(3, 1),
    nn.Sigmoid()
)

criterion = nn.BCELoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
model.train()

for epoch in range(epochs):
    for batch_idx, (data, target) in enumerate(train_loader):
        optimizer.zero_grad()
        outputs = model(data).flatten()
        loss = criterion(outputs, target)
        loss.backward()
        optimizer.step()


model.eval()

with torch.no_grad():
    total_correct = 0
    total_samples = 0
    test_loss = 0

    for data, target in test_loader:
        outputs = model(data).flatten()
        loss = criterion(outputs, target)
        test_loss += loss.item()

        pred = (outputs > 0.5).float()
        total_correct += pred.eq(target).sum().item()
        total_samples += target.size(0)

    test_loss /= len(test_loader)
    accuracy = 100. * total_correct / total_samples

    print(f'\nTest Set: Average Loss: {test_loss:.4f}, Accuracy: {accuracy:.2f}%')

df = pd.read_csv(r'titanic_dataset.csv')

print(df.head())
print(df.info())

df = df.dropna()

numeric_columns = ['Age', 'Fare']
df[numeric_columns] = (df[numeric_columns] - df[numeric_columns].mean()) / df[numeric_columns].std()
df['Sex'] = df['Sex'].map(lambda x: 1 if x == 'male' else 0)

df = df[['Pclass', 'Sex', 'Age', 'Fare', 'Survived']]

print(df.head())
print(df.info())

tensor_data = torch.from_numpy(df.values).float()
X, y = tensor_data[:, :-1], tensor_data[:, -1]
tensor_dataset = TensorDataset(X, y)

total_size = len(tensor_dataset)
train_size = int(0.8 * total_size)
test_size = total_size - train_size

batch_size = 32
epochs = 1000

train_dataset, test_dataset = random_split(
    tensor_dataset,
    [train_size, test_size],
    generator=torch.Generator().manual_seed(53)
)

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

model = nn.Sequential(
    nn.Linear(4, 5),
    nn.ReLU(),
    nn.Linear(5, 3),
    nn.ReLU(),
    nn.Linear(3, 1),
    nn.Sigmoid()
)

criterion = nn.BCELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
model.train()

for epoch in range(epochs):
    for data, target in train_loader:
        optimizer.zero_grad()
        output = model(data).squeeze()
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()

print('The model has been trained!')

model.eval()
all_predictions = []
all_targets = []
total_correct = 0
total_loss = 0
total_samples = 0

with torch.no_grad():
    for data, target in test_loader:
        batch_output = model(data).squeeze()
        batch_loss = criterion(batch_output, target)
        total_loss += batch_loss.item()

        probabilities = torch.sigmoid(batch_output)
        pred = (probabilities > 0.5).float()
        all_predictions.extend(probabilities.cpu().numpy())
        all_targets.extend(target.cpu().numpy())

        total_correct += pred.eq(target).sum().item()
        total_samples += len(data)

avg_loss = total_loss / len(test_loader)
test_accuracy = 100. * total_correct / total_samples

print(f'\nAverage Loss: {avg_loss:.4f}, Accuracy: {test_accuracy:.2f}%')

y_true = np.array(all_targets)
y_scores = np.array(all_predictions)
RocCurveDisplay.from_predictions(y_true, y_scores)
plt.title("ROC Curve")
plt.show()

df = pd.read_csv(r'/content/house_prices.csv')

print(df.head())
print(df.columns)
print(df.info())

keep_columns = ['LotFrontage', 'LotArea', 'OverallQual', 'OverallCond',
                'MasVnrArea', 'TotalBsmtSF', 'GrLivArea', 'PoolArea',
                'MiscVal', 'SalePrice']
df = df[keep_columns]

df = df.dropna()

continuous_features = ['LotFrontage', 'LotArea', 'MasVnrArea',
                      'TotalBsmtSF', 'GrLivArea', 'PoolArea', 'MiscVal']
discrete_features = ['OverallQual', 'OverallCond']
df[continuous_features] = (df[continuous_features] - df[continuous_features].mean()) / df[continuous_features].std()
df[discrete_features] = df[discrete_features].astype(np.float64)

print(df.head())
print('\n')
print(df.info())

dataset = torch.from_numpy(df.values).float()
X, y = dataset[:, :-1], dataset[:, -1]
tensor_dataset = TensorDataset(X, y)

total_size = len(tensor_dataset)
train_size = int(0.8 * total_size)
test_size = total_size - train_size

batch_size = 32
epochs = 1000

train_dataset, test_dataset = random_split(
    tensor_dataset,
    [train_size, test_size],
    generator=torch.Generator().manual_seed(53)
)

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

model = nn.Sequential(
    nn.Linear(9, 6),
    nn.ReLU(),
    nn.Linear(6, 9),
    nn.ReLU(),
    nn.Linear(9, 3),
    nn.ReLU(),
    nn.Linear(3, 1),
)

criterion = nn.MSELoss()
optimizer = torch.optim.RMSprop(model.parameters(), lr=0.01)
model.train()

for epoch in range(epochs):
    for data, target in train_loader:
        optimizer.zero_grad()
        batch_outputs = model(data).squeeze()
        batch_loss = criterion(batch_outputs, target)
        batch_loss.backward()
        optimizer.step()

print('The model has been trained!')

model.eval()
all_predictions = []
all_targets = []
total_loss = 0

with torch.no_grad():
    for data, target in test_loader:
        batch_outputs = model(data).squeeze()
        batch_loss = criterion(batch_outputs, target)
        total_loss += batch_loss.item()
        all_predictions.extend(batch_outputs.cpu().numpy())
        all_targets.extend(target.cpu().numpy())

avg_loss = total_loss / len(test_loader)
mse = mean_squared_error(all_targets, all_predictions)
mae = mean_absolute_error(all_targets, all_predictions)
r2 = r2_score(all_targets, all_predictions)

print(f'\nAverage Loss: {avg_loss:.4f}, MSE: {mse:.2f}, MAE: {mae:.2f}, R²: {r2:.4f}')'''
    print(code)

def flowlab5():
    """Complete Lab 5: CNN Fashion-MNIST"""
    code = '''import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

train_data = datasets.FashionMNIST(root='./data', train=True, download=True, transform=transform)
test_data = datasets.FashionMNIST(root='./data', train=False, download=True, transform=transform)

train_loader = DataLoader(train_data, batch_size=64, shuffle=True)
test_loader = DataLoader(test_data, batch_size=1000, shuffle=False)

class FashionCNN(nn.Module):
    def __init__(self):
        super(FashionCNN, self).__init__()

        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.pool1 = nn.MaxPool2d(2, 2)

        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.pool2 = nn.MaxPool2d(2, 2)


        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.pool1(F.relu(self.bn1(self.conv1(x))))
        x = self.pool2(F.relu(self.bn2(self.conv2(x))))
        x = x.view(-1, 64 * 7 * 7)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

model = FashionCNN()

criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

epochs = 100
train_losses = []
test_accuracies = []
train_accuracies = []

for epoch in range(epochs):
    model.train()
    running_loss = 0.0
    correct_train = 0
    total_train = 0

    for images, labels in train_loader:
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total_train += labels.size(0)
        correct_train += (predicted == labels).sum().item()

    model.eval()
    correct_test = 0
    total_test = 0
    with torch.no_grad():
        for images, labels in test_loader:
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total_test += labels.size(0)
            correct_test += (predicted == labels).sum().item()

    train_acc = 100 * correct_train / total_train
    test_acc = 100 * correct_test / total_test
    train_losses.append(running_loss / len(train_loader))
    train_accuracies.append(train_acc)
    test_accuracies.append(test_acc)


plt.plot(train_losses, label='Training Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Training Loss per Epoch')
plt.legend()
plt.show()

#  POST LAB TASKS

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import numpy as np
import random



device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

train_dataset = torchvision.datasets.FashionMNIST(root='./data', train=True, transform=transform, download=True)
test_dataset = torchvision.datasets.FashionMNIST(root='./data', train=False, transform=transform, download=True)

train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=1000, shuffle=False)


# Task 1

class DeepCNN(nn.Module):
    def __init__(self):
        super(DeepCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding='same')
        self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding='same')
        self.bn2 = nn.BatchNorm2d(64)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding='same')
        self.bn3 = nn.BatchNorm2d(128)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(128 * 3 * 3, 256)
        self.fc2 = nn.Linear(256, 10)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)

    def forward(self, x):
        x = self.pool(self.relu(self.bn1(self.conv1(x))))
        x = self.pool(self.relu(self.bn2(self.conv2(x))))
        x = self.pool(self.relu(self.bn3(self.conv3(x))))
        x = x.view(-1, 128 * 3 * 3)
        x = self.dropout(self.relu(self.fc1(x)))
        x = self.fc2(x)
        return x


model = DeepCNN().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)


def train_model(model, optimizer, lr_label, epochs=10):
    train_losses, test_accuracies = [], []
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        train_losses.append(running_loss / len(train_loader))


        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for images, labels in test_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, preds = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (preds == labels).sum().item()
        test_acc = 100 * correct / total
        test_accuracies.append(test_acc)

        print(f"[{lr_label}] Epoch {epoch+1}/{epochs} | Loss: {train_losses[-1]:.4f} | Test Acc: {test_acc:.2f}%")
    return train_losses, test_accuracies


train_losses, test_accs = train_model(model, optimizer, "Task1", epochs=10)


# Task 2
model_lr = DeepCNN().to(device)
optimizer_lr = optim.SGD(model_lr.parameters(), lr=0.1, momentum=0.9)

lr_losses, lr_accs = train_model(model_lr, optimizer_lr, "LR=0.001", epochs=10)

plt.figure(figsize=(7,4))
plt.plot(train_losses, label='Original LR=0.01')
plt.plot(lr_losses, label='New LR=0.001')
plt.title("Learning Rate Comparison")
plt.xlabel("Epochs")
plt.ylabel("Training Loss")
plt.legend()
plt.show()



# Task 3

model_adam = DeepCNN().to(device)
optimizer_adam = optim.Adam(model_adam.parameters(), lr=0.001)

adam_losses, adam_accs = train_model(model_adam, optimizer_adam, "Adam", epochs=30)

plt.figure(figsize=(7,4))
plt.plot(lr_losses, label='SGD (LR=0.001)')
plt.plot(adam_losses, label='Adam')
plt.title("Optimizer Comparison")
plt.xlabel("Epochs")
plt.ylabel("Training Loss")
plt.legend()
plt.show()


# Task 4
classes = train_dataset.classes
y_true, y_pred = [], []

model_adam.eval()
with torch.no_grad():
    for images, labels in test_loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model_adam(images)
        _, preds = torch.max(outputs, 1)
        y_true.extend(labels.cpu().numpy())
        y_pred.extend(preds.cpu().numpy())

cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(8,6))
sns.heatmap(cm, annot=False, cmap='Blues', xticklabels=classes, yticklabels=classes)
plt.title("Confusion Matrix (Adam Model)")
plt.xlabel("Predicted")
plt.ylabel("True")
plt.show()


class_acc = cm.diagonal() / cm.sum(axis=1)
for i, acc in enumerate(class_acc):
    print(f"{classes[i]:<15}: {acc*100:.2f}%")


confused_pairs = np.unravel_index(np.argsort(cm, axis=None)[-20:], cm.shape)
pairs = list(zip(confused_pairs[0], confused_pairs[1]))
unique_confused = [(classes[i], classes[j]) for i, j in pairs if i != j][-3:]
print("\nTop 3 Confused Class Pairs:", unique_confused)

# Task 5
torch.save(model_adam.state_dict(), "fashion_cnn_adam.pth")


loaded_model = DeepCNN().to(device)
loaded_model.load_state_dict(torch.load("fashion_cnn_adam.pth"))
loaded_model.eval()


samples = random.sample(range(len(test_dataset)), 5)
plt.figure(figsize=(10,2))
for idx, i in enumerate(samples):
    image, label = test_dataset[i]
    with torch.no_grad():
        output = loaded_model(image.unsqueeze(0).to(device))
        pred = output.argmax(1).item()
    plt.subplot(1,5,idx+1)
    plt.imshow(image.squeeze(), cmap='gray')
    plt.title(f"T:{classes[label]}\nP:{classes[pred]}")
    plt.axis('off')
plt.show()
'''
    print(code)

def flowlab6():
    """Complete Lab 6: CNN Custom Filters"""
    code = '''import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Define custom filters
edge_filter = np.array([[ -1, -1, -1],
                        [ -1, 8, -1],
                        [ -1, -1, -1]])

vertical_filter = np.array([[ 1, 0, -1],
                            [ 1, 0, -1],
                            [ 1, 0, -1]])

horizontal_filter = np.array([[ 1, 1, 1],
                              [ 0, 0, 0],
                              [-1, -1, -1]])

smoothing_filter = np.array([[ 1, 1, 1],
                            [ 1, 1, 1],
                            [ 1, 1, 1]]) / 9.0

sharpening_filter = np.array([[ 0, -1, 0],
                              [-1, 5, -1],
                              [ 0, -1, 0]])

edge_filter = edge_filter.reshape((3,3,1,1))
vertical_filter = vertical_filter.reshape((3,3,1,1))
horizontal_filter = horizontal_filter.reshape((3,3,1,1))
smoothing_filter = smoothing_filter.reshape((3,3,1,1))
sharpening_filter = sharpening_filter.reshape((3,3,1,1))


image_path = "/content/2-dogs.jpg"
img = Image.open(image_path)
img_array = np.array(img)
img_array


img_array = img_array.astype('float32')
input_image = img_array.reshape(1,img_array.shape[0],img_array.shape[1],3)

plt.imshow(input_image[0,:,:,0])
plt.title("Original Image")
plt.axis('off')
plt.show()

input_image.shape

#Edge Model
edge_model = models.Sequential()
edge_model.add(layers.Conv2D(
    filters=1,
    kernel_size=(3, 3),
    input_shape=(input_image.shape[1],input_image.shape[2],1),
    use_bias=False
))
edge_model.layers[0].set_weights([edge_filter])

output_image = edge_model.predict(input_image)
plt.imshow(output_image[0,:,:,0],cmap='gray')
plt.axis('off')
plt.show()

#vertical Model
edge_model = models.Sequential()
edge_model.add(layers.Conv2D(
    filters=1,
    kernel_size=(3, 3),
    input_shape=(input_image.shape[1],input_image.shape[2],1),
    use_bias=False
))
edge_model.layers[0].set_weights([vertical_filter])

output_image = edge_model.predict(input_image)
plt.imshow(output_image[0,:,:,0],cmap='gray')
plt.axis('off')
plt.show()

#smoothing Model
edge_model = models.Sequential()
edge_model.add(layers.Conv2D(
    filters=1,
    kernel_size=(3, 3),
    input_shape=(input_image.shape[1],input_image.shape[2],1),
    use_bias=False
))
edge_model.layers[0].set_weights([smoothing_filter])

output_image = edge_model.predict(input_image)
plt.imshow(output_image[0,:,:,0],cmap='gray')
plt.axis('off')
plt.show()

#Sharpening Model
edge_model = models.Sequential()
edge_model.add(layers.Conv2D(
    filters=1,
    kernel_size=(3, 3),
    input_shape=(input_image.shape[1],input_image.shape[2],1),
    use_bias=False
))
edge_model.layers[0].set_weights([sharpening_filter])

output_image = edge_model.predict(input_image)
plt.imshow(output_image[0,:,:,0],cmap='gray')
plt.axis('off')
plt.show()'''
    print(code)

def flowlab7():
    """Complete Lab 7: Transfer Learning with ResNet18"""
    code = '''import torch
import torch.nn as nn
import torchvision.models as models
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt

transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=3),
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

train_data = datasets.FashionMNIST(root='./data', train=True, download=True, transform=transform)
test_data = datasets.FashionMNIST(root='./data', train=False, download=True, transform=transform)

train_loader = DataLoader(train_data, batch_size=64, shuffle=True)
test_loader = DataLoader(test_data, batch_size=1000, shuffle=False)

model = models.resnet18(pretrained=True)

for param in model.parameters():
    param.requires_grad = False

model.fc = nn.Linear(model.fc.in_features, 10)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.fc.parameters(), lr=0.01, momentum=0.9)

epochs = 10
train_losses = []
test_accuracies = []

for epoch in range(epochs):
    model.train()
    running_loss = 0.0
    
    for images, labels in train_loader:
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
    
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in test_loader:
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    test_acc = 100 * correct / total
    train_losses.append(running_loss / len(train_loader))
    test_accuracies.append(test_acc)
    
    print(f"Epoch {epoch+1}: Loss={train_losses[-1]:.4f}, Test Acc={test_acc:.2f}%")

plt.figure(figsize=(10,4))
plt.subplot(1,2,1)
plt.plot(train_losses, label='Training Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

plt.subplot(1,2,2)
plt.plot(test_accuracies, label='Test Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

torch.save(model.state_dict(), 'fashion_resnet18.pth')
'''
    print(code)

def flowoel1():
    """OEL Task 1: Healthcare Classification"""
    code = '''import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix
import matplotlib.pyplot as plt

file_path = '/content/healthcare_dataset.csv'
data = pd.read_csv(file_path)
print(data.head)

print(data.info())

data = pd.get_dummies(data, drop_first=True)

X = data.iloc[:, :-1].values
y = data.iloc[:, -1].values



scaler = StandardScaler()
X = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

X_train = torch.tensor(X_train, dtype=torch.float32)
X_test = torch.tensor(X_test, dtype=torch.float32)
y_train = torch.tensor(y_train, dtype=torch.float32).view(-1, 1)
y_test = torch.tensor(y_test, dtype=torch.float32).view(-1, 1)

input_size = X_train.shape[1]

model = nn.Sequential(
    nn.Linear(input_size, 16),
    nn.ReLU(),
    nn.Linear(16, 8),
    nn.ReLU(),
    nn.Linear(8, 1),
    nn.Sigmoid()
)


X_train.shape



loss_fn = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)


all_loss = []  # store loss values
epochs = 50

for i in range(epochs):
    y_pred = model(X_train)
    loss = loss_fn(y_pred, y_train)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    all_loss.append(loss.item())

    print("Epoch:", i+1, "Loss:", round(loss.item(), 4))

# Draw loss graph by Sohail
plt.figure(figsize=(5,4))
plt.plot(all_loss, marker='o')
plt.title("Loss over Epochs")
plt.xlabel("Epoch number")
plt.ylabel("Loss value")
plt.grid(True)
plt.show()


y_pred_test = model(X_test)
y_pred_labels = (y_pred_test > 0.5).float()


acc = accuracy_score(y_test, y_pred_labels)
cm = confusion_matrix(y_test, y_pred_labels)

print("Test Accuracy:", round(acc * 100, 2), "%")
print("Confusion Matrix:\n", cm)


y_pred_train = model(X_train)
train_labels = (y_pred_train > 0.5).float()

train_acc = accuracy_score(y_train, train_labels)
print("Train Accuracy:", round(train_acc * 100, 2), "%")


if train_acc - acc > 0.15:
    print("Model is OVERFITTING.")
elif train_acc < 0.7 and acc < 0.7:
    print("Model is UNDERFITTING.")
else:
    print("Model is GOOD.")
'''
    print(code)

def flowoel2():
    """OEL Task 2: Traffic Sign CNN"""
    code = '''from google.colab import drive
drive.mount('/content/drive')

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split
import matplotlib.pyplot as plt
import random






transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor()
])



data = datasets.ImageFolder("/content/drive/MyDrive/trafficnet_dataset_v1", transform=transform)
train_data, val_data = random_split(data, [int(0.8*len(data)), len(data)-int(0.8*len(data))])
train_loader = DataLoader(train_data, batch_size=32, shuffle=True)
val_loader = DataLoader(val_data, batch_size=32)


class CNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, 3)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(16, 32, 3)
        self.fc1 = nn.Linear(32 * 30 * 30, 64)
        self.drop = nn.Dropout(0.3)
        self.fc2 = nn.Linear(64, 4)
        self.softmax = nn.Softmax(dim=1)
    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        x = x.view(x.size(0), -1)
        x = torch.relu(self.fc1(x))
        x = self.drop(x)
        x = self.fc2(x)
        x = self.softmax(x)
        return x

model = CNN()
loss_fn = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=0.01)


train_accs, val_accs = [], []

for epoch in range(20):
    model.train()
    correct, total = 0, 0
    for imgs, labels in train_loader:
        optimizer.zero_grad()
        outputs = model(imgs)
        loss = loss_fn(outputs, labels)
        loss.backward()
        optimizer.step()
        _, preds = torch.max(outputs, 1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)
    train_acc = correct / total
    train_accs.append(train_acc)

    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for imgs, labels in val_loader:
            outputs = model(imgs)
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    val_acc = correct / total
    val_accs.append(val_acc)
    print(f"Epoch {epoch+1}: Train Acc={train_acc:.2f}, Val Acc={val_acc:.2f}")


plt.plot(train_accs, label='Train Acc')
plt.plot(val_accs, label='Val Acc')
plt.legend()
plt.show()

classes = data.classes
model.eval()
with torch.no_grad():
    for i in range(5):
        img, label = random.choice(val_data)
        plt.imshow(img.permute(1, 2, 0))
        output = model(img.unsqueeze(0))
        pred = torch.argmax(output, 1).item()
        plt.title(f"Predicted: {classes[pred]}")
        plt.show()
'''
    print(code)


def flowlab8():
    """Complete Lab 8: Autoencoders (Undercomplete, Denoising, Convolutional)"""
    code = '''import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import matplotlib.pyplot as plt

# Load MNIST dataset
transform = transforms.Compose([transforms.ToTensor()])
train_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
test_dataset = datasets.MNIST(root='./data', train=False, download=True, transform=transform)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

# Define Undercomplete Autoencoder
class UndercompleteAutoencoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(784, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, 784),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

# Train Undercomplete Autoencoder
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = UndercompleteAutoencoder().to(device)
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-8)

epochs = 20
losses = []

for epoch in range(epochs):
    for images, _ in train_loader:
        images = images.view(-1, 28 * 28).to(device)
        optimizer.zero_grad()
        reconstructed = model(images)
        loss = criterion(reconstructed, images)
        loss.backward()
        optimizer.step()
        losses.append(loss.item())
    
    if (epoch + 1) % 5 == 0:
        print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.6f}")

# Plot loss
plt.plot(losses)
plt.xlabel('Iterations')
plt.ylabel('Loss')
plt.title('Undercomplete Autoencoder Training Loss')
plt.show()

# Visualize reconstructions
model.eval()
dataiter = iter(test_loader)
images, _ = next(dataiter)
images_flat = images.view(-1, 28 * 28).to(device)

with torch.no_grad():
    reconstructed = model(images_flat)

fig, axes = plt.subplots(nrows=2, ncols=10, figsize=(10, 3))
for i in range(10):
    axes[0, i].imshow(images[i].squeeze().numpy(), cmap='gray')
    axes[0, i].axis('off')
    axes[1, i].imshow(reconstructed[i].cpu().numpy().reshape(28, 28), cmap='gray')
    axes[1, i].axis('off')
plt.show()

# Denoising Autoencoder
model_denoising = UndercompleteAutoencoder().to(device)
optimizer = optim.Adam(model_denoising.parameters(), lr=1e-3, weight_decay=1e-8)
noise_factor = 0.5

print("Training Denoising Autoencoder...")
for epoch in range(20):
    for images, _ in train_loader:
        images = images.view(-1, 28 * 28).to(device)
        noisy_images = images + noise_factor * torch.randn_like(images)
        noisy_images = torch.clamp(noisy_images, 0., 1.)
        
        optimizer.zero_grad()
        reconstructed = model_denoising(noisy_images)
        loss = criterion(reconstructed, images)
        loss.backward()
        optimizer.step()
    
    if (epoch + 1) % 5 == 0:
        print(f"Epoch [{epoch+1}/20], Loss: {loss.item():.6f}")

# Convolutional Autoencoder for FashionMNIST
fashion_train = datasets.FashionMNIST(root='./data', train=True, download=True, transform=transform)
fashion_test = datasets.FashionMNIST(root='./data', train=False, download=True, transform=transform)

fashion_train_loader = DataLoader(fashion_train, batch_size=64, shuffle=True)
fashion_test_loader = DataLoader(fashion_test, batch_size=64, shuffle=False)

class ConvAutoencoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(1, 16, 3, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(16, 32, 3, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, 3, stride=2, padding=1),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(64, 32, 3, stride=2, padding=1, output_padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(32, 16, 3, stride=2, padding=1, output_padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(16, 1, 3, stride=2, padding=1, output_padding=1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

model_conv = ConvAutoencoder().to(device)
optimizer = optim.Adam(model_conv.parameters(), lr=1e-3)

print("Training Convolutional Autoencoder...")
for epoch in range(20):
    for images, _ in fashion_train_loader:
        images = images.to(device)
        optimizer.zero_grad()
        reconstructed = model_conv(images)
        loss = criterion(reconstructed, images)
        loss.backward()
        optimizer.step()
    
    if (epoch + 1) % 5 == 0:
        print(f"Epoch [{epoch+1}/20], Loss: {loss.item():.6f}")

print("Lab 8 Complete!")
'''
    print(code)


def flowlab9():
    """Complete Lab 9: Recurrent Neural Networks (RNN)"""
    code = '''import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, TensorDataset, random_split
import pandas as pd
import matplotlib.pyplot as plt
from tensorflow.keras.datasets import imdb
from tensorflow.keras.preprocessing.sequence import pad_sequences

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# In-lab: QA Dataset
df = pd.read_csv("100_Unique_QA_Dataset.csv")

def tokenize(text):
    text = text.lower().replace('?','').replace("'","")
    return text.split()

vocab = {'<UNK>': 0}
def build_vocab(row):
    for token in tokenize(row['question']) + tokenize(row['answer']):
        if token not in vocab:
            vocab[token] = len(vocab)

df.apply(build_vocab, axis=1)
print(f"Vocab Size: {len(vocab)}")

def text_to_indices(text, vocab):
    return [vocab.get(token, vocab['<UNK>']) for token in tokenize(text)]

class QADataset(Dataset):
    def __init__(self, df, vocab):
        self.df = df
        self.vocab = vocab
    
    def __len__(self):
        return len(self.df)
    
    def __getitem__(self, idx):
        question = text_to_indices(self.df.iloc[idx]['question'], self.vocab)
        answer = text_to_indices(self.df.iloc[idx]['answer'], self.vocab)
        return torch.tensor(question), torch.tensor(answer)

class SimpleRNN(nn.Module):
    def __init__(self, vocab_size):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, 50)
        self.rnn = nn.RNN(50, 64, batch_first=True)
        self.fc = nn.Linear(64, vocab_size)
    
    def forward(self, x):
        embeds = self.embedding(x)
        output, hidden = self.rnn(embeds)
        return self.fc(output[:, -1, :])

dataset = QADataset(df, vocab)
dataloader = DataLoader(dataset, batch_size=1, shuffle=True)

model = SimpleRNN(len(vocab)).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

print("Training QA RNN...")
for epoch in range(50):
    total_loss = 0
    for question, answer in dataloader:
        question, answer = question.to(device), answer.to(device)
        optimizer.zero_grad()
        output = model(question)
        loss = criterion(output, answer[0])
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    
    if (epoch + 1) % 10 == 0:
        print(f"Epoch {epoch+1}, Loss: {total_loss:.4f}")

# Post-lab: IMDB Sentiment Analysis
VOCAB_SIZE = 10000
MAX_LEN = 200
BATCH_SIZE = 64

(X_train, y_train), (X_test, y_test) = imdb.load_data(num_words=VOCAB_SIZE)
X_train = pad_sequences(X_train, maxlen=MAX_LEN, padding='pre')
X_test = pad_sequences(X_test, maxlen=MAX_LEN, padding='pre')

train_dataset = TensorDataset(
    torch.tensor(X_train, dtype=torch.long),
    torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
)
test_dataset = TensorDataset(
    torch.tensor(X_test, dtype=torch.long),
    torch.tensor(y_test, dtype=torch.float32).unsqueeze(1)
)

train_size = int(0.8 * len(train_dataset))
val_size = len(train_dataset) - train_size
train_set, val_set = random_split(train_dataset, [train_size, val_size])

train_loader = DataLoader(train_set, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_set, batch_size=BATCH_SIZE, shuffle=False)

class SentimentRNN(nn.Module):
    def __init__(self, vocab_size):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, 32, padding_idx=0)
        self.rnn = nn.RNN(32, 64, batch_first=True)
        self.fc = nn.Linear(64, 1)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        embeds = self.embedding(x)
        rnn_out, _ = self.rnn(embeds)
        out = self.fc(rnn_out[:, -1, :])
        return self.sigmoid(out)

model = SentimentRNN(VOCAB_SIZE).to(device)
criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

print("Training Sentiment RNN...")
for epoch in range(10):
    model.train()
    for X_batch, y_batch in train_loader:
        X_batch, y_batch = X_batch.to(device), y_batch.to(device)
        optimizer.zero_grad()
        outputs = model(X_batch)
        loss = criterion(outputs, y_batch)
        loss.backward()
        optimizer.step()
    
    model.eval()
    val_correct = 0
    val_total = 0
    with torch.no_grad():
        for X_batch, y_batch in val_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            outputs = model(X_batch)
            predicted = (outputs > 0.5).float()
            val_correct += (predicted == y_batch).sum().item()
            val_total += y_batch.size(0)
    
    val_acc = 100 * val_correct / val_total
    print(f"Epoch {epoch+1}, Val Accuracy: {val_acc:.2f}%")

print("Lab 9 Complete!")
'''
    print(code)


def flowlab10():
    """Complete Lab 10: LSTM for Next Word Prediction"""
    code = '''import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import string

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Sample FAQ text
raw_text = """
The Data Science Mentorship Program follows a monthly subscription model in which students 
are required to make a payment of Rs. 799 per month. The total duration of the program is 
seven months, which makes the complete fee approximately Rs. 5600.
"""

def tokenize_text(text):
    text = text.casefold()
    cleaned = "".join([c for c in text if c not in string.punctuation])
    return cleaned.split()

def make_vocab(tokens):
    vocab = {"<pad>": 0, "<unk>": 1}
    for word in sorted(set(tokens)):
        if word not in vocab:
            vocab[word] = len(vocab)
    return vocab

tokens = tokenize_text(raw_text)
vocab = make_vocab(tokens)
idx_to_word = {v: k for k, v in vocab.items()}

# Create sequences
sequence_length = 5
input_sequences = []

for i in range(len(tokens) - sequence_length):
    seq = [vocab[w] for w in tokens[i:i + sequence_length]]
    input_sequences.append(seq)

data_tensor = torch.tensor(input_sequences, dtype=torch.long)
X = data_tensor[:, :-1]
y = data_tensor[:, -1]

class NextWordDataset(Dataset):
    def __init__(self, X, y):
        self.X = X
        self.y = y
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

train_size = int(0.8 * len(X))
val_size = len(X) - train_size

dataset = NextWordDataset(X, y)
train_set, val_set = torch.utils.data.random_split(dataset, [train_size, val_size])

train_loader = DataLoader(train_set, batch_size=32, shuffle=True)
val_loader = DataLoader(val_set, batch_size=32, shuffle=False)

class NextWordLSTM(nn.Module):
    def __init__(self, vocab_size, embed_dim=64, hidden_dim=100):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)
    
    def forward(self, x):
        embeds = self.embedding(x)
        lstm_out, _ = self.lstm(embeds)
        out = self.fc(lstm_out[:, -1, :])
        return out

model = NextWordLSTM(len(vocab)).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

print("Training Next-Word LSTM...")
for epoch in range(50):
    model.train()
    for X_batch, y_batch in train_loader:
        X_batch, y_batch = X_batch.to(device), y_batch.to(device)
        optimizer.zero_grad()
        outputs = model(X_batch)
        loss = criterion(outputs, y_batch)
        loss.backward()
        optimizer.step()
    
    if (epoch + 1) % 10 == 0:
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                outputs = model(X_batch)
                loss = criterion(outputs, y_batch)
                val_loss += loss.item()
        print(f"Epoch {epoch+1}, Val Loss: {val_loss/len(val_loader):.4f}")

# Prediction function
def predict_next_word(seed_text, model, vocab, idx_to_word, seq_len=4):
    model.eval()
    tokens = tokenize_text(seed_text)[-seq_len:]
    indices = [vocab.get(w, vocab['<unk>']) for w in tokens]
    
    while len(indices) < seq_len:
        indices.insert(0, vocab['<pad>'])
    
    input_tensor = torch.tensor([indices], dtype=torch.long).to(device)
    
    with torch.no_grad():
        output = model(input_tensor)
        _, predicted_idx = torch.max(output, 1)
    
    return idx_to_word.get(predicted_idx.item(), '<unk>')

# Test prediction
test_text = "the data science mentorship"
predicted = predict_next_word(test_text, model, vocab, idx_to_word)
print(f"Input: '{test_text}'")
print(f"Predicted next word: '{predicted}'")

print("Lab 10 Complete!")
'''
    print(code)


def flowlab8():
    """Complete Lab 8: Autoencoders (Undercomplete, Denoising, Convolutional)"""
    from ._lab_code import LAB_CODE
    code = LAB_CODE.get(8, "Lab 8 code not found")
    print(code)


def flowlab9():
    """Complete Lab 9: Recurrent Neural Networks (RNN) & IMDB Sentiment"""
    from ._lab_code import LAB_CODE
    code = LAB_CODE.get(9, "Lab 9 code not found")
    print(code)


def flowlab10():
    """Complete Lab 10: LSTM for Next Word Prediction"""
    from ._lab_code import LAB_CODE
    code = LAB_CODE.get(10, "Lab 10 code not found")
    print(code)


def flowlab11():
    """Complete Lab 11: GAN - Generative Adversarial Networks"""
    from ._lab_code import LAB_CODE
    code = LAB_CODE.get(11, "Lab 11 code not found")
    print(code)


def list_ann_labs():
    """List all available ANN lab functions"""
    labs = {
        1: "flowlab1() - PyTorch Tensor Operations",
        2: "flowlab2() - Perceptron Learning Algorithm",
        3: "flowlab3() - ADALINE Delta Rule",
        4: "flowlab4() - Multi-Layer Perceptron",
        5: "flowlab5() - CNN Fashion-MNIST Classification",
        6: "flowlab6() - CNN Custom Filters & Image Processing",
        7: "flowlab7() - Transfer Learning with ResNet18",
        8: "flowlab8() - Autoencoders (Undercomplete, Denoising, Convolutional)",
        9: "flowlab9() - Recurrent Neural Networks & IMDB Sentiment Analysis",
        10: "flowlab10() - LSTM for Next Word Prediction",
        11: "flowlab11() - GAN - Generative Adversarial Networks"
    }
    print("\n" + "=" * 70)
    print("AVAILABLE ANN LAB FUNCTIONS")
    print("=" * 70)
    for lab_id, description in labs.items():
        print(f"  Lab {lab_id:2}: {description}")
    print("=" * 70 + "\n")
