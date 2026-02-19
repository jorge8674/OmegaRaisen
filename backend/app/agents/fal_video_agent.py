"""
Fal Video Agent - Video generation via Fal.ai (Kling, Hunyuan, Wan)
Filosofía: No velocity, only precision 🐢💎
"""
import os
import logging
from typing import Optional
import fal_client

logger = logging.getLogger(__name__)


class FalVideoAgent:
    """Agent for AI video generation using Fal.ai models"""

    MODEL_MAP = {
        "kling": "fal-ai/kling-video/v2/standard/text-to-video",
        "hunyuan": "fal-ai/hunyuan-video",
        "wan": "fal-ai/wan-t2v"
    }

    def __init__(self):
        fal_client.api_key = os.getenv("FAL_KEY")
        self.default_model = "kling"

    async def execute(
        self,
        prompt: str,
        model: str = "kling",
        duration: int = 5,
        aspect_ratio: str = "16:9"
    ) -> dict:
        """
        Generate video using Fal.ai models

        Args:
            prompt: Text description of the video
            model: Model key (kling, hunyuan, wan)
            duration: Video duration in seconds
            aspect_ratio: Video aspect ratio (16:9, 9:16, 1:1)

        Returns:
            dict with video_url, model, prompt, duration, status
        """
        try:
            # Resolve model name
            model_id = self.MODEL_MAP.get(model, self.MODEL_MAP[self.default_model])

            logger.info(f"FalVideoAgent: Generating video with {model_id}")

            # Prepare arguments based on model
            arguments = {
                "prompt": prompt
            }

            # Model-specific parameters
            if model == "kling":
                arguments["duration"] = duration
                arguments["aspect_ratio"] = aspect_ratio
            elif model == "hunyuan":
                arguments["duration"] = duration
                arguments["aspect_ratio"] = aspect_ratio
            elif model == "wan":
                arguments["num_frames"] = duration * 8  # ~8 fps

            # Subscribe to Fal model (async)
            result = await fal_client.subscribe_async(
                model_id,
                arguments=arguments
            )

            # Extract video URL from result
            video_url = None
            if "video" in result and "url" in result["video"]:
                video_url = result["video"]["url"]
            elif "video_url" in result:
                video_url = result["video_url"]
            elif "output" in result:
                video_url = result["output"]

            if not video_url:
                raise Exception(f"No video URL in result: {result.keys()}")

            logger.info(f"FalVideoAgent: Video generated successfully: {video_url}")

            return {
                "video_url": video_url,
                "model": model,
                "model_id": model_id,
                "prompt": prompt,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "status": "success"
            }

        except Exception as e:
            logger.error(f"FalVideoAgent failed: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "model": model,
                "prompt": prompt
            }

    def get_available_models(self) -> dict:
        """Get list of available models"""
        return {
            "kling": {
                "name": "Kling Video V2",
                "description": "High-quality text-to-video from Kuaishou",
                "max_duration": 10,
                "aspect_ratios": ["16:9", "9:16", "1:1"]
            },
            "hunyuan": {
                "name": "Hunyuan Video",
                "description": "Tencent's video generation model",
                "max_duration": 10,
                "aspect_ratios": ["16:9", "9:16", "1:1"]
            },
            "wan": {
                "name": "Wan T2V",
                "description": "Fast text-to-video generation",
                "max_frames": 80,
                "aspect_ratios": ["16:9"]
            }
        }
