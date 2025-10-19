import asyncio
import re
from .text_utils import scrub_unsafe_characters, chunk_text
from .feels_classifier import classify_sentiment
from .mqtt_publisher import get_mqtt_publisher

async def process_message_for_tts(message: str, persona: str) -> list[dict]:
    """
    Processes a message by chunking, scrubbing, and classifying sentiment for each chunk.

    Args:
        message: The input message string from the LLM.

    Returns:
        A list of dictionaries, where each dictionary contains the processed chunk,
        its sentiment classification, and the original chunk.
        Example: [{"original_chunk": "...", "processed_chunk": "...", "sentiment": {"emotion": "joy", "score": 0.99}}]
    """
    
    # Chunk the message if it's too long
    # The chunk_text function handles the tokenization and splitting
    chunks = chunk_text(message)
    
    # Classify sentiment for all chunks in parallel (non-blocking)
    sentiment_tasks = [asyncio.get_event_loop().run_in_executor(None, classify_sentiment, chunk) for chunk in chunks]
    sentiments = await asyncio.gather(*sentiment_tasks)
    
    processed_results = []

    for chunk, sentiment in zip(chunks, sentiments):
        # Scrub unsafe characters from the chunk
        scrubbed_chunk = scrub_unsafe_characters(chunk)
        
        # Remove asterisk actions for TTS (e.g., *action* -> removed)
        tts_chunk = re.sub(r'\*.*?\*', '', scrubbed_chunk).strip()
        
        # Print debug statement
        if "error" not in sentiment:
            print(f"Debug: Sentiment for chunk '{chunk}' - Emotion: {sentiment['dominant_emotion']}, Score: {sentiment['dominant_score']:.2f}")
        else:
            print(f"Debug: Sentiment classification failed for chunk '{chunk}': {sentiment['error']}")
            
        processed_results.append({
            "original_chunk": chunk,
            "processed_chunk": tts_chunk,
            "sentiment": sentiment
        })
    
    # Publish aggregated emotion to MQTT
    if processed_results:
        # Aggregate weights across all chunks
        all_weights = {}
        for result in processed_results:
            sentiment = result["sentiment"]
            if "weights" in sentiment:
                for emotion, weight in sentiment["weights"].items():
                    all_weights[emotion] = all_weights.get(emotion, 0) + weight
        
        # Normalize aggregated weights
        total_weight = sum(all_weights.values())
        if total_weight > 0:
            aggregated_weights = {emotion: weight / total_weight for emotion, weight in all_weights.items()}
        else:
            aggregated_weights = {}
        
        # Find dominant emotion from aggregated
        dominant_emotion = max(aggregated_weights, key=aggregated_weights.get) if aggregated_weights else "neutral"
        dominant_score = aggregated_weights.get(dominant_emotion, 0) if aggregated_weights else 0
        
        aggregated_sentiment = {
            "dominant_emotion": dominant_emotion,
            "dominant_score": dominant_score,
            "weights": aggregated_weights
        }
        
        # Publish to MQTT
        mqtt_publisher = get_mqtt_publisher()
        mqtt_publisher.publish_emotion(persona.lower(), aggregated_sentiment)
    
    return processed_results

# Example usage (optional, for testing the function)
if __name__ == "__main__":
    long_message = "This is a very long message that needs to be processed. It contains various emotions and characters. I am so happy today! But also a little bit sad. What a surprise! This should be chunked and analyzed. Let's see if it works. 😊👍" * 5
    
    print("--- Processing long message ---")
    results = process_message_for_tts(long_message, "yoda")
    
    for i, result in enumerate(results):
        print(f"\n--- Chunk {i+1} ---")
        print(f"Original Chunk: {result['original_chunk'][:100]}...") # Print first 100 chars
        print(f"Scrubbed Chunk: {result['processed_chunk'][:100]}...") # Print first 100 chars
        print(f"Sentiment: {result['sentiment']}")

    short_message = "I feel great!"
    print("\n--- Processing short message ---")
    results_short = process_message_for_tts(short_message, "yoda")
    for i, result in enumerate(results_short):
        print(f"\n--- Chunk {i+1} ---")
        print(f"Original Chunk: {result['original_chunk']}")
        print(f"Scrubbed Chunk: {result['processed_chunk']}")
        print(f"Sentiment: {result['sentiment']}")