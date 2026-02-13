"""
Content Creator Agent
Generates multimedia content (text, images, videos)
"""
from typing import Dict, Any, List, Optional
import logging
from app.agents.base_agent import BaseAgent, AgentRole, AgentState
from app.infrastructure.ai.openai_service import openai_service

logger = logging.getLogger(__name__)


class ContentCreatorAgent(BaseAgent):
    """
    Agent specialized in content generation
    - Text captions
    - Hashtags
    - Images
    - Video scripts
    """
    
    def __init__(self, agent_id: str = "content_creator_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.CONTENT_CREATOR,
            model="gpt-4o",
            tools=["text_generation", "image_generation", "hashtag_research"]
        )
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute content generation task
        
        Args:
            task: Task parameters
                - type: "caption" | "image" | "hashtags" | "video_script"
                - topic: Content topic
                - platform: Target platform
                - tone: Content tone
                
        Returns:
            Generated content
        """
        self.set_state(AgentState.WORKING)
        
        try:
            task_type = task.get("type")
            
            if task_type == "caption":
                result = await self._generate_caption(task)
            elif task_type == "image":
                result = await self._generate_image(task)
            elif task_type == "hashtags":
                result = await self._generate_hashtags(task)
            elif task_type == "video_script":
                result = await self._generate_video_script(task)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            # Store in memory
            await self.store_memory(f"last_{task_type}", result)
            
            self.set_state(AgentState.IDLE)
            return result
            
        except Exception as e:
            logger.error(f"Content creation error: {e}")
            self.set_state(AgentState.ERROR)
            raise
    
    async def _generate_caption(
        self,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate social media caption"""
        topic = task.get("topic", "")
        platform = task.get("platform", "instagram")
        tone = task.get("tone", "professional")
        
        system_message = (
            f"You are a social media expert creating content for {platform}. "
            f"Write in a {tone} tone. Keep it engaging and authentic."
        )
        
        prompt = (
            f"Create a compelling {platform} caption about: {topic}\n"
            f"Requirements:\n"
            f"- Tone: {tone}\n"
            f"- Include call-to-action\n"
            f"- Optimize for engagement\n"
            f"- Max 2200 characters"
        )
        
        caption = await openai_service.generate_text(
            prompt=prompt,
            system_message=system_message,
            temperature=0.8
        )
        
        return {
            "caption": caption,
            "platform": platform,
            "tone": tone,
            "length": len(caption)
        }
    
    async def _generate_image(
        self,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate image with DALL-E 3"""
        prompt = task.get("prompt", "")
        size = task.get("size", "1024x1024")
        quality = task.get("quality", "standard")
        
        urls = await openai_service.generate_image(
            prompt=prompt,
            size=size,
            quality=quality
        )
        
        return {
            "image_urls": urls,
            "prompt": prompt,
            "size": size,
            "quality": quality
        }
    
    async def _generate_hashtags(
        self,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate relevant hashtags"""
        topic = task.get("topic", "")
        count = task.get("count", 10)
        platform = task.get("platform", "instagram")
        
        prompt = (
            f"Generate {count} highly relevant hashtags for {platform} "
            f"about: {topic}\n"
            f"Requirements:\n"
            f"- Mix of popular and niche hashtags\n"
            f"- Relevant to the topic\n"
            f"- Format: #hashtag (one per line)"
        )
        
        response = await openai_service.generate_text(
            prompt=prompt,
            temperature=0.6
        )
        
        # Parse hashtags
        hashtags = [
            line.strip()
            for line in response.split("\n")
            if line.strip().startswith("#")
        ]
        
        return {
            "hashtags": hashtags[:count],
            "topic": topic,
            "platform": platform
        }
    
    async def _generate_video_script(
        self,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate video script"""
        topic = task.get("topic", "")
        duration = task.get("duration", 30)
        style = task.get("style", "professional")
        
        prompt = (
            f"Create a {duration}-second video script about: {topic}\n"
            f"Style: {style}\n"
            f"Include:\n"
            f"- Hook (first 3 seconds)\n"
            f"- Main content\n"
            f"- Call-to-action\n"
            f"- Visual suggestions"
        )
        
        script = await openai_service.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_tokens=500
        )
        
        return {
            "script": script,
            "duration": duration,
            "style": style,
            "topic": topic
        }


# Global instance
content_creator_agent = ContentCreatorAgent()
