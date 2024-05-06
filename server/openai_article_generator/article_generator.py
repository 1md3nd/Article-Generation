# Importing necessary libraries and modules
from langchain.prompts import PromptTemplate
import os
from langchain_openai import OpenAI
from helper import prompts
from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from helper.models import ArticleModel, ArticleGenerationInput, ArticleGenerationOutput, ArticleURLInput
from langchain_core.runnables.base import RunnableLambda
from stablilty_with_cloudinary.image_generator import ImageGenerator 
from datetime import datetime
from langchain_community.document_loaders import WebBaseLoader
import spacy
from helper.callbacks import MyCallbackHandler

# Load English language model from spaCy
nlp = spacy.load("en_core_web_sm")

# Load environment variables from .env file
load_dotenv()

# Create an instance of ImageGenerator for generating and uploading images
image_generator_and_uploader = ImageGenerator()

# Extract OpenAI API key from environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')

# Load prompt templates from config
article_from_topic_template = prompts.article_from_topic_template
article_from_context_template = prompts.article_from_context_template

# Create an instance of JsonOutputParser for parsing JSON outputs
output_parser = JsonOutputParser(pydantic_object=ArticleModel)

# Create PromptTemplate instances for manual creation
article_from_topic_prompt = PromptTemplate(
    template=article_from_topic_template,
    input_variables=['topic', 'description', 'authors'],
    partial_variables={"format_instructions": output_parser.get_format_instructions()})

# Create PromptTemplate instances for URL form
article_from_context_prompt = PromptTemplate(
    input_variables=['article_context'],
    template=article_from_context_template,
    partial_variables={"format_instructions": output_parser.get_format_instructions()})

callback_handler = MyCallbackHandler()
# Initialize OpenAI model
llm = OpenAI(model='gpt-3.5-turbo-instruct', temperature=0.5, max_tokens=-1, callbacks=[callback_handler])
 
def get_token_feedback_from_callbacks():
    token_usage = {
        'llm_invoke_count': callback_handler.llm_invoke_count,
        'total_tokens_used': callback_handler.total_tokens_used,
        'completion_tokens_used': callback_handler.completion_tokens_used,
        'prompt_tokens_used': callback_handler.prompt_tokens_used,
        'last_llm_token_feedback': callback_handler.last_llm_token_feedback
    }
    return token_usage

# Function to extract metadata from LLM response
def extract_metadata_from_response(llm_response, image_urls):
    """Extract metadata from LLM response."""
    res = {}
    res['title'] = llm_response.get('title', "")
    res['authors'] = " ".join(llm_response.get('authors', "")[:2])
    res['abstract'] = llm_response.get('abstract', "")
    curr_datetime = datetime.now().strftime("%Y-%m-%d %H:%M")
    generated_datetime = llm_response.get('publication_date', "")
    res['publication_date'] = generated_datetime if generated_datetime in ("", " ") else curr_datetime
    res['image_urls'] = image_urls
    res['keywords'] = llm_response.get('keywords', "")
    temp_article = llm_response.get('article', "")
    if temp_article:
        res['article_contents'] = temp_article.split("\n\n")
    return res

# Function to generate and upload images asynchronously
async def generate_upload_image(llm_response):
    """Generate and upload images."""
    image_prompt = llm_response['image_prompt']
    if image_prompt:
        image_urls = image_generator_and_uploader.generate_and_upload_images(image_prompt)
    response = extract_metadata_from_response(llm_response, image_urls)
    return response

# Function to fetch article context from a given URL
async def get_article_context(request):
    """Fetch article context from a URL."""
    try:
        loader = WebBaseLoader(request['article_url'])
        docs = loader.load()
        page_content = docs[0].page_content
        page_content = page_content.replace('\t', ' ').replace('\n', ' ').replace("  ", "")
        nlp_doc = nlp(page_content)
        keywords = nlp_doc.ents
        res_keywords = " ".join(str(key) for key in keywords)
        return {'article_context': res_keywords}
    except Exception as e:
        print(f"Error occurred while fetching article at {request['article_url']}: {e}")
        return {'error': e}

# Define model chains
from_topic_chain = article_from_topic_prompt | llm | output_parser | RunnableLambda(generate_upload_image)
from_context_chain = RunnableLambda(get_article_context) | article_from_context_prompt | llm | output_parser | RunnableLambda(generate_upload_image)

# Define input and output types for model chains
from_topic_chain = from_topic_chain.with_types(input_type=ArticleGenerationInput, output_type=ArticleGenerationOutput)
from_context_chain = from_context_chain.with_types(input_type=ArticleURLInput, output_type=ArticleGenerationOutput)
