import streamlit as st
import requests
import os
import numpy # Use this to organize snippets information later on
import openai
import time

openai_api_key = os.environ.get('OPENAI_API_KEY')

def search_bing(query):
    url = "https://api.bing.microsoft.com/v7.0/search"
    headers = {
        "Ocp-Apim-Subscription-Key": os.getenv('BING_API_KEY'),
    }
    params = {
        "q": query,
    }

    response = requests.get(url, headers=headers, params=params)
    results = response.json().get("webPages", {}).get("value", [])
    
    return results

def get_prompt_str_using_bing(search_query, data):
    data_str = '\n'.join(data)
    #returning as HTML so we don't need to execute in streamlit
    return f"""
    Question: {search_query}
    Input: {data_str}
    Output: 
    - Return code to create an embeddable HTML visualization widget with above data in streamlit
    - Aim to answer the question and include relevant info in your visualization
    - Minimize error
    - Do not include any explanation in your response. Make the code runnable as is
    - Make the visualization look great. eg. Feel free to include images in your html
    """

# Try: GPT4 built-in web search (currently in repair)
# def get_prompt_str(search_query, urls):
#     #returning as HTML so we don't need to execute in streamlit
#     return f"""
#     Given a search query: {search_query}, search the web for information.
#     """
#     Output: 
#     - Return code to create an HTML visualization widget with above info in plain HTML
#     - Aim to answer the question and include relevant info in your visualization
#     - Do not include any explanation in your response. Make the code runnable as is
#     - Make the visualization look great. eg. Feel free to include images in your html
#     """

# Try: Reading from url
# def get_prompt_str(search_query, urls):
#     ... some handling of multiple urls
#     #returning as HTML so we don't need to execute in streamlit
#     return f"""
#     Input:
#     [Text from: {url}]
#     Output: 
#     - Return code to create an HTML visualization widget with above info in plain HTML
#     - Aim to answer the question and include relevant info in your visualization
#     - Do not include any explanation in your response. Make the code runnable as is
#     - Make the visualization look great. eg. Feel free to include images in your html
#     """

def prompt_gpt(prompt):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


st.title('Bing Search App')
query = st.text_input('Enter your search query:')
if query:
    search_query = f"Searching for: {query}"
    st.write(search_query)
    results = search_bing(query)
    all_snippets = []
    for result in results:
        # [Text from: url] in GPT4 plus prompt for internet access
        # st.markdown(f"[{result['name']}]({result['url']})")
        # TODO: instead of immediately printing a snippet, paste the info into chatGPT as input
        # and prompt - "Input: {this information} Output: create an HTML widget in streamlit"
        
        all_snippets.append(result['snippet'])

    
    prompt_input = get_prompt_str_using_bing(search_query=search_query, data=all_snippets)

    # Ask GPT, measure prompt execution time
    prompt_start_time = time.time()
    html_response = prompt_gpt(prompt=prompt_input)
    prompt_end_time = time.time()
    prompt_execution_time = prompt_end_time - prompt_start_time
    st.write(f"GPT execution time: {prompt_execution_time:.2f} seconds")

    # Display in html
    # There’s also a components.iframe in case you want to embed an external website into Streamlit, such as components.iframe("https://docs.streamlit.io/en/latest")
    # st.components.v1.html(html_response, height=600)

    # Display in code (important: check the code to avoid security risks)
    # Display the code
    st.write("Code from GPT:")
    st.code(html_response)

    # Optional: Ask the user if they want to execute the code
    if st.button("Execute Code"):
        # WARNING: Be very careful with this! Make sure the code is safe to run.
        exec(html_response)
    

