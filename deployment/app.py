import pandas as pd
import streamlit as st
import joblib
import eda

navigation = st.sidebar.selectbox('Page:', ('Predictor','EDA'))

# select page
if navigation == 'EDA':
    eda.run()
    exit()

else:
    pass

def array_to_dataframe(X, columns):
      """Convert numpy array back to DataFrame for ColumnTransformer compatibility."""
      return pd.DataFrame(X, columns=columns)
with open('model_best.pkl', 'rb') as file_5:
 model_best = joblib.load(file_5)

def run():
    st.title("IBM Employee Attrition Prediction")
    st.image('https://www.executivegrapevine.com/uploads/articles/story-ibm-chief-says-staff-in-office-3-days-or-more.jpg',
            caption='source: IBM')

    st.markdown("### Repository Link: https://github.com/BramD1/Employee-Attrition-Prediction ")

    with st.form(key='form parameters'):
        name = st.text_input('Name of Employee')
        education = st.selectbox('Education level:', ('Highschool', 'College', 'Bachelor', 'Master', 'PhD'))
        Age = st.number_input("Employee's Age", min_value=0)
        DailyRate = st.number_input("Employee Rate Daily", min_value=0)
        DistanceFromHome = st.number_input("Employee's Distance from home", min_value=0)
        MonthlyIncome = st.number_input("Employee's monthly salary", min_value=0, step=1000)
        TotalWorkingYears = st.number_input("Employee's work experience", min_value=0)
        TrainingTimesLastYear = st.number_input("Employee's last year training time", min_value=0)
        YearsAtCompany = st.number_input("Length of time the employee has worked", min_value=0)
        BusinessTravel = st.selectbox('How often does the employee travel?', ('Travel_Rarely', 'Travel_Frequently', 'Non-Travel'))
        Department = st.selectbox('Which department the employee works?', ('Sales', 'Research & Development', 'Human Resources'))
        OverTime = st.selectbox('Does the employee do overtime?', ('Yes', 'No'))
        EnvironmentSatisfaction = st.slider('How did the employee rate the working environment?', 1,4)
        JobSatisfaction = st.slider('How satisfied was the employee with his/her job?', 1,4)
        StockOptionLevel = st.number_input("What is the stock option level of the employee?", min_value=0, max_value=3)
        WorkLifeBalance = st.slider('How did the employee rate the work life balance?', 1,4)

        submit = st.form_submit_button('Predict Attrition')

    data_raw = {
    'Name' : name,
    'Education': education,
    'Age': Age,
    'DailyRate': DailyRate,
    'DistanceFromHome': DistanceFromHome,
    'MonthlyIncome': MonthlyIncome,
    'TotalWorkingYears': TotalWorkingYears,
    'TrainingTimesLastYear': TrainingTimesLastYear,
    'YearsAtCompany': YearsAtCompany,
    'BusinessTravel': BusinessTravel,
    'Department': Department,
    'OverTime': OverTime,
    'EnvironmentSatisfaction': EnvironmentSatisfaction,
    'JobSatisfaction': JobSatisfaction,
    'StockOptionLevel': StockOptionLevel,
    'WorkLifeBalance':WorkLifeBalance ,
    }

    data = pd.DataFrame([data_raw])
    st.dataframe(data)
    if submit:
        result = model_best.predict(data)
        if result == 1:
            st.write(f'{name} will be attrited')
        
        else:
            st.write(f'{name} will not be attrited')
if __name__ == '__main__':
    run()
    
