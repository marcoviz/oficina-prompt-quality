"""Importa o prompt semente sem descartar mensagens ou acoplar um modelo."""
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langsmith import Client
from utils import check_env_vars, save_yaml

ROOT = Path(__file__).resolve().parents[1]
SEED = 'leonanluppi/bug_to_user_story_v1'
load_dotenv(ROOT / '.env')

def serialize_prompt(prompt):
    if not isinstance(prompt, ChatPromptTemplate):
        raise ValueError('Esperado ChatPromptTemplate sem modelo acoplado.')
    system, user = [], []
    for message in prompt.messages:
        if isinstance(message, SystemMessagePromptTemplate):
            system.append(message.prompt.template)
        elif isinstance(message, HumanMessagePromptTemplate):
            user.append(message.prompt.template)
        else:
            raise ValueError('Mensagem não suportada: exportação não pode perder conteúdo.')
    if len(system) != 1 or len(user) != 1:
        raise ValueError('Esperada uma mensagem system e uma user.')
    return {'bug_to_user_story_v1': {
        'description': 'Prompt semente importado do Hub para comparação',
        'system_prompt': system[0], 'user_prompt': user[0], 'version': 'v1',
        'tags': ['bug-analysis', 'user-story'],
    }}

def pull_prompts_from_langsmith():
    prompt = Client().pull_prompt(SEED, dangerously_pull_public_prompt=True)
    target = ROOT / 'prompts/bug_to_user_story_v1.yml'
    if not save_yaml(serialize_prompt(prompt), str(target)):
        raise OSError('Não foi possível salvar o prompt.')
    return target

def main():
    if not check_env_vars(['LANGSMITH_API_KEY']):
        return 1
    try:
        print(f'Prompt salvo em {pull_prompts_from_langsmith()}')
        return 0
    except Exception as exc:
        print(f'Importação não concluída ({type(exc).__name__}). Confira acesso e configuração.', file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
