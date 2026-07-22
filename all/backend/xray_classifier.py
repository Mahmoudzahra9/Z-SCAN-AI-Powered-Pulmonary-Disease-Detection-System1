import torch
from PIL import Image
import io
import os

_processor = None
_model = None

def _load_clip_model():
    """Load CLIP model once at startup. Called on module import."""
    global _processor, _model
    try:
        from transformers import CLIPProcessor, CLIPModel
        model_id = "openai/clip-vit-base-patch32"
        cache_dir = os.path.join(os.path.dirname(__file__), ".cache")

        print("⏳ Loading CLIP model for chest X-ray verification...")
        _processor = CLIPProcessor.from_pretrained(model_id, cache_dir=cache_dir)
        _model = CLIPModel.from_pretrained(model_id, cache_dir=cache_dir)
        _model.eval()
        print("✅ CLIP model loaded and ready.")
    except Exception as e:
        print(f"⚠️  CLIP model could not be loaded: {e}")
        _processor = None
        _model = None

# Load immediately when this module is imported (once at server startup)
_load_clip_model()


def check_is_chest_xray(image_bytes):
    """
    Use cached CLIP model (loaded at startup) to verify the image is a chest X-ray.
    Returns (is_xray: bool, confidence: float).
    If CLIP is unavailable, returns (True, 1.0) to allow normal inference.
    """
    if _model is None or _processor is None:
        return True, 1.0

    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        labels = [
            "a chest x-ray scan or lung radiography medical image",
            "a regular photo or portrait or cartoon or document or landscape or animal"
        ]

        inputs = _processor(text=labels, images=img, return_tensors="pt", padding=True)
        with torch.no_grad():
            outputs = _model(**inputs)
            probs = outputs.logits_per_image.softmax(dim=1)

        xray_prob = probs[0][0].item()
        is_xray = xray_prob > 0.65
        return is_xray, xray_prob
    except Exception as e:
        print(f"⚠️  CLIP verification error: {e}")
        return True, 1.0
