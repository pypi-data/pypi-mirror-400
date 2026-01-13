from eagle.agents.react_agent.base import ReactPlanningAgent
from eagle.agents.base import BasicWorkingMemoryState
from eagle.utils.message_enrichment_utils import set_now_time_to_string

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
import logging

# Nodes:
def observe_node(state: BasicWorkingMemoryState, config: RunnableConfig, store) -> BasicWorkingMemoryState:
    return {
        "node_from": "observe_node",
        "i_need_a_feedback": False,
        "execution_is_complete": False
    }

def route_after_plan(state: BasicWorkingMemoryState, config: RunnableConfig, store):

    # Get the callback manager for the plan node
    plan_node_callback_manager = config.get("configurable").get("plan_node_callback_manager")

    # Route the state and config to the appropriate callback manager
    plan_node_callback_manager.on_plan_node_end(state, config)

    # call the original route function
    logging.info("Plan is complete, proceeding to execute node.")
    return "execute"

def execute_plan(state: BasicWorkingMemoryState, config: RunnableConfig, store):

    return {
            "node_from": "execute_node",
            "i_need_a_feedback": False,
            "execution_is_complete": True,
            "my_plan_is_complete": False,
            "messages": [AIMessage(content=set_now_time_to_string(state.plan), name=config.get("configurable").get("agent_name"))],
        }

class PlanningAgent(ReactPlanningAgent):

    OBSERVE_NODE = observe_node
    ROUTE_AFTER_PLAN = route_after_plan
    EXECUTE_PLAN = execute_plan
