# ML

def ml_help():
    print(
        '''
    Welcome to the ML Practicals CLI! 🚀

    This tool allows you to print the code for various machine learning practicals.
    You can run any command either directly from your terminal or by calling its
    function within a Python environment.

    =========================
    == General Commands    ==
    =========================
    
    Command: ml-help
    Function: ml_help()
    Description: Shows this help message.

    Command: ml-index
    Function: ml_index()
    Description: Displays the full list of practicals.

    =========================
    == Practical Commands  ==
    =========================

    --- Practical 1: Data Pre-processing ---
    ml-prac-1a      (ml_prac_1a)
    ml-prac-1b      (ml_prac_1b)
    ml-prac-1c      (ml_prac_1c)
    ml-prac-1d      (ml_prac_1d)

    --- Practical 2: Testing Hypothesis ---
    ml-prac-2a      (ml_prac_2a)

    --- Practical 3: Linear Models ---
    ml-prac-3a      (ml_prac_3a)
    ml-prac-3b      (ml_prac_3b)
    ml-prac-3c      (ml_prac_3c)
    
    --- Practical 4: Discriminative Models ---
    ml-prac-4a      (ml_prac_4a)
    ml-prac-4b      (ml_prac_4b)
    ml-prac-4c      (ml_prac_4c)
    ml-prac-4d      (ml_prac_4d)
    ml-prac-4e      (ml_prac_4e)
    ml-prac-4f      (ml_prac_4f)

    --- Practical 5: Generative Models ---
    ml-prac-5a      (ml_prac_5a)
    ml-prac-5b      (ml_prac_5b)

    --- Practical 6: Probabilistic Models ---
    ml-prac-6a      (ml_prac_6a)
    ml-prac-6b      (ml_prac_6b)

    --- Practical 7: Model Evaluation ---
    ml-prac-7a      (ml_prac_7a)
    ml-prac-7b      (ml_prac_7b)

    --- Practical 8: Bayesian Learning ---
    ml-prac-8a      (ml_prac_8a)

    --- Practical 9: Deep Generative Models ---
    ml-prac-9a      (ml_prac_9a)
        '''
    )

def ml_index():
    print(
        '''
1. Data Pre-processing and Exploration
    1a. Load a CSV dataset. Handle missing values, inconsistent formatting, and outliers.
    1b. Load a dataset, calculate descriptive summary statistics, create visualizations using different graphs, and identify potential features and target variables Note: Explore Univariate and Bivariate graphs (Matplotlib) and Seaborn for visualization.
    1c. Create or Explore datasets to use all pre-processing routines like label encoding, scaling and binerization.
    1d. Design a simple machine learning model to train the training instances and test the same.

2. Testing Hypothesis
    2a. Implement and demonstrate the find-s algorithm for finding the most specific hypothesis based on given set of training data samples. Read the training data from a. CSV file and generate the final specific hypothesis (Create your dataset).

3. Linear Models
    3a. Simple Linear Regression: Fit a linear regression model on a dataset. Interpret coefficients, make predictions, and evaluate performance using metrics like R-squared and MSE.
    3b. Multiple Linear Regression: Extend linear regression to multiple features. Handle feature selection and potential multi collinearity.
    3c. Regularized Linear Models (Ridge, Lasso, ElasticNet): Implement regression variants like LASSO aid Ridge on any generated dataset.

4. Discriminative Models
    4a. Logistic Regression: Perform binary classification using logistic regression. Calculate accuracy, precision, recall, and understand the ROC curve.
    4b. k-nearest Neighbor: Implement and demonstrate k-nearest Neighbor algorithm. Read the training data from .CSV file and build a model to classify the test sample. Print both correct and wrong predictions.
    4c. Decision Tree: Build decision tree classifier or regressor. Control hyperparameters like tree depth to avoid overfitting. Visualize the tree.
    4d. Support Vector Machine: Implement a Support Vector Machine for any relevant dataset.
    4e. Random Forest ensemble: Train the random forest ensemble. Experiment with the number of trees and feature sampling. Compare performance to a single decision tree.
    4f. Gradient Boosting machine: Implement a gradient boosting machine. Tune hyper parameters and explore feature importance.

5. Generative Models
    5a. Implement and demonstrate the working of a Naïve Bayesian classifier using a sample data set. Build the model to classify a test sample.
    5b. Implement Hidden Markov Models using hmmlearn.

6. Probabilistic Models
    6a. Implement Bayesian Linear Regression to explore prior and posterior distribution.
    6b. Implement Gaussian Mixture Models for density estimation and unsupervised clustering.

7. Model Evaluation and Hyperparameter Tuning
    7a. Implement cross-validation techniques (k-fold, stratified, etc.) for robust model evaluation.
    7b. Systematically explore combinations of hyperparameters to optimize model performance. (use grid and randomized search).

8. Bayesian learning
    8a. Implement Bayesian Learning using inferences.

9. Deep Generative Models
    9a. Set up a generator network to produce samples and a discriminator network to distinguish between real and generated data. (Use a simple dataset).

10. Model Deployment
    10a. Develop an API to deploy your model and perform predictions.
        '''
    )

def ml_prac_1a():
    print(
        '''
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Load Data
data = sns.load_dataset('titanic')
data.to_csv('titanic.csv', index=False)  # Save to CSV (for practical requirement)
df = pd.read_csv('titanic.csv')

# 2. Handle Missing Values
df['age'].fillna(df['age'].median(), inplace=True)
df['embarked'].fillna(df['embarked'].mode()[0], inplace=True)
df.drop(columns=['deck'], inplace=True)

# 3. Handle Inconsistent Formatting
df['sex'] = df['sex'].str.lower()
df['embarked'] = df['embarked'].str.upper()

# 4. Handle Outliers using IQR
Q1, Q3 = df['age'].quantile([0.25, 0.75])
IQR = Q3 - Q1
low, high = Q1 - 1.5*IQR, Q3 + 1.5*IQR
df['age'] = np.clip(df['age'], low, high)

# 5. Visualize
sns.boxplot(x=df['age'])
plt.title("Age after Outlier Handling")
plt.show()
        '''
    )

def ml_prac_1b():
    print(
        '''
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Load Data
df = sns.load_dataset('iris')

# 2. Summary Statistics
print(df.describe())

# 3. Univariate Visualization
sns.histplot(df['sepal_length'], kde=True)
plt.title("Sepal Length Distribution")
plt.show()

# 4. Bivariate Visualization
sns.scatterplot(x='sepal_length', y='petal_length', hue='species', data=df)
plt.title("Sepal vs Petal Length")
plt.show()
        '''
    )

def ml_prac_1c():
    print(
        '''
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.preprocessing import LabelEncoder, StandardScaler, Binarizer
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Load Data
iris = load_iris()
df = pd.DataFrame(iris.data, columns=iris.feature_names)
df['species'] = iris.target

# 2. Label Encoding
le = LabelEncoder()
df['species'] = le.fit_transform(df['species'])

# 3. Scaling
scaler = StandardScaler()
df_scaled = pd.DataFrame(scaler.fit_transform(df.iloc[:, :-1]), columns=iris.feature_names)

# 4. Binarization
binz = Binarizer(threshold=0.0)
df_bin = pd.DataFrame(binz.fit_transform(df_scaled), columns=iris.feature_names)

# 5. Visualize
sns.pairplot(pd.concat([df_scaled, df['species']], axis=1), hue='species')
plt.suptitle("Scaled Data Visualization", y=1.02)
plt.show()
        '''
    )

def ml_prac_1d():
    print(
        '''
import numpy
import matplotlib.pyplot as plt
numpy.random.seed(2)
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

x = numpy.random.normal(3,1,100)
y = numpy.random.normal(156,40,100)/x

plt.scatter(x,y)
plt.xlabel("X")
plt.ylabel("Y")
plt.title("Scatter Plot of X vs Y")
plt.show()

train_x = x[:80]
train_y = y[:80]
test_x = x[:20]
test_y = y[:20]

plt.scatter(train_x, train_y)
plt.xlabel("train_x")
plt.ylabel("train_y")
plt.title("Training Data Scatter Plot")
plt.show()

train_x,test_x,train_y,test_y = train_test_split(x,y,test_size=0.3)

plt.scatter(test_x,test_y)
plt.xlabel("test_x")
plt.ylabel("test_y")
plt.title("Test Data Scatter Plot")
plt.show()

mymodel = numpy.poly1d(numpy.polyfit(train_x, train_y,4))
myline = numpy.linspace(0,6,100)

plt.scatter(train_x, train_y)
plt.plot(myline, mymodel(myline))
plt.xlabel("train_x")
plt.ylabel("train_y")
plt.title("Polynomial Regression Fit on Training Data")
plt.show()
        '''
    )

def ml_prac_2a():
    print(
        '''
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load Data
# (Create a simple dataset and save as CSV)
data = {
    'Sky': ['Sunny', 'Sunny', 'Rainy', 'Sunny', 'Cloudy', 'Rainy'],
    'Temp': ['Warm', 'Cold', 'Warm', 'Warm', 'Warm', 'Cold'],
    'Humidity': ['Normal', 'High', 'High', 'Normal', 'Normal', 'High'],
    'Wind': ['Strong', 'Weak', 'Strong', 'Weak', 'Weak', 'Weak'],
    'Water': ['Warm', 'Warm', 'Cold', 'Warm', 'Cold', 'Cold'],
    'Forecast': ['Same', 'Change', 'Change', 'Same', 'Same', 'Change'],
    'EnjoySport': ['Yes', 'No', 'No', 'Yes', 'Yes', 'No']
}
df = pd.DataFrame(data)
df.to_csv('finds_dataset.csv', index=False)

# 2. Read Dataset
df = pd.read_csv('finds_dataset.csv')
print(df)

# 3. Select Positive Instances (EnjoySport = Yes)
positive = df[df['EnjoySport'] == 'Yes'].iloc[:, :-1].values

# 4. Implement Find-S Algorithm
hypothesis = list(positive[0])
for sample in positive[1:]:
    for i in range(len(hypothesis)):
        if hypothesis[i] != sample[i]:
            hypothesis[i] = '?'

print("\nFinal Specific Hypothesis:", hypothesis)

# 5. Visualization (Count of Attributes by Class)
sns.countplot(x='Sky', hue='EnjoySport', data=df)
plt.title("Sky vs EnjoySport")
plt.show()
        '''
    )

def ml_prac_3a():
    print(
        '''
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

# 1. Load Data
data = fetch_california_housing(as_frame=True)
df = data.frame[['MedInc', 'MedHouseVal']]

# 2. Split Data
X_train, X_test, y_train, y_test = train_test_split(df[['MedInc']], df[['MedHouseVal']], 
                                                    test_size=0.2, random_state=42)

# 3. Train Model
model = LinearRegression()
model.fit(X_train, y_train)

# 4. Evaluate
y_pred = model.predict(X_test)
print("Coefficient:", model.coef_[0])
print("Intercept:", model.intercept_)
print("R² Score:", r2_score(y_test, y_pred))
print("MSE:", mean_squared_error(y_test, y_pred))

# 5. Visualize
sns.scatterplot(x='MedInc', y='MedHouseVal', data=df.sample(500))
plt.plot(X_test, y_pred, color='red')
plt.title("Simple Linear Regression: Income vs House Value")
plt.show()
        '''
    )

def ml_prac_3b():
    print(
        '''
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

# 1. Load Data
data = fetch_california_housing(as_frame=True)
df = data.frame[['MedInc', 'HouseAge', 'AveRooms', 'AveOccup', 'MedHouseVal']]

# 2. Split Data
X = df[['MedInc', 'HouseAge', 'AveRooms', 'AveOccup']]
y = df['MedHouseVal']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Train Model
model = LinearRegression()
model.fit(X_train, y_train)

# 4. Evaluate
y_pred = model.predict(X_test)
print("Coefficients:", model.coef_)
print("Intercept:", model.intercept_)
print("R² Score:", r2_score(y_test, y_pred))
print("MSE:", mean_squared_error(y_test, y_pred))

# 5. Visualize
sns.heatmap(df.corr(), annot=True, cmap="coolwarm")
plt.title("Feature Correlation Heatmap")
plt.show()
        '''
    )

def ml_prac_3c():
    print(
        '''
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.metrics import r2_score, mean_squared_error

# 1. Load Data
data = load_diabetes(as_frame=True)
df = data.frame

# 2. Split Data
X = df.drop(columns=['target'])
y = df['target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Train Models
ridge = Ridge(alpha=1.0)
lasso = Lasso(alpha=0.1)
elastic = ElasticNet(alpha=0.1, l1_ratio=0.5)

ridge.fit(X_train, y_train)
lasso.fit(X_train, y_train)
elastic.fit(X_train, y_train)

# 4. Evaluate
models = {'Ridge': ridge, 'Lasso': lasso, 'ElasticNet': elastic}
results = {}
for name, model in models.items():
    y_pred = model.predict(X_test)
    results[name] = r2_score(y_test, y_pred)
    print(f"\n{name} Model")
    print("Coefficients:", model.coef_)
    print("R²:", r2_score(y_test, y_pred))
    print("MSE:", mean_squared_error(y_test, y_pred))

# 5. Visualize
sns.barplot(x=list(results.keys()), y=list(results.values()))
plt.title("Regularized Model Comparison (R² Score)")
plt.show()
        '''
    )

def ml_prac_4a():
    print(
        '''
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_curve, auc

# 1. Load Data
data = load_breast_cancer(as_frame=True)
X, y = data.data, data.target

# 2. Split Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Train Model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# 4. Evaluate
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred))
print("Recall:", recall_score(y_test, y_pred))

# 5. Visualize ROC
fpr, tpr, _ = roc_curve(y_test, model.predict_proba(X_test)[:, 1])
plt.plot(fpr, tpr, label=f"AUC = {auc(fpr, tpr):.2f}")
plt.plot([0, 1], [0, 1], 'r--')
plt.title("ROC Curve - Logistic Regression")
plt.legend()
plt.show()
        '''
    )

def ml_prac_4b():
    print(
        '''
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.decomposition import PCA

wine = load_wine()
df = pd.DataFrame(wine.data, columns=wine.feature_names)
df['target'] = wine.target

df.to_csv("wine_dataset.csv", index=False)
data = pd.read_csv("wine_dataset.csv")

X = data.drop("target", axis=1)
y = data["target"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = KNeighborsClassifier(n_neighbors=5)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))

results = pd.DataFrame({"Actual": y_test, "Predicted": y_pred})
results["Match"] = results["Actual"] == results["Predicted"]
print("\\n✅ Correct Predictions:\\n", results[results["Match"]])
print("\\n❌ Wrong Predictions:\\n", results[~results["Match"]])

plt.figure(figsize=(6, 4))
sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d', cmap='OrRd',
            xticklabels=wine.target_names, yticklabels=wine.target_names)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.show()

pca = PCA(n_components=2)
X_test_pca = pca.fit_transform(X_test)

plt.figure(figsize=(8, 5))
scatter = plt.scatter(X_test_pca[:, 0], X_test_pca[:, 1], c=y_pred, cmap='plasma', edgecolor='k', s=100)
plt.xlabel("PCA Component 1")
plt.ylabel("PCA Component 2")
plt.title("KNN Predictions (PCA 2D)")
plt.legend(handles=scatter.legend_elements()[0], labels=list(wine.target_names))
plt.grid(True)
plt.show()
        '''
    )

def ml_prac_4c():
    print(
        '''
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

# 1. Load Data
data = load_iris()
X, y = data.data, data.target

# 2. Split Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Train Model
tree = DecisionTreeClassifier(max_depth=3, random_state=42)
tree.fit(X_train, y_train)

# 4. Evaluate
y_pred = tree.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))

# 5. Visualize Tree
plt.figure(figsize=(10,5))
plot_tree(tree, feature_names=data.feature_names, class_names=data.target_names, filled=True)
plt.title("Decision Tree Visualization")
plt.show()
        '''
    )

def ml_prac_4d():
    print(
        '''
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

# 1. Load Data
data = load_iris(as_frame=True)
df = data.frame

# 2. Split Data
X_train, X_test, y_train, y_test = train_test_split(
    df[data.feature_names], df['target'], test_size=0.2, random_state=42)

# 3. Train Model
svm = SVC(kernel='rbf', gamma='scale')
svm.fit(X_train, y_train)

# 4. Evaluate
y_pred = svm.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))

# 5. Simple Visualization using Seaborn pairplot
df_vis = df.copy()
df_vis['predicted'] = svm.predict(df[data.feature_names])

sns.pairplot(df_vis, vars=data.feature_names[:2], hue='predicted', palette='Set2')
plt.suptitle("SVM Classification Visualization", y=1.02)
plt.show()
        '''
    )

def ml_prac_4e():
    print(
        '''
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

# 1. Load Data
data = load_iris()
X, y = data.data, data.target

# 2. Split Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Train Models
from sklearn.tree import DecisionTreeClassifier
tree = DecisionTreeClassifier(random_state=42)
forest = RandomForestClassifier(n_estimators=100, random_state=42)
tree.fit(X_train, y_train)
forest.fit(X_train, y_train)

# 4. Evaluate
print("Decision Tree Accuracy:", accuracy_score(y_test, tree.predict(X_test)))
print("Random Forest Accuracy:", accuracy_score(y_test, forest.predict(X_test)))

# 5. Visualize Feature Importance
plt.barh(data.feature_names, forest.feature_importances_)
plt.title("Feature Importance - Random Forest")
plt.show()
        '''
    )

def ml_prac_4f():
    print(
        '''
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

# 1. Load Data
data = load_breast_cancer()
X, y = data.data, data.target

# 2. Split Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Train Model
gbm = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
gbm.fit(X_train, y_train)

# 4. Evaluate
y_pred = gbm.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))

# 5. Visualize Feature Importance
plt.barh(data.feature_names, gbm.feature_importances_, )
plt.title("Feature Importance - Gradient Boosting")
plt.show()
        '''
    )

def ml_prac_5a():
    print(
        '''
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Load Data
data = load_iris()
X, y = data.data, data.target

# 2. Split Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Train Model
nb = GaussianNB()
nb.fit(X_train, y_train)

# 4. Evaluate
y_pred = nb.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Test Sample Prediction:", nb.predict([X_test[0]]))

# 5. Visualize
sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d', cmap='Blues')
plt.title("Naïve Bayes Confusion Matrix")
plt.show()
        '''
    )

def ml_prac_5b():
    print(
        '''
import numpy as np
from hmmlearn import hmm

model = hmm.GaussianHMM(n_components=2, covariance_type="diag", n_iter=100)

X = np.array([[1.0], [2.0], [3.0], [2.0], [1.0],
              [6.0], [7.0], [8.0], [7.0], [6.0]])

lengths = [len(X)]

model.fit(X, lengths)

hidden_states = model.predict(X)

print("Hidden States:", hidden_states)

X_new, Z_new = model.sample(5)
print("\\nGenerated sequence of observations:\\n", X_new)
print("Generated hidden states:\\n", Z_new)
        '''
    )

def ml_prac_6a():
    print(
        '''
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.linear_model import BayesianRidge
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import numpy as np

# 1. Load Data
data = load_diabetes()
X, y = data.data, data.target

# 2. Split Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Train Model
model = BayesianRidge()
model.fit(X_train, y_train)

# 4. Evaluate
y_pred = model.predict(X_test)
print("R² Score:", r2_score(y_test, y_pred))
print("MSE:", mean_squared_error(y_test, y_pred))

# 5. Visualize Coefficient Uncertainty
plt.figure(figsize=(8,4))
plt.bar(range(len(model.coef_)), model.coef_, yerr=model.sigma_.diagonal()[:len(model.coef_)], alpha=0.6)
plt.title("Bayesian Regression Coefficients with Uncertainty")
plt.xlabel("Feature Index")
plt.ylabel("Coefficient Value")
plt.show()
        '''
    )

def ml_prac_6b():
    print(
        '''
from sklearn.datasets import make_blobs
from sklearn.mixture import GaussianMixture
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Generate Data
X, _ = make_blobs(n_samples=300, centers=3, cluster_std=1.0, random_state=42)

# 2. Initialize Model
gmm = GaussianMixture(n_components=3, random_state=42)

# 3. Train Model
gmm.fit(X)
labels = gmm.predict(X)

# 4. Evaluate (Cluster Centers)
print("Cluster Means:\n", gmm.means_)

# 5. Visualize Clusters
sns.scatterplot(x=X[:,0], y=X[:,1], hue=labels, palette='viridis')
plt.title("Gaussian Mixture Clustering Results")
plt.show()
        '''
    )

def ml_prac_7a():
    print(
        '''
from sklearn.datasets import load_iris
from sklearn.model_selection import KFold, StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
import numpy as np

# 1. Load Data
data = load_iris()
X, y = data.data, data.target

# 2. Initialize Model
model = LogisticRegression(max_iter=1000)

# 3. K-Fold Cross Validation
kf = KFold(n_splits=5, shuffle=True, random_state=42)
kf_scores = cross_val_score(model, X, y, cv=kf)
print("K-Fold Scores:", kf_scores)
print("Mean Accuracy (K-Fold):", np.mean(kf_scores))

# 4. Stratified K-Fold Cross Validation
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
skf_scores = cross_val_score(model, X, y, cv=skf)
print("\nStratified K-Fold Scores:", skf_scores)
print("Mean Accuracy (Stratified):", np.mean(skf_scores))

# 5. Visualize
import matplotlib.pyplot as plt
plt.boxplot([kf_scores, skf_scores], labels=['K-Fold', 'Stratified'])
plt.title("Cross-Validation Accuracy Comparison")
plt.ylabel("Accuracy")
plt.show()
        '''
    )

def ml_prac_7b():
    print(
        '''
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

# 1. Load Data
data = load_iris()
X, y = data.data, data.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 2. Initialize Model
rf = RandomForestClassifier(random_state=42)

# 3. Define Parameter Grids
param_grid = {'n_estimators': [50, 100, 150], 'max_depth': [3, 5, None]}
param_dist = {'n_estimators': range(50, 200), 'max_depth': [2, 3, 5, None]}

# 4. Grid Search and Random Search
grid = GridSearchCV(rf, param_grid, cv=3)
grid.fit(X_train, y_train)
rand = RandomizedSearchCV(rf, param_distributions=param_dist, n_iter=5, cv=3, random_state=42)
rand.fit(X_train, y_train)

print("Best Grid Search Params:", grid.best_params_)
print("Best Random Search Params:", rand.best_params_)

# Evaluate on test set
grid_acc = accuracy_score(y_test, grid.predict(X_test))
rand_acc = accuracy_score(y_test, rand.predict(X_test))
print("\nGrid Search Accuracy:", grid_acc)
print("Random Search Accuracy:", rand_acc)

# 5. Visualize
plt.bar(["GridSearchCV", "RandomizedSearchCV"], [grid_acc, rand_acc], color=['skyblue', 'orange'])
plt.title("Accuracy Comparison after Hyperparameter Tuning")
plt.ylabel("Accuracy")
plt.show()
        '''
    )

def ml_prac_8a():
    print(
        '''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# Load Dataset
iris = load_iris()
X, y = iris.data, iris.target
df = pd.DataFrame(X, columns=iris.feature_names)
df['target'] = y
print(df.head())

# Split Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train Model
model = GaussianNB()
model.fit(X_train, y_train)

# Predict & Evaluate
y_pred = model.predict(X_test)
print("\nAccuracy:", round(accuracy_score(y_test, y_pred), 3))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# Visualizations
plt.figure(figsize=(5,4))
sns.countplot(x='target', data=df, palette='viridis')
plt.title("Class Distribution in Iris Dataset")
plt.show()

cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, cmap="Blues", xticklabels=iris.target_names, yticklabels=iris.target_names)
plt.title("Confusion Matrix - GaussianNB")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()
        '''
    )

def ml_prac_9a():
    print(
        '''
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt

def real_data(n=1000):
    return torch.randn(n, 1) * 1.5 + 2

class Generator(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(1, 8),
            nn.ReLU(),
            nn.Linear(8, 1)
        )
    def forward(self, z):
        return self.model(z)

class Discriminator(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(1, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()
        )
    def forward(self, x):
        return self.model(x)

G, D = Generator(), Discriminator()
criterion = nn.BCELoss()
opt_G = optim.Adam(G.parameters(), lr=0.01)
opt_D = optim.Adam(D.parameters(), lr=0.01)

epochs = 2000
for epoch in range(epochs):
    real = real_data(32)
    fake = G(torch.randn(32, 1))
    D_loss = criterion(D(real), torch.ones(32, 1)) + criterion(D(fake.detach()), torch.zeros(32, 1))
    opt_D.zero_grad()
    D_loss.backward()
    opt_D.step()

    fake = G(torch.randn(32, 1))
    G_loss = criterion(D(fake), torch.ones(32, 1))
    opt_G.zero_grad()
    G_loss.backward()
    opt_G.step()

    if epoch % 500 == 0:
        print(f"Epoch {epoch}, D_loss: {D_loss.item():.4f}, G_loss: {G_loss.item():.4f}")

real_samples = real_data(500).detach().numpy()
fake_samples = G(torch.randn(500, 1)).detach().numpy()

plt.hist(real_samples, bins=30, alpha=0.5, label="Real Data")
plt.hist(fake_samples, bins=30, alpha=0.5, label="Generated Data")
plt.legend()
plt.show()
        '''
    )

def ml_prac_10a():
    print(
        '''
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Load and Train Model
iris = load_iris()
X, y = iris.data, iris.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

model = LogisticRegression(max_iter=200)
model.fit(X_train, y_train)

print("Model trained with accuracy:", round(accuracy_score(y_test, model.predict(X_test)), 3))

# Create Flask App
app = Flask(__name__)

# Define Prediction Route
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    features = np.array(data['features']).reshape(1, -1)
    prediction = model.predict(features)[0]
    result = {'predicted_class': iris.target_names[prediction]}
    return jsonify(result)

# Run App
if __name__ == '__main__':
    app.run(debug=True)

# Test this by running this command from cmd:
curl -X POST http://127.0.0.1:5000/predict -H "Content-Type: application/json" -d "{\"features\":[5.1,3.5,1.4,0.2]}"
        '''
    )