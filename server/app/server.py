from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse,RedirectResponse
from langserve import add_routes
from dotenv import load_dotenv
from openai_article_generator.article_generator import from_topic_chain, from_context_chain
from openai_article_generator.article_generator import get_token_feedback_from_callbacks
load_dotenv()


# Create FastAPI app
app = FastAPI(
    title='LangChain Server',
    version="1.0",
    description='Article Generator App'
)

# Add routes for article generation and information extraction
add_routes(app, from_topic_chain, path='/openai_article_topic',include_callback_events=True)
add_routes(app, from_context_chain, path='/openai_article_context')

# Redirect root to docs
@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


@app.get('/tokens-usage')
def get_token_usage():
    return get_token_feedback_from_callbacks()

# Error handling
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"message": "Internal Server Error"})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})


# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)