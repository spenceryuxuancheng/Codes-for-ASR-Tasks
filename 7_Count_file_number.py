import os

def find_mp3_documents(folder_path):
    mp3_list = []
    count_all = 0

    # Iterate through each subfolder
    for subfolder, _, files in os.walk(folder_path):
        # Create sets of base names
        mp3_list = {file[:-4] for file in files if file.endswith('.mp3')}
        count_all += len(mp3_list)
    
    return count_all

# Path to the main folder containing subfolders
folder_path = 'Alignment_Input'
missing_documents = find_mp3_documents(folder_path)
print(missing_documents)
