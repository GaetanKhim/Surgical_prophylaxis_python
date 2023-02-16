#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  5 10:10:30 2021

@author: gaetan
"""

import numpy as np 
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")
st.set_option("deprecation.showPyplotGlobalUse", False)

surgical_prophylaxis_TK = pd.read_csv("Surgical_prophylaxis_data_Takeo.csv", error_bad_lines=False) 
        
#Below is the number of deduplicated files. Some patient had 2 operations and were incuded in the dataframe twice. This variable accounts for those who had 2 operations and counts them as 1 patient. 

patient_audited = surgical_prophylaxis_TK.groupby("What_is_the_patient_s_PRMS_code").Ward_admission.count().reset_index()
#print(patient_audited)
patient_audited_count = patient_audited["What_is_the_patient_s_PRMS_code"].count()
#print(patient_audited_count)

#Below is the number of unduplicated reports in the Kobo dataframe. This includes both patient who had an operation(s) and those who did not.  

unduplicated_data = surgical_prophylaxis_TK.groupby("Ward_admission").What_is_the_patient_s_PRMS_code.count().reset_index()

unduplicated_data.rename(columns={"Ward_admission": "Ward audited", "What_is_the_patient_s_PRMS_code": "Number of procedures audited in each ward"}, inplace=True)
#print(unduplicated_data)

total_unduplicated_data = unduplicated_data.sum(axis=0).reset_index()
#print(total_unduplicated_data)

total_unduplicated_data_sum = total_unduplicated_data.loc[1, 0]
#print(total_unduplicated_data_sum)

admission_status = pd.value_counts(surgical_prophylaxis_TK["Admission_status"]).reset_index()
admission_status.rename(columns={"index": "Admission status", "Admission_status": "Total number of reports"}, inplace=True)
#print(admission_status)

#Below is the number of patients that had received operations versus those that did not in OB-GYN.
operative_status_ob_gyn = surgical_prophylaxis_TK.groupby("IPD_care/operative_statusIPD").Ward_admission.count().reset_index()
operative_status_ob_gyn.rename(columns={"IPD_care/operative_statusIPD" : "Patient operative status", "Ward_admission": "Total number of patients"}, inplace=True)

operation_type_ob_gyn = surgical_prophylaxis_TK.groupby("IPD_care/operative_procedureIPD").Ward_admission.count().reset_index()

#Table of operations that should have/should not have had prophylaxis and did OBGYN.
operations_should_did_prophylaxis = surgical_prophylaxis_TK.groupby("IPD_care/Surgical_prophylaxisIPD2")["IPD_care/Surgical_prophylaxisIPD"].count().reset_index()
#print(operations_should_did_prophylaxis)


#total operations do not include N/A OBGYN.
total_operations = operations_should_did_prophylaxis["IPD_care/Surgical_prophylaxisIPD"].sum()
#print(total_operations)

#Operations that should get prophylaxis and did OBGYN.
row_op = operations_should_did_prophylaxis[operations_should_did_prophylaxis["IPD_care/Surgical_prophylaxisIPD2"] == "Yes"].reset_index()

def num_op_proph_should_did():
    if row_op.empty == True:
        return (0)
    else:
        return numerator_op
    
numerator_op = row_op.loc[0, "IPD_care/Surgical_prophylaxisIPD"]

#Operations that should not get prophylaxis and did OBGYN.
row_op2 = operations_should_did_prophylaxis[operations_should_did_prophylaxis["IPD_care/Surgical_prophylaxisIPD2"] == "No"].reset_index()

def num_op_shouldnt_did():
    if row_op2.empty == True:
        return (0)
    else:
        return row_op2.loc[0, "IPD_care/Surgical_prophylaxisIPD"]
    
numerator_op2 = num_op_shouldnt_did()

#Percentage
percentages = (numerator_op/total_operations * 100)
rounded_percentage = percentages.round(2)

percentages_2 = (numerator_op2/total_operations * 100)
rounded_percentage2 = percentages_2.round(2)
#print(rounded_percentage)
#print(rounded_percentage2)

#Appraisal function
def appraisal(): 
    if rounded_percentage > 95:
        return "This is a job well done, the team has a high compliance rate to the guidelines. The team correctly administered prophylaxis in procedures that required it."
    else: 
        return "Although the team does not have a 95% complliance rate at this stage, this is a great effort."

def appraisal_2(): 
    if rounded_percentage2 > 0: 
        return "Remember to correctly prescribe prophylaxis in procedures where it is required, the auditor providing feedback will go through the operation(s) in which prophylaxis was given for the incorrect indication."
    else:
        return "Excellent, prophylaxis was given for the correct indications only."
            
operations_should_did_prophylaxis.rename(columns={"IPD_care/Surgical_prophylaxisIPD2": "Procedures which prophylaxis should be given", "IPD_care/Surgical_prophylaxisIPD": "Procedures which prophylaxis was given"}, inplace=True) 

#Was the correct antibiotic given for prophylaxis for the operations where prophylaxis was indicated? Formula below OBGYN.

correct_antibiotic_prophylaxis_df = surgical_prophylaxis_TK["IPD_care/Antibiotic_prophylaxisIPD2"].value_counts().reset_index()
correct_antibiotic_prophylaxis_value = correct_antibiotic_prophylaxis_df.loc[0, "IPD_care/Antibiotic_prophylaxisIPD2"]
percentage_correct_antibiotic = (correct_antibiotic_prophylaxis_value/numerator_op * 100)
rounded_percentage_correct_antibiotic = percentage_correct_antibiotic.round(2)

def appraisal_3() :
    if rounded_percentage_correct_antibiotic > 95:
        return "Well done. The patients that were indicated to get prophylaxis got the correct medication as per the guidelines."
    else: 
        return "Although the team has not reached 95% compliance to giving the right antibiotic for prophylaxis, this is a good effort. The auditor will feedback on the operations with the incorrect prescriptions."
    
# Was the antibiotic given less than 60mn before incision. OBGYN 

less_60mn = surgical_prophylaxis_TK.groupby(["IPD_care/Surgical_prophylaxisIPD2", "IPD_care/Antibiotic_prophylaxisIPD3"])["IPD_care/Surgical_prophylaxisIPD"].count().reset_index()
row_less_60mn_1 = less_60mn[less_60mn["IPD_care/Surgical_prophylaxisIPD2"] == "Yes"].reset_index()
row_less_60mn = row_less_60mn_1[row_less_60mn_1["IPD_care/Antibiotic_prophylaxisIPD3"] == "Yes"].reset_index()
less_60mn_value = row_less_60mn.loc[0, "IPD_care/Surgical_prophylaxisIPD"]

def num_less_60():
    if row_less_60mn.empty == True:
        return (0)
    else:
        return less_60mn_value
    
percentage_60mn = (less_60mn_value/numerator_op*100)
rounded_percentage_60_mn = percentage_60mn.round(2)

def appraisal_4():
    if rounded_percentage_60_mn >95:
        return "Excellent! The anesthetist team provided the antibiotic in the correct time window >95% of the time."
    else: 
        return "We can do better! Remember to clearly write in the anesthetic sheet when the antibiotic has been given! The auditor will provide feedback on the procedures with incorrect timing."

# Were antibiotics given post-op in patients that only needed to have prophylaxis? Create a table: should the patient have had Abx post-op and did they get Abx post-op. 

post_op_abx = surgical_prophylaxis_TK.groupby(["IPD_care/Surgical_prophylaxisIPD", "IPD_care/Antibiotic_prophylaxisIPD6"])["IPD_care/Antibiotic_prophylaxisIPD4"].count().reset_index()

def post_op_abx_OBGYN_null_df():
    if post_op_abx.empty == True:
        return (0)

def post_op_abx_OBGYN_df():
    if post_op_abx.empty == False:
        return post_op_abx[post_op_abx["IPD_care/Surgical_prophylaxisIPD"] == "Yes"].reset_index() 
        
post_op_abx_df2 = post_op_abx_OBGYN_df()

def post_op_abx_OBGYN_value(): 
    if post_op_abx_df2 is None: 
        return (0)    
    else:
        return post_op_abx_df2.loc[0, "IPD_care/Antibiotic_prophylaxisIPD4"]
    
post_op_abx_value = post_op_abx_OBGYN_value()

percentage_post_op_abx = (post_op_abx_value/total_operations * 100)
rounded_post_op_abx = percentage_post_op_abx.round(2)

def appraisal_5(): 
    if rounded_post_op_abx > 5: 
        return "Avoid giving antibiotics post-operatively in procedures where they are not needed. The auditor will give overall feedback on the operations that received post-operative antibiotics and provide recommendations for improving practices."
    else: 
        return "Excellent job! Most of the patients that did not require post-operative antibiotics were not prescribed antibiotics."

#Breakdown of procedures that did not get prophylaxis.
operations_no_prophylaxis = surgical_prophylaxis_TK.groupby("IPD_care/Surgical_prophylaxisIPD3")["IPD_care/Surgical_prophylaxisIPD"].count().reset_index()

operations_no_prophylaxis.rename(columns={"IPD_care/Surgical_prophylaxisIPD3": "Procedures in which NO prophylaxis is indicated", "IPD_care/Surgical_prophylaxisIPD": "Procedures which prophylaxis was not given"}, inplace=True) 

operation_no_prophylaxis_total = operations_no_prophylaxis["Procedures which prophylaxis was not given"].sum()

row_no_proph = operations_no_prophylaxis[operations_no_prophylaxis["Procedures in which NO prophylaxis is indicated"] == "Yes"].reset_index()

def no_proph():
    if row_no_proph.empty == True:
        return (0)
    else:
        return row_no_proph.loc[0, "Procedures which prophylaxis was not given"]

operations_should_did_not_prophylaxis_value = no_proph()
percentage_no_prophylaxis = (operations_should_did_not_prophylaxis_value/operation_no_prophylaxis_total*100)
rounded_percentage_no_prophylaxis = percentage_no_prophylaxis.round(2) 

def appraisal_6():
    if rounded_percentage_no_prophylaxis > 95: 
        return "Well done. Most procedures that did not need prophylaxis didn't get prophylaxis. The auditor will go through the operations that should have received prophylaxis and did not."
    else: 
        return "Although the team has not reached >95% compliance, this is a great effort. the auditor will go through the operations that received prophylaxis when it was not indicated."

#Post-op antibiotics in patients that did not get prophylaxis. 

post_op_abx_no_prophylaxis = surgical_prophylaxis_TK.groupby(["IPD_care/Surgical_prophylaxisIPD", "IPD_care/Surgical_prophylaxisIPD3", "IPD_care/Antibiotic_prophylaxisIPD6"])["IPD_care/Antibiotic_prophylaxisIPD4"].count().reset_index()

def post_op_abx_no_proph_null_df(): 
    if post_op_abx_no_prophylaxis.empty == True:
        return (0)
    else:
        return post_op_abx_no_prophylaxis
    
post_op_abx_no_proph_df = post_op_abx_no_proph_null_df()

def post_op_abx_no_proph_value():
    if post_op_abx_no_proph_df is None: 
        return (0)
    else:
        return post_op_abx_no_proph_df.loc[0, "IPD_care/Antibiotic_prophylaxisIPD4"]

post_op_abx_no_prophylaxis_value = (post_op_abx_no_proph_value()) 
percentage_abx_post_op_no_proph = (post_op_abx_no_prophylaxis_value/operation_no_prophylaxis_total*100)
rounded_percentage_abx_post_op_no_proph = percentage_abx_post_op_no_proph.round(2)

#should get post_op abx in patients that did not get prophylaxis

row_post_op_should_get_not_proph = post_op_abx_no_prophylaxis[post_op_abx_no_prophylaxis["IPD_care/Antibiotic_prophylaxisIPD6"] == "Yes"].reset_index()

def post_op_abx_should_get_not_proph_df():
    if row_post_op_should_get_not_proph.empty == True:
        return (0)
    else:
        return row_post_op_should_get_not_proph.loc[0, "IPD_care/Antibiotic_prophylaxisIPD4"]

post_op_should_get_not_proph_value = post_op_abx_should_get_not_proph_df()

def percentage(): 
    if post_op_abx_no_prophylaxis_value == (0):
        return (0)
    else:
        return (post_op_should_get_not_proph_value/post_op_abx_no_prophylaxis_value*100)

percentage_2 = percentage()
percentage_3 = float(percentage_2)
percentage_4 = round(percentage_3, 2)

def appraisal_7(): 
    if percentage_4 >95:
        return "Excellent job. Most of the operations that should have received post-op antibiotics did."  
    else:
        return "This is a good effort. A number of operations that did not require post-operative antibiotics received it. Remember that many procedures only need one pre-operative dose. The auditor will go through the operation(s) and provide feedback." 

#This is for the tabs at top of the page
st.markdown(
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">',
    unsafe_allow_html=True,
)
query_params = st.experimental_get_query_params()
tabs = ["General", "OB-GYN", "General surgery", "Auditor readme"]
if "tab" in query_params:
    active_tab = query_params["tab"][0]
else:
    active_tab = "General"

if active_tab not in tabs:
    st.experimental_set_query_params(tab="General")
    active_tab = "General"

li_items = "".join(
    f"""
    <li class="nav-item">
        <a class="nav-link{' active' if t==active_tab else ''}" href="/?tab={t}">{t}</a>
    </li>
    """
    for t in tabs
)
tabs_html = f"""
    <ul class="nav nav-tabs">
    {li_items}
    </ul>
"""

st.markdown(tabs_html, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if active_tab == "General":
    st.title("Surgical prophylaxis feedback")
    st.write("This report is directed to the management and ward staff. The purpose of this report is to provide feedback regarding surgical prophylaxis, which includes number of patients operated, number of patients that received prophylaxis, number of patients indicated to receive prophylaxis")
    st.write("Data reported for: ", surgical_prophylaxis_TK.loc[0, "Which_months_s_will_you_audit"], surgical_prophylaxis_TK.loc[0, "Which_year_will_you_audit"])
    st.write("The number of patients (both operated and non-operated) audited for this period: ", patient_audited_count, "(This data is deduplicated. Patients who have done more than one procedure are counted once.)") 
    st.write("The total number of non-deduplicated reports entered in the Kobo Toolbox: ", total_unduplicated_data_sum, "(This is a total count of patients that had one or more operations as well as patients who did not have a procedure done.) This number will be used as our denominator for our report.")
    st.write("The number of Kobo reports that were from outpatient versus inpatient setting: ", admission_status)
    st.write("The wards in which the Kobo reports were collected from: ", unduplicated_data)
    
elif active_tab == "OB-GYN":
    
    #Below is the sorting operation so the graphs goes from smallest to highest values
    sorted_operation_type = operation_type_ob_gyn.sort_values("Ward_admission")

# Below is the bar plot for each type of surgeries done in OB-GYN
    
    st.write("The number of patients in OB-GYN that have undergone a procedure versus those that did not: ", operative_status_ob_gyn)
    
    st.subheader("Breakdown of the different operations done in OB-GYN:")
 
    bar_plot_px = px.bar(operation_type_ob_gyn, x="IPD_care/operative_procedureIPD", y="Ward_admission", hover_name="IPD_care/operative_procedureIPD", color="IPD_care/operative_procedureIPD", text="Ward_admission", labels = {"IPD_care/operative_procedureIPD": "Type of operation", "Ward_admission": "Number of procedures"}).update_xaxes(categoryorder="total ascending").update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    st.plotly_chart(bar_plot_px, use_container_width=True)
    
    st.write("Total procedures that received prophylaxis: ", total_operations, "NOTE: we have excluded procedures that have received prophylaxis that were not included in the guidelines.")

    st.subheader("Breakdown of procedures __*that received*__ prophylaxis: ")
    st.table(data = operations_should_did_prophylaxis)

    st.write(numerator_op, " of ", total_operations, "(", rounded_percentage, " %)",  "operations that had an indication to receive prophylaxis, received it.")

    st.write(appraisal())

    st.write(numerator_op2, " of ", total_operations, "(", rounded_percentage2, "%)", "operations that did not have an indication to receive prophylaxis, received it.")

    st.write(appraisal_2())

    st.subheader("Number of operations with the correct antibiotic prescription:") 
    st.write("(This only includes surgeries that were indicated to have prophylaxis and received it.)")
    st.write(correct_antibiotic_prophylaxis_value, " of ", numerator_op, "(", rounded_percentage_correct_antibiotic, "%)" " surgical prophylaxis prescriptions were correct.")

    st.write(appraisal_3())

    st.subheader("Number of operations with prophylaxis provided <60mn before incision:")
    st.write("(This only includes surgeries that were indicated to have prophylaxis and received it.)")
    st.write(less_60mn_value, " of ", numerator_op, "(", rounded_percentage_60_mn, "%)" " surgical prophylaxis prescriptions were given <60mn before incision")

    st.write(appraisal_4())

    st.subheader("Number of operations that received post-operative antibiotics:")
    st.write("(This only includes surgeries where prophylaxis was given. This DOES NOT include surgeries that were initially clean/contaminated but became contaminated during operation due to soiling from stools, urine etc...)")
    st.write(post_op_abx_value, " of ", total_operations, "(", rounded_post_op_abx, "%)" " patients received antibiotic post operatively and did not need to.")

    st.write(appraisal_5())

    st.markdown("""---""")

    st.write("Total procedures that did not receive prophylaxis:", operation_no_prophylaxis_total, "NOTE: we have excluded procedures that were not included in the guidelines.")

    st.subheader("Breakdown of procedures that __*did not receive*__ prophylaxis: ")
    st.table(data = operations_no_prophylaxis)

    st.write(operations_should_did_not_prophylaxis_value, " of ", operation_no_prophylaxis_total, "(", rounded_percentage_no_prophylaxis , "%)", "operations that did not have an indication to receive prophylaxis, did not receive prophylaxis.")

    st.write(appraisal_6())

    st.subheader("Number of operations that received post-operative antibiotics:")

    st.write(post_op_abx_no_prophylaxis_value, " of ", operation_no_prophylaxis_total, "(", rounded_percentage_abx_post_op_no_proph, "%)", "operations that did not have an indications to receive prophylaxis received post-op antibiotics.")

    st.write(post_op_should_get_not_proph_value, " of ", post_op_abx_no_prophylaxis_value, "(", percentage_4, "%)", "operations that received post-operative antibiotics should have received it. The auditor will feedback if the operation(s) that needed post-operative antibiotics also needed to have microbiology specimen collected.")

    st.write(appraisal_7())

elif active_tab == "General surgery": 
    
    operation_gen_surg_breakdown = surgical_prophylaxis_TK.groupby("IPD_careSW/Ward_name")["IPD_careSW/operative_statusIPDSW"].count().reset_index()
    operation_gen_surg_breakdown.rename(columns={"IPD_careSW/Ward_name": "Specialty", "IPD_careSW/operative_statusIPDSW": "Number of operations"}, inplace=True)
    
    operative_status_Gen_surg = surgical_prophylaxis_TK.groupby("IPD_careSW/operative_statusIPDSW")["Ward_admission"].count().reset_index()
    operative_status_Gen_surg.rename(columns={"IPD_careSW/operative_statusIPDSW" : "Patient operative status", "Ward_admission": "Total number of patients"}, inplace=True)

    operation_type_gen_surg_GI = surgical_prophylaxis_TK.groupby("IPD_careSW/operative_procedureIPD_GI").Ward_admission.count().reset_index()
    
    operation_should_proph_GI = surgical_prophylaxis_TK.groupby(["IPD_careSW/Antibiotic_prophylaxisIPD4SW", "IPD_careSW/Ward_name"])["IPD_careSW/Surgical_prophylaxisIPD2SW"].count().reset_index()


    row_should_proph_GI = operation_should_proph_GI[operation_should_proph_GI["IPD_careSW/Antibiotic_prophylaxisIPD4SW"] == "No"].reset_index()
    
    def operation_should_proph_GI(): 
        if row_should_proph_GI.empty == True:
            return (0)
        else:
            return row_should_proph_GI.loc[0, "IPD_careSW/Surgical_prophylaxisIPD2SW"]
    
    operation_should_proph_GI_value = operation_should_proph_GI() 
    
#Breakdown of procedure that should vs should not receive prophylaxis, correct antibiotic prescription, <60mn. Which received post op antibiotics and micro (GI). 
    
    operation_should_did_proph_GI = surgical_prophylaxis_TK.groupby(["IPD_careSW/operative_procedureIPD_GI", "IPD_careSW/Antibiotic_prophylaxisIPD4SW", "IPD_careSW/Surgical_prophylaxisIPD2SW"])["IPD_careSW/Surgical_prophylaxisIPDSW"].count().reset_index()
    operation_should_did_proph_GI.rename(columns={"IPD_careSW/operative_procedureIPD_GI": "Procedure", "IPD_careSW/Antibiotic_prophylaxisIPD4SW": "Received post-operative antibiotics", "IPD_careSW/Surgical_prophylaxisIPD2SW": "Should receive prophylaxis", "IPD_careSW/Surgical_prophylaxisIPDSW": "Received prophylaxis"}, inplace=True)
    
    operation_proph_GI_Abx = surgical_prophylaxis_TK.groupby(["IPD_careSW/operative_procedureIPD_GI", "IPD_careSW/Surgical_prophylaxisIPDSW", "IPD_careSW/Antibiotic_prophylaxisIPD2SW"])["IPD_careSW/Surgical_prophylaxisIPD2SW"].count().reset_index()
    operation_proph_GI_Abx.rename(columns={"IPD_careSW/operative_procedureIPD_GI": "Procedure", "IPD_careSW/Surgical_prophylaxisIPDSW": "Received prophylaxis", "IPD_careSW/Antibiotic_prophylaxisIPD2SW": "Received the correct antibiotic for prophylaxis", "IPD_careSW/Surgical_prophylaxisIPD2SW": "Number of procedures"}, inplace=True)
    
    operation_proph_GI_Abx_60mn = surgical_prophylaxis_TK.groupby(["IPD_careSW/operative_procedureIPD_GI", "IPD_careSW/Antibiotic_prophylaxisIPD2SW", "IPD_careSW/Antibiotic_prophylaxisIPD3SW"])["IPD_careSW/Surgical_prophylaxisIPDSW"].count().reset_index()  
    operation_proph_GI_Abx_60mn.rename(columns={"IPD_careSW/operative_procedureIPD_GI": "Procedure", "IPD_careSW/Antibiotic_prophylaxisIPD2SW": "Correct antibiotic prophylaxis", "IPD_careSW/Antibiotic_prophylaxisIPD3SW": "Prophylaxis given <60mn before incision", "IPD_careSW/Surgical_prophylaxisIPDSW": "Number of procedures"}, inplace=True)
    
    operation_GI_micro = surgical_prophylaxis_TK.groupby(["IPD_careSW/operative_procedureIPD_GI", "IPD_careSW/micro_SWIPD"])["IPD_careSW/Antibiotic_prophylaxisIPD4SW"].count().reset_index()
    operation_GI_micro.rename(columns={"IPD_careSW/operative_procedureIPD_GI": "Procedure", "IPD_careSW/micro_SWIPD": "Was a microbiology specimen sent to the lab?", "IPD_careSW/Antibiotic_prophylaxisIPD4SW": "Number of procedures"}, inplace=True)

    operation_type_gen_surg_ortho = surgical_prophylaxis_TK.groupby("IPD_careSW/operative_procedureIPD_ortho").Ward_admission.count().reset_index()
    
    operation_should_proph_ortho = surgical_prophylaxis_TK.groupby(["IPD_careSW/operative_procedureIPD_ortho"])["IPD_careSW/operative_statusIPDSW"].count().reset_index()
    operation_should_proph_ortho.rename(columns={"IPD_careSW/operative_procedureIPD_ortho": "Procedure", "IPD_careSW/operative_statusIPDSW": "Total number of procedures"}, inplace=True)
    operation_should_proph_ortho1 = surgical_prophylaxis_TK.groupby(["IPD_careSW/operative_procedureIPD_ortho"])["IPD_careSW/Surgical_prophylaxisIPD2SW"].count().reset_index()
    operation_should_proph_ortho1.rename(columns={"IPD_careSW/operative_procedureIPD_ortho": "Procedure", "IPD_careSW/Surgical_prophylaxisIPD2SW": "Received prophylaxis"}, inplace=True)
    
    operation_proph_ortho_Abx = surgical_prophylaxis_TK.groupby(["IPD_careSW/operative_procedureIPD_ortho", "IPD_careSW/Antibiotic_prophylaxisIPD2SW"])["IPD_careSW/Surgical_prophylaxisIPD2SW"].count().reset_index()
    operation_proph_ortho_Abx.rename(columns={"IPD_careSW/operative_procedureIPD_ortho": "Procedure", "IPD_careSW/Antibiotic_prophylaxisIPD2SW": "Correct prophyaxis given?", "IPD_careSW/Surgical_prophylaxisIPD2SW": "Procedures that received prophylaxis"}, inplace=True)
    
    operation_proph_ortho_60mn = surgical_prophylaxis_TK.groupby(["IPD_careSW/operative_procedureIPD_ortho", "IPD_careSW/Antibiotic_prophylaxisIPD3SW"])["IPD_careSW/Surgical_prophylaxisIPD2SW"].count().reset_index()
    operation_proph_ortho_60mn.rename(columns={"IPD_careSW/operative_procedureIPD_ortho": "Procedure", "IPD_careSW/Antibiotic_prophylaxisIPD3SW": "Prophylaxis given <60mn before incision", "IPD_careSW/Surgical_prophylaxisIPD2SW": "Procedures that received prophylaxis"}, inplace=True)
    
    operation_ortho_post_op = surgical_prophylaxis_TK.groupby(["IPD_careSW/operative_procedureIPD_ortho"])["IPD_careSW/Antibiotic_prophylaxisIPD6SW"].count().reset_index()
    operation_ortho_post_op.rename(columns={"IPD_careSW/operative_procedureIPD_ortho": "Procedure", "IPD_careSW/Antibiotic_prophylaxisIPD6SW": "Received post-op antibiotics"}, inplace=True)
    
    operation_ortho_post_op_details = surgical_prophylaxis_TK.groupby(["IPD_careSW/operative_procedureIPD_ortho", "IPD_careSW/Antibiotic_prophylaxisIPD6SW", "IPD_careSW/What_post_operative_al_surgery_inpatient", "IPD_careSW/How_many_days_did_th_ly_General_surgery"])["IPD_careSW/Antibiotic_prophylaxisIPD4SW"].count().reset_index()
    operation_ortho_post_op_details.rename(columns={"IPD_careSW/operative_procedureIPD_ortho": "Procedures", "IPD_careSW/Antibiotic_prophylaxisIPD6SW": "Procedures that should and did receive post-operative antibiotics", "IPD_careSW/What_post_operative_al_surgery_inpatient": "Post-operative Abx category", "IPD_careSW/How_many_days_did_th_ly_General_surgery": "Number of days of post-operative antibiotics", "IPD_careSW/Antibiotic_prophylaxisIPD4SW": "Number of procedures"}, inplace=True)
    operation_ortho_post_op_details2 = operation_ortho_post_op_details[["Procedures", "Procedures that should and did receive post-operative antibiotics", "Post-operative Abx category", "Number of days of post-operative antibiotics", "Number of procedures"]]
    operation_ortho_post_op_details2["Number of days of post-operative antibiotics"] = operation_ortho_post_op_details2["Number of days of post-operative antibiotics"].astype(int).astype(str) 
    
    operations_ortho_micro = surgical_prophylaxis_TK.groupby(["IPD_careSW/operative_procedureIPD_ortho", "IPD_careSW/micro_SWIPD"])["IPD_careSW/What_post_operative_al_surgery_inpatient"].count().reset_index()
    operations_ortho_micro.rename(columns={"IPD_careSW/operative_procedureIPD_ortho": "Procedures", "IPD_careSW/micro_SWIPD": "Was a microbiology specimen taken?", "IPD_careSW/What_post_operative_al_surgery_inpatient": "Total number of procedures"}, inplace=True)
    
    operations_micro_type_ortho = surgical_prophylaxis_TK.groupby(["IPD_careSW/operative_procedureIPD_ortho", "IPD_careSW/Microbiology_IPDSW/micro_IPD2SW/Blood_culture", "IPD_careSW/Microbiology_IPDSW/micro_IPD2SW/Pus_aspirate", "IPD_careSW/Microbiology_IPDSW/micro_IPD2SW/Pus_swab", "IPD_careSW/Microbiology_IPDSW/micro_IPD2SW/Bone", "IPD_careSW/Microbiology_IPDSW/micro_IPD2SW/Tissue", "IPD_careSW/Microbiology_IPDSW/micro_IPD2SW/Urine", "IPD_careSW/Microbiology_IPDSW/micro_IPD2SW/Other"])["IPD_careSW/micro_SWIPD"].count().reset_index()
    operations_micro_type_ortho.rename(columns={"IPD_careSW/operative_procedureIPD_ortho": "Procedures", "IPD_careSW/Microbiology_IPDSW/micro_IPD2SW/Blood_culture": "Blood cultures", "IPD_careSW/Microbiology_IPDSW/micro_IPD2SW/Pus_aspirate": "Pus aspirate", "IPD_careSW/Microbiology_IPDSW/micro_IPD2SW/Pus_swab": "Pus swab", "IPD_careSW/Microbiology_IPDSW/micro_IPD2SW/Bone": "Bone", "IPD_careSW/Microbiology_IPDSW/micro_IPD2SW/Tissue": "Tissue", "IPD_careSW/Microbiology_IPDSW/micro_IPD2SW/Urine": "Urine", "IPD_careSW/Microbiology_IPDSW/micro_IPD2SW/Other": "Other", "IPD_careSW/micro_SWIPD": "Number of cases"}, inplace=True)

    
    operation_type_gen_surg_uro = surgical_prophylaxis_TK.groupby("IPD_careSW/operative_procedureIPD_uro").Ward_admission.count().reset_index()

    operation_type_gen_surg_ENT = surgical_prophylaxis_TK.groupby("IPD_careSW/What_procedure_was_d_IPD_ENT_procedure").Ward_admission.count().reset_index()

    operation_type_gen_surg_dental = surgical_prophylaxis_TK.groupby("IPD_careSW/What_procedure_was_d_D_Dental_procedure").Ward_admission.count().reset_index()
    
#Below is the sorting operation so the graphs goes from smallest to highest values

    sorted_operation_type_GI = operation_type_gen_surg_GI.sort_values("Ward_admission")
    sorted_operation_type_ortho = operation_type_gen_surg_ortho.sort_values("Ward_admission")
    sorted_operation_type_uro = operation_type_gen_surg_uro.sort_values("Ward_admission")
    sorted_operation_type_ENT = operation_type_gen_surg_ENT.sort_values("Ward_admission")
    sorted_operation_type_dental = operation_type_gen_surg_dental.sort_values("Ward_admission")

# Below is the bar plot for each type of surgeries done in GI

    st.write("The number of patients in general surgery that have undergone a procedure versus those that did not:")
    st.write(operative_status_Gen_surg)
    
    st.write("Breakdown of surgeries depending on specialties:")
    st.table(operation_gen_surg_breakdown.assign(hack="").set_index("hack"))
    
    st.subheader("Breakdown of the different operations done in general surgery (GI):")
    
    bar_plot_px2 = px.bar(operation_type_gen_surg_GI, x="IPD_careSW/operative_procedureIPD_GI", y="Ward_admission", hover_name="IPD_careSW/operative_procedureIPD_GI", color="IPD_careSW/operative_procedureIPD_GI", text="Ward_admission", labels = {"IPD_careSW/operative_procedureIPD_GI": "Type of operation", "Ward_admission": "Number of procedures"}).update_xaxes(categoryorder="total ascending").update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    st.plotly_chart(bar_plot_px2, use_container_width=True)
    
    st.write("PLEASE READ: the auditor needs to count the number of surgeries that need prophylaxis. This number is to be used as reference to look at overall compliance to guidelines. You can click out the infected surgeries in the legend on the right side of the graph to help you get the correct count.")
    
    st.subheader("Breakdown of procedures __*that received*__ prophylaxis and post-operative antibiotics :")
    st.table(operation_should_did_proph_GI.assign(hack="").set_index("hack"))
    
    st.subheader("Number of procedures with the correct/incorrect antibiotic prescription for prophylaxis:")
    st.table(operation_proph_GI_Abx.assign(hack="").set_index("hack"))
    st.write("The auditor will go through the operations that did not have the right antibiotic prophylaxis given.")
    
    st.subheader("Number of procedures with prophylaxis provided <60mn before incision:")
    st.table(operation_proph_GI_Abx_60mn.assign(hack="").set_index("hack"))
    
    st.subheader("Procedures that had microbiology specimen collected:")
    st.table(operation_GI_micro.assign(hack="").set_index("hack"))
    st.write("The auditor will provide feedback on operations in which it is indicated to send microbiology specimen to the laboratory.")
    
        #auditor feedback critical! We want the surgeons to give prophylaxis to all patients BUT if per-operatively they see a certain diagnosis then this will dictate the treatent protocol (prophylaxis only vs treatment.) I do not think complicated and uncomplicated appendicitis can be differentiated clinically (unless peritoneal appendicitis vs all other types of appendicitis) and therefore we must specify that this approach is correct and that even though we do not provide feedback, this habit must be maintained. 
    
    
    st.markdown("""---""")
    
# Below is the bar plot for each type of surgeries done in orthopedics

    st.subheader("Breakdown of the different operations done in general surgery (Orthopedics):")
    
    bar_plot_px3 = px.bar(operation_type_gen_surg_ortho, x="IPD_careSW/operative_procedureIPD_ortho", y="Ward_admission", hover_name="IPD_careSW/operative_procedureIPD_ortho", color="IPD_careSW/operative_procedureIPD_ortho", text="Ward_admission", labels = {"IPD_careSW/operative_procedureIPD_ortho": "Type of operation", "Ward_admission": "Number of procedures"}).update_xaxes(categoryorder="total ascending").update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    st.plotly_chart(bar_plot_px3, use_container_width=True)
    
    st.subheader("Comparison between total number of operations and operations that have received prophylaxis:")
    
    col1, col2 = st.columns([0.5, 0.5])
    
    with col1: 
        st.write("Total operations done:")
        st.table(operation_should_proph_ortho.assign(hack="").set_index("hack"))
    
    with col2:
        st.write("Got prophylaxis (excludes infections, other, unclear, which equal 0 below):")
        st.table(operation_should_proph_ortho1.assign(hack="").set_index("hack"))
    st.write("The auditor will go through the procedures that have/have not received prophylaxis and highlight the areas for improvement. *It is recommended that the auditor has the guidelines available to clarify any areas of uncertainty.*")
    
    st.subheader("Number of procedures that received the correct antibiotic for prophylaxis")
    st.table(operation_proph_ortho_Abx.assign(hack="").set_index("hack"))
    st.write("The auditor will provide feedback on both surgeries that had the correct and incorrect antibiotic prophylaxis.")
    
    st.subheader("Number of procedures that received antibiotic prophylaxis <60mn before incision.")
    st.table(operation_proph_ortho_60mn.assign(hack="").set_index("hack"))
    st.write('The auditor will provide feedback on the timing of antibiotics prophylaxis. It is recommended to give prophylaxis <60mn prior to incision.')
    
    st.subheader("Comparison  between total number of operations and operations that have received post-operative antibiotics:")
    
    col1, col2 = st.columns([0.5, 0.5])
    
    with col1: 
        st.write("Total operations done:")
        st.table(operation_should_proph_ortho.assign(hack="").set_index("hack"))
    
    with col2:
        st.write("Got post-op antibiotics (Excludes unclear operations, which equal 0 below):")
        st.table(operation_ortho_post_op.assign(hack="").set_index("hack"))
    st.write('The auditor will provide feedback on post-operative antibiotics prescriptions. Clean/clean contaminated surgeries do not usually need post-operative antibiotics.')
    
    st.subheader("Breakdown of contaminated/dirty operations that received post-operative antibiotics:")
    st.table(operation_ortho_post_op_details2.assign(hack="").set_index("hack"))
    st.write("some operations may only need a few days of post-operative antibiotics (i.e: procedures requiring pre-emptive antibiotics), other operations might need longer durations for up to 4-6 weeks (i.e: osteomyelitis.)")
    
    st.subheader("Breakdown of operations that had a microbiology specimen collected:")
    st.write("(This only includes contaminated/dirty surgeries, clean/clean-contaminated surgeries = 0)")
    st.table(operations_ortho_micro.assign(hack="").set_index("hack"))
    st.write("Some operations must have multiple deep specimens collected to help provide information regarding the offending pathogen(s). Other operations (i.e: requiring pre-emptive antibiotics) usually do not require for specimens to be collected.")
    
    st.subheader("Breakdown of types of microbiology specimen collected:")
    st.write("The number of cases, represents the number of procedures that had a microbiology done. One case can have multiple cultures. (i.e: one case may have both the value \"true\" assigned to blood culture and pus aspirate.)") 
    st.write("- \"True\" means that a culture was done, \"False\" means that the culture was not done.")
    st.table(operations_micro_type_ortho.assign(hack="").set_index("hack"))
    st.write("The auditor will go through the types of microbiology specimen collected and provide recommendations. Deep specimens (i.e: bone, tissue) usually provide more reliable information on the offending pathogens.")

## need to stress test when Kobo back on. 

elif active_tab == "Auditor readme":
    st.write("PLEASE READ: this section is to provide support to the auditor when providing feedback. The auditor must ensure that every sections of the auditor readme has been addressed prior to presenting the data. It is highly recommended for the auditor to make a few slides for conclusion and recommendations based on the data.")
    
    st.write("In the section for GI surgery: Breakdown of procedures that received prophylaxis and post-operative antibiotics : (includes both non-infected and infected GI surgeries), please provide feedback for the clean/clean contaminated surgeries only for prophylaxis. The denominator is above the table and should guide you to know what the compliance rate is. You may also provide feedback on post-operative antibiotics for all type of surgeries. It is not as critical to provide prophylaxis feedback to infected surgeries, but it needs to be clear that the surgeons must continue that practice as it is usually not possible to distinguish a non-complicated appendicitis from a complicated appendicitis pre-operatively.")
    
    st.write("in the section for GI surgery: Number of procedures with the correct/incorrect antibiotic prescription for prophylaxis, please focus on the clean/contaminated surgeries for feedback in the first instance. Then provide recommendations for the infected surgeries.")
             
    st.write("The above recommendations also applies to orthopedic surgeries")

    

