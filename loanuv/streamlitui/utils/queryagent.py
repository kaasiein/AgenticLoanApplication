#Build agent
import re
from unittest import result

from numpy import number
from sqlalchemy import false
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage
from typing import Annotated
from langgraph.graph.message import add_messages
#graph
from langgraph.graph import StateGraph, START, END
from IPython.display import display, Image
from langgraph.prebuilt import ToolNode, tools_condition 
from IPython.display import display, Image

groq_api_key ="YOUR_GROQ_API_KEY"  # Replace with your actual Groq API key
llm=ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-8b-instant")
from langchain_community.tools.tavily_search import TavilySearchResults
TAVILT_API_KEY="yOUR_TAVILY_API_KEY"  # Replace with your actual Tavily API key
travily=TavilySearchResults(tavily_api_key=TAVILT_API_KEY)
#print(travily.invoke("What is the current stock price of Apple?"))
#print(llm_with_tools.invoke("capital of india"))
tools=[travily]
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_groq import ChatGroq   
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

class QueryState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    #messages: list[AnyMessage]
    name_address: str
    gst_number: str
    org_name: str
    loan_purpose: str
    loan_amount: str
    loan_duration: str
    next: bool
    trust_response: str
    loan_eligibility: str
    loan_aggrement: str

def check_assets(state: QueryState):     
    print("inside evaluvate asset llm...")
    print(state)    
    state["messages"].append({"role": "user", "content": (f"{state['org_name']} total assets FY 2025 balance sheet site:moneycontrol.com OR site:economictimes.indiatimes.com OR site:screener.in")}) 
    llm_with_tools=llm.bind_tools(tools=tools)   
    ai_msg = llm_with_tools.invoke(state["messages"]) 
    response= {"messages": [llm_with_tools.invoke(state["messages"])]}  
    if hasattr(ai_msg, "tool_calls") and ai_msg.tool_calls:
        result = travily.invoke(ai_msg.tool_calls[0]["args"]["query"])
        final = llm_with_tools.invoke(state["messages"] + [ai_msg, {"role": "tool", "content": str(result), "tool_call_id": ai_msg.tool_calls[0]["id"]}])
        text = final.content
        print(final)      
    else:
        text = ai_msg.content
        final = ai_msg
    match = re.search(r"(\d+)%", text)
    
    value = int(match.group(1)) if match else 10
    value60 = value *60/100
    print(value)
    loan_amount=float(state['loan_amount'])
    print(loan_amount)
    if loan_amount> value:
        print("loan amount is higher than total assets...")
        state["loan_eligibility"]="Sorry, the requested Loan amount is much higher than your total assets, you are not eligible for the loan."        
    elif loan_amount< value60:
        print("loan amount is within the acceptable range...")
        state["loan_eligibility"]="Congratulations, you are eligible for the loan."
    else:
        x=value60
        print("you get discounted loan")
        state["loan_eligibility"]="Congratulations! You are eligible for the loan. However, based on your eligibility, we can only offer a loan amount of ₹{x} crores."
    print("11....")
    print(state)
    return state
 

def tool_calling_llm(state: QueryState):     
    print("inside tool calling llm...")
    state["messages"].append({"role": "user", "content": (f"Evaluate whether {state['org_name']} is a trustworthy company for loan approval. Check for any involvement in major financial fraud cases. Provide a risk assessment and give trust level in percentage.")})  
    llm_with_tools=llm.bind_tools(tools=tools)   
    ai_msg = llm_with_tools.invoke(state["messages"]) 
    response= {"messages": [llm_with_tools.invoke(state["messages"])]}  
    if hasattr(ai_msg, "tool_calls") and ai_msg.tool_calls:
        result = travily.invoke(ai_msg.tool_calls[0]["args"]["query"])
        final = llm_with_tools.invoke(state["messages"] + [ai_msg, {"role": "tool", "content": str(result), "tool_call_id": ai_msg.tool_calls[0]["id"]}])
        text = final.content
        print(final)      
    else:
        text = ai_msg.content
        final = ai_msg
    match = re.search(r"(\d+)%", text)
    confidence = int(match.group(1)) if match else 0
    print("Confidence:", confidence)
    state["messages"].append({
    "role": "assistant",
    "content": str(confidence)})
    if confidence > 30:
        state["trust_response"]="Congratulation, you creared the intial eligibility criteria."
        print(state)
    else:
        state["trust_response"]="Sorry, you are not eligible for the loan."
        print(state)
    return (state)
def grantLoan(state):
    print("inside grant loan...")

    import json
    import re

    def extract_total_assets(text: str):
        patterns = [
            r"Total Assets[^0-9]*([\d,]+\.\d+)",
            r"Total Assets[^0-9]*([\d,]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1).replace(",", ""))
        return None

    llm_with_tools = llm.bind_tools(tools=tools)

    # LLM only for tool triggering (not extraction)
    user_msg = {
        "role": "user",
        "content": f"Find latest total assets of {state['org_name']} in INR crores."
    }
    state["messages"].append(user_msg)

    ai_msg = llm_with_tools.invoke(state["messages"])
    print("AI Message:", ai_msg)

    if hasattr(ai_msg, "tool_calls") and ai_msg.tool_calls:
        tool_call = ai_msg.tool_calls[0]
        query = tool_call["args"]["query"]

        print("Calling tool with query:", query)

        # Call tool
        tool_result = travily.invoke(query)
        print("Raw Tool result:", tool_result)

        # Convert tool result to string
        tool_text = json.dumps(tool_result)

        # Extract numeric asset value
        asset_value = extract_total_assets(tool_text)
        print("Extracted Asset Value:", asset_value)
        state["messages"].append({
                "role": "assistant",
                "content": str(asset_value)})

        final_value = asset_value if asset_value is not None else 0

        # Update state (ONLY NUMBER in response)
        state["messages"].append(ai_msg)
        state["messages"].append({
            "role": "assistant",
            "content": str(final_value)
        })

        return {
            "messages": state["messages"],
            "asset_value": final_value
        }

    else:
        state["messages"].append(ai_msg)
        return {
            "messages": state["messages"],
            "asset_value": 0
        }

def tool_calling_condition(state: QueryState): 
    confidence = int(state["messages"][-1].content)
    print("inside tool calling condetion...")
    if confidence > 30:
        state["trust_response"]="Congratulation, you creared the intial eligibility criteria."
        print(state)
        return "check_assets"
    else:
        state["trust_response"]="Sorry, you are not eligible for the loan."
        print(state)
        return "Complete"
def grant_loan_condition(state: QueryState):   
    
    loaneligibility= state["loan_eligibility"]
    print(state)
    if loaneligibility=="Sorry, the requested Loan amount is much higher than your total assets, you are not eligible for the loan." :
        print("loan amount is higher than total assets...")
        state["loan_eligibility"]=="Sorry, the requested Loan amount is much higher than your total assets, you are not eligible for the loan."        
        return "Complete"
    elif loaneligibility=="Congratulations, you are eligible for the loan.":
        print("loan amount is within the acceptable range...")
        state["loan_eligibility"]="Congratulations, you are eligible for the loan."
        return "loanAggrement"
    else:
        x=value60
        print("you get discounted loan")
        state["loan_eligibility"]="Congratulations! You are eligible for the loan. However, based on your eligibility, we can only offer a loan amount of ₹{x} crores."
        return "loanAggrement"
import re
global match
match = 0

def checkFraud(state:QueryState):
    print("9...")
      
    #llm_with_tools=llm.bind_tools(tools=tools)
    #print(llm_with_tools.invoke("capital of india"))
    print("inside check fraud...")
    return state
def returnLoanStatus(state:QueryState):
    print("inside return loan status...")
    return state

def loanAggrement(state:QueryState):
    print("inside loan aggrement...")
    response=(llm.invoke("Take this as input and generate a loan agreement letter "+str(state)))
    state["loan_aggrement"]=(response.content)
    print(response.content)
    return state
def callAgent(state:QueryState):
    print("8...")
    print(state)
    loanWF = StateGraph(QueryState)
    loanWF.add_node("grantLoan", grantLoan)
    loanWF.add_node("checkFraud", checkFraud)
    loanWF.add_node("tool_calling_llm", tool_calling_llm)
    loanWF.add_node("tools", ToolNode(tools))
    loanWF.add_node("check_assets", check_assets)
    loanWF.add_node("loanAggrement", loanAggrement)
    loanWF.add_node("Complete", returnLoanStatus)

    loanWF.add_edge(START, "checkFraud")
    loanWF.add_edge("checkFraud","tool_calling_llm")  
    loanWF.add_conditional_edges("tool_calling_llm", tool_calling_condition)
    loanWF.add_conditional_edges("check_assets", grant_loan_condition) 
    #loanWF.add_conditional_edges("grantLoan", grant_loan_condition)
    ##loanWF.add_edge(START, "grantLoan")
    ##loanWF.add_conditional_edges("grantLoan", grant_loan_condition)
    ###loanWF.add_edge(START, "loanAggrement")
    loanWF.add_edge("loanAggrement", "Complete")
    app = loanWF.compile()  
        
    result = app.invoke(state)  
    user_input="hi ther my name is kasi"    
    events=app.stream({"messages":[("user", user_input)]})
    return result

#to del start
qstate: QueryState = {
    "messages": [],
    "name_address": "",
    "gst_number": "",
    "org_name": "",
    "loan_purpose": "",
    "loan_amount": "",
    "loan_duration": "",
    "next": False
    }
qstate["name_address"]="Kasi Ramanathan, 403 Architha daffodils, 17th cross, RR nager, Bangalore 560098"
#qstate["gst_number"]="07AAECR2971C1ZN"
#qstate["org_name"]="Nexa Evergreens Pvt Ltd"Barbeque Nation
qstate["org_name"]="Barbeque Nation"
qstate["loan_amount"]=900
#callAgent(qstate)  uncomment for command line testing


def query_Name_LLM(state:State):
  #  messages = [    {"role": "system", "content": "get the answer for all the queries, keep asking the qurey in different working until you get mort then 80% confident answer, the querires are 1. what is your name, 2. provide your gst number, 3. why do you need loan is it for new business or for extending your new business, 4. How much loan amount do you want, 5. what duration do you want "},
   # {"role": "user", "content": ""}]
    #print(state)
    #print(state["messages"])
    messages = [{"role": "system", "content": "Can you identify the person’s name and address from the provided information?"},
                {"role": "user", "content": state["messages"]}]
    result=llm.invoke(messages) 
    state["name_address"]=result.content
    #print(result.content)
    return{"messages":result.content}
def validateGstnLLM(state:State):
    print("1...")
   # print(state["messages"])
    messages = [{"role": "system", "content": "Check if the input is like the GSTIN format sample 07AAECR2971C1ZN using length, character pattern, and position rules. Return only the result and a confidence score in percentage."},
                {"role": "user", "content": state["messages"]}]
    gstnResult=llm.invoke(messages) 
    state["gst_number"]=gstnResult.content
    print("2...")
    print(gstnResult.content)
    match = re.search(r'(\d+)\s*%', gstnResult.content)
    match = (match.group(1) if match else 0)    
    if int(match)>30:        
        return True, "Can you provide your Orgonization Name?"
    else:
        
        return False, "Could you provide a valid GSTIN number?"
def validateAmtLLM(state:State):
    print("7...")
    print(state)
    messages = [{"role": "system", "content": "Determine whether the provided input is a positive number, return also the confidence score."},
            {"role": "user", "content": state["messages"]}]
    amtResult=llm.invoke(messages)
    state["loan_amount"]=amtResult.content
    match = re.search(r'(\d+)\s*%', amtResult.content)
    match = (match.group(1) if match else 0)  
    print(match)  
    if int(match)>30:
        return True, "Priocessing loan request..."        
    else:
        return False, "Could you provide a valid loan amount in crores"
    
def validateOrgLLM(state:State):
    print("5...")
    print(state["messages"])
    messages = [{"role": "system", "content": "Determine if the input represents a valid organization. Return only the result and a confidence score. If the input indicates ‘new business’, skip validation and return 100% confidence"},
                {"role": "user", "content": state["messages"]}]
    print(messages)
    orgResult=llm.invoke(messages) 
    state["org_name"]=orgResult.content
    print("6...")
    print(orgResult.content)
    match = re.search(r'(\d+)\s*%', orgResult.content)
    match = (match.group(1) if match else 0)    
    if int(match)>30:
        return True, "Specify the desired loan amount in crores."        
    else:
        return False, "Could you provide a valid Orgonization Name?"
        

def query_get_LLM_output(address):
    nameaddress=[{"role": "system", "content": "Does this appear to be a valid address? Please provide your confidence level as a percentage."},
                   {"role": "user", "content": address }]
    validAddress=llm.invoke(nameaddress)
    match = re.search(r'(\d+)\s*%', validAddress.content)
    match = (match.group(1) if match else 0)
    print("2...")
    print(validAddress.content)
    if int(match)>30:
        return True, "Can you provide your GSTIN number?"
    else:
        return False, "Could you please enter a valid name and address?"

#def query_gst_LLM_again(state:State):

query_builder=StateGraph(QueryState)
query_builder.add_node("query_Name_LLM", query_Name_LLM)
#query_builder.add_node("get_gst", query_Name_LLM)
#query_builder.add_node("get_perpose", query_Name_LLM)
query_builder.add_edge(START, "query_Name_LLM")
#query_builder.add_conditional_edge()
query_builder.add_edge("query_Name_LLM", END)
query_graph=query_builder.compile()
#query_graph.invoke({"messages": "Kasi Ramanathan, 403 Architha daffodils, 17th cross, RR nager, Bangalore 560098"})
def validateAgent(message):
    result=query_Name_LLM( {"messages": message})
    return(result)
  #  return(result["messages"][-1].content)
def validateGstnImpl(message):
    result=validateGstnLLM( {"messages": message})
    return(result)
def validateOrgImpl(message):
    result=validateOrgLLM( {"messages": message})
    return(result)
def validateAmtImpl(message):
    result=validateAmtLLM( {"messages": message})
    return(result)

#print(graph.invoke({"messages": "What is the current stock price of Apple?"}))             
from langchain_core.messages import HumanMessage
def callGraph(userinput):
    result=graph.invoke({
        "messages": [HumanMessage(content=userinput)]
    })
    return(result["messages"][-1].content)

def queryagent(state:State):
    messages = [    {"role": "system", "content": "get the answer for all the queries, keep asking the qurey in different working until you get mort then 80% confident answer, the querires are 1. what is your name, 2. provide your gst number, 3. why do you need loan is it for new business or for extending your new business, 4. How much loan amount do you want, 5. what duration do you want "},
    {"role": "user", "content": ""}]
    result=llm.invoke(messages)
    print(result.content)  
def getUserName(state:State):
    messages = [    {"role": "system", "content": "get the name of the user if you find it suspicious then return null"},
    {"role": "user", "content": ""}]
    result=llm.invoke(messages)
    print(result.content)
#getUserName(State)
#getInfoBuilder=StateGraph(State)

def calltestllm(message):
    result=graph.invoke({"messages": message})
    return(result["messages"][-1].content)