import os

def find_documents(folder_path):
    """Count all files in folder and subfolders and return count + list"""
    doc_list_all = []
    count_all = 0

    # Iterate through each subfolder
    for subfolder, _, files in os.walk(folder_path):
        for file in files:
            # Store basename without extension
            base_name = file[:-4] if file.endswith('.mp3') or file.endswith('.mp4') else file
            doc_list_all.append(base_name)
            count_all += 1

    
    return count_all, doc_list_all

# Path to the main folder containing subfolders
folder_path_1 = '/Users/SSSPR/Documents/Zhang_Caicai/2_MAIN_Narrative/MAIN_Narrative_mp3:4_Backup/MAIN_Narrative_mp3_Backup'
folder_path_2 = '/Users/SSSPR/Documents/Zhang_Caicai/2_MAIN_Narrative/MAIN_Narrative_mp3:4_Backup/MAIN_Narrative_mp4_Backup'
folder_path_3 = '/Users/SSSPR/Documents/Zhang_Caicai/2_MAIN_Narrative/MAIN_Narrative_mp3:4_Backup/MAIN_Narrative_output_mp4-mp3'

documents_1 = find_documents(folder_path_1)
documents_2 = find_documents(folder_path_2)
documents_3 = find_documents(folder_path_3)
print(f"Folder 1: {documents_1[0]} files")
print(f"Folder 2: {documents_2[0]} files")
print(f"Folder 3: {documents_3[0]} files")

# Find missing files in folder 3 compared to folder 2
missing_in_3 = list(set(documents_2[1]) - set(documents_3[1]))
print(f"\nMissing in Folder 3 (from Folder 2): {len(missing_in_3)} file(s)")
if missing_in_3:
    for missing_file in sorted(missing_in_3):
        print(f"  - {missing_file}")


