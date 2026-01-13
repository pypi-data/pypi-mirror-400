def program1():
    code = """\
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris

# 1. Load the Iris dataset
iris = load_iris()
df_iris = pd.DataFrame(data=iris.data, columns=iris.feature_names)
df_iris['species'] = iris.target_names[iris.target]

print("Dataset loaded successfully.")

# 2. Perform basic data exploration
print("\n--- Basic Data Exploration ---")
print("\nMissing values:")
print(df_iris.isnull().sum())

print("\nData types:")
print(df_iris.dtypes)

print("\nSummary statistics:")
print(df_iris.describe())

# 3. Create visualizations
print("\n--- Visualizations ---")

# Histograms for numerical features
plt.figure(figsize=(12, 8))
for i, feature in enumerate(iris.feature_names):
    plt.subplot(2, 2, i + 1)
    sns.histplot(df_iris[feature], kde=True)
    plt.title(f'Histogram of {feature}')
plt.tight_layout()
plt.show()

# Scatter plot for relationships between features (e.g., sepal length vs. sepal width)
plt.figure(figsize=(8, 6))
sns.scatterplot(x='sepal length (cm)', y='sepal width (cm)', hue='species', data=df_iris)
plt.title('Scatter Plot of Sepal Length vs. Sepal Width')
plt.show()

# Box plots to understand distribution across species
plt.figure(figsize=(12, 8))
for i, feature in enumerate(iris.feature_names):
    plt.subplot(2, 2, i + 1)
    sns.boxplot(x='species', y=feature, data=df_iris)
    plt.title(f'Box Plot of {feature} by Species')
plt.tight_layout()
plt.show()
"""
    print(code)


def program2():
    code = """\
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
url = "https://raw.githubusercontent.com/selva86/datasets/master/BostonHousing.csv" df = pd.read_csv(url)
print("\n--- First 5 rows ---") print(df.head())
print("\n--- Data Info ---") print(df.info())
print("\n--- Summary Statistics ---") print(df.describe())
X = df[['rm']] # Feature must be 2D
y = df['medv'] # Target
model = LinearRegression() 
model.fit(X, y)
print("\nIntercept (b0):", model.intercept_) 
print("Slope (b1):", model.coef_[0])
y_pred = model.predict(X)
print("\nMean Squared Error:", mean_squared_error(y, y_pred)) print("R2 Score:", r2_score(y, y_pred))
# Regression Line Plot
plt.figure(figsize=(8,6))
plt.scatter(X, y, color='blue', alpha=0.6, label='Actual') plt.plot(X, y_pred, color='red', linewidth=2, label='Regression line') plt.xlabel("Average number of rooms per dwelling (RM)") plt.ylabel("Median home value (MEDV)")
plt.title("Simple Linear Regression: RM vs MEDV")
plt.legend()
plt.show()
# Residuals Plot
residuals = y - y_pred
plt.figure(figsize=(8,6))
plt.scatter(y_pred, residuals, color='purple', alpha=0.6) plt.axhline(y=0, color='black', linestyle='--') plt.xlabel("Predicted MEDV")
plt.ylabel("Residuals (Actual - Predicted)") plt.title("Residuals Plot")
plt.show()
"""
    print(code)


def program3():
    code = """\
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix, classification_report
data = load_breast_cancer() X = data.data
y = data.target
# Split dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
# Create Logistic Regression model
model = LogisticRegression(max_iter=10000) model.fit(X_train, y_train)
# Make predictions
y_pred = model.predict(X_test)
# Evaluate the model
accuracy = accuracy_score(y_test, y_pred) 
precision = precision_score(y_test, y_pred) 
recall = recall_score(y_test, y_pred) 
conf_matrix = confusion_matrix(y_test, y_pred)
# Print results
print("Logistic Regression Model Evaluation:") print(f"Accuracy: {accuracy:.4f}") print(f"Precision: {precision:.4f}") print(f"Recall: {recall:.4f}") print("\nConfusion Matrix:")
print(conf_matrix)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=data.target_names))
# Plot Confusion Matrix
plt.figure(figsize=(6,4))
sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues",
xticklabels=data.target_names, yticklabels=data.target_names) plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix - Logistic Regression") plt.show()

"""
    print(code)


def program4():
    code = """\
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

# 1️⃣ Load the Iris dataset
iris = datasets.load_iris()
X = iris.data[:, :2]   # Take only the first 2 features for 2D visualization
y = iris.target

# 2️⃣ Split into training and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# 3️⃣ Standardize the features for better k-NN performance
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

# Function to plot decision boundaries for different k values
def plot_decision_boundaries(k_values):
    h = 0.02  # step size in the mesh
    cmap_light = ListedColormap(['#FFAAAA', '#AAFFAA', '#AAAAFF'])
    cmap_bold = ['red', 'green', 'blue']

    x_min, x_max = X_train[:, 0].min() - 1, X_train[:, 0].max() + 1
    y_min, y_max = X_train[:, 1].min() - 1, X_train[:, 1].max() + 1

    xx, yy = np.meshgrid(
        np.arange(x_min, x_max, h),
        np.arange(y_min, y_max, h)
    )

    plt.figure(figsize=(15, 4))

    for i, k in enumerate(k_values):
        clf = KNeighborsClassifier(n_neighbors=k)
        clf.fit(X_train, y_train)

        Z = clf.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)

        plt.subplot(1, len(k_values), i + 1)
        plt.contourf(xx, yy, Z, alpha=0.4, cmap=cmap_light)
        plt.scatter(
            X_train[:, 0], X_train[:, 1],
            c=y_train, edgecolor='k', s=40,
            cmap=ListedColormap(cmap_bold)
        )
        plt.title(f"k = {k}")

    plt.suptitle("k-NN Decision Boundaries for Different k Values")
    plt.show()

# 4️⃣ Experiment with different k values and visualize
k_values = [1, 5, 15]
plot_decision_boundaries(k_values)

# 5️⃣ Evaluate accuracy for different k
print("Accuracy on Test Set:")
for k in k_values:
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X_train, y_train)

    y_pred = knn.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print(f"k = {k}: {acc:.2f}")

"""
    print(code)


def program5():
    code = """\
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier, plot_tree, export_text
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt

# Step 2: Load the dataset
iris = load_iris()
X = pd.DataFrame(iris.data, columns=iris.feature_names)
y = pd.Series(iris.target, name='target')

# Step 3: Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Step 4: Initialize and train the Decision Tree model
model = DecisionTreeClassifier(criterion='entropy', max_depth=3, random_state=42)
model.fit(X_train, y_train)

# Step 5: Make predictions
y_pred = model.predict(X_test)

# Step 6: Evaluate model performance
print("Decision Tree Classifier Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n",
      classification_report(y_test, y_pred, target_names=iris.target_names))

# Step 7: Visualize the Decision Tree
plt.figure(figsize=(12, 8))
plot_tree(
    model,
    feature_names=iris.feature_names,
    class_names=iris.target_names,
    filled=True,
    rounded=True,
    fontsize=10
)
plt.title("Decision Tree Visualization - Iris Dataset")
plt.show()

# Step 8: Display Decision Rules (Text Format)
print("\nDecision Rules:\n")
rules = export_text(model, feature_names=iris.feature_names)
print(rules)

"""
    print(code)


def program6():
    code = """\
# K-Means Clustering on Iris Dataset (without labels)

# Step 1: Import required libraries
import pandas as pd
import numpy as np
from sklearn import datasets
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

# Step 2: Load the Iris dataset (without labels)
iris = datasets.load_iris()
X = iris.data   # Only features, no target labels

# Step 3: Standardize the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Step 4: Apply K-Means clustering
kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(X_scaled)

# Step 5: Get cluster labels and centroids
labels = kmeans.labels_
centroids = kmeans.cluster_centers_

# Step 6: Visualize the clusters
plt.figure(figsize=(8, 6))
plt.scatter(X_scaled[:, 0], X_scaled[:, 1], c=labels, cmap='viridis', s=50)
plt.scatter(centroids[:, 0], centroids[:, 1], c='red', s=200, marker='X', label='Centroids')
plt.title("K-Means Clustering on Iris Dataset")
plt.xlabel("Feature 1 (standardized)")
plt.ylabel("Feature 2 (standardized)")
plt.legend()
plt.show()

# Step 7: Print cluster centers
print("Cluster Centers (Standardized Feature Space):\n", centroids)

# Step 8: Compare predicted clusters with actual labels (optional)
y_true = iris.target
print("\nActual Labels (0=setosa, 1=versicolor, 2=virginica):")
print(y_true[:10])

print("Predicted Cluster Labels:")
print(labels[:10])

"""
    print(code)


def program7():
    code = """\
# Support Vector Machine (SVM) for MNIST handwritten digit classification

from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt

# Step 1: Load MNIST dataset
digits = datasets.load_digits()

# Display basic info
print("Image Data Shape:", digits.data.shape)
print("Label Data Shape:", digits.target.shape)

# Step 2: Visualize some samples
plt.figure(figsize=(8, 4))
for index, (image, label) in enumerate(zip(digits.data[0:8], digits.target[0:8])):
    plt.subplot(2, 4, index + 1)
    plt.imshow(image.reshape(8, 8), cmap=plt.cm.gray)
    plt.title(f'Target: {label}')
plt.show()

# Step 3: Split dataset into train and test sets
X_train, X_test, y_train, y_test = train_test_split(
    digits.data, digits.target, test_size=0.3, random_state=42
)

# Step 4: Feature scaling
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Step 5: Train SVM classifier
svm_clf = SVC(kernel='rbf', gamma=0.05, C=10)
svm_clf.fit(X_train, y_train)

# Step 6: Predict test data
y_pred = svm_clf.predict(X_test)

# Step 7: Evaluate performance
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("Accuracy:", accuracy_score(y_test, y_pred))

# Step 8: Visualize some predictions
plt.figure(figsize=(8, 4))
for i in range(8):
    plt.subplot(2, 4, i + 1)
    plt.imshow(X_test[i].reshape(8, 8), cmap=plt.cm.gray)
    plt.title(f'Pred: {y_pred[i]} | True: {y_test[i]}')
plt.show()

"""
    print(code)


def program8():
    code = """\
# Principal Component Analysis (PCA) on MNIST Dataset

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_openml
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Step 1: Load MNIST dataset
print("Loading MNIST dataset...")
mnist = fetch_openml('mnist_784', version=1)
X = mnist.data
y = mnist.target.astype(int)

print("Dataset shape:", X.shape)

# Step 2: Standardize the data
print("Standardizing data...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Step 3: Apply PCA
pca = PCA(n_components=50)   # Reduce to 50 dimensions for visualization
X_pca = pca.fit_transform(X_scaled)

print("Reduced dataset shape:", X_pca.shape)

# Step 4: Plot explained variance ratio
plt.figure(figsize=(8, 5))
plt.plot(np.cumsum(pca.explained_variance_ratio_), marker='o')
plt.title('Explained Variance by Principal Components')
plt.xlabel('Number of Components')
plt.ylabel('Cumulative Explained Variance')
plt.grid(True)
plt.show()

# Step 5: Visualize first 2 principal components
plt.figure(figsize=(8, 6))
plt.scatter(X_pca[:10000, 0], X_pca[:10000, 1],
            c=y[:10000], cmap='tab10', s=10)

plt.colorbar(label='Digit Label')
plt.title('MNIST data projected onto first 2 Principal Components')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.show()

"""
    print(code)


def main():
    print("Choose program:")
    print("1 - Program 1")
    print("2 - Program 2")
    print("3 - Program 3")
    print("4 - Program 4")
    print("5 - Program 5")
    print("6 - Program 6")
    print("7 - Program 7")
    print("8 - Program 8")

    choice = input("Enter number: ")

    programs = {
        "1": program1,
        "2": program2,
        "3": program3,
        "4": program4,
        "5": program5,
        "6": program6,
        "7": program7,
        "8": program8,
    }

    if choice in programs:
        programs[choice]()
    else:
        print("Invalid choice")
