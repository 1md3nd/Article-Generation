import streamlit as st
from utils import generate_html

# Check if authors are available in session state, otherwise redirect to the main page
if 'authors' not in st.session_state or st.session_state.authors is None:
    st.switch_page("streamlit_app.py")
st.sidebar.page_link("streamlit_app.py",label="Home Page")
# Get the generated article from session state
generated_article = st.session_state.generated_article

# Generate HTML code for the article
html_code = generate_html.generate_html_code(generated_article)

# Create two columns layout for displaying HTML code and preview
col1, col2 = st.columns([0.4, 0.6])

# Display HTML code in the first column
with col1:
    st.header('Copy HTML')
    st.code(html_code)

# Display preview of the HTML in the second column
with col2:
    st.header('Preview')
    st.markdown(html_code, unsafe_allow_html=True)
