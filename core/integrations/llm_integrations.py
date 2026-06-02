from radport.core.integrations.PROMPTS import CX_RAY


def claude_prompt_CX_call_generate_md(patient_data,checklist_data): #CHEST X RAY ONLY PROMPT
    prompt = CX_RAY.format(patient_data,checklist_data)
