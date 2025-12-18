import os
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from bert_analysis import predict_emotions
from langchain_core.messages import SystemMessage

# Load environment variables from .env file
load_dotenv()

HF_API_KEY = os.environ.get("HF_TOKEN")
HF_BASE_URL = "https://router.huggingface.co/v1"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_NAME = "openai/gpt-oss-20b:groq"

llm = ChatOpenAI(
    model=MODEL_NAME,
    openai_api_key=HF_API_KEY,
    openai_api_base=HF_BASE_URL,
    max_retries=3,
    timeout=60,
)


def generate_text(text) -> str:
    res_bert = predict_emotions(text)
    logger.info(f"Detected Emotions: {res_bert}")

    prompt = f"""### ROLE & OBJECTIVE
        You are a compassionate, non-judgmental mental health support assistant. 
        Your goal is to provide emotional support, validate the user's feelings, and offer gentle coping strategies.
        You are NOT a doctor and cannot provide medical diagnoses.

        ### INPUT CONTEXT
        - User Input: "{text}"
        - Detected Emotion (via analysis): "{res_bert}"

        ### GUIDELINES
        1. **Empathy First:** Start by validating the user's feelings based on the "{res_bert}". Acknowledge their state without being patronizing.
        2. **Non-Judgmental Tone:** Ensure your language is safe, open, and accepting, as per the core requirement for accessible support.
        3. **Brevity & Warmth:** Keep responses concise (2-3 sentences) but warm. Do not write long essays.
        4. **Actionable Help:** If appropriate, suggest a simple wellness activity (e.g., deep breathing, taking a walk, listening to music) relevant to their mood.
        5. **Safety Guardrails:**
        - If the user mentions self-harm, suicide, or severe danger, IMMEDIATELY stop acting as a chatbot and provide the standard suicide prevention hotline number for India (or their region) and urge them to seek professional help.
        - Do not claim to cure depression or anxiety.

        ### RESPONSE STRUCTURE
        [Validation of Emotion] + [Supportive Statement] + [Gentle Question or Coping Suggestion]"""

    messages = [SystemMessage(content=prompt)]
    response = llm.invoke(messages)
    return response


if __name__ == "__main__":
    answer = generate_text(
        "I am feeling very sad that i scored less marks in my Fat exam."
    )
    logger.info(f"answer:{answer.content}")
