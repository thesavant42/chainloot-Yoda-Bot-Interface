# Early feelings classifier test script
import torch
import warnings
from transformers import pipeline, AutoTokenizer, logging

# Set transformers logging to show only errors
logging.set_verbosity_error()

# Trained on 28 different emotional expressions
#
# https://huggingface.co/joeddav/distilbert-base-uncased-go-emotions-student/tree/main
#
# | admiration | curiosity | fear | optimism |
# | amusement | desire | gratitude | pride |
# | anger | disappointment | grief | realization |
# | annoyance | disapproval | joy | relief |
# | approval | disgust | love | remorse |
# | caring | embarrassment | nervousness | sadness |
# | confusion | excitement | neutral | surprise |
#

model_id = "joeddav/distilbert-base-uncased-go-emotions-student"

# print(f"Loading standard model: {model_id}")
classifier = pipeline(
    "text-classification",
    model=model_id,
    device=0,
    top_k=1
)

# Define your input text
text = "I'm so excited for the concert tonight!"

# Pass the text to the classifier to get predictions
predictions = classifier(text)

print(predictions)