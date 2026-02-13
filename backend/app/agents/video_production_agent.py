"""
Video Production Agent
Specialized in video script writing and production planning
"""
from typing import Dict, Any, List
from datetime import datetime
import logging
from app.agents.base_agent import BaseAgent, AgentRole, AgentState
from app.infrastructure.ai.openai_service import openai_service
from app.infrastructure.ai.claude_service import claude_service
from app.services.video_pipeline import (
    VideoSpec,
    VideoScript,
    VideoScene,
    VideoProductionPlan,
    calculate_scene_count,
    validate_duration_for_platform,
    estimate_word_count
)

logger = logging.getLogger(__name__)


class VideoProductionAgent(BaseAgent):
    """
    Agent specialized in video production
    - Video script writing with powerful hooks
    - Production planning with shot lists
    - Hook optimization for first 3 seconds
    - Platform adaptation
    - Video idea generation
    """

    def __init__(self, agent_id: str = "video_production_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.CONTENT_CREATOR,
            model="gpt-4",
            tools=[
                "script_writer",
                "hook_optimizer",
                "shot_planner",
                "platform_adapter"
            ]
        )

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute video production task"""
        self.set_state(AgentState.WORKING)

        try:
            task_type = task.get("type")

            if task_type == "write_script":
                result = await self.write_video_script(
                    VideoSpec(**task["spec"]),
                    task["brand_voice"],
                    task["key_message"]
                )
            elif task_type == "production_plan":
                result = await self.create_production_plan(
                    VideoSpec(**task["spec"]),
                    VideoScript(**task["script"])
                )
            elif task_type == "optimize_hook":
                result = await self.optimize_hook(
                    task["platform"],
                    task["niche"],
                    task["content_topic"]
                )
            elif task_type == "adapt_script":
                result = await self.adapt_script_for_platform(
                    VideoScript(**task["script"]),
                    task["target_platform"]
                )
            elif task_type == "generate_ideas":
                result = await self.generate_video_ideas(
                    task["niche"],
                    task["platform"],
                    task["content_pillars"]
                )
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            self.set_state(AgentState.IDLE)
            return result.model_dump() if hasattr(result, 'model_dump') else result

        except Exception as e:
            logger.error(f"Video production execution error: {e}")
            self.set_state(AgentState.ERROR)
            raise

    async def write_video_script(
        self,
        spec: VideoSpec,
        brand_voice: str,
        key_message: str
    ) -> VideoScript:
        """Write complete video script with powerful hook"""
        # First, generate hook using Claude for creativity
        hook_prompt = (
            f"Create a powerful 3-second video hook for:\n"
            f"Platform: {spec.platform}\n"
            f"Topic: {spec.title}\n"
            f"Audience: {spec.target_audience}\n"
            f"Style: {spec.style}\n\n"
            f"The hook must grab attention INSTANTLY. Return ONLY the hook text (15-20 words max)."
        )

        hook = await claude_service.generate_text(
            prompt=hook_prompt,
            max_tokens=50,
            temperature=0.9
        )

        # Generate full script using GPT-4
        scene_count = calculate_scene_count(spec.duration_seconds)
        word_count = estimate_word_count(spec.duration_seconds)

        script_prompt = (
            f"Write a {spec.duration_seconds}-second video script for {spec.platform}.\n\n"
            f"Title: {spec.title}\n"
            f"Hook (already created): {hook.strip()}\n"
            f"Brand voice: {brand_voice}\n"
            f"Key message: {key_message}\n"
            f"Style: {spec.style} ({spec.visual_style})\n"
            f"Target: {spec.target_audience}\n\n"
            f"Create {scene_count} scenes with narration and visual descriptions.\n"
            f"End with a clear call-to-action.\n"
            f"Total words: ~{word_count}\n\n"
            f"Format each scene as:\n"
            f"SCENE X (Xs): [narration] | Visual: [description] | Overlay: [text or 'none'] | Transition: [cut/fade/slide]"
        )

        script_content = await openai_service.generate_text(
            prompt=script_prompt,
            max_tokens=800,
            temperature=0.7
        )

        # Parse scenes (simplified parsing)
        scenes = []
        lines = script_content.split('\n')
        scene_num = 1

        for line in lines:
            if 'SCENE' in line.upper():
                # Extract scene details (simplified)
                scenes.append(VideoScene(
                    scene_number=scene_num,
                    duration_seconds=spec.duration_seconds // scene_count,
                    narration=line[:100],
                    visual_description=f"Visual for scene {scene_num}",
                    text_overlay=None,
                    transition="fade" if scene_num < scene_count else "cut"
                ))
                scene_num += 1

        # Fallback if parsing fails
        if not scenes:
            scenes = [
                VideoScene(
                    scene_number=1,
                    duration_seconds=spec.duration_seconds,
                    narration=key_message,
                    visual_description=f"{spec.visual_style} visuals",
                    text_overlay=spec.title,
                    transition="fade"
                )
            ]

        # Generate CTA using Claude
        cta_prompt = f"Create a compelling call-to-action for a {spec.platform} video about: {spec.title}"
        cta = await claude_service.generate_text(
            prompt=cta_prompt,
            max_tokens=30,
            temperature=0.8
        )

        return VideoScript(
            hook=hook.strip(),
            scenes=scenes,
            call_to_action=cta.strip(),
            total_duration_seconds=spec.duration_seconds,
            word_count=word_count
        )

    async def create_production_plan(
        self,
        spec: VideoSpec,
        script: VideoScript
    ) -> VideoProductionPlan:
        """Create detailed production plan with shot list"""
        prompt = (
            f"Create a production plan for this video:\n\n"
            f"Title: {spec.title}\n"
            f"Duration: {spec.duration_seconds}s\n"
            f"Platform: {spec.platform}\n"
            f"Scenes: {len(script.scenes)}\n\n"
            f"Provide:\n"
            f"1. Shot list (5-7 specific shots needed)\n"
            f"2. Text overlays (3-5 key text elements)\n"
            f"3. Audio suggestions (music style, sound effects)\n"
            f"4. Production tips (3-5 practical tips)"
        )

        plan_content = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=600,
            temperature=0.6
        )

        # Parse production elements (simplified)
        shot_list = [
            f"Shot {i+1}: {spec.visual_style} angle"
            for i in range(min(6, len(script.scenes)))
        ]

        text_overlays = [
            {"text": script.hook, "timing": "0-3s"},
            {"text": script.call_to_action, "timing": f"{spec.duration_seconds-5}-{spec.duration_seconds}s"}
        ]

        audio_suggestions = [
            f"{spec.style} background music",
            "Upbeat tempo matching platform style",
            "Sound effects for transitions"
        ]

        production_tips = [
            f"Optimize for {spec.aspect_ratio} aspect ratio",
            "Shoot in good lighting for clarity",
            "Keep text large and readable on mobile"
        ]

        # Estimate production time (simplified)
        estimated_hours = (len(script.scenes) * 0.5) + 2.0  # 30min per scene + 2h editing

        return VideoProductionPlan(
            spec=spec,
            script=script,
            shot_list=shot_list,
            text_overlays=text_overlays,
            audio_suggestions=audio_suggestions,
            estimated_production_hours=estimated_hours,
            production_tips=production_tips
        )

    async def optimize_hook(
        self,
        platform: str,
        niche: str,
        content_topic: str
    ) -> dict[str, List[str]]:
        """Generate 3 hook options for first 3 seconds"""
        prompt = (
            f"Create 3 different attention-grabbing hooks for a {platform} video.\n\n"
            f"Niche: {niche}\n"
            f"Topic: {content_topic}\n\n"
            f"Each hook must:\n"
            f"- Be 15-20 words max\n"
            f"- Create curiosity or urgency\n"
            f"- Work in first 3 seconds\n\n"
            f"Return as:\n"
            f"1. [hook]\n"
            f"2. [hook]\n"
            f"3. [hook]"
        )

        hooks_text = await claude_service.generate_text(
            prompt=prompt,
            max_tokens=150,
            temperature=0.9
        )

        hooks = [
            line.strip()[3:].strip()
            for line in hooks_text.split('\n')
            if line.strip() and line[0].isdigit()
        ][:3]

        return {"hooks": hooks, "platform": platform, "niche": niche}

    async def adapt_script_for_platform(
        self,
        script: VideoScript,
        target_platform: str
    ) -> VideoScript:
        """Adapt existing script for another platform"""
        if not validate_duration_for_platform(target_platform, script.total_duration_seconds):
            # Adjust duration to platform limits
            script.total_duration_seconds = 60 if "shorts" in target_platform else 90

        prompt = (
            f"Adapt this video script for {target_platform}:\n\n"
            f"Original hook: {script.hook}\n"
            f"Original CTA: {script.call_to_action}\n"
            f"Duration: {script.total_duration_seconds}s\n\n"
            f"Maintain core message but optimize for {target_platform} audience."
        )

        adapted_content = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=400,
            temperature=0.7
        )

        # Keep scenes but update narration slightly
        adapted_scenes = [
            VideoScene(
                scene_number=scene.scene_number,
                duration_seconds=scene.duration_seconds,
                narration=scene.narration,
                visual_description=scene.visual_description,
                text_overlay=scene.text_overlay,
                transition=scene.transition
            )
            for scene in script.scenes
        ]

        return VideoScript(
            hook=script.hook,
            scenes=adapted_scenes,
            call_to_action=script.call_to_action,
            total_duration_seconds=script.total_duration_seconds,
            word_count=script.word_count
        )

    async def generate_video_ideas(
        self,
        niche: str,
        platform: str,
        content_pillars: List[str]
    ) -> List[dict[str, str]]:
        """Generate 5 video ideas with title, hook and concept"""
        prompt = (
            f"Generate 5 viral video ideas for {platform}.\n\n"
            f"Niche: {niche}\n"
            f"Content pillars: {', '.join(content_pillars)}\n\n"
            f"For each idea provide:\n"
            f"- Title (engaging, 5-10 words)\n"
            f"- Hook (first 3 seconds)\n"
            f"- Concept (brief description)\n\n"
            f"Format as:\n"
            f"1. TITLE | HOOK | CONCEPT"
        )

        ideas_text = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=500,
            temperature=0.8
        )

        ideas = []
        for line in ideas_text.split('\n'):
            if line.strip() and '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    title = parts[0].split('.', 1)[-1].strip()
                    ideas.append({
                        "title": title,
                        "hook": parts[1],
                        "concept": parts[2]
                    })

        return ideas[:5]


# Global instance
video_production_agent = VideoProductionAgent()
