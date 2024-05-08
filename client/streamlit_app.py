import streamlit as st
import requests
from utils.generate_html import generate_html_code
import pdfkit
import random
from datetime import datetime
import pandas as pd

# Constants for FastAPI server URLs
ARTICLE_TOPIC_API_URL = "http://localhost:8000/openai_article_topic/invoke"
ARTICLE_CONTEXT_API_URL = "http://localhost:8000/openai_article_context/invoke"
TOKENS_USAGE_API_URL = "http://localhost:8000/tokens-usage"

# Set page configuration
st.set_page_config(layout="wide", page_title='Article Generation')
st.title('Article Generation App')

def generate_article_by_topic(**kwargs):
    """Generate article by making a POST request to the FastAPI server."""
    try:
        data = { "input" : {"topic": kwargs['topic'], "description": kwargs['description'], "authors": kwargs['authors']}}
        response = requests.post(ARTICLE_TOPIC_API_URL, json=data)
        response.raise_for_status()  # Raise an exception for any HTTP error
    except requests.RequestException as e:
        st.error(f"Error generating article: {e}")
        return None
    else:
        return response.json()

def generate_article_by_context(article_url):
    """Generate article by making a POST request to the FastAPI server."""
    try:
        data = {"input" : {"article_url": article_url}}
        response = requests.post(ARTICLE_CONTEXT_API_URL, json=data)
        response.raise_for_status()  # Raise an exception for any HTTP error
    except requests.RequestException as e:
        st.error(f"Error generating article: {e}")
        return None
    else:
        return response.json()

def get_tokens_usage():
    """"GET the tokens usage from the server"""
    try:
        response = requests.get(TOKENS_USAGE_API_URL)
        response.raise_for_status()
    except Exception as e:
        st.write(f'Error in getting tokens_usage: {e}')
        return {}
    else:
        return response.json()
    
def manual_input_form(st):
    """Render manual input form."""
    form = st.form('manual_form')
    topic_text = form.text_input("Enter the topic of the Article")
    description_text = form.text_input('Enter the description of the Article')
    submitted = form.form_submit_button('Submit')

    if submitted and (topic_text or description_text):
        return (topic_text, description_text)
    elif submitted:
        form.warning('Please enter both topic and description.')

def url_input_form(st):
    """Render URL input form."""
    form = st.form('url_form')
    input_url = form.text_input("Enter reference URL to get content")
    submitted = form.form_submit_button('Submit')

    if submitted and input_url:
        return input_url
    elif submitted:
        form.warning('Please enter the URL.')

def random_form(tab):
    """Render random form."""
    # Define dictionary of topics and descriptions
    topic_descriptions = {
        "Technology": [
            "The latest advancements in technology...",
            "Discover new gadgets and innovations...",
            "Insights into the world of AI and machine learning..."
        ],
        "Health": [
            "Tips for maintaining a healthy lifestyle...",
            "Explore natural remedies for common ailments...",
            "The importance of exercise and nutrition..."
        ],
        "Travel": [
            "Explore exotic destinations around the world...",
            "Tips for budget-friendly travel...",
            "Discover hidden gems off the beaten path..."
        ],
        # Add more topics and descriptions as needed
    }

    # Get a list of topics
    topics = list(topic_descriptions.keys())
    col1,col2 = tab.columns(2)
    topic_form = col1.form('random_form_topic')
    selected_topic = topic_form.radio("Select a topic:", options=topics)
    topic_submitted = topic_form.form_submit_button('Select Topic')

    if topic_submitted:
        st.session_state['rand_topic'] = selected_topic

    if 'rand_topic' in st.session_state:
        desc_form = col2.form('random_form_desc')
        default_description = random.choice(topic_descriptions[st.session_state['rand_topic']])
        selected_description = desc_form.text_input("Enter description:", value=default_description)
        desc_submitted = desc_form.form_submit_button('Select Description')

        if desc_submitted:
            st.session_state['rand_desc'] = selected_description
            return True
    return False

def sidebar_authors():
    """Render sidebar authors form."""
    form = st.sidebar.form('metadata')
    authors_input = form.text_input('Author(s) Name')
    submit_button = form.form_submit_button('Submit')
    if submit_button and authors_input:
        st.session_state['authors'] = authors_input
        return authors_input
    elif submit_button:
        st.warning('Please provide a name for the author')
    display_token_feedback_with_cost(st.sidebar)

def render_article_content():
    """Render article content."""
    metadata = st.session_state['generated_article']
    download_article()
    image_urls = metadata['image_urls']
    article_list = metadata['article_contents']

    col1,col2 = st.columns([0.3, 0.7])

    if image_urls:
        col1.image(image_urls[0],width=300)
    col2.subheader(f"{metadata['title']} ",divider='rainbow')
    col2.subheader(f"Author(s): {metadata['authors']}")
    publish_date = metadata['publication_date'] if metadata['publication_date'] not in (''," ") else datetime.now().strftime("%Y-%m-%d %H:%M")
    col2.caption(f"Publish Date : {publish_date}")
    col2.caption(f"Keywords : {metadata['keywords']}")
    col2.caption(f"Abstract : {metadata['abstract']}")
    image_ref_idx = set([2,3,1])
    curr_image = 0
    if article_list:
        for idx in range(len(article_list)):
            if idx in image_ref_idx and image_urls:
                col1,col2 = st.columns([0.4,0.6])
                col1.image(image_urls[curr_image],width=400)
                curr_image+=1
                col2.write(article_list[idx])
            else:
                st.write(article_list[idx])

def calculate_average_cost(token_feedback, cost_per_1000_tokens_completion, cost_per_1000_tokens_total):
    total_tokens_used = token_feedback['total_tokens_used']
    completion_tokens_used = token_feedback['completion_tokens_used']
    prompt_tokens_used = token_feedback['prompt_tokens_used']
    llm_invoke_count = token_feedback['llm_invoke_count']
    
    # Calculate average tokens used per request
    average_tokens_used_per_request = total_tokens_used / llm_invoke_count
    
    # Calculate cost based on completion tokens and total tokens used
    completion_cost = (completion_tokens_used / 1000) * cost_per_1000_tokens_completion
    total_cost = (total_tokens_used / 1000) * cost_per_1000_tokens_total
    
    # Calculate average cost per request
    average_cost_per_request = (completion_cost + total_cost) / llm_invoke_count
    
    return average_cost_per_request

cost_per_1000_tokens_completion = 0.0015  # Cost per 1000 completion tokens
cost_per_1000_tokens_total = 0.0020  # Cost per 1000 total tokens

# Define a function to display token feedback data and average cost
def display_token_feedback_with_cost(stt):
    token_feedback = get_tokens_usage()
    stt.subheader("Token Feedback:")
    stt.write(f"LLM Invoke Count: {token_feedback['llm_invoke_count']}")
    stt.write(f"Total Tokens Used: {token_feedback['total_tokens_used']}")
    stt.write(f"Completion Tokens Used: {token_feedback['completion_tokens_used']}")
    stt.write(f"Prompt Tokens Used: {token_feedback['prompt_tokens_used']}")
    stt.subheader("Last LLM Token Feedback:")
    df = pd.DataFrame(token_feedback['last_llm_token_feedback'].items(),columns=('tokens feedback','counts'))
    stt.table(df)
    stt.subheader("Average Tokens Used per Request Cost:")
    stt.write(f"${calculate_average_cost(token_feedback, cost_per_1000_tokens_completion, cost_per_1000_tokens_total):.4f} per request")

def show_forms(authors):
    """Render forms."""
    with st.container():
        tabs_map = ['Manual Generation','URL','Random']
        tabs = st.tabs(tabs_map)

        if tabs[0]:
            data_manual = manual_input_form(tabs[0])
        if tabs[1]:
            data_url = url_input_form(tabs[1])
        if tabs[2]:
            data_random = random_form(tabs[2])
        response = None
        with st.spinner("Loading..."):
            if data_manual:
                response = generate_article_by_topic(topic=data_manual[0], description=data_manual[1], authors=authors)
            elif data_url:
                data_url = data_url.strip().strip('"').strip("'")
                response = generate_article_by_context(article_url=data_url)
            elif data_random:
                response = generate_article_by_topic(topic=st.session_state['rand_topic'], description=st.session_state['rand_desc'], authors=authors)

        if response and 'error' in response:
            st.warning('There was some problem with generating the article... Please Try Again..')
        elif response:
            st.success('The Article Generation was successful..')
            if 'output' in response:
                st.session_state['generated_article'] = response['output']
            else:
                st.session_state['generated_article'] = response
        if 'generated_article' in st.session_state and st.session_state['generated_article'] is not None:
            render_article_content()

                

@st.cache_data
def convert_html_to_pdf(html_content, pdf_path):
    """Convert HTML content to PDF."""
    try:
        pdfkit.from_string(html_content, pdf_path)
        print(f"PDF generated and saved at {pdf_path}")
    except Exception as e:
        print(f"PDF generation failed: {e}")

def download_article():
    """Download article as PDF."""
    with st.popover('Download'):
        generated_article = st.session_state['generated_article']
        html_code = generate_html_code(generated_article)
        convert_html_to_pdf(html_code, 'output.pdf')
        try:
            with open("output.pdf", "rb") as file:
                btn = st.download_button(
                    label="Download Article",
                    data=file,
                    file_name="output.pdf",
                    mime="text/pdf"
                )
        except FileNotFoundError as e:
            print(f"Error: {e}")

def main():
    """Main function to run the Streamlit app."""
    if 'authors' not in st.session_state:
        st.session_state["authors"] = None
    if 'generated_article' not in st.session_state:
        st.session_state["generated_article"] = None
    sidebar_authors()

    authors = st.session_state['authors']
    st.sidebar.page_link("pages/generate_html_page.py",label="Generate HTML Code")
    if authors:
        st.caption(f"Current Author Name is : {authors}")
        show_forms(authors)
    else:
        st.error('Author name is required to generate articles ')

if __name__ == "__main__":
    main()
