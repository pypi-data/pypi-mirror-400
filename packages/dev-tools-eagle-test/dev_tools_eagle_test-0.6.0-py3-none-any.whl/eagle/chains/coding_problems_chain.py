from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence, RunnablePassthrough
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.output_parsers.string import StrOutputParser
from operator import itemgetter

# Define prompts for different languages
PROMPTS = {
    "pt-br": """
Você planejou e criou um código para executar um código para atender a uma demanda. Você chegou ao seu limite de tentativas e precisa explicar ao demandante, em linguagem humana, o motivo da desistência.
O plano para a criação do código foi o seguinte:
----- Plano ----
{{ plan }}
----------------

A explicação do erro na última tentativa foi o seguinte:
----- Erro -----
{{ previous_error_explanation }}
----------------

Retorne, então, com um texto com a explicação para o demandante. Se julgar necessário, mostre as porções do teu código que estão com problema etc.
Retorne APENAS a explicação, sem se dirigir a ninguém, somente o texto da explicação.
""",
    "en": """
You planned and implemented code to fulfill a request. You have reached the limit of your attempts and must explain to the requester, in plain human language, why you are stopping further attempts.

The plan used to create the code was:
----- Plan ----
{{ plan }}
----------------

The explanation of the error on the last attempt was:
----- Error -----
{{ previous_error_explanation }}
----------------

Return a clear, polite explanation addressed to the requester describing why you are giving up. If helpful, show the portions of your code that are causing the problem, suggest possible next steps or workarounds, and mention any assumptions, missing information, or external constraints that prevented a successful solution.
Return ONLY the explanation, not refering yourself to someone, only the explanation text.
"""
}

def create_explanation_chain(
    prompt_language: str,
    llm: BaseLanguageModel
) -> RunnableSequence:
    """
    Create an explanation chain based on the provided configuration.

    Args:
        prompt_language (str): Language for the prompt (e.g., "pt-br", "en").
        llm (BaseLanguageModel): Language model to be used for summarization.

    Returns:
        RunnableSequence: A chain that summarizes an explanation based on the provided configuration.
    """
    
    
    # Select the appropriate prompt template
    if prompt_language not in PROMPTS:
        raise ValueError(f"Unsupported prompt language: {prompt_language}")
    prompt = PromptTemplate.from_template(PROMPTS[prompt_language], template_format="jinja2")

    # Create chain using LCEL
    chain = (
        {"plan": itemgetter('plan'), "previous_error_explanation": itemgetter('previous_error_explanation')}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain
