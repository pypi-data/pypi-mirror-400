from typing import Optional, List, Dict, Any, Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from eagle.memory.planning.plans_qa_memory import PlansQAMemory

# Input para busca de planos
class PossiblePlansQAToolInput(BaseModel):
    question: str = Field(description="A request of a plan to do something. ('How to...?', 'What is the best way to...?' etc.)")

# Novo input para busca de fontes por titles
class PlansQASourcesByTitleToolInput(BaseModel):
    titles: List[str] = Field(description="Lista de títulos das fontes desejadas.")

class PossiblePlansQATool(BaseTool):
    """
    Tool para buscar e apresentar planos mais próximos semanticamente, sem rodar chain.
    """
    name: str = "possible_plans_qa_tool"
    description: str = (
        "Retorna uma representação textual dos planos mais próximos semanticamente da pergunta, "
        "com perguntas relacionadas e descrições resumidas, sem gerar resposta direta."
    )
    memory: PlansQAMemory
    prompt_language: str
    limit: int
    plans_set_id: Any
    filter_sources: Optional[List[str]]

    # Textos multilíngues
    TEXTS: dict = {
        "pt-br": {
            "no_results": "Nenhum plano encontrado.",
            "result_sep": "------------ Resultado {idx} ------------",
            "for_questions": "Para as perguntas abaixo:",
            "source_knowledge": "Temos a seguinte fonte de conhecimento:",
            "title": "Título: {title}",
            "short_desc": "Descrição resumida: {short_desc}",
        },
        "en": {
            "no_results": "No plan found.",
            "result_sep": "------------ Result {idx} ------------",
            "for_questions": "For the questions below:",
            "source_knowledge": "We have the following knowledge source:",
            "title": "Title: {title}",
            "short_desc": "Short description: {short_desc}",
        }
    }

    args_schema: Type[BaseModel] = PossiblePlansQAToolInput

    def _get_text(self, key):
        lang = getattr(self, "prompt_language", "pt-br")
        return self.TEXTS.get(lang, self.TEXTS["pt-br"]).get(key, "")

    def _format_results(self, plans: List[Dict[str, Any]]) -> str:
        """
        Formata os resultados conforme o modelo solicitado.
        """
        if not plans:
            return self._get_text("no_results")
        grouped = {}
        for plan in plans:
            key = (plan.get("title", ""), plan.get("short_description", ""))
            grouped.setdefault(key, []).append(plan["question"])
        result_lines = []
        for idx, ((title, short_desc), questions) in enumerate(grouped.items(), 1):
            result_lines.append(self._get_text("result_sep").format(idx=idx))
            result_lines.append(self._get_text("for_questions"))
            for q in questions:
                result_lines.append(q)
            result_lines.append(self._get_text("source_knowledge"))
            result_lines.append(self._get_text("title").format(title=title))
            result_lines.append(self._get_text("short_desc").format(short_desc=short_desc))
        return "\n".join(result_lines)

    def _run(self, **_inputs: PossiblePlansQAToolInput) -> str:
        inputs = PossiblePlansQAToolInput(**_inputs)
        plans = self.memory.search_memories(
            plans_set_id=self.plans_set_id,
            query=inputs.question,
            limit=self.limit,
            filter_sources=self.filter_sources
        )
        return self._format_results(plans)

    async def _arun(self, **_inputs: PossiblePlansQAToolInput) -> str:
        inputs = PossiblePlansQAToolInput(**_inputs)
        plans = await self.memory.asearch_memories(
            plans_set_id=self.plans_set_id,
            query=inputs.question,
            limit=self.limit,
            filter_sources=self.filter_sources
        )
        return self._format_results(plans)

class PlansQASourcesByTitleTool(BaseTool):
    """
    Tool para apresentar as fontes de conhecimento (texto completo) de um conjunto de planos, filtrando por títulos.
    """
    name: str = "plans_qa_sources_by_title_tool"
    description: str = (
        "Retorna as fontes de conhecimento (texto completo) dos planos presentes na memória para um determinado plans_set_id, "
        "filtrando por uma lista de títulos."
    )
    memory: PlansQAMemory
    plans_set_id: Any

    # Textos multilíngues
    TEXTS: dict = {
        "pt-br": {
            "no_results": "Nenhuma fonte encontrada.",
            "result_sep": "------------ Fonte {idx} ------------",
            "title": "Título: {title}",
            "short_desc": "Descrição resumida: {short_desc}",
            "full_text": "Texto completo:",
        },
        "en": {
            "no_results": "No source found.",
            "result_sep": "------------ Source {idx} ------------",
            "title": "Title: {title}",
            "short_desc": "Short description: {short_desc}",
            "full_text": "Full text:",
        }
    }

    args_schema: Type[BaseModel] = PlansQASourcesByTitleToolInput
    prompt_language: str = "pt-br"

    def _get_text(self, key):
        lang = getattr(self, "prompt_language", "pt-br")
        return self.TEXTS.get(lang, self.TEXTS["pt-br"]).get(key, "")

    def _run(self, **_inputs: PlansQASourcesByTitleToolInput) -> str:
        inputs = PlansQASourcesByTitleToolInput(**_inputs)
        plans = self.memory.search_memories(
            plans_set_id=self.plans_set_id,
            filter_titles=inputs.titles,
            limit=1000
        )
        if not plans:
            return self._get_text("no_results")
        grouped = {}
        for plan in plans:
            key = plan.get("title", "")
            grouped[key] = plan  # Mantém apenas um plano por título
        result_lines = []
        for idx, (title, plan) in enumerate(grouped.items(), 1):
            short_desc = plan.get("short_description", "")
            result_lines.append(self._get_text("result_sep").format(idx=idx))
            result_lines.append(self._get_text("title").format(title=title))
            result_lines.append(self._get_text("short_desc").format(short_desc=short_desc))
            result_lines.append(self._get_text("full_text"))
            result_lines.append(plan.get("plan", ""))
        return "\n".join(result_lines)

    async def _arun(self, **_inputs: PlansQASourcesByTitleToolInput) -> str:
        inputs = PlansQASourcesByTitleToolInput(**_inputs)
        plans = await self.memory.asearch_memories(
            plans_set_id=self.plans_set_id,
            filter_titles=inputs.titles,
            limit=1000
        )
        if not plans:
            return self._get_text("no_results")
        grouped = {}
        for plan in plans:
            key = plan.get("title", "")
            grouped[key] = plan  # Mantém apenas um plano por título
        result_lines = []
        for idx, (title, plan) in enumerate(grouped.items(), 1):
            short_desc = plan.get("short_description", "")
            result_lines.append(self._get_text("result_sep").format(idx=idx))
            result_lines.append(self._get_text("title").format(title=title))
            result_lines.append(self._get_text("short_desc").format(short_desc=short_desc))
            result_lines.append(self._get_text("full_text"))
            result_lines.append(plan.get("plan", ""))
        return "\n".join(result_lines)