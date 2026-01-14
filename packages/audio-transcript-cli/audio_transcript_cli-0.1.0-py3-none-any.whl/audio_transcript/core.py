import torch
import numpy as np
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
from pydub import AudioSegment
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def transcribe(
    audio_path: str,
    model_name: str = "openai/whisper-large-v2",
    chunk_length_ms: int = 30000,
    device: str = None
) -> str:
    """
    Transcribe an audio file using Whisper in chunks.

    Args:
        audio_path: Path to the audio file.
        model_name: Name of the Hugging Face model to use.
        chunk_length_ms: Length of each chunk in milliseconds.
        device: Device to use ('cuda', 'cpu', 'mps'). Auto-detected if None.

    Returns:
        The complete transcription text.
    """
    # Device detection
    if device is None:
        if torch.cuda.is_available():
            device = "cuda"
        elif torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"
    
    logger.info(f"Using device: {device}")

    # Load model and processor
    logger.info(f"Loading model: {model_name}...")
    try:
        processor = AutoProcessor.from_pretrained(model_name)
        model = AutoModelForSpeechSeq2Seq.from_pretrained(model_name)
        model.to(device)
    except Exception as e:
        logger.error(f"Failed to load model {model_name}: {e}")
        raise

    # Load and process audio
    logger.info(f"Loading audio file: {audio_path}")
    try:
        audio = AudioSegment.from_file(audio_path)
    except Exception as e:
        logger.error(f"Failed to load audio file: {e}")
        raise ValueError(f"Could not load audio file {audio_path}. Ensure ffmpeg is installed.")

    # Convert to mono and set sample rate to 16kHz (Whisper requirement)
    audio = audio.set_channels(1).set_frame_rate(16000)
    
    duration_ms = len(audio)
    logger.info(f"Audio duration: {duration_ms / 1000:.2f} seconds")
    
    transcriptions = []
    num_chunks = (duration_ms // chunk_length_ms) + 1
    
    for i in range(0, duration_ms, chunk_length_ms):
        chunk_num = (i // chunk_length_ms) + 1
        logger.info(f"Processing chunk {chunk_num}/{num_chunks}...")
        
        # Extract chunk
        chunk = audio[i:i + chunk_length_ms]
        
        # Convert to numpy array
        # pydub stores audio as raw bytes, we need to convert to float32 normalized to [-1, 1]
        samples = np.array(chunk.get_array_of_samples(), dtype=np.float32)
        
        # Normalize to [-1, 1] range based on the sample width
        # AudioSegment.array_type returns the python array type code (e.g. 'h' for short)
        sample_max_value = float(2 ** (8 * chunk.sample_width - 1))
        samples = samples / sample_max_value
        
        # Process audio features
        try:
            inputs = processor(samples, sampling_rate=16000, return_tensors="pt")
            input_features = inputs.input_features.to(device)
            
            # Generate transcription
            with torch.no_grad():
                predicted_ids = model.generate(
                    input_features,
                    max_length=448,
                    num_beams=5
                )
            
            # Decode
            transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
            transcriptions.append(transcription)
        except Exception as e:
            logger.error(f"Error processing chunk {chunk_num}: {e}")
            # Continue processing other chunks? Or fail?
            # For now, let's append a placeholder or empty string to avoid total failure
            transcriptions.append(f"[Error in chunk {chunk_num}]")
    
    full_transcript = " ".join(transcriptions)
    return full_transcript
