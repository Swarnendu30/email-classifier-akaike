import re
import pandas as pd

# Define a global separator pattern (space and special characters)
SEPARATOR = r"(?:[ \.,/\\|:;‐‑‒–—―\-])?"

def process_text(text):
    masked_text = text
    masking_log = pd.DataFrame(columns=["type", "match", "start", "end"])
    CARD = 0

    # Email detection
    if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text):
        masked_text, masking_log = mask_email(masked_text, masking_log)

    # Phone number detection format
    if (re.search(rf"\+{SEPARATOR}(?:\d{SEPARATOR}){{9,}}", text) or
        re.search(rf"\b(?:\d{SEPARATOR}){{9,11}}\b", text)):
        masked_text, masking_log = mask_phone(masked_text, masking_log)

    # Bank/Card detection
    card_pattern = rf"(?i)(credit|debit|bank{SEPARATOR}card|payment{SEPARATOR}card)"
    if re.search(card_pattern, text):
        masked_text, masking_log, CARD = mask_bank(masked_text, masking_log, CARD)

    # UID/Aadhaar detection
    uid = rf"(?i)(aadhaar|aadhar|adhar|uidai|(?<![a-zA-Z])u{SEPARATOR}i{SEPARATOR}d(?![a-zA-Z]))"
    if re.search(uid, text):
        masked_text, masking_log = mask_uid(masked_text, masking_log)
    
    # DOB detection
    dob_pattern = rf"(?i)(date{SEPARATOR}of{SEPARATOR}birth|birth{SEPARATOR}date|(?<![a-zA-Z])d{SEPARATOR}o{SEPARATOR}b(?![a-zA-Z]))"
    if re.search(dob_pattern, text):
        masked_text, masking_log = mask_dob(masked_text, masking_log)
    
    if CARD >= 1:
        masked_text, masking_log = mask_expiry(masked_text, masking_log)
        masked_text, masking_log = mask_cvv(masked_text, masking_log)
    
    # Name detection
    masked_text, masking_log = mask_name(masked_text, masking_log)

    return masked_text, masking_log

def mask_email(masked_text, masking_log):
    # Define the email regex pattern
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    # Find all email matches in the masked_text
    matches = re.finditer(email_pattern, masked_text)
    
    for match in matches:
        # Extract match details
        start, end = match.span()
        email = match.group(0)
        
        # Create a new DataFrame with the match details
        match_details = pd.DataFrame([{
            "type": "email", 
            "match": email, 
            "start": start, 
            "end": end
        }])
        
        # Concatenate the new match details with the existing masking_log
        masking_log = pd.concat([masking_log, match_details], ignore_index=True)
        
        # Replace the matched email with [email]
        masked_text = masked_text[:start] + '[email]' + masked_text[end:]
    
    return masked_text, masking_log

def mask_phone(masked_text, masking_log):
    # Define international and local phone number patterns
    intl_pattern = rf"\+{SEPARATOR}(?:\d{SEPARATOR}){{9,}}"
    local_pattern = rf"\b(?:\d{SEPARATOR}){{9,11}}\b"
    
    # Combine both patterns using OR
    combined_pattern = rf"{intl_pattern}|{local_pattern}"
    
    # Compile the regex pattern
    pattern = re.compile(combined_pattern)
    
    # Find all matches
    matches = list(pattern.finditer(masked_text))
    
    # Reverse matches to avoid issues when replacing
    for match in reversed(matches):
        start, end = match.span()
        phone = match.group(0)

        # Create a new log entry
        match_details = pd.DataFrame([{
            "type": "phone",
            "match": phone,
            "start": start,
            "end": end
        }])
        
        # Append to the log using pd.concat
        masking_log = pd.concat([masking_log, match_details], ignore_index=True)

        # Replace the phone number with [phone]
        masked_text = masked_text[:start] + '[phone]' + masked_text[end:]
    
    return masked_text, masking_log

def mask_bank(masked_text, masking_log, CARD):
    # Match 15-digit or 16-digit card numbers with optional separators
    card_pattern = rf"""(?<!\d)(
        (?:\d{{4}}{SEPARATOR}\d{{6}}{SEPARATOR}\d{{5}})
        |
        (?:\d{{4}}{SEPARATOR}\d{{4}}{SEPARATOR}\d{{4}}{SEPARATOR}\d{{4}})
        |
        (?:\d{{15}}(?!\d))
        |
        (?:\d{{16}}(?!\d))
    )(?!\d)"""

    matches = list(re.finditer(card_pattern, masked_text, re.VERBOSE))

    for match in reversed(matches):
        start, end = match.span()
        card = match.group(0)

        match_details = pd.DataFrame([{
            "type": "card_number",
            "match": card,
            "start": start,
            "end": end
        }])

        masking_log = pd.concat([masking_log, match_details], ignore_index=True)
        CARD = CARD + 1
        masked_text = masked_text[:start] + '[card]' + masked_text[end:]
    
    return masked_text, masking_log, CARD

def mask_uid(masked_text, masking_log):
    uid_pattern = rf"(?<!\d)(?:\d{{4}}{SEPARATOR}\d{{4}}{SEPARATOR}\d{{4}}|\d{{3}}{SEPARATOR}\d{{3}}{SEPARATOR}\d{{3}}{SEPARATOR}\d{{3}}|\d{{12}})(?!\d)"
    
    matches = list(re.finditer(uid_pattern, masked_text))

    for match in reversed(matches):
        start, end = match.span()
        uid = match.group(0)

        match_details = pd.DataFrame([{
            "type": "uid",
            "match": uid,
            "start": start,
            "end": end
        }])

        masking_log = pd.concat([masking_log, match_details], ignore_index=True)
        masked_text = masked_text[:start] + '[uid]' + masked_text[end:]

    return masked_text, masking_log

def mask_dob(masked_text, masking_log):
    month_names = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|" \
                  r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    day_suffix = r"(?:[0-2]?[0-9]|3[01])(?:st|nd|rd|th)?"
    year_full = r"(?:19|20)\d{2}"
    year_short = r"\d{2}"
    SEPARATOR = r"(?:[ \.,/\\|:;‐‑‒–—―\-])"

    patterns = [
        # Month Day Year (e.g., April 23 2025)
        rf"\b{month_names}{SEPARATOR}{day_suffix}{SEPARATOR}{year_full}\b",
        # Day Month Year (e.g., 23 April 2025)
        rf"\b{day_suffix}{SEPARATOR}{month_names}{SEPARATOR}{year_full}\b",
        # YYYY-MM-DD or YYYY/MM/DD (ISO)
        rf"\b{year_full}{SEPARATOR}\d{{1,2}}{SEPARATOR}\d{{1,2}}\b",
        # DD/MM/YYYY or MM/DD/YYYY
        rf"\b\d{{1,2}}{SEPARATOR}\d{{1,2}}{SEPARATOR}{year_full}\b",
        # M/D/YY or D/M/YY
        rf"\b\d{{1,2}}{SEPARATOR}\d{{1,2}}{SEPARATOR}{year_short}\b",
        # April 23rd 2025
        rf"\b{month_names}{SEPARATOR}{day_suffix}{SEPARATOR}{year_full}\b",
        # 23rd April 2025
        rf"\b{day_suffix}{SEPARATOR}{month_names}{SEPARATOR}{year_full}\b",
        # 23rd of April 2025
        rf"\b{day_suffix}{SEPARATOR}of{SEPARATOR}{month_names}{SEPARATOR}{year_full}\b"
    ]

    combined_pattern = re.compile("|".join(patterns), re.IGNORECASE)
    matches = list(combined_pattern.finditer(masked_text))

    for match in reversed(matches):
        start, end = match.span()
        dob = match.group(0)

        match_details = pd.DataFrame([{
            "type": "dob",
            "match": dob,
            "start": start,
            "end": end
        }])

        masking_log = pd.concat([masking_log, match_details], ignore_index=True)
        masked_text = masked_text[:start] + '[dob]' + masked_text[end:]

    return masked_text, masking_log

def mask_expiry(masked_text, masking_log):
    expiry_pattern = rf"(?<!\d)(\d{{2}}{SEPARATOR}\d{{2}})(?!\d)"
    matches = list(re.finditer(expiry_pattern, masked_text))
    
    for match in reversed(matches):
        start, end = match.span()
        expiry = match.group(0)
        masking_log = pd.concat([masking_log, pd.DataFrame([{
            "type": "expiry_date",
            "match": expiry,
            "start": start,
            "end": end
        }])], ignore_index=True)
        masked_text = masked_text[:start] + '[expiry]' + masked_text[end:]

    return masked_text, masking_log

def mask_cvv(masked_text, masking_log):
    cvv_pattern = r"(?<!\d)(\d{3,4})(?!\d)"
    matches = list(re.finditer(cvv_pattern, masked_text))

    for match in reversed(matches):
        start, end = match.span()
        cvv = match.group()

        # Skip if next to obvious large numbers like card numbers
        if len(cvv) == 3 or len(cvv) == 4:
            masking_log = pd.concat([masking_log, pd.DataFrame([{
                "type": "cvv",
                "match": cvv,
                "start": start,
                "end": end
            }])], ignore_index=True)
            masked_text = masked_text[:start] + '[cvv]' + masked_text[end:]

    return masked_text, masking_log

def mask_name(masked_text, masking_log):
    name_pattern = re.compile(
        r"\bmy name is\b\s*(.+?)(?=[!?,;\.\n])", re.IGNORECASE
    )

    matches = list(name_pattern.finditer(masked_text))

    for match in reversed(matches):
        name = match.group(1).strip()
        start = match.start(1)
        end = match.end(1)

        if name:
            masking_log = pd.concat([masking_log, pd.DataFrame([{
                "type": "name",
                "match": name,
                "start": start,
                "end": end
            }])], ignore_index=True)

            masked_text = masked_text[:start] + '[name]' + masked_text[end:]

    return masked_text, masking_log

