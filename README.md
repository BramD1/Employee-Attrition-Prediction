![Alt text](image.jpg.crdownload)

>source img: https://www.callcentrehelper.com/what-is-attrition-209083.htm
# 📊 Project Title: Employee Attrition Prediction
## 📝 Overview
This is a Data Science Project using a classification machine learning algorithm where I predict whether an employee would be attrited or not. Attrited by definition is when an employee were to exit a company by any causes. Companies will benefit more if they were to know an employee would be attrited before the attrition happened, because keeping an employee will be more cost effective than hiring new ones. This model can be useful for managers, or HR teams.

## Deployment Link (Hugging Face):
https://huggingface.co/spaces/Bram33/Employee_Attrition 

## 📂 Dataset
Source: https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset/data 

Size: 1470 rows × 35 columns

Description: This is IBM employee dataset that I gathered from Kaggle

## 🔧 Technologies Used
Programming Language: Python

Libraries: SciPy, Pandas, Seaborn, Matplotlib, NumPy, Joblib, Imbalanced-learn, Scikit-learn, XGBoost, Streamlit

Tools: Jupyter Notebook, Streamlit, Hugging Face

## 🚀 Workflow
### 1️ Data Loading
This is the part where I explore the data for a bit and found columns that are already encoded. These columns will be useful for the EDA and FE part.
### 2️ Exploratory Data Analysis 
I gathered insights that is used for business insight, as well as for the FE part:
1. The effect of business travel towards attrition, which has no correlation
2. Education level income comparison, where PhD holders have significantly higher income on average
3. Distribution of education background within the company
4. Distribution of gender within the department in the company
5. Correlation analysis of attrition and the numerical columns
6. Correlational analysis of attrition and the categorical columns
### 3 Feature Engineering
This is the part where I preprocess the data before training them in the model:
1. Feature Selection and Splitting
- In this part, I pick the columns that have correlation with attrition that is shown in the EDA part 5 & 6
- I also split the X and y variable in this part
2. Cardinality Check:
- This part is another feature selection where I check which categorical columns have the highest number of unique value and drop them
3. Splitting Train and Test:
- I set the testing size to be 15% of the dataset and the random state is 2
4. Handling Missing Values:
- I found no missing values within the dataset
5. Handling Outlier:
- I decide to not handle the outlier because the number of outlier is so little and the only column that has it seems to provide important information to be feed to the model
6. Pipeline:
- This part is where I preprocess the data so that I can have easier time transforming the data later in both the inference and deployment part
### 4 Model Training, Evaluation, and Tuning
1. Model Training:
- The models that I have trained are 5 in total: KNN, Decision Tree, Random Forrest, SVC, and XGBoost.
2. Model Evaluation:
- The model that seems to have the best score in our metric of interest is SVC.
3. Model Tuning:
- I used grid search to find the best parameter for my model
### 5 Model Saving
I saved the model, with the pipeline included using joblib
### 6 Inference and deployment
On the inference part, I test the model using a new data I made myself. The problem in the inference part and maybe at the deployment part is that the model cannot recognize age as an indicator of attrition if you take a look at the file `P1M2_Bramantyo_inf.ipynb`. The deployment folder consists of file needed to deploy the model that is made to Hugging Face.
### 7 Conclusion & Suggestion
The model that is developed has successfully reduce the number of false negative to only 4% which may make it reliable if used for the people inside the company. However, we cannot use this for potential candidates as seen within the inference file.

### 8 Update about deployment
api\ is the folder that consist of the modular python for deployment purposes. Trying how to learn to deploy model

The only suggestion for this model is that we need more data to convince the model that age is a significant factor for attrition.

## Thank You For Visiting!!

📬 Connect with me and give me feedback

💼 Linkedin: https://www.linkedin.com/in/bramantyo-anandaru-suyadi-0b9729208/ 