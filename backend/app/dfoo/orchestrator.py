import uuid
from datetime import datetime

from app.agents.base import AgentInput
from app.agents.intake_agent import IntakeAgent

from .task_state import (
    Task,
    TaskStatus,
    Investigation,
)

from .task_repository import (
    TaskRepository,
    InvestigationRepository,
)


class DFOO:

    def __init__(self):

        # Temporary in-memory repositories
        self.task_repository = TaskRepository()
        self.investigation_repository = InvestigationRepository()

        # Agent registry
        self.agents = {
            "intake_agent": IntakeAgent(),
        }

    async def start_investigation(
        self,
        product: dict
    ):

        # -----------------------------------
        # 1. Create investigation
        # -----------------------------------

        investigation_id = str(uuid.uuid4())

        investigation = Investigation(
            id=investigation_id,
            input_data=product,
            status=TaskStatus.PENDING,
        )

        self.investigation_repository.create(
            investigation
        )

        print(
            f"[DFOO] Investigation "
            f"{investigation_id} created"
        )

        # -----------------------------------
        # 2. Create initial task
        # -----------------------------------

        task_id = str(uuid.uuid4())

        task = Task(
            id=task_id,
            investigation_id=investigation_id,
            agent_name="intake_agent",
            input_data={
            "product": product
        },
            depends_on=[],
        )

        self.task_repository.create_task(task)

        investigation.task_ids.append(task_id)

        self.investigation_repository.update(
            investigation
        )

        print(
            f"[DFOO] Task {task_id} created: "
            f"intake_agent"
        )

        # -----------------------------------
        # 3. Execute task
        # -----------------------------------

        await self.run_task(task_id)

        # -----------------------------------
        # 4. Update investigation status
        # -----------------------------------

        task = self.task_repository.get_task(task_id)

        if task.status == TaskStatus.DONE:

            investigation.status = TaskStatus.DONE

        else:

            investigation.status = TaskStatus.FAILED

        investigation.updated_at = datetime.utcnow()

        self.investigation_repository.update(
            investigation
        )

        print(
            f"[DFOO] Investigation "
            f"{investigation_id} → "
            f"{investigation.status.value}"
        )

        return investigation

    # =======================================
    # TASK EXECUTION
    # =======================================

    async def run_task(
        self,
        task_id: str
    ):

        task = self.task_repository.get_task(
            task_id
        )

        if task is None:
            raise ValueError(
                f"Task {task_id} not found"
            )

        # -----------------------------------
        # Check dependencies
        # -----------------------------------

        if not self.can_run(task):

            print(
                f"[DFOO] Task {task.id} "
                f"cannot run yet"
            )

            return task

        # -----------------------------------
        # Find agent
        # -----------------------------------

        agent = self.agents.get(
            task.agent_name
        )

        if agent is None:

            task.status = TaskStatus.FAILED
            task.output_data = {
                "error": (
                    f"Agent '{task.agent_name}' "
                    f"not registered"
                )
            }

            self.task_repository.update_task(
                task
            )

            return task

        # -----------------------------------
        # Execute with retry
        # -----------------------------------

        while task.attempts < task.max_attempts:

            task.status = TaskStatus.RUNNING
            task.attempts += 1
            task.updated_at = datetime.utcnow()

            self.task_repository.update_task(
                task
            )

            print(
                f"[DFOO] Task {task.id} "
                f"→ RUNNING "
                f"(attempt {task.attempts})"
            )

            try:

                result = await agent.run(
                    AgentInput(
                        investigation_id=(
                            task.investigation_id
                        ),
                        context=task.input_data,
                    )
                )

                if result.success:

                    task.status = TaskStatus.DONE

                    task.output_data = (
                        result.model_dump()
                    )

                    task.updated_at = (
                        datetime.utcnow()
                    )

                    self.task_repository.update_task(
                        task
                    )

                    print(
                        f"[DFOO] Task {task.id} "
                        f"→ DONE"
                    )

                    return task

                # Agent returned failure
                task.status = TaskStatus.RETRY

                task.output_data = (
                    result.model_dump()
                )

                self.task_repository.update_task(
                    task
                )

                print(
                    f"[DFOO] Task {task.id} "
                    f"→ RETRY"
                )

            except Exception as error:

                task.status = TaskStatus.RETRY

                task.output_data = {
                    "error": str(error)
                }

                self.task_repository.update_task(
                    task
                )

                print(
                    f"[DFOO] Task {task.id} "
                    f"→ RETRY"
                )

        # -----------------------------------
        # Maximum retries reached
        # -----------------------------------

        task.status = TaskStatus.FAILED
        task.updated_at = datetime.utcnow()

        self.task_repository.update_task(
            task
        )

        print(
            f"[DFOO] Task {task.id} "
            f"→ FAILED"
        )

        return task

    # =======================================
    # DEPENDENCY CHECK
    # =======================================

    def can_run(
        self,
        task: Task
    ) -> bool:

        for dependency_id in task.depends_on:

            dependency = (
                self.task_repository.get_task(
                    dependency_id
                )
            )

            if dependency is None:
                return False

            if dependency.status != TaskStatus.DONE:
                return False

        return True