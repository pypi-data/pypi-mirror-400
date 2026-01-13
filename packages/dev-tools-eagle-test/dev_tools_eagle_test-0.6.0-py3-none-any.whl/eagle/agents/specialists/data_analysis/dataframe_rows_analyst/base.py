from eagle.agents.react_agent.base import (
    ReactPlanningAgent,
    ReactPlanningAgentConfigSchema,
    get_vision_context,
    node_path_count,
    create_react_agent,
    process_graph_stream,
    ReactAgentState
)
from eagle.memory.shared.shared_objects_memory import SharedObjectsMemory
from eagle.agents.base import BasicWorkingMemoryState
from eagle.agents.specialists.data_analysis.dataframe_rows_analyst.prompts import prompt_generator
from eagle.utils.message_enrichment_utils import set_now_time_to_string
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from pydantic import Field, BaseModel
from typing import List
from langchain.prompts import ChatPromptTemplate

# Config Schema

class NewColumnProposal(BaseModel):
    column_name: str = Field(name="column_name", description="The name of the new column to be added to the dataframe.")
    column_description: str = Field(name="column_description", description="A brief description of the new column.")
    column_type: str = Field(name="column_type", description="The data type of the new column (e.g., integer, float, string).")

class DataFrameRowsAnalystAgentConfigSchema(ReactPlanningAgentConfigSchema):
    dataframe_shared_object_id: str = Field(name="dataframe_shared_object_id", description="The ID of the shared dataframe object to analyze.")
    dataframe_shared_object_list_of_idx_to_analyse: List[int] = Field(name="dataframe_shared_object_list_of_idx_to_analyse", description="The list of row indices to analyze in the dataframe.")
    new_columns_proposals: List[NewColumnProposal] = Field(name="new_columns_proposals", description="A list of proposals for new columns to be added to the dataframe.")

# Auxiliar functions
def generate_dataframe_rows_observation(config, store) -> str:
    observe_node_prompt_language = config.get("configurable").get("observe_node_llm_prompt_language")

    prompt_data = prompt_generator.generate_prompt(
        prompt_name="observe",
        language=observe_node_prompt_language,
        llm=None,
        use_structured_output=False
    )

    prompt = prompt_data["prompt"]

    chat_id = config.get("configurable").get("chat_id")
    object_id = config.get("configurable").get("dataframe_shared_object_id")

    shared_memory: SharedObjectsMemory = store.get_memory("shared_objects")

    memory_object = shared_memory.get_memory_object(
        chat_id=chat_id,
        object_id=object_id
    )

    if memory_object is None:
        return None
    
    df = memory_object.object
    dataframe_shared_object_list_of_idx_to_analyse = config.get("configurable").get("dataframe_shared_object_list_of_idx_to_analyse", [])

    df_for_observation = df.iloc[dataframe_shared_object_list_of_idx_to_analyse]

    observation = prompt.format(dataframe_representation=df_for_observation.to_string())

    return observation

# Nodes:
def observe_node(state: BasicWorkingMemoryState, config: RunnableConfig, store) -> BasicWorkingMemoryState:
    state = node_path_count(state, state.node_from, "observe_node")
    node_callback_manager = config.get("configurable").get("observe_node_callback_manager")
    node_callback_manager.on_observe_node_start(state, config)
    
    observation = generate_dataframe_rows_observation(config, store)

    if observation is None:
        return {
            "node_from": "observe_node",
            "i_need_a_feedback": False,
            "execution_is_complete": True,
            "messages": [AIMessage(content=set_now_time_to_string("Shared memory object not found."), name=config.get("configurable").get("agent_name"))],
        }

    return {
        "node_from": "observe_node",
        "i_need_a_feedback": False,
        "execution_is_complete": False,
        "observation": observation
    }

def plan_node(state: BasicWorkingMemoryState, config: RunnableConfig, store) -> BasicWorkingMemoryState:
    """Bypassing plan"""
    state = node_path_count(state, state.node_from, "plan_node")
    return {
        "node_from": "plan_node",
        "i_need_a_feedback": False,
        "execution_is_complete": False,
        "my_plan_is_complete": True,
        "observation": state.observation,
        "plan": "",
    }

def _generate_execute_node(prompt_name):
    def _execute_node(state: BasicWorkingMemoryState, config: RunnableConfig, store):
        
        state = node_path_count(state, state.node_from, "execute_node")
        node_callback_manager = config.get("configurable").get("execute_node_callback_manager")
        node_callback_manager.on_execute_node_start(state, config)
        execute_node_llm = config.get("configurable").get("execute_node_llm")
        execute_node_prompt_language = config.get("configurable").get("execute_node_llm_prompt_language")
        execute_node_has_vision = config.get("configurable").get("execute_node_has_vision", False)
        execute_node_llm_use_structured_output = config.get("configurable").get("execute_node_llm_use_structured_output", False)
        prompt_data = prompt_generator.generate_prompt(
            prompt_name=prompt_name,
            language=execute_node_prompt_language,
            llm=execute_node_llm,
            use_structured_output=execute_node_llm_use_structured_output
        )
        
        prompt = prompt_data["prompt"]
        output_parser = prompt_data["output_parser"]

        chat_id = config.get("configurable").get("chat_id")

        tools = config.get("configurable").get("executing_tools", [])

        important_guidelines = config.get("configurable").get("execute_important_guidelines")

        shared_memory_configs = config.get("configurable").get("execute_shared_objects_config")
        shared_memory: SharedObjectsMemory = store.get_memory("shared_objects")

        window_size = min(config.get("configurable").get("chat_history_window_size"), len(state.messages))
        
        new_columns_proposals = config.get("configurable").get("new_columns_proposals", [])

        message = None
        inputs = {
            "messages": state.messages[-window_size:],
            "observation": state.observation,
            "plan": state.plan,
            "tools_interactions": {}
        }
        while not isinstance(message, AIMessage):
            # Fetch object summary
            objects_summary = ""

            if shared_memory:
                last_memories_metadata = shared_memory.get_last_memories_metadata(chat_id=chat_id, k=shared_memory_configs['k'])
                object_ids = [metadata.object_id for metadata in last_memories_metadata]
                objects_summary = shared_memory.generate_summary_from_object_ids(
                    chat_id=chat_id, object_ids=object_ids, language=shared_memory_configs['language']
                )
                vision_context = None
                if execute_node_has_vision and objects_summary:
                    vision_context = get_vision_context(
                        node_prompt_language=execute_node_prompt_language,
                        node_llm=execute_node_llm,
                        node_prompt_use_structured_output=execute_node_llm_use_structured_output,
                        shared_memory=shared_memory,
                        config=config,
                        messages=state.messages[-window_size:],
                        plan=state.plan,
                        observation=state.observation,
                        objects_summary=objects_summary,
                        important_guidelines=important_guidelines
                    )
            else:
                vision_context = None
            
            prompt_partial = prompt.partial(
                agent_name=config.get("configurable").get("agent_name"),
                agent_description=config.get("configurable").get("agent_description"),
                messages=state.messages[-window_size:],
                new_columns_proposals=new_columns_proposals,
                observation=state.observation,
                plan=state.plan,
                objects_summary=objects_summary,
                important_guidelines=important_guidelines,
                tools_interactions=inputs.get("tools_interactions", {})
            )

            rendered_messages = prompt_partial.format_messages()

            if vision_context:
                rendered_messages.append(vision_context)

            graph = create_react_agent(
                model=execute_node_llm,
                prompt=ChatPromptTemplate.from_messages(rendered_messages),
                tools=tools,
                state_schema=ReactAgentState
            )
            inputs, message = process_graph_stream(graph, inputs, config)

        if message.type == "ai":
            response = output_parser.parse(message)
        else:
            raise ValueError(f"Expected AI message but got: {message.__class__}")
        
        return {
            "node_from": "execute_node",
            "i_need_a_feedback": False,
            "execution_is_complete": True,
            "my_plan_is_complete": False,
            "messages": [AIMessage(content=response.json(), name=config.get("configurable").get("agent_name"))],
        }
    
    return _execute_node

# Agent

class DataFrameRowsAnalystAgent(ReactPlanningAgent):

    CONFIG_SCHEMA = DataFrameRowsAnalystAgentConfigSchema
    OBSERVE_NODE = observe_node
    PLAN_NODE = plan_node
    EXECUTE_NODE = _generate_execute_node("execute_analysis")

class DataFrameRowsReaderAgent(ReactPlanningAgent):
    CONFIG_SCHEMA = DataFrameRowsAnalystAgentConfigSchema
    OBSERVE_NODE = observe_node
    PLAN_NODE = plan_node
    EXECUTE_NODE = _generate_execute_node("execute_reading")
