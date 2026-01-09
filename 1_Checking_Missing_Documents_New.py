import os

def find_missing_documents(folder_path):
    missing_docs = []

    # Iterate through each subfolder
    for subfolder, _, files in os.walk(folder_path):
        # Create sets of base names
        mp3_names = {file[:-4] for file in files if file.endswith('.mp3')}
        chat_names = {file[:-4] for file in files if file.endswith('.cha')}
        
        # Find symmetric difference - names that only appear in one set
        only_in_mp3 = mp3_names - chat_names
        only_in_cha = chat_names - mp3_names
        
        # Add missing files
        for name in only_in_mp3:
            missing_docs.append(os.path.join(subfolder, f"{name}.mp3"))
        for name in only_in_cha:
            missing_docs.append(os.path.join(subfolder, f"{name}.cha"))
    
    return missing_docs

# Path to the main folder containing subfolders
folder_path = 'Alignment_Output_1.6_-t%WOR'
missing_documents = find_missing_documents(folder_path)

# Output the result
if missing_documents:
    print(f"Found {len(missing_documents)} missing companion files:")
    for doc in missing_documents:
        print(f"Missing: {doc}")
else:
    print("No missing companion files found.")