import pandas as pd
from classify import classify_text
from mask import process_text

def handle_email_processing(email_text: str):
    # Step 1: Mask PII
    masked_text, masking_log = process_text(email_text)
    
    # Step 2: Classify masked content
    classification_list = classify_text(masked_text)
    category = classification_list[0] if classification_list else "Uncategorized"
    
    # Step 3: Convert masking log to structured list
    entity_list = []
    if not masking_log.empty:
        for _, row in masking_log.iterrows():
            entity_list.append({
                "position": [int(row["start"]), int(row["end"])],
                "classification": row["type"],
                "entity": row["match"]
            })
    
    # Step 4: Return full response structure
    return {
        "input_email_body": email_text,
        "list_of_masked_entities": entity_list,
        "masked_email": masked_text,
        "category_of_the_email": category
    }
