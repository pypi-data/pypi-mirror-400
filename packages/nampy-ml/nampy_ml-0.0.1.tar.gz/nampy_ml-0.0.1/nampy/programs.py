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
print("\\n--- Basic Data Exploration ---")
print("\\nMissing values:")
print(df_iris.isnull().sum())

print("\\nData types:")
print(df_iris.dtypes)

print("\\nSummary statistics:")
print(df_iris.describe())

# 3. Create visualizations
print("\\n--- Visualizations ---")

# Histograms
plt.figure(figsize=(12, 8))
for i, feature in enumerate(iris.feature_names):
    plt.subplot(2, 2, i + 1)
    sns.histplot(df_iris[feature], kde=True)
    plt.title(f'Histogram of {feature}')
plt.tight_layout()
plt.show()

# Scatter plot
plt.figure(figsize=(8, 6))
sns.scatterplot(
    x='sepal length (cm)',
    y='sepal width (cm)',
    hue='species',
    data=df_iris
)
plt.title('Scatter Plot of Sepal Length vs. Sepal Width')
plt.show()

# Box plots
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

url = "https://raw.githubusercontent.com/selva86/datasets/master/BostonHousing.csv"
df = pd.read_csv(url)

print(df.head())
print(df.info())
print(df.describe())

X = df[['rm']]
y = df['medv']

model = LinearRegression()
model.fit(X, y)

print(model.intercept_)
print(model.coef_[0])

y_pred = model.predict(X)

print(mean_squared_error(y, y_pred))
print(r2_score(y, y_pred))

plt.scatter(X, y)
plt.plot(X, y_pred)
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

data = load_breast_cancer()
X = data.data
y = data.target

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = LogisticRegression(max_iter=10000)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print(accuracy_score(y_test, y_pred))
print(precision_score(y_test, y_pred))
print(recall_score(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred, target_names=data.target_names))
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

iris = datasets.load_iris()
X = iris.data[:, :2]
y = iris.target

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

print("k-NN program for Iris dataset")
"""
    print(code)


def program5():
    code = """\
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier, plot_tree, export_text
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt
import pandas as pd

iris = load_iris()
X = pd.DataFrame(iris.data, columns=iris.feature_names)
y = pd.Series(iris.target)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

model = DecisionTreeClassifier(criterion="entropy", max_depth=3)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print(accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))
"""
    print(code)


def program6():
    code = """\
from sklearn import datasets
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

iris = datasets.load_iris()
X = iris.data

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(X_scaled)

print(kmeans.cluster_centers_)
"""
    print(code)


def program7():
    code = """\
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

digits = datasets.load_digits()

X_train, X_test, y_train, y_test = train_test_split(
    digits.data, digits.target, test_size=0.3, random_state=42
)

sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

svm = SVC(kernel="rbf", gamma=0.05, C=10)
svm.fit(X_train, y_train)

print("SVM program")
"""
    print(code)


def program8():
    code = """\
from sklearn.datasets import fetch_openml
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import numpy as np

mnist = fetch_openml("mnist_784", version=1)
X = mnist.data
y = mnist.target.astype(int)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

pca = PCA(n_components=50)
X_pca = pca.fit_transform(X_scaled)

print("PCA on MNIST")
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
