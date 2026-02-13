"""
A/B Testing Agent
Specialized in scientific experimentation and statistical analysis
"""
from typing import Dict, Any, List
from datetime import datetime
import logging
from app.agents.base_agent import BaseAgent, AgentRole, AgentState
from app.infrastructure.ai.openai_service import openai_service
from app.services.experiment_engine import (
    Experiment,
    ABVariant,
    ABTestResult,
    generate_experiment_id,
    generate_variant_id,
    calculate_engagement_rate,
    calculate_statistical_significance,
    determine_minimum_sample_size,
    is_result_conclusive,
    identify_winner,
    calculate_lift
)

logger = logging.getLogger(__name__)


class ABTestingAgent(BaseAgent):
    """
    Agent specialized in A/B testing and experimentation
    - Scientific experiment design
    - Variant creation
    - Statistical analysis
    - Insight generation
    - Next test recommendations
    """

    def __init__(self, agent_id: str = "ab_testing_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.ANALYTICS,
            model="gpt-4",
            tools=[
                "experiment_designer",
                "variant_generator",
                "statistical_analyzer",
                "insight_engine"
            ]
        )
        # In-memory storage (in production, use database)
        self.experiments_db: Dict[str, Experiment] = {}

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute A/B testing task"""
        self.set_state(AgentState.WORKING)

        try:
            task_type = task.get("type")

            if task_type == "design_experiment":
                result = await self.design_experiment(
                    task["hypothesis"],
                    task["variable"],
                    task["base_content"],
                    task["platform"]
                )
            elif task_type == "create_variants":
                result = await self.create_variants(
                    task["base_content"],
                    task["variable"],
                    task["client_niche"]
                )
            elif task_type == "analyze_results":
                result = await self.analyze_results(
                    Experiment(**task["experiment"])
                )
            elif task_type == "generate_insights":
                result = await self.generate_insights(
                    [ABTestResult(**r) for r in task["results"]],
                    task["client_id"]
                )
            elif task_type == "recommend_next":
                result = await self.recommend_next_test(
                    [Experiment(**e) for e in task["completed_experiments"]],
                    task["client_goals"]
                )
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            self.set_state(AgentState.IDLE)
            return result.model_dump() if hasattr(result, 'model_dump') else result

        except Exception as e:
            logger.error(f"A/B testing execution error: {e}")
            self.set_state(AgentState.ERROR)
            raise

    async def design_experiment(
        self,
        hypothesis: str,
        variable: str,
        base_content: dict[str, str],
        platform: str
    ) -> Experiment:
        """Design scientific experiment with clear variants"""
        experiment_id = generate_experiment_id()

        prompt = (
            f"Design an A/B test experiment:\n\n"
            f"Hypothesis: {hypothesis}\n"
            f"Variable to test: {variable}\n"
            f"Platform: {platform}\n"
            f"Base content: {base_content}\n\n"
            f"Provide:\n"
            f"1. Clear hypothesis statement\n"
            f"2. Success metrics\n"
            f"3. Expected effect size"
        )

        experiment_plan = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=300,
            temperature=0.6
        )

        # Calculate minimum sample size
        effect_size = 0.1  # Expecting 10% improvement
        confidence = 0.95
        min_sample = determine_minimum_sample_size(effect_size, confidence)

        # Create initial variants (will be populated by create_variants)
        experiment = Experiment(
            experiment_id=experiment_id,
            client_id="default_client",
            hypothesis=hypothesis,
            variable_tested=variable,
            variants=[],
            status="draft",
            started_at=datetime.now().isoformat(),
            completed_at=None,
            target_sample_size=min_sample,
            platform=platform
        )

        self.experiments_db[experiment_id] = experiment
        logger.info(f"Designed experiment {experiment_id}")

        return experiment

    async def create_variants(
        self,
        base_content: dict[str, str],
        variable: str,
        client_niche: str
    ) -> List[ABVariant]:
        """Create A and B variants for testing"""
        prompt = (
            f"Create 2 variations for A/B testing:\n\n"
            f"Variable to test: {variable}\n"
            f"Niche: {client_niche}\n"
            f"Base content: {base_content}\n\n"
            f"Create:\n"
            f"Variant A (Control): {base_content.get('caption', 'Original version')}\n"
            f"Variant B (Test): Improved version focusing on {variable}\n\n"
            f"Make the change significant but focused on ONE variable only."
        )

        variants_text = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=400,
            temperature=0.7
        )

        # Create variant objects
        variant_a = ABVariant(
            variant_id=generate_variant_id(),
            variant_name="A",
            description="Control variant (original)",
            content=base_content,
            impressions=0,
            engagements=0,
            clicks=0,
            conversions=0,
            engagement_rate=0.0
        )

        # Create modified content for variant B
        modified_content = base_content.copy()
        if variable == "caption":
            # Extract variant B caption from AI response (simplified)
            modified_content["caption"] = variants_text[:200]
        elif variable == "hashtags":
            modified_content["hashtags"] = ["#trending", "#viral", "#growth"]

        variant_b = ABVariant(
            variant_id=generate_variant_id(),
            variant_name="B",
            description=f"Test variant (modified {variable})",
            content=modified_content,
            impressions=0,
            engagements=0,
            clicks=0,
            conversions=0,
            engagement_rate=0.0
        )

        return [variant_a, variant_b]

    async def analyze_results(
        self,
        experiment: Experiment
    ) -> ABTestResult:
        """Analyze experiment results with statistical significance"""
        if len(experiment.variants) < 2:
            raise ValueError("Need at least 2 variants to analyze")

        # Calculate engagement rates for all variants
        for variant in experiment.variants:
            variant.engagement_rate = calculate_engagement_rate(
                variant.engagements,
                variant.impressions
            )

        # Compare variants (assuming first is control)
        control = experiment.variants[0]
        test = experiment.variants[1]

        # Calculate statistical significance
        significance = calculate_statistical_significance(control, test)

        # Determine winner
        winner = identify_winner(experiment.variants)

        # Check if conclusive
        avg_sample_size = sum(v.impressions for v in experiment.variants) // len(experiment.variants)
        conclusive = is_result_conclusive(
            significance,
            avg_sample_size,
            experiment.target_sample_size
        )

        # Calculate lift
        lift = calculate_lift(control.engagement_rate, test.engagement_rate)

        # Generate AI insights
        prompt = (
            f"Analyze these A/B test results:\n\n"
            f"Variable tested: {experiment.variable_tested}\n"
            f"Control (A): {control.engagement_rate:.2%} engagement rate\n"
            f"Test (B): {test.engagement_rate:.2%} engagement rate\n"
            f"Lift: {lift:.1f}%\n"
            f"Statistical significance: p={significance:.3f}\n"
            f"Sample size: {avg_sample_size}\n\n"
            f"Provide 3 key insights about these results."
        )

        insights_text = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=250,
            temperature=0.6
        )

        insights = [
            line.strip()
            for line in insights_text.split('\n')
            if line.strip() and len(line.strip()) > 15
        ][:3]

        # Generate recommendation
        if conclusive and winner:
            recommendation = f"Implement Variant {winner} - statistically significant improvement of {lift:.1f}%"
        elif not conclusive:
            recommendation = f"Continue test - need {experiment.target_sample_size - avg_sample_size} more samples"
        else:
            recommendation = "No significant difference - keep current approach"

        result = ABTestResult(
            test_id=experiment.experiment_id,
            winner_variant=winner,
            statistical_significance=significance,
            confidence_level=0.95,
            is_conclusive=conclusive,
            sample_size_per_variant=avg_sample_size,
            minimum_sample_needed=experiment.target_sample_size,
            recommendation=recommendation,
            insights=insights
        )

        logger.info(f"Analyzed experiment {experiment.experiment_id}: winner={winner}")
        return result

    async def generate_insights(
        self,
        results: List[ABTestResult],
        client_id: str
    ) -> List[str]:
        """Generate cumulative insights from multiple experiments"""
        prompt = (
            f"Analyze these A/B test results for client {client_id}:\n\n"
        )

        for i, result in enumerate(results[:5], 1):
            prompt += (
                f"{i}. Test {result.test_id}\n"
                f"   Winner: {result.winner_variant or 'None'}\n"
                f"   Conclusive: {result.is_conclusive}\n"
                f"   Insights: {', '.join(result.insights[:2])}\n\n"
            )

        prompt += (
            "Based on ALL these tests, provide 5 strategic insights:\n"
            "1. Patterns across tests\n"
            "2. What's working consistently\n"
            "3. What to avoid\n"
            "4. Audience preferences\n"
            "5. Next optimization opportunity"
        )

        insights_text = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=400,
            temperature=0.6
        )

        insights = [
            line.strip()[3:].strip() if line.strip()[0].isdigit() else line.strip()
            for line in insights_text.split('\n')
            if line.strip() and len(line.strip()) > 20
        ][:5]

        return insights

    async def recommend_next_test(
        self,
        completed_experiments: List[Experiment],
        client_goals: List[str]
    ) -> dict[str, str]:
        """Recommend next experiment based on history"""
        tested_variables = [exp.variable_tested for exp in completed_experiments]

        prompt = (
            f"Based on completed A/B tests, recommend the next experiment:\n\n"
            f"Already tested: {', '.join(tested_variables)}\n"
            f"Client goals: {', '.join(client_goals)}\n\n"
            f"Recommend:\n"
            f"1. Variable to test next\n"
            f"2. Hypothesis\n"
            f"3. Why this test matters\n"
            f"4. Expected impact"
        )

        recommendation_text = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=300,
            temperature=0.7
        )

        # Parse recommendation (simplified)
        untested_variables = ["cta", "hook", "image", "posting_time", "hashtags", "caption"]
        next_variable = next(
            (v for v in untested_variables if v not in tested_variables),
            "cta"
        )

        return {
            "recommended_variable": next_variable,
            "hypothesis": f"Testing {next_variable} will improve engagement",
            "reasoning": recommendation_text[:200],
            "expected_impact": "Moderate to high"
        }


# Global instance
ab_testing_agent = ABTestingAgent()
