from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class Oim3640Crew():
    """OIM3640 Learning Log Generator Crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def code_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['code_analyzer'],
            verbose=True
        )

    @agent
    def learning_log_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['learning_log_writer'],
            verbose=True
        )

    @task
    def analyze_code_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_code_task'],
        )

    @task
    def write_learning_log_task(self) -> Task:
        return Task(
            config=self.tasks_config['write_learning_log_task'],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
