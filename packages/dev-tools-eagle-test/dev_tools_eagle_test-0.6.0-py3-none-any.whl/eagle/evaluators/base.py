from eagle.agents.react_agent.base import ReactPlanningAgent, ReactPlanningAgentConfigSchema
from eagle.agents.base import BasicWorkingMemoryState
import pandas as pd
from pydantic import BaseModel

class AgentEvaluationResultSchema(BaseModel):
    description: str
    score: float

class AgentEvaluationScenario:

    SCENARIOS_DATA_COLUMNS: list = ["states", "configs", "evaluation_criteria"]

    def __init__(self, scenarios_data: pd.DataFrame = pd.DataFrame({"states": [], "configs": [], "evaluation_criteria": []})):
        
        self.scenarios_data = scenarios_data
        self.check_scenarios_data()

    def check_scenarios_data(self):
        for column in self.SCENARIOS_DATA_COLUMNS:
            assert column in self.scenarios_data.columns, f"Column '{column}' not present in scenarios_data."

    def add_scenario(self, state: BasicWorkingMemoryState, config: dict, evaluation_criteria: str):
        config = ReactPlanningAgentConfigSchema(**config).model_dump()
        self.scenarios_data.loc[len(self.scenarios_data)] = {
            "states": state,
            "configs": config,
            "evaluation_criteria": evaluation_criteria
        }
        
class AgentEvaluationBase:

    def __init__(self, agent: ReactPlanningAgent, scenario: AgentEvaluationScenario):
        self.agent = agent
        self.scenario = scenario

    def evaluate_case(self, state: BasicWorkingMemoryState, config: dict, evaluation_criteria: str) -> AgentEvaluationResultSchema:
        """
        Deve ser implementado nas subclasses.
        Deve retornar AgentEvaluationResultSchema.
        """
        raise NotImplementedError("This method must be implemented.")
    
    def get_results_new_columns(self):
        # Subclasses should override this to specify which columns to collect from the result
        return ["description", "score"]

    def evaluate(self):
        results = {col: [] for col in self.get_results_new_columns()}
        for idx, row in self.scenario.scenarios_data.iterrows():
            result = self.evaluate_case(
                state=row["states"],
                config=row["configs"],
                evaluation_criteria=row["evaluation_criteria"]
            )
            result_dict = result.model_dump()
            for col in self.get_results_new_columns():
                results[col].append(result_dict.get(col))
        results_df = self.scenario.scenarios_data.copy()
        for col in self.get_results_new_columns():
            results_df[col] = results[col]
        return results_df

