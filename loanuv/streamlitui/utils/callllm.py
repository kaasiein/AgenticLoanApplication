from langchain_groq import ChatGroq
groq_api_key ="YOUR_GROQ_API_KEY"  # Replace with your actual Groq API key
llm=ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-8b-instant")
#https://www.youtube.com/watch?v=b2iM9bPdAEs&list=PLZoTAELRMXVNAprLfaHq64tBeCGvWSVpv


#tools   
def tool_calling_llm():
    from langchain_community.tools.tavily_search import TavilySearchResults
    TAVILT_API_KEY="YOUR_TAVILY_API_KEY"  # Replace with your actual Tavily API key
    travily=TavilySearchResults(tavily_api_key=TAVILT_API_KEY)
    #print(travily.invoke("What is the current stock price of Apple?"))
    tools=[travily]
    llm_with_tools=llm.bind_tools(tools=tools)
    print(llm_with_tools.invoke("recent news on ai?"))
    return llm_with_tools
def callllm(string):
    result=llm.invoke(string)
    return result.content

