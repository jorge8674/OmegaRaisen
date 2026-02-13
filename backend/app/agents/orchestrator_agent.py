"""
Orchestrator Agent
Master coordinator for all 14 agents and workflows
"""
from typing import Dict, Any, List
from datetime import datetime
import logging
from app.agents.base_agent import BaseAgent, AgentRole, AgentState
from app.infrastructure.ai.openai_service import openai_service
from app.services.task_router import (
    AgentTask,
    WorkflowExecution,
    WorkflowStep,
    OrchestratorState,
    generate_task_id,
    generate_workflow_id,
    get_next_available_step,
    calculate_system_load,
    route_task_to_agent,
    get_workflow_progress,
    estimate_workflow_completion,
    prioritize_tasks
)

logger = logging.getLogger(__name__)


# Predefined workflows for the agency
WORKFLOWS = {
    "full_content_pipeline": [
        {"agent": "content_creator", "action": "generate_content", "depends_on": [], "parallel_with": []},
        {"agent": "brand_voice", "action": "validate_brand_voice", "depends_on": ["generate_content"], "parallel_with": []},
        {"agent": "scheduling", "action": "schedule_post", "depends_on": ["validate_brand_voice"], "parallel_with": []}
    ],
    "crisis_response": [
        {"agent": "crisis_manager", "action": "assess_crisis", "depends_on": [], "parallel_with": []},
        {"agent": "crisis_manager", "action": "draft_statement", "depends_on": ["assess_crisis"], "parallel_with": []},
        {"agent": "engagement", "action": "respond_comments", "depends_on": ["draft_statement"], "parallel_with": []},
        {"agent": "monitor", "action": "monitor_recovery", "depends_on": ["respond_comments"], "parallel_with": []}
    ],
    "weekly_client_report": [
        {"agent": "analytics", "action": "analyze_weekly_metrics", "depends_on": [], "parallel_with": []},
        {"agent": "growth_hacker", "action": "identify_growth_opportunities", "depends_on": ["analyze_weekly_metrics"], "parallel_with": []},
        {"agent": "report_generator", "action": "generate_report", "depends_on": ["identify_growth_opportunities"], "parallel_with": []}
    ],
    "trend_to_content": [
        {"agent": "trend_hunter", "action": "hunt_trends", "depends_on": [], "parallel_with": []},
        {"agent": "strategy", "action": "create_strategy", "depends_on": ["hunt_trends"], "parallel_with": []},
        {"agent": "content_creator", "action": "generate_content", "depends_on": ["create_strategy"], "parallel_with": []},
        {"agent": "brand_voice", "action": "validate_brand", "depends_on": ["generate_content"], "parallel_with": []},
        {"agent": "scheduling", "action": "schedule", "depends_on": ["validate_brand"], "parallel_with": []}
    ],
    "competitive_analysis": [
        {"agent": "competitive_intel", "action": "analyze_competitors", "depends_on": [], "parallel_with": []},
        {"agent": "analytics", "action": "benchmark_performance", "depends_on": ["analyze_competitors"], "parallel_with": []},
        {"agent": "strategy", "action": "update_strategy", "depends_on": ["benchmark_performance"], "parallel_with": []},
        {"agent": "report_generator", "action": "generate_report", "depends_on": ["update_strategy"], "parallel_with": []}
    ]
}


class OrchestratorAgent(BaseAgent):
    """
    Master orchestrator agent - coordinates all 14 agents
    - Workflow execution
    - Task routing
    - System state monitoring
    - Workflow pause/resume
    """

    def __init__(self, agent_id: str = "orchestrator_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.STRATEGY,
            model="gpt-4",
            tools=[
                "workflow_executor",
                "task_router",
                "system_monitor",
                "load_balancer"
            ]
        )
        # In-memory storage (in production, use database)
        self.workflows_db: Dict[str, WorkflowExecution] = {}
        self.tasks_queue: List[AgentTask] = []
        self.agent_registry = {
            "content_creator": "online",
            "strategy": "online",
            "analytics": "online",
            "engagement": "online",
            "monitor": "online",
            "brand_voice": "online",
            "competitive_intel": "online",
            "trend_hunter": "online",
            "crisis_manager": "online",
            "report_generator": "online",
            "growth_hacker": "online",
            "video_production": "online",
            "scheduling": "online",
            "ab_testing": "online"
        }

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute orchestration task"""
        self.set_state(AgentState.WORKING)

        try:
            task_type = task.get("type")

            if task_type == "execute_workflow":
                result = await self.execute_workflow(
                    task["workflow_name"],
                    task["client_id"],
                    task["params"]
                )
            elif task_type == "route_task":
                result = await self.route_task(
                    task["task_type"],
                    task["payload"]
                )
            elif task_type == "get_system_state":
                result = await self.get_system_state()
            elif task_type == "pause_workflow":
                result = await self.pause_workflow(
                    task["workflow_id"],
                    task["reason"]
                )
            elif task_type == "get_workflow_status":
                result = await self.get_workflow_status(
                    task["workflow_id"]
                )
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            self.set_state(AgentState.IDLE)
            return result.model_dump() if hasattr(result, 'model_dump') else result

        except Exception as e:
            logger.error(f"Orchestrator execution error: {e}")
            self.set_state(AgentState.ERROR)
            raise

    async def execute_workflow(
        self,
        workflow_name: str,
        client_id: str,
        params: dict[str, str | int | List]
    ) -> WorkflowExecution:
        """Execute complete workflow coordinating multiple agents"""
        if workflow_name not in WORKFLOWS:
            raise ValueError(f"Unknown workflow: {workflow_name}")

        workflow_id = generate_workflow_id()
        workflow_template = WORKFLOWS[workflow_name]

        # Create workflow steps
        steps = []
        for i, step_template in enumerate(workflow_template):
            step = WorkflowStep(
                step_id=f"step_{i+1}",
                agent=step_template["agent"],
                action=step_template["action"],
                depends_on=step_template["depends_on"],
                parallel_with=step_template["parallel_with"]
            )
            steps.append(step)

        # Create workflow execution
        workflow = WorkflowExecution(
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            client_id=client_id,
            status="running",
            steps=steps,
            completed_steps=[],
            current_step=steps[0].step_id if steps else None,
            started_at=datetime.now().isoformat(),
            estimated_completion=None,
            results={}
        )

        # Estimate completion time
        workflow.estimated_completion = estimate_workflow_completion(workflow)

        # Store workflow
        self.workflows_db[workflow_id] = workflow

        logger.info(f"Started workflow {workflow_name} ({workflow_id}) for client {client_id}")

        # Execute first step (in production, this would be async task queue)
        first_step = get_next_available_step(workflow)
        if first_step:
            # Simulate step execution
            workflow.completed_steps.append(first_step.step_id)
            workflow.results[first_step.step_id] = {
                "status": "completed",
                "agent": first_step.agent,
                "action": first_step.action
            }

        return workflow

    async def route_task(
        self,
        task_type: str,
        payload: dict[str, str | int | List | Dict]
    ) -> AgentTask:
        """Route task to correct agent automatically"""
        # Determine which agent should handle this
        assigned_agent = route_task_to_agent(task_type)

        # Create task
        task = AgentTask(
            task_id=generate_task_id(),
            workflow_id=None,
            task_type=task_type,
            assigned_agent=assigned_agent,
            priority=payload.get("priority", "normal"),  # type: ignore
            payload=payload,
            status="queued",
            created_at=datetime.now().isoformat(),
            started_at=None,
            completed_at=None,
            result=None,
            error=None
        )

        # Add to queue
        self.tasks_queue.append(task)

        # Prioritize queue
        self.tasks_queue = prioritize_tasks(self.tasks_queue)

        logger.info(f"Routed task {task.task_id} to {assigned_agent}")

        return task

    async def get_system_state(self) -> OrchestratorState:
        """Get complete system state in real-time"""
        active_workflows = len([
            w for w in self.workflows_db.values()
            if w.status == "running"
        ])

        queued_tasks = len([
            t for t in self.tasks_queue
            if t.status == "queued"
        ])

        agents_online = len([
            status for status in self.agent_registry.values()
            if status == "online"
        ])

        system_load = calculate_system_load(active_workflows, queued_tasks)

        return OrchestratorState(
            active_workflows=active_workflows,
            queued_tasks=queued_tasks,
            agents_online=agents_online,
            agents_status=self.agent_registry,
            system_load=system_load,
            last_health_check=datetime.now().isoformat()
        )

    async def pause_workflow(
        self,
        workflow_id: str,
        reason: str
    ) -> WorkflowExecution:
        """Pause workflow (useful for human approval)"""
        if workflow_id not in self.workflows_db:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow = self.workflows_db[workflow_id]
        workflow.status = "paused"

        logger.info(f"Paused workflow {workflow_id}: {reason}")

        return workflow

    async def get_workflow_status(
        self,
        workflow_id: str
    ) -> WorkflowExecution:
        """Get current status of specific workflow"""
        if workflow_id not in self.workflows_db:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow = self.workflows_db[workflow_id]

        # Update progress info
        progress = get_workflow_progress(workflow)

        logger.info(
            f"Workflow {workflow_id}: {workflow.status} "
            f"({progress:.1%} complete)"
        )

        return workflow


# Global instance
orchestrator_agent = OrchestratorAgent()
