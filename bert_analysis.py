from transformers import AutoModel, AutoTokenizer
import torch
import torch.nn as nn
import os

# Set offline mode to use cached models
os.environ["TRANSFORMERS_OFFLINE"] = "1"


# Define the same model architecture as in the notebook
class BERTClass(nn.Module):
    def __init__(self):
        super(BERTClass, self).__init__()
        self.roberta = AutoModel.from_pretrained("roberta-base", local_files_only=True)
        self.fc = nn.Linear(768, 5)

    def forward(self, ids, mask, token_type_ids):
        _, features = self.roberta(
            ids, attention_mask=mask, token_type_ids=token_type_ids, return_dict=False
        )
        output = self.fc(features)
        return output


# Initialize model and tokenizer
model = BERTClass()
tokenizer = AutoTokenizer.from_pretrained("roberta-base", local_files_only=True)

# Load the trained weights
PATH = r"D:\sentinal\model.bin"
state_dict = torch.load(PATH, map_location=torch.device("cpu"))

# Remove position_ids if present (it's a buffer, not a parameter)
if "roberta.embeddings.position_ids" in state_dict:
    del state_dict["roberta.embeddings.position_ids"]

model.load_state_dict(state_dict)
model.eval()

# Emotion labels (must match the 5 outputs from the model's fc layer)
emotion_labels = ["anger", "fear", "joy", "sadness", "surprise"]


# Function to predict emotions from text
def predict_emotions(text, threshold=0.5):
    # Tokenize the input text
    inputs = tokenizer.encode_plus(
        text,
        truncation=True,
        add_special_tokens=True,
        max_length=200,
        padding="max_length",
        return_token_type_ids=True,
        return_tensors="pt",
    )

    ids = inputs["input_ids"]
    mask = inputs["attention_mask"]
    token_type_ids = inputs["token_type_ids"]

    # Get model output
    with torch.no_grad():
        outputs = model(ids, mask, token_type_ids)
        predictions = torch.sigmoid(outputs).cpu().numpy()[0]

    # Convert predictions to emotion labels
    detected_emotions = []
    emotion_scores = {}

    for idx, (emotion, score) in enumerate(zip(emotion_labels, predictions)):
        emotion_scores[emotion] = float(score)
        if score >= threshold:
            detected_emotions.append(emotion)

    return {
        "text": text,
        "detected_emotions": detected_emotions if detected_emotions else ["neutral"],
        "emotion_scores": emotion_scores,
    }
