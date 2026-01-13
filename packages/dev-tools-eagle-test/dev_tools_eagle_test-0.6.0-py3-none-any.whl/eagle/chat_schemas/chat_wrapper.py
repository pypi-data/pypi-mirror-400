from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from eagle.agents.base import BasicAgent, BasicWorkingMemoryState
from eagle.chat_schemas.base import BasicChatConfigSchema

class FuncWrapper:

    def __init__(self, x):
        self.__func__ = x

class ChatWrapperAgent(BasicAgent):
    """
    Transforms a chat into a simple agent.
    """

    CONFIG_SCHEMA = BasicChatConfigSchema

    def __init__(self, name, description, chat):
        super().__init__(name=name, description=description)
        self.chat = chat

        self.OBSERVE_NODE = FuncWrapper(self.transfer_node)

    def transfer_node(self, state: BasicWorkingMemoryState, config: RunnableConfig, store) -> BasicWorkingMemoryState:
        
        chat_config = config.get("configurable")
        state_to_chat = {
            "messages_with_requester": state.messages
        }

        self.chat.run(state_to_chat, chat_config, store)

        messages = self.chat.state_snapshot.values["messages_with_requester"]

        return {
            "node_from": "observe_node",
            "i_need_a_feedback": False,
            "execution_is_complete": True,
            "messages": [AIMessage(content=messages[-1].content, name=self.name, id=messages[-1].id)],
        }


