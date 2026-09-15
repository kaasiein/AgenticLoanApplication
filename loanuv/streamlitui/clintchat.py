import streamlit as st
from utils import callllm
from utils import queryagent
import pandas as pd
from io import StringIO
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
st.title("Online loan application for businesses")
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.name_address=""
    st.session_state.gst_number=""
    st.session_state.org_name=""
    st.session_state.loan_amount=0
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def nextNode(prompt):   
    gonext=False 
    st.session_state.messages.append({"role": "user", "content": prompt})
    response=queryagent.validateAgent(prompt) ##call your agent hear
    with st.chat_message("assistant"):
        st.markdown(response['messages'])
    gonext, nextaction=queryagent.query_get_LLM_output(response["messages"])
    print("1...")
    print(gonext)
    print(nextaction)
    with st.chat_message("assistant"):
        st.markdown(nextaction)    
    if gonext:
        st.session_state.name_address=prompt
    return gonext  
def validateGstn(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    gonext, nextaction=queryagent.validateGstnImpl(prompt) 
    print(nextaction)
    with st.chat_message("assistant"):
        st.markdown(nextaction)  
    if gonext:
        st.session_state.gst_number=prompt
    return gonext
def validateOrg(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    gonext, nextaction=queryagent.validateOrgImpl(prompt) 
    print(nextaction)
    with st.chat_message("assistant"):
        st.markdown(nextaction)  
    if gonext:
        st.session_state.org_name=prompt
    return gonext
def validateAmt(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    gonext, nextaction=queryagent.validateAmtImpl(prompt) 
    print(nextaction)
    with st.chat_message("assistant"):
        st.markdown(nextaction)  
    if gonext:
        st.session_state.loan_amount=prompt
    return gonext
addr=False 
gstn=False
orgn=False
if "step" not in st.session_state:
    st.session_state.step = "main"  
   # st.session_state.step = "agg"  
if st.session_state.step == "main":
    st.chat_message("assistant").markdown("Can you provide your name and address?")
    if prompt :=  st.chat_input("Name & Address Text", key="main_chat"):
        with st.chat_message("user"):
            st.markdown(prompt)  
        print("4...") 
        print(addr) 
        if addr != True:
            addr=nextNode(prompt)
        if addr == True:
            st.session_state.step = "gst"   
            st.rerun()
        print(addr == True and gstn != True)
elif st.session_state.step == "gst":
    st.chat_message("assistant").markdown("Can you provide your GSTIN number?")
    if gst_prompt := st.chat_input("Enter GSTN #", key="gst_chat"):     
        with st.chat_message("user"):
            st.markdown(gst_prompt)   
        print("3...")
        # st.chat_message("assistant").markdown("Could you provide your business GSTN number?")
        gstn=validateGstn(gst_prompt)
        print(gstn)
        if gstn == True:
            st.session_state.step = "org"   
            print(st.session_state.step)
            st.rerun()
elif st.session_state.step == "org":
    st.chat_message("assistant").markdown("Can you provide your Orgonization Name?")
    if org_prompt := st.chat_input("Enter Orgonization Name", key="org_chat"):     
        with st.chat_message("user"):
            st.markdown(org_prompt)   
        print("6...")
        orgn=validateOrg(org_prompt)
        if orgn == True:
            st.session_state.step = "amt"   
            print(st.session_state.step)
            st.rerun()
        #call agent to validate froud
        #grant only loan amount that is less then 5 times the profit.
        #also consider the existing loan.
        # generate a downloadable file with conditions         
elif st.session_state.step == "amt":   
    st.chat_message("assistant").markdown("Can you provide the required loan amount in Crores") 
    if amt_prompt := st.chat_input("Enter Loan Amount", key="amt_chat"):     
        with st.chat_message("user"):
            st.markdown(amt_prompt)   
        print("6...")
        amtn=validateAmt(amt_prompt)   
        if amtn == True:
            st.session_state.step = "agg"   
            print(st.session_state.step)
            st.rerun()                                                 
elif st.session_state.step == "agg":
    print("Name & Address: "+st.session_state.name_address)
    print("GSTN: "+st.session_state.gst_number)
    print("Org Name: "+st.session_state.org_name)
    print("Loan Amount: "+st.session_state.loan_amount)
    print("6...")    
    qstate: queryagent.QueryState = {
    "messages": [],
    "name_address": "",
    "gst_number": "",
    "org_name": "",
    "loan_purpose": "",
    "loan_amount": "",
    "loan_duration": "",
    "next": False,
    "trust_response": "",
    "loan_eligibility": "",
    "loan_aggrement": ""
    }
    qstate["name_address"]=st.session_state.name_address
    qstate["gst_number"]=st.session_state.gst_number
    qstate["org_name"]=st.session_state.org_name  
    qstate["loan_amount"]=st.session_state.loan_amount
    ageentresponse=queryagent.callAgent(qstate)
    
    print("10...")
    print(ageentresponse)
    with st.chat_message("assistant"):
        st.markdown(ageentresponse["trust_response"])
        if(ageentresponse["loan_eligibility"]!=""):
            st.markdown(ageentresponse["loan_eligibility"])
        if(ageentresponse["loan_aggrement"]!=""):
            data = "Hello, this is your file content"
            data=ageentresponse["loan_aggrement"]
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer)
            styles = getSampleStyleSheet()

            content = []
            content.append(Paragraph(data, styles["Normal"]))

            doc.build(content)
            buffer.seek(0)

            st.download_button(
                label="Download PDF",
                data=buffer,
                file_name="output.pdf",
                mime="application/pdf"
            )
            #st.markdown(ageentresponse["loan_aggrement"])

uploaded_file=None
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    st.write(bytes_data)

    # To convert to a string based IO:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    st.write(stringio)

    # To read file as string:
    string_data = stringio.read()
    st.write(string_data)

    # Can be used wherever a "file-like" object is accepted:
    dataframe = pd.read_csv(uploaded_file)
    st.write(dataframe)