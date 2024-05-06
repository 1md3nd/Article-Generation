from langchain.pydantic_v1 import BaseModel, Field
from typing import List, Optional

class ArticleModel(BaseModel):
    title : str = Field(description="The title of the article.")
    authors: List[str] = Field(description="The author(s) of the article.")
    abstract : str = Field(description="A brief summary of the article's content.")
    image_prompt : str = Field(description="A combination of positive relevant to the 'article_name', 'article_description', and 'article'. These prompts contain only descriptive text visually describing the images (the images do not contain any text) and do not include conclusions about the images.")
    article : str = Field(description="The generated article and do not use any \" inside the article.")
    publication_date : str = Field(description="if plucation_data is provided in Context or if not present just return '' empty string. ")
    keywords : str = Field(description="The most relevant keywords for the article.")


class ArticleGenerationInput(BaseModel):
    topic: str
    description: str
    authors: str

class ArticleGenerationOutput(BaseModel):
    title: str
    authors: Optional[str]
    abstract: str
    publication_date: str
    image_urls: List[str]
    keywords: str
    article_contents: Optional[List[str]]

class ArticleURLInput(BaseModel):
    article_url : str