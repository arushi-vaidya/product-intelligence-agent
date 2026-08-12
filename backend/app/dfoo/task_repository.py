from typing import Optional

from .task_state import Task, Investigation


class TaskRepository:

    def __init__(self):
        self.tasks: dict[str, Task] = {}

    def create_task(self, task: Task) -> Task:
        self.tasks[task.id] = task
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def update_task(self, task: Task) -> Task:
        self.tasks[task.id] = task
        return task

    def get_tasks_for_investigation(
        self,
        investigation_id: str
    ) -> list[Task]:

        return [
            task
            for task in self.tasks.values()
            if task.investigation_id == investigation_id
        ]


class InvestigationRepository:

    def __init__(self):
        self.investigations: dict[str, Investigation] = {}

    def create(
        self,
        investigation: Investigation
    ) -> Investigation:

        self.investigations[investigation.id] = investigation
        return investigation

    def get(
        self,
        investigation_id: str
    ) -> Optional[Investigation]:

        return self.investigations.get(investigation_id)

    def update(
        self,
        investigation: Investigation
    ) -> Investigation:

        self.investigations[investigation.id] = investigation
        return investigation

    def list_all(self) -> list[Investigation]:
        return sorted(
            self.investigations.values(),
            key=lambda investigation: investigation.created_at,
            reverse=True,
        )