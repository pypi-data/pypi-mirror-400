from eagle.agents.react_agent.base import ReactPlanningAgent, ReactAgentState, process_graph_stream
from eagle.memory.shared.shared_objects_memory import SharedObjectsMemory
# Importamos os estados do supervisor SIMPLES como base
from eagle.chat_schemas.relay_schemas.agents.moderator_simple_agent.supervisor import (
    get_vision_context,
    node_path_count,
    RelayModeratorReactAgentState,
    RelayModeratorSimpleAgentWorkingMemoryState
)
# Importamos os novos prompts de PLANNING
from eagle.chat_schemas.relay_schemas.agents.moderator_planning_agent.prompts import prompt_generator
from eagle.utils.message_enrichment_utils import set_now_time_to_string
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime, timezone
from pydantic import Field
from typing import List

# --- 1. ESTADO ---
# O estado do Planning Agent herda do Simple Agent (que já tem 'ordem')
# A classe base ReactPlanningAgent já adiciona 'plan', 'observation', etc.
class RelayModeratorPlanningAgentWorkingMemoryState(RelayModeratorSimpleAgentWorkingMemoryState):
    """Working memory state for the Relay Moderator Planning Agent."""
    pass

# --- 2. NÓ DE OBSERVAÇÃO ---
def observe_node(state: RelayModeratorPlanningAgentWorkingMemoryState, config: RunnableConfig, store) -> dict:
    """
    Processa a fase de observação (triagem).
    Decide se vai para o PLANEJAMENTO ou se responde diretamente.
    """
    state = node_path_count(state, state.node_from, "observe_node")
    node_callback_manager = config.get("configurable").get("observe_node_callback_manager")
    node_callback_manager.on_observe_node_start(state, config)
    observe_node_llm = config.get("configurable").get("observe_node_llm")
    observe_node_prompt_language = config.get("configurable").get("observe_node_llm_prompt_language")
    observe_node_has_vision = config.get("configurable").get("observe_node_has_vision", False)
    observe_node_llm_use_structured_output = config.get("configurable").get("observe_node_llm_use_structured_output", False)
    
    # Chama o prompt 'observe_relay'
    prompt_data = prompt_generator.generate_prompt(
        prompt_name="observe_relay",
        language=observe_node_prompt_language,
        use_structured_output=observe_node_llm_use_structured_output,
        llm=observe_node_llm if observe_node_llm else None
    )
    prompt = prompt_data["prompt"]
    output_parser = prompt_data["output_parser"]
    
    chat_id = config.get("configurable").get("chat_id")
    shared_memory_configs = config.get("configurable").get("execute_shared_objects_config")
    shared_memory: SharedObjectsMemory = store.get_memory("shared_objects")
    tools = config.get("configurable").get("executing_tools", [])
    important_guidelines = config.get("configurable").get("observe_important_guidelines")
    window_size = min(config.get("configurable").get("chat_history_window_size"), len(state.messages_with_requester))
    window_size_2 = min(config.get("configurable").get("chat_history_window_size"), len(state.messages_with_agents))

    message = None
    inputs = {
        "messages": [state.messages_with_requester[-1]] if state.messages_with_requester else [],
        "messages_with_requester": state.messages_with_requester[-window_size:],
        "messages_with_agents": state.messages_with_agents[-window_size_2:],
        "participants": state.participants,
        "plan": state.plan,
        "observation": state.observation,
        "tools_interactions": {}
    }
    while not isinstance(message, AIMessage):
        objects_summary = ""
        must_cite_objects_summary = ""
        vision_context = None

        if shared_memory:
            last_memories_metadata = shared_memory.get_last_memories_metadata(chat_id=chat_id, k=shared_memory_configs['k'])
            object_ids = [metadata.object_id for metadata in last_memories_metadata]
            must_cite_object_ids = []
            if state.interaction_initial_datetime:
                for metadata in last_memories_metadata:
                    if datetime.fromtimestamp(metadata.created_at / 1000).astimezone(timezone.utc) >= state.interaction_initial_datetime:
                        must_cite_object_ids.append(metadata.object_id)
            objects_summary = shared_memory.generate_summary_from_object_ids(
                chat_id=chat_id, object_ids=list(set(object_ids)-set(must_cite_object_ids)), language=shared_memory_configs['language']
            )
            must_cite_objects_summary = shared_memory.generate_summary_from_object_ids(
                chat_id=chat_id, object_ids=must_cite_object_ids, language=shared_memory_configs['language']
            )
            vision_context = None
            if observe_node_has_vision and objects_summary:
                vision_context = get_vision_context(
                    node_prompt_language=observe_node_prompt_language,
                    node_llm=observe_node_llm,
                    node_prompt_use_structured_output=observe_node_llm_use_structured_output,
                    shared_memory=shared_memory,
                    config=config,
                    messages_with_requester=state.messages_with_requester[-window_size:],
                    messages_with_agents=state.messages_with_agents[-window_size_2:],
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
             messages_with_requester=state.messages_with_requester[-window_size:],
             messages_with_agents=state.messages_with_agents[-window_size_2:],
             observation=state.observation,
             plan=state.plan,
             participants=state.participants,
             objects_summary=objects_summary,
             must_cite_objects_summary=must_cite_objects_summary,
             important_guidelines=important_guidelines,
             tools_interactions=inputs.get("tools_interactions", {})
        )
        rendered_messages = prompt_partial.format_messages()
        if vision_context:
            rendered_messages.append(vision_context)
        
        graph = create_react_agent(
            model=observe_node_llm,
            prompt=ChatPromptTemplate.from_messages(rendered_messages),
            tools=tools,
            state_schema=RelayModeratorReactAgentState
        )
        inputs, message = process_graph_stream(graph, inputs, config)

    if message.type == "ai":
        response = output_parser.parse(message)
    else:
        raise ValueError(f"Expected AI message but got: {message.__class__}")

    # --- LÓGICA DE RETORNO CORRIGIDA ---
    if response.action == "continue_with_requester":
        # Responde diretamente, encerra o ciclo do agente.
        return {
            "node_from": "observe_node",
            "i_need_a_feedback": False,
            "execution_is_complete": True,
            "my_plan_is_complete": True, # Plano não foi necessário
            "observation": response.message,
            "messages_with_requester": [
                AIMessage(content=set_now_time_to_string(response.message), name=config.get("configurable").get("agent_name"))
            ],
            "flow_direction": "requester",
            "ordem": [] # Garante que a ordem seja limpa
        }
    elif response.action == "continue_with_participants":
        # Precisa de planejamento, avança para o nó de plan
        return {
            "node_from": "observe_node",
            "i_need_a_feedback": False,
            "execution_is_complete": False, # Continua para o plan
            "my_plan_is_complete": False,
            "observation": response.message, # Passa observações para o plan
        }
    else:
        raise ValueError(f"Invalid action in response: {response.action}")

# --- 3. NÓ DE PLANEJAMENTO ---
def plan_node(state: RelayModeratorPlanningAgentWorkingMemoryState, config: RunnableConfig, store) -> dict:
    """
    Processa a fase de planejamento.
    """
    state = node_path_count(state, state.node_from, "plan_node") 
    node_callback_manager = config.get("configurable").get("plan_node_callback_manager")
    node_callback_manager.on_plan_node_start(state, config)
    plan_node_llm = config.get("configurable").get("plan_node_llm")
    plan_node_prompt_language = config.get("configurable").get("plan_node_llm_prompt_language")
    plan_node_has_vision = config.get("configurable").get("plan_node_has_vision", False)
    plan_node_llm_use_structured_output = config.get("configurable").get("plan_node_llm_use_structured_output", False)
    
    # Chama o prompt 'plan_relay'
    prompt_data = prompt_generator.generate_prompt(
        prompt_name="plan_relay",
        language=plan_node_prompt_language,
        use_structured_output=plan_node_llm_use_structured_output,
        llm=plan_node_llm if plan_node_llm else None
    )
    prompt = prompt_data["prompt"]
    output_parser = prompt_data["output_parser"]
    
    chat_id = config.get("configurable").get("chat_id")
    shared_memory_configs = config.get("configurable").get("execute_shared_objects_config")
    shared_memory: SharedObjectsMemory = store.get_memory("shared_objects")
    tools = config.get("configurable").get("executing_tools", [])
    important_guidelines = config.get("configurable").get("plan_important_guidelines")
    window_size = min(config.get("configurable").get("chat_history_window_size"), len(state.messages_with_requester))
    window_size_2 = min(config.get("configurable").get("chat_history_window_size"), len(state.messages_with_agents))

    message = None
    inputs = {
        "messages": [state.messages_with_requester[-1]] if state.messages_with_requester else [],
        "messages_with_requester": state.messages_with_requester[-window_size:],
        "messages_with_agents": state.messages_with_agents[-window_size_2:],
        "participants": state.participants,
        "plan": state.plan,
        "observation": state.observation,
        "tools_interactions": {}
    }
    while not isinstance(message, AIMessage):
        objects_summary = ""
        must_cite_objects_summary = ""
        vision_context = None
        if shared_memory:
            last_memories_metadata = shared_memory.get_last_memories_metadata(chat_id=chat_id, k=shared_memory_configs['k'])
            object_ids = [metadata.object_id for metadata in last_memories_metadata]
            must_cite_object_ids = []
            if state.interaction_initial_datetime:
                for metadata in last_memories_metadata:
                    if datetime.fromtimestamp(metadata.created_at / 1000).astimezone(timezone.utc) >= state.interaction_initial_datetime:
                        must_cite_object_ids.append(metadata.object_id)
            objects_summary = shared_memory.generate_summary_from_object_ids(
                chat_id=chat_id, object_ids=list(set(object_ids)-set(must_cite_object_ids)), language=shared_memory_configs['language']
            )
            must_cite_objects_summary = shared_memory.generate_summary_from_object_ids(
                chat_id=chat_id, object_ids=must_cite_object_ids, language=shared_memory_configs['language']
            )
            vision_context = None
            if plan_node_has_vision and objects_summary:
                vision_context = get_vision_context(
                    node_prompt_language=plan_node_prompt_language,
                    node_llm=plan_node_llm,
                    node_prompt_use_structured_output=plan_node_llm_use_structured_output,
                    shared_memory=shared_memory,
                    config=config,
                    messages_with_requester=state.messages_with_requester[-window_size:],
                    messages_with_agents=state.messages_with_agents[-window_size_2:],
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
            messages_with_requester=state.messages_with_requester[-window_size:],
            messages_with_agents=state.messages_with_agents[-window_size_2:],
            observation=state.observation,
            plan=state.plan,
            participants=state.participants,
            objects_summary=objects_summary,
            must_cite_objects_summary=must_cite_objects_summary,
            important_guidelines=important_guidelines,
            tools_interactions=inputs.get("tools_interactions", {})
        )
        rendered_messages = prompt_partial.format_messages()
        if vision_context:
            rendered_messages.append(vision_context)

        graph = create_react_agent(
            model=plan_node_llm,
            prompt=ChatPromptTemplate.from_messages(rendered_messages),
            tools=tools,
            state_schema=RelayModeratorReactAgentState
        )
        inputs, message = process_graph_stream(graph, inputs, config)

    if message.type == "ai":
        response = output_parser.parse(message)
    else:
        raise ValueError(f"Expected AI message but got: {message.__class__}")
    
    # Esta lógica de retorno está CORRETA para o ReactPlanningAgent
    if response.action == "execute":
        return {
            "node_from": "plan_node",
            "i_need_a_feedback": False,
            "execution_is_complete": False, # Avança para o execute
            "my_plan_is_complete": True, # O plano está pronto
            "observation": "",
            "plan": response.message
        }
    elif response.action == "nothing":
        return {
            "node_from": "plan_node",
            "i_need_a_feedback": False,
            "execution_is_complete": False,
            "my_plan_is_complete": False, # O plano falhou, volta ao observe
            "observation": "",
            "plan": response.message
        }
    else:
        raise ValueError(f"Invalid action in response: {response.action}")

# --- 4. NÓ DE EXECUÇÃO ---
def execute_node(state: RelayModeratorPlanningAgentWorkingMemoryState, config: RunnableConfig, store) -> dict:
    """
    Processa a fase de execução.
    Decide se inicia um ciclo RELAY ou se responde ao demandante.
    """
    state = node_path_count(state, state.node_from, "execute_node") 
    node_callback_manager = config.get("configurable").get("execute_node_callback_manager")
    node_callback_manager.on_execute_node_start(state, config)
    execute_node_llm = config.get("configurable").get("execute_node_llm")
    execute_node_prompt_language = config.get("configurable").get("execute_node_llm_prompt_language")
    execute_node_has_vision = config.get("configurable").get("execute_node_has_vision", False)
    execute_node_llm_use_structured_output = config.get("configurable").get("execute_node_llm_use_structured_output", False)
    
    # Chama o prompt 'execute_relay'
    prompt_data = prompt_generator.generate_prompt(
        prompt_name="execute_relay",
        language=execute_node_prompt_language,
        use_structured_output=execute_node_llm_use_structured_output,
        llm=execute_node_llm if execute_node_llm else None
    )
    prompt = prompt_data["prompt"]
    output_parser = prompt_data["output_parser"]
    
    chat_id = config.get("configurable").get("chat_id")
    shared_memory_configs = config.get("configurable").get("execute_shared_objects_config")
    shared_memory: SharedObjectsMemory = store.get_memory("shared_objects")
    tools = config.get("configurable").get("executing_tools", [])
    important_guidelines = config.get("configurable").get("execute_important_guidelines")
    window_size = min(config.get("configurable").get("chat_history_window_size"), len(state.messages_with_requester))
    window_size_2 = min(config.get("configurable").get("chat_history_window_size"), len(state.messages_with_agents))

    message = None
    inputs = {
        "messages": [state.messages_with_requester[-1]] if state.messages_with_requester else [],
        "messages_with_requester": state.messages_with_requester[-window_size:],
        "messages_with_agents": state.messages_with_agents[-window_size_2:],
        "participants": state.participants,
        "plan": state.plan,
        "observation": state.observation,
        "tools_interactions": {}
    }
    while not isinstance(message, AIMessage):
        objects_summary = ""
        must_cite_objects_summary = ""
        vision_context = None
        if shared_memory:
            last_memories_metadata = shared_memory.get_last_memories_metadata(chat_id=chat_id, k=shared_memory_configs['k'])
            object_ids = [metadata.object_id for metadata in last_memories_metadata]
            must_cite_object_ids = []
            if state.interaction_initial_datetime:
                for metadata in last_memories_metadata:
                    if datetime.fromtimestamp(metadata.created_at / 1000).astimezone(timezone.utc) >= state.interaction_initial_datetime:
                        must_cite_object_ids.append(metadata.object_id)
            objects_summary = shared_memory.generate_summary_from_object_ids(
                chat_id=chat_id, object_ids=list(set(object_ids)-set(must_cite_object_ids)), language=shared_memory_configs['language']
            )
            must_cite_objects_summary = shared_memory.generate_summary_from_object_ids(
                chat_id=chat_id, object_ids=must_cite_object_ids, language=shared_memory_configs['language']
            )
            vision_context = None
            if execute_node_has_vision and objects_summary:
                vision_context = get_vision_context(
                    node_prompt_language=execute_node_prompt_language,
                    node_llm=execute_node_llm,
                    node_prompt_use_structured_output=execute_node_llm_use_structured_output,
                    shared_memory=shared_memory,
                    config=config,
                    messages_with_requester=state.messages_with_requester[-window_size:],
                    messages_with_agents=state.messages_with_agents[-window_size_2:],
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
            messages_with_requester=state.messages_with_requester[-window_size:],
            messages_with_agents=state.messages_with_agents[-window_size_2:],
            observation=state.observation,
            plan=state.plan,
            participants=state.participants,
            objects_summary=objects_summary,
            must_cite_objects_summary=must_cite_objects_summary,
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
            state_schema=RelayModeratorReactAgentState
        )
        inputs, message = process_graph_stream(graph, inputs, config)

    if message.type == "ai":
        response = output_parser.parse(message)
    else:
        raise ValueError(f"Expected AI message but got: {message.__class__}")

    # --- LÓGICA DE RETORNO CORRIGIDA ---
    if response.action == "continue_with_requester":
        # Plano executado, responde ao demandante e encerra o ciclo.
        return {
            "node_from": "execute_node",
            "i_need_a_feedback": False,
            "execution_is_complete": True, # Encerra o ciclo do agente
            "my_plan_is_complete": True,
            "observation": response.message,
            "messages_with_requester": [
                AIMessage(content=set_now_time_to_string(response.message), name=config.get("configurable").get("agent_name"))
            ],
            "flow_direction": "requester",
            "ordem": [] # Limpa a ordem
        }
    elif response.action == "continue_with_participants_relay":
        # Inicia o ciclo Relay. O ciclo do agente supervisor termina aqui.
        if response.message:
            messages_with_agents = [
                AIMessage(content=set_now_time_to_string(response.message), name=config.get("configurable").get("agent_name")) 
            ]
        else:
            messages_with_agents = []
        return {
            "node_from": "execute_node",
            "i_need_a_feedback": False,
            "execution_is_complete": True, # Encerra o ciclo do agente
            "my_plan_is_complete": True, # O plano foi executado (iniciando o relay)
            "observation": "Iniciando ciclo de colaboração Relay.",
            "messages_with_agents": messages_with_agents,
            "flow_direction": "agents",
            "ordem": response.order # Passa a ordem para o schema
        }
    else:
        raise ValueError(f"Invalid action in response: {response.action}")

# --- 5. CLASSE DO AGENTE ---
class RelayModeratorPlanningAgent(ReactPlanningAgent):
    """
    Moderador do esquema Relay que utiliza um ciclo Observe-Plan-Execute.
    """
    AGENT_TYPE = "relay_moderator_planning"
    WORKING_MEMORY_STATE = RelayModeratorPlanningAgentWorkingMemoryState
    OBSERVE_NODE = observe_node
    PLAN_NODE = plan_node
    EXECUTE_NODE = execute_node

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)