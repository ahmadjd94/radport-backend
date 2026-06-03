from copy import deepcopy


def merge_flow_with_report(flow_obj, study_report_obj):
    """
    Merge Flow.structure (schema) with StudyReport.report_data (answers).

    Each item in the structure gains:
      - user_answer: selected option(s) from answers['selections'][item_id]
      - user_description: free text from answers['descriptions'][item_id]
      - is_answered: bool

    Section notes (__note__<section_id>) are also merged.
    Conditional reveals are handled recursively.
    """
    enriched = deepcopy(flow_obj.structure)
    answers = study_report_obj.report_data
    if answers:
        selections = answers['selections']
        descriptions = answers['descriptions']
    else:
        selections = {}
        descriptions = {}

    # Traverse sections → groups → items
    for section_id, section in enriched.get('sections', {}).items():
        # Attach section-level note
        section_note_key = f"__note__{section_id}"
        if section_note_key in descriptions:
            section['user_section_note'] = descriptions[section_note_key]

        # Traverse groups
        for group in section.get('groups', []):
            for item in group.get('items', []):
                item_id = item['item_id']

                # Merge answer
                if item_id in selections:
                    item['user_answer'] = selections[item_id]
                    item['is_answered'] = True
                else:
                    item['user_answer'] = None
                    item['is_answered'] = False

                # Merge description
                if item_id in descriptions:
                    item['user_description'] = descriptions[item_id]
                else:
                    item['user_description'] = None

                # Handle conditional reveals
                if 'conditional' in item and 'reveals' in item['conditional']:
                    reveals_item = item['conditional']['reveals']
                    reveals_item_id = reveals_item['item_id']

                    if reveals_item_id in selections:
                        reveals_item['user_answer'] = selections[reveals_item_id]
                        reveals_item['is_answered'] = True
                    else:
                        reveals_item['user_answer'] = None
                        reveals_item['is_answered'] = False

                    if reveals_item_id in descriptions:
                        reveals_item['user_description'] = descriptions[reveals_item_id]
                    else:
                        reveals_item['user_description'] = None

    return enriched