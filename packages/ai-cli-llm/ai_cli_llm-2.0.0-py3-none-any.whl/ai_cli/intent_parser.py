import spacy

nlp = spacy.load('en_core_web_sm')

def detect_intent_and_entities(text):
    doc = nlp(text.lower())
    intent = 'UNKNOWN'
    entities = {'source': None, 'destination': None}

    # Intent Detection
    lemmas = [t.lemma_ for t in doc]
    if any(l in ['list', 'show', 'display'] for l in lemmas) and not any(l in ['content', 'inside'] for l in lemmas):
        intent = 'LIST_FILES' # 'show files', 'list directory'
    elif any(l in ['read', 'cat', 'type', 'print'] for l in lemmas) or (any(l in ['show', 'display'] for l in lemmas) and any(l in ['content'] for l in lemmas)):
        intent = 'READ_FILE' # 'read file.txt', 'show content of x'
    elif any(l in ['where', 'location'] for l in lemmas):
        intent = 'CURRENT_DIR'
    elif any(l in ['create', 'make'] for l in lemmas):
        intent = 'CREATE_FOLDER'
    elif any(l in ['delete', 'remove'] for l in lemmas):
        intent = 'DELETE_FILE'
    elif any(l in ['copy', 'duplicate', 'cp'] for l in lemmas):
        intent = 'COPY_FILE'
    elif any(l in ['move', 'mv', 'rename'] for l in lemmas):
        intent = 'MOVE_FILE'
    elif any(l in ['help', 'assist'] for l in lemmas):
        intent = 'HELP'

    # Entity Extraction (Dependency Parsing)
    # Strategy: Find the main verb/root, look for direct objects (source) and prepositional objects (destination)
    
    # 1. Identify potential targets (files/dirs) - Nouns/Proper Nouns, but arguably anything not a stopword could be a filename
    # A simple but more robust heuristic for filenames: often direct objects of variable length.
    
    # Simplified extraction for prototype:
    # Source: The recognized direct object of the command verb.
    # Destination: Object of 'to' or 'into' preposition.

    for token in doc:
        print(f"[DEBUG LOOP] Token: {token.text}, Dep: {token.dep_}, Pos: {token.pos_}, is_dobj: {token.dep_ == 'dobj'}")
        # Check if token is the root verb or related to it
        if token.dep_ == 'dobj':
            entities['source'] = token.text
        
        if token.dep_ == 'pobj' and token.head.text in ['to', 'into', 'in']:
            entities['destination'] = token.text

    # Fallback: if no dependency match, check all non-stop/non-punct tokens
    # This catches filenames that Spacy might misclassify (e.g. as ADV or ADJ)
    candidates = []
    skip_lemmas = ['list', 'show', 'display', 'read', 'cat', 'type', 'print', 
                   'where', 'location', 'create', 'make', 'delete', 'remove', 
                   'copy', 'duplicate', 'cp', 'move', 'mv', 'rename', 'help', 'assist',
                   'to', 'into', 'in', 'file', 'folder', 'directory', 'content']
    
    for token in doc:
        if not token.is_stop and not token.is_punct and token.lemma_ not in skip_lemmas:
            candidates.append(token.text)
    
    if not entities['source'] and candidates:
        entities['source'] = candidates[0]
    
    if intent in ['COPY_FILE', 'MOVE_FILE'] and not entities['destination']:
        # If we assigned candidate[0] to source, candidate[1] is dest
        if entities['source'] in candidates and len(candidates) > 1:
            idx = candidates.index(entities['source'])
            if idx + 1 < len(candidates):
                entities['destination'] = candidates[idx + 1]

    return intent, entities


def detect_intent(text):
    intent, _ = detect_intent_and_entities(text)
    return intent
