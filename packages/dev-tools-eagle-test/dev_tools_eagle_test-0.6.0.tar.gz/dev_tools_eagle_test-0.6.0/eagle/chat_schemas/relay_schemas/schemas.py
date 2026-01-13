from eagle.chat_schemas.base import BasicChatSchema, BasicChatState
from eagle.agents.base import BasicAgent
from langchain_core.runnables import RunnableConfig
from pydantic import Field
from typing import List
from langgraph.checkpoint.memory import InMemorySaver

class RelayChatState(BasicChatState):
    ordem: List[str] = Field(default_factory=list, description="Ordem dos participantes para o ciclo atual.")
    current_participant_index: int = Field(default=0, description="Índice do participante atual na lista 'ordem'.")

class RelayChatSchema(BasicChatSchema):
    WORKING_MEMORY_STATE = RelayChatState

    def __init__(self, moderator: BasicAgent):
        super().__init__(moderator)

    def supervisor_agent_node_generator(self) -> callable:
        """
        Gera o nó do supervisor, que decide a ordem do próximo ciclo.
        """
        def supervisor_node(state: RelayChatState, config: RunnableConfig, store) -> dict:
            supervisor = self._multiagent_index[self._supervisor.name]
            supervisor_config = config.get("configurable").get("agent_configs").get(self._supervisor.name)
            supervisor_state = {
                "messages_with_requester": state.messages_with_requester,
                "messages_with_agents": state.messages_with_agents,
                "participants": state.participants,
                "interaction_initial_datetime": state.interaction_initial_datetime,
            }
            supervisor.run(supervisor_state, supervisor_config)
            agent_snapshot = supervisor.state_snapshot

            if agent_snapshot.values["flow_direction"] == "agents":
                return {
                    "flow_direction": "agents",
                    "messages_with_agents": agent_snapshot.values["messages_with_agents"],
                    "ordem": agent_snapshot.values["ordem"],
                    "current_participant_index": 0
                }
            elif agent_snapshot.values["flow_direction"] == "requester":
                return {
                    "flow_direction": "requester",
                    "messages_with_requester": agent_snapshot.values["messages_with_requester"],
                    "ordem": []
                }
            else:
                raise ValueError("Direção de fluxo inválida do nó supervisor.")
        return supervisor_node

    def multiagent_agent_node_generator(self, agent_name: str) -> callable:
        """
        Gera o nó para um agente, que incrementa o contador do ciclo após a execução.
        """
        base_agent_node = super().multiagent_agent_node_generator(agent_name)
        def agent_node_with_increment(state: RelayChatState, config: RunnableConfig, store) -> dict:
            update_dict = base_agent_node(state, config, store)
            update_dict['current_participant_index'] = state.current_participant_index + 1
            return update_dict
        return agent_node_with_increment

    def next_agent_node(self, state: RelayChatState) -> dict:
        """
        Este nó, definido em base.py, atua como um ponto de junção.
        Ele não altera o estado, apenas permite que o fluxo convirja antes do roteamento.
        """
        return {}

    def dynamic_relay_router(self, state: RelayChatState) -> str:
        """
        Esta função é o roteador. Ela lê o estado e retorna o NOME do próximo nó.
        """
        ordem_do_ciclo = state.ordem
        index_atual = state.current_participant_index

        failure_condition = False
        if index_atual > 0:
            if not self._multiagent_index[state.ordem[index_atual-1]].state_snapshot.values['execution_is_complete']:
                failure_condition = True

        if not ordem_do_ciclo or index_atual >= len(ordem_do_ciclo) or failure_condition:
            # Fim do ciclo, volta para o supervisor
            supervisor_callable_name = self._set_node_callable_name(self._supervisor.name)
            return f"{supervisor_callable_name}_node"
        else:
            # Continua o ciclo para o próximo participante
            proximo_participante = ordem_do_ciclo[index_atual]
            return self._set_node_callable_name(proximo_participante) + "_node"

    def add_multiagent_edges(self):
        """
        Conecta as peças do grafo.
        """
        self._graph_builder.add_conditional_edges(
            "next_agent_node",
            self.dynamic_relay_router,
            {
                # Lista de todos os destinos possíveis
                **{f"{self._set_node_callable_name(name)}_node": f"{self._set_node_callable_name(name)}_node" 
                   for name in self._multiagent_index.keys()}
            }
        )

        # Após cada agente participante falar, o controle volta para o ponto de junção (next_agent_node).
        for agent_name in self._multiagent_index.keys():
            if agent_name != self._supervisor.name:
                callable_name = self._set_node_callable_name(agent_name)
                self._graph_builder.add_edge(f"{callable_name}_node", "next_agent_node")

