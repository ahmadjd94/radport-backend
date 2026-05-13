# models.py or serializers.py
from copy import deepcopy


def merge_checklist_with_answers(checklist_obj, report_obj):
    """
    Merge checklist schema with report answers.

    Input:
      checklist_obj.structure = full schema with sections → groups → items
      report_obj.report_data = sparse answers {item_id: [selections], descriptions: {...}}

    Output:
      enriched structure with each item containing its answer + description
    """
    schema = deepcopy(checklist_obj.structure)
    answers = report_obj.report_data

    selections = answers.get('selections', {})
    descriptions = answers.get('descriptions', {})

    # Traverse and enrich
    for section_id, section in schema['sections'].items():
        # Add section-level note if exists
        section_note_key = f"__note__{section_id}"
        if section_note_key in descriptions:
            section['section_note'] = descriptions[section_note_key]

        # Traverse groups → items
        for group in section.get('groups', []):
            for item in group.get('items', []):
                item_id = item['item_id']

                # Attach answer
                if item_id in selections:
                    item['user_answer'] = selections[item_id]
                    item['is_answered'] = True
                else:
                    item['user_answer'] = None
                    item['is_answered'] = False

                # Attach description/free text
                if item_id in descriptions:
                    item['user_description'] = descriptions[item_id]

    return schema