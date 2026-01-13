import os
import platform

def map_command(intent, user_input, entities=None):
    is_windows = os.name == 'nt'
    
    # helper to get source/dest safe
    source = entities.get('source') if entities else None
    destination = entities.get('destination') if entities else None

    if intent == "CREATE_FOLDER":
        # Prefer entity if available
        folder_name = source
        if not folder_name:
            parts = user_input.replace("create folder", "").replace("make folder", "").split()
            if parts:
                folder_name = parts[-1]
        
        if folder_name:
             return f"mkdir {folder_name}"

    elif intent == "LIST_FILES":
        if is_windows:
            return "dir"
        return "ls -R" 

    elif intent == "READ_FILE":
        if source:
            if is_windows:
                return f"type {source}"
            return f"cat {source}"

    elif intent == "CURRENT_DIR":
        if is_windows:
            return "cd"
        return "pwd"

    elif intent == "DELETE_FILE":
        filename = source
        if not filename:
             parts = user_input.replace("delete", "").replace("remove", "").split()
             if parts:
                 filename = parts[-1]
        
        if filename:
            if is_windows:
                return f"del /Q {filename}"
            return f"rm -f {filename}"

    elif intent == "COPY_FILE":
        if source and destination:
            if is_windows:
                return f"copy {source} {destination}"
            return f"cp {source} {destination}"
    
    elif intent == "MOVE_FILE":
        if source and destination:
            if is_windows:
                return f"move {source} {destination}"
            return f"mv {source} {destination}"

    elif intent == "HELP": 
        return "HELP_MESSAGE"
    
    return None
