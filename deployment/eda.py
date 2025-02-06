import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

def run():
    st.title("IBM Employee Attrition Data Analysis")
    st.image('https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/IBM_logo.svg/1000px-IBM_logo.svg.png', caption='source: IBM')

    st.markdown("### Repository Link: https://github.com/BramD1/Employee-Attrition-Prediction ")

    st.write('# What is Atrrition?')
    st.image('https://www.teamly.com/blog/wp-content/uploads/2022/06/Types-of-Employee-Attrition.png',
    caption='source: teamly.com')
    st.write('''
    Attrition is when an employee leaves a company caused by resignation, being fired, death, and other types of reason that can cause him/her to be removed from the company. Attrition is different from turnover because turnover is when an employee leaves the company voluntarily. Companies use attrition rate to measure the number of employees leaving the organization. This rate will be seen by potential candidates who are looking to work for the company. This is why companies need to find ways to reduce it by identifying candidates that may be attrited or not.
    ''')

    st.write('---')

    palette = sns.color_palette('bright') 

    df = pd.read_csv('WA_Fn-UseC_-HR-Employee-Attrition.csv')

    st.write('## Company Gender Ratio ')
    st.write('The first EDA that I will show is the gender ratio within the company:')

    fig = plt.figure(figsize=(4,4))
    plt.pie(df['Gender'].value_counts(), labels=['Male', 'Female'], colors=palette, autopct='%.0f%%')

    st.pyplot(fig)
    st.write('''As you can see the pie chart below, this company is very male dominated. From the data gathered, the exact number of Male employee is 882, while Female employee is 588. 
            Below is an interactive pie chart to see the gender ratio of each department, and as you might expect, each of them are Male dominated.
            ''')


    st.write('### Department Gender Ratio ')
    st.write('You can select which department below you want to see the gender distribution of')
    option = st.selectbox('Department: ', ('Sales', 'Research & Development', 'Human Resources'))
    filtered_df = df[df['Department'] == option]
    fig = plt.figure(figsize=(4,4))
    plt.pie(filtered_df['Gender'].value_counts(), labels=['Male', 'Female'], colors=palette, autopct='%.0f%%')

    st.pyplot(fig)
    st.write('Although it may seems surprising, gender distribution is not an indicator of whether an employee is being attrited or not')
    st.write('---')


    st.write("## Employee Background Education")
    st.write("Second EDA will be about the diversity of the employee's background education:")
    fig = plt.figure(figsize=(4,4))
    plt.pie(df['EducationField'].value_counts(), labels=['Life Sciences', 'Other', 'Medical', 'Marketing',
        'Technical Degree', 'Human Resources'], colors=palette, autopct='%.0f%%')

    st.pyplot(fig)
    st.write("Because the category 'others' is the education background not being inputed, we cannot gather much insight regarding the diversity of education and the effect on employee being attrited.")

    st.write("### Background Education for Each Department")
    st.write('Here you can select to see the diversity of education for each department: ')
    option_edu = st.selectbox('Education Background for: ', ('Sales', 'Research & Development', 'Human Resources'))
    filtered_education_df = df[df['Department'] == option_edu]
    education_counts = filtered_education_df['EducationField'].value_counts()

    fig = plt.figure(figsize=(4, 4))
    plt.pie(education_counts, labels=education_counts.index, colors=palette[:len(education_counts)], autopct='%.0f%%')
    st.pyplot(fig)
    st.write('---')

    st.write('## Education Level Salary Distribution')
    st.write('For the final EDA, I will showcase the salary distribution of each education level from high school to PhD')
    df['level'] = df['Education'].astype(str).replace('1', 'Highschool').replace('2', 'College').replace('3', 'Bachelor').replace('4', 'Master').replace('5', 'PhD')
    option_edu_level = st.selectbox('Education level: ', ('Highschool', 'College', 'Bachelor', 'Master', 'PhD'))
    filtered_education_level = df[df['level'] == option_edu_level]
    fig= plt.figure(figsize=(4,4))
    sns.histplot(filtered_education_level['MonthlyIncome'], bins=20, kde=True)
    st.pyplot(fig)
    st.write('''
    For the exact average number of monthly salary for each education level:
    - Average sallary of workers with no college education: 5640.57
    - Average sallary of workers with some college education: 6226.65
    - Average sallary of workers with bachelor degree: 6517.26
    - Average sallary of workers with master degree: 6832.40
    - Average sallary of workers with doctoral degree: 8277.65
    ''')

if __name__ == '__main__':
    run()