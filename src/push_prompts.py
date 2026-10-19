"""Valida o YAML e publica a versão otimizada no Prompt Hub."""
import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client
from utils import check_env_vars, load_yaml

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')

def build_template(data):
    return ChatPromptTemplate.from_messages([
        ('system', data['system_prompt']), ('human', data['user_prompt'])
    ])

def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    errors = []
    if not isinstance(prompt_data, dict):
        return False, ['O prompt deve ser um objeto YAML.']
    for key in ('description', 'system_prompt', 'user_prompt', 'version'):
        value = prompt_data.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f'Campo textual obrigatório: {key}')
    techniques = prompt_data.get('techniques_applied', [])
    if not isinstance(techniques, list) or not all(isinstance(x, str) for x in techniques):
        errors.append('techniques_applied deve ser uma lista de nomes.')
    elif len(set(techniques)) < 2 or 'few-shot' not in techniques:
        errors.append('Informe few-shot e uma técnica adicional.')
    if '[TODO]' in str(prompt_data) or prompt_data.get('version') != 'v2':
        errors.append('Versão deve ser v2, sem marcadores pendentes.')
    if not errors:
        try:
            template = build_template(prompt_data)
            if set(template.input_variables) != {'bug_report'}:
                errors.append('A única variável permitida é bug_report.')
            template.invoke({'bug_report': 'Relato com {chaves} literais'})
        except (ValueError, KeyError, TypeError):
            errors.append('Template inválido; revise variáveis e chaves literais.')
    return not errors, errors

def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    valid, errors = validate_prompt(prompt_data)
    if not valid:
        print('\n'.join(errors), file=sys.stderr)
        return False
    username = os.getenv('USERNAME_LANGSMITH_HUB', '')
    if not re.fullmatch(r'[A-Za-z0-9_-]+', username):
        print('Configure seu handle em USERNAME_LANGSMITH_HUB.', file=sys.stderr)
        return False
    if prompt_name != 'bug_to_user_story_v2':
        return False
    try:
        url = Client().push_prompt(
            f'{username}/{prompt_name}', object=build_template(prompt_data),
            is_public=True, description=prompt_data['description'],
            tags=list(dict.fromkeys(prompt_data.get('tags', []) + prompt_data['techniques_applied'])),
        )
        print(f'Prompt publicado: {url}')
        return True
    except Exception as exc:
        print(f'Publicação não concluída ({type(exc).__name__}). Verifique chave e handle.', file=sys.stderr)
        return False

def main():
    if not check_env_vars(['LANGSMITH_API_KEY', 'USERNAME_LANGSMITH_HUB']):
        return 1
    prompts = load_yaml(str(ROOT / 'prompts/bug_to_user_story_v2.yml'))
    if not isinstance(prompts, dict) or set(prompts) != {'bug_to_user_story_v2'}:
        print('O arquivo deve conter somente bug_to_user_story_v2.', file=sys.stderr)
        return 1
    return 0 if push_prompt_to_langsmith('bug_to_user_story_v2', prompts['bug_to_user_story_v2']) else 1

if __name__ == '__main__':
    sys.exit(main())
