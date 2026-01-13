from typing import Type, List
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
import pandas as pd
from matplotlib.figure import Figure
from plotly import graph_objects as go
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models.chat_models  import BaseChatModel
from eagle.memory.shared.shared_objects_memory import SharedObjectsMemory
from eagle.toolkits_adapters.langchain_experimental.agents.agent_toolkits.pandas.base import create_pandas_dataframe_agent

# callback

class PythonObjectCapture(BaseCallbackHandler):
    def __init__(self):
        self.objects = []

    def on_tool_end(self, output, **kwargs):
        # Aqui o output é o próprio objeto Python retornado pelo REPL,
        # não a string, caso eval retorne algo não-string.
        
        if not isinstance(output, tuple):
            output = (output,)

        for item in output:    
            if isinstance(item, Figure):
                title = ""
                for axis in item.axes:
                    if hasattr(axis, 'title'):
                        title = axis.title._text
                        break

                self.objects.append({
                    "object_name": title if title else None,
                    "description": title if title else None,
                    "obj": item,
                    "object_type": type(item).__name__
                })
            elif isinstance(item, go.Figure):
                title = item.layout.title.text if item.layout.title and item.layout.title.text else None

                self.objects.append({
                    "object_name": title if title else None,
                    "description": title if title else None,
                    "obj": item,
                    "object_type": type(item).__name__
                })
            
            elif isinstance(item, pd.DataFrame):

                self.objects.append(
                    {
                        "object_name": None,
                        "description": None,
                        "obj": item,
                        "object_type": type(item).__name__
                    }
                )

class CodingDataFrameHandlingToolInput(BaseModel):
    tabelas_ids: List[str] = Field(
        description="Tabelas a serem usadas na análise."
    )
    demanda: str = Field(
        description="Descrição da demanda a ser realizada nas tabelas."
    )

class CodingDataFrameHandlingTool(BaseTool):
    name: str = "analisa_dataframes_tool"
    description: str = "Manipulação e análise de DataFrames / Tabelas para atender demandas específicas."
    args_schema: Type[BaseModel] = CodingDataFrameHandlingToolInput
    
    shared_objects_memory: SharedObjectsMemory
    _fixed_guidelines = [
        "Você inicialmente só está lendo um head() das tabelas, então não faça suposições sobre os dados além do que é mostrado no head(). Teus cálculos devem considerar que os dados completos podem ter mais linhas e valores diferentes.",
        "Só gere figuras e gráficos **se isso for pedido explicitamente** na demanda. Mesmo se a figura for gerada, narre em texto os insights sobre os dados de onde as figuras foram geradas.",
        "JAMAIS, em hipótese alguma, chame '.show()' em figuras eventualmente geradas. Elas devem retornar sem chamarem .show e qualquer momento no código.",
        "Se gráficos precisarem ser construídos, use SEMPRE plotly, JAMAIS matplotlib!",
        "Se eventualmente for produzida uma figura, retorne o objeto figura gerado.",
    ]

    custom_guidelines: List[str] = [
    ]

    llm: BaseChatModel

    def _run(self, **_inputs: CodingDataFrameHandlingToolInput) -> object:
        inputs = CodingDataFrameHandlingToolInput(**_inputs)

        objects_list = [self.shared_objects_memory.get_memory_object(chat_id=self.shared_objects_memory.conversation_id, object_id=tabela_id) for tabela_id in inputs.tabelas_ids]
        dfs = [obj.object for obj in objects_list]
        
        for df, tabela_id in zip(dfs, inputs.tabelas_ids):
            if not isinstance(df, pd.DataFrame):
                return f"O objeto de id {tabela_id} não é um DataFrame do pandas e, portanto, não pode ser manipulado por esta tool."
            
            if df.empty:
                return f"O objeto de id {tabela_id} é um DataFrame vazio."
        
        captor = PythonObjectCapture()

        agent = create_pandas_dataframe_agent(
            self.llm,
            dfs,
            agent_type="tool-calling",
            allow_dangerous_code=True,
            callbacks=[captor],
            tool_callbacks=[captor],      # <— ESSA É A CHAVE EM ALGUNS CASOS
            agent_executor_kwargs={"callbacks": [captor]},
            verbose=True,
            include_df_in_prompt=True
        )

        guidelines = "\n".join([f"{i}) {g}" for i, g in enumerate(self._fixed_guidelines + self.custom_guidelines)])

        query = f"""
{inputs.demanda}
---------------
Diretrizes importantes:
{guidelines}
"""
        response = agent.invoke(query, config={"callbacks": [captor]})

        added_objects_str_list = []
        for object in captor.objects:
            _generic_name = f"{object['object_type']}"
            _generic_description = f"{object['object_type']} gerado pela demanda '{inputs.demanda}' sobre o dataframes de id {inputs.tabelas_ids}."
            
            description=object['description'] if object['description'] is not None else _generic_description
            object_name=object['object_name'] if object['object_name'] is not None else _generic_name
            
            object_id = self.shared_objects_memory.put_memory(
                chat_id=self.shared_objects_memory.conversation_id,
                obj=object["obj"],
                description=description,
                object_name=object_name,
                object_type=object['object_type'],
                additional_namespace_levels=(self.shared_objects_memory.conversation_id,),
            )

            added_objects_str_list.append(f"Adicionado ao workspace o {object_name}, um {object['object_type']}, com o id {object_id}.")

        added_objects_str = '\n'.join(added_objects_str_list)

        return f"""
{response['output']}
------------------------
{added_objects_str}
"""

