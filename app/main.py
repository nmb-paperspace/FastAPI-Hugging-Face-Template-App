from fastapi import FastAPI
from contextlib import asynccontextmanager
from transformers import AutoTokenizer, pipeline

import torch
import transformers
from transformers import AutoTokenizer

# function to return a transformers pipeline for translation
#def get_translation_pipeline():
#    return pipeline('translation', model='/opt/integrations/opus-mt-en-es', tokenizer='/opt/integrations/opus-mt-en-es')

def get_text_generation_pipeline():

    pipe = pipeline(
        'text-generation',
        model='/opt/integrations/mpt-125m',
        tokenizer=AutoTokenizer.from_pretrained('EleutherAI/gpt-neox-20b'),
        device='cuda:0',
        trust_remote_code=True,
        use_auth_token='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',
        max_new_tokens=100,
        do_sample=True,
        use_cache=True
        )

    return pipe

models = {}

# creating an async context manager to define events to take place on startup and shutdown of the FastAPI app
# more information about lifespan events can be found here: https://fastapi.tiangolo.com/advanced/events/
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model on startup
    #models['translation'] = get_translation_pipeline()
    models['generated_text'] = get_text_generation_pipeline()
    yield
    # Clean up the ML models and release the resources on shutdown
    models.clear()

app = FastAPI(lifespan=lifespan)

# startup checks detect if a container has started successfully which will then kickoff the liveness and readiness checks
@app.get("/startup/", status_code=200)
def startup_check():
    return "Startup check succeeded."

# liveness checks detect deployment containers that transition to an unhealthy state and remedy said situations through targeted restarts
@app.get("/liveness/", status_code=200)
def liveness_check():
    return "Liveness check succeeded."

# readiness checks tell our load balancers when a container is ready to receive traffic
@app.get("/readiness/", status_code=200)
def readiness_check():
    return "Readiness check succeeded."

@app.get("/")
async def root():
    return {"message": "Welcome to my FastAPI + Hugging Face app!"}

## translate endpoint that takes in an english string and returns the spanish translation
#@app.get("/translate")
#async def translate(text_input: str):
#    return models['translation'](text_input)[0]

# "generate" endpoint that takes in a prompt and returns the model's response
@app.get("/generate")
async def generate(text_input: str):
    return models['generated_text'](text_input)[0]

# Add additional endpoints below
