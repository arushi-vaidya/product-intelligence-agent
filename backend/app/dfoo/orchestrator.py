import uuid
from datetime import datetime

from app.agents.base import AgentInput
from app.agents.intake_agent import IntakeAgent
from app.agents.research_agent import ResearchAgent
from app.agents.akgp_agent import AKGPAgent
from app.agents.source_validation_agent import (
    SourceValidationAgent
)
from app.agents.product_intelligence_agent import (
    ProductIntelligenceAgent
)
from app.agents.document_agent import (
    DocumentAgent
)
from app.agents.canonical_resolution_agent import (
    CanonicalResolutionAgent
)

from .task_state import (
    Task,
    TaskStatus,
    Investigation,
)

from .task_repository import (
    TaskRepository,
    InvestigationRepository,
)
from app.agents.specification_agent import (
    SpecificationAgent
)
from app.agents.conflict_agent import ConflictAgent


class DFOO:

    def __init__(self):

        # Temporary in-memory repositories
        self.task_repository = TaskRepository()
        self.investigation_repository = InvestigationRepository()

        # Agent registry
        self.agents = {
            "intake_agent": IntakeAgent(),
            "research_agent": ResearchAgent(),
            "source_validation_agent": SourceValidationAgent(),
            "document_agent": DocumentAgent(),
            "specification_agent": SpecificationAgent(),
            "conflict_agent": ConflictAgent(),
            "akgp_agent": AKGPAgent(),
            "product_intelligence_agent": ProductIntelligenceAgent(),
            "canonical_resolution_agent": CanonicalResolutionAgent(),
        }

    def create_task(
            self,
            investigation_id: str,
            agent_name: str,
            input_data: dict,
            depends_on: list[str] | None = None,
        ):

            task_id = str(uuid.uuid4())

            task = Task(
                id=task_id,
                investigation_id=investigation_id,
                agent_name=agent_name,
                input_data=input_data,
                depends_on=depends_on or [],
            )

            self.task_repository.create_task(task)

            investigation = (
                self.investigation_repository.get(
                    investigation_id
                )
            )

            if investigation:
                investigation.task_ids.append(task_id)
                investigation.updated_at = datetime.utcnow()

                self.investigation_repository.update(
                    investigation
                )

            print(
                f"[DFOO] Task {task_id} created: "
                f"{agent_name}"
            )

            return task

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
        # 2. Create Intake task
        # -----------------------------------

        intake_task = self.create_task(
            investigation_id=investigation_id,
            agent_name="intake_agent",
            input_data={
                "product": product
            },
        )

        # -----------------------------------
        # 3. Execute Intake task
        # -----------------------------------

        await self.run_task(
            intake_task.id
        )

        # Get updated task after execution
        intake_task = (
            self.task_repository.get_task(
                intake_task.id
            )
        )

        # -----------------------------------
        # 4. Create Research task
        #    ONLY if Intake succeeded
        # -----------------------------------

        if intake_task.status == TaskStatus.DONE:

            intake_output = (
                intake_task.output_data
                .get("data", {})
            )

            research_task = self.create_task(
                investigation_id=investigation_id,
                agent_name="research_agent",
                input_data=intake_output,
                depends_on=[
                    intake_task.id
                ],
            )

            # -----------------------------------
            # 5. Execute Research task
            # -----------------------------------

            await self.run_task(
                research_task.id
            )
            research_task = (
    self.task_repository.get_task(
        research_task.id
    )
)

        if research_task.status == TaskStatus.DONE:

            research_output = (
                research_task.output_data
                .get("data", {})
            )

            validation_input = {
                "manufacturer": product.get(
                    "manufacturer"
                ),
                "mpn": product.get(
                    "mpn"
                ),
                "sources": research_output.get(
                    "sources",
                    []
                ),
            }

            validation_task = self.create_task(
                investigation_id=investigation_id,
                agent_name="source_validation_agent",
                input_data=validation_input,
                depends_on=[
                    research_task.id
                ],
            )

            await self.run_task(
                validation_task.id
            )
            validation_task = (
    self.task_repository.get_task(
        validation_task.id
    )
)

        if validation_task.status != TaskStatus.DONE:

            investigation.status = (
                TaskStatus.FAILED
            )

            self.investigation_repository.update(
                investigation
            )

            return investigation


        # -----------------------------------
        # 5. Document extraction
        # -----------------------------------

        validation_output = (
            validation_task.output_data
            .get("data", {})
        )

        document_input = {
            "manufacturer": product.get(
                "manufacturer"
            ),
            "mpn": product.get(
                "mpn"
            ),
            "validated_sources": (
                validation_output.get(
                    "validated_sources",
                    []
                )
            ),
        }

        document_task = self.create_task(
            investigation_id=investigation_id,
            agent_name="document_agent",
            input_data=document_input,
            depends_on=[
                validation_task.id
            ],
        )

        await self.run_task(
            document_task.id
        )
        document_task = (
    self.task_repository.get_task(
        document_task.id
    )
)

        if document_task.status != TaskStatus.DONE:

            investigation.status = (
                TaskStatus.FAILED
            )

            self.investigation_repository.update(
                investigation
            )

            return investigation


        # -----------------------------------
        # 6. Specification extraction
        # -----------------------------------

        document_output = (
            document_task.output_data
            .get("data", {})
        )

        specification_input = {
            "manufacturer": product.get(
                "manufacturer"
            ),
            "mpn": product.get(
                "mpn"
            ),
            "documents": document_output.get(
                "documents",
                []
            ),
        }

        specification_task = self.create_task(
            investigation_id=investigation_id,
            agent_name="specification_agent",
            input_data=specification_input,
            depends_on=[
                document_task.id
            ],
        )

        await self.run_task(
            specification_task.id
        )
        specification_task = (
    self.task_repository.get_task(
        specification_task.id
    )
)

        if specification_task.status != TaskStatus.DONE:

            investigation.status = TaskStatus.FAILED

            self.investigation_repository.update(
                investigation
            )

            return investigation


        # -----------------------------------
        # 7. Conflict / Quality Analysis
        # -----------------------------------

        specification_output = (
            specification_task.output_data
            .get("data", {})
        )

        conflict_input = {
            "manufacturer": product.get(
                "manufacturer"
            ),
            "mpn": product.get(
                "mpn"
            ),
            "specifications": (
                specification_output.get(
                    "specifications",
                    {}
                )
            ),
        }

        conflict_task = self.create_task(
            investigation_id=investigation_id,
            agent_name="conflict_agent",
            input_data=conflict_input,
            depends_on=[
                specification_task.id
            ],
        )

        await self.run_task(
            conflict_task.id
        )
        conflict_task = (
    self.task_repository.get_task(
        conflict_task.id
    )
)

        if conflict_task.status != TaskStatus.DONE:

            investigation.status = (
                TaskStatus.FAILED
            )

            self.investigation_repository.update(
                investigation
            )

            return investigation


        # -----------------------------------
        # 8. AKGP
        # -----------------------------------

        conflict_output = (
            conflict_task.output_data
            .get("data", {})
        )

        akgp_input = {
            "manufacturer": product.get("manufacturer"),
            "mpn": product.get("mpn"),

            "specifications": (
                conflict_output.get(
                    "specifications",
                    {}
                )
            ),

            "conflicts": (
                conflict_output.get(
                    "conflicts",
                    []
                )
            ),

            "sources": research_output.get(
                "sources",
                []
            ),
        }

        akgp_task = self.create_task(
            investigation_id=investigation_id,
            agent_name="akgp_agent",
            input_data=akgp_input,
            depends_on=[
                conflict_task.id
            ],
        )

        await self.run_task(
            akgp_task.id
        )
        # -----------------------------------
# 9. Canonical Product Resolution
# -----------------------------------

        akgp_task = self.task_repository.get_task(
            akgp_task.id
        )

        if akgp_task.status != TaskStatus.DONE:

            investigation.status = (
                TaskStatus.FAILED
            )

            self.investigation_repository.update(
                investigation
            )

            return investigation


        akgp_output = (
            akgp_task.output_data
            .get("data", {})
        )


        canonical_input = {

            "manufacturer": product.get(
                "manufacturer"
            ),

            "mpn": product.get(
                "mpn"
            ),

            "specifications": (
                conflict_output.get(
                    "specifications",
                    {}
                )
            ),

            "variants": (
                akgp_output.get(
                    "variants",
                    []
                )
            ),

            "conflict_resolutions": (
                akgp_output.get(
                    "conflict_resolutions",
                    []
                )
            ),
        }


        canonical_task = self.create_task(

            investigation_id=investigation_id,

            agent_name=(
                "canonical_resolution_agent"
            ),

            input_data=canonical_input,

            depends_on=[
                akgp_task.id
            ],
        )


        await self.run_task(
            canonical_task.id
        )
        # -----------------------------------
# 9. Product Intelligence
# -----------------------------------

        akgp_task = self.task_repository.get_task(
            akgp_task.id
        )

        if akgp_task.status != TaskStatus.DONE:

            investigation.status = TaskStatus.FAILED

            self.investigation_repository.update(
                investigation
            )

            return investigation


        # Get AKGP output
        akgp_output = (
            akgp_task.output_data
            .get("data", {})
        )


        # -----------------------------------
        # Build Product Intelligence input
        # -----------------------------------

        canonical_task = (
    self.task_repository.get_task(
        canonical_task.id
    )
)

        if canonical_task.status != TaskStatus.DONE:

            investigation.status = (
                TaskStatus.FAILED
            )

            self.investigation_repository.update(
                investigation
            )

            return investigation


        canonical_output = (
            canonical_task.output_data
            .get("data", {})
        )


        product_intelligence_input = {

            "manufacturer": product.get(
                "manufacturer"
            ),

            "mpn": product.get(
                "mpn"
            ),

            "canonical_product": (
                canonical_output.get(
                    "canonical_product",
                    {}
                )
            ),

            "knowledge_graph": (
                akgp_output.get(
                    "knowledge_graph",
                    {}
                )
            ),

            "conflict_resolutions": (
                akgp_output.get(
                    "conflict_resolutions",
                    []
                )
            ),
        }


        # -----------------------------------
        # Create Product Intelligence task
        # -----------------------------------

        product_intelligence_task = self.create_task(
            investigation_id=investigation_id,
            agent_name="product_intelligence_agent",
            input_data=product_intelligence_input,
            depends_on=[
                canonical_task.id
            ],
        )


        # -----------------------------------
        # Execute Product Intelligence
        # -----------------------------------

        await self.run_task(
            product_intelligence_task.id
        )

        # -----------------------------------
        # 6. Determine final investigation status
        # -----------------------------------

        final_task = (
    self.task_repository.get_task(
        product_intelligence_task.id
    )
)

        if final_task.status == TaskStatus.DONE:

            investigation.status = TaskStatus.DONE

        else:

            investigation.status = TaskStatus.FAILED

        investigation.updated_at = datetime.utcnow()

        self.investigation_repository.update(
            investigation
        )

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