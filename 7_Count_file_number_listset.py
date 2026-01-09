import os

def find_documents(folder_path):
    doc_list = []
    doc_list_all = []
    count_all = 0

    # Iterate through each subfolder
    for subfolder, _, files in os.walk(folder_path):
        # Create sets of base names
        for file in files:
            doc_list_all.append(file[:-4])
            doc_list.append(file)
            count_all += len(doc_list)
            doc_list = []

    
    return count_all, doc_list_all

# Path to the main folder containing subfolders
folder_path_1 = 'MAIN_Narrative'
folder_path_2 = 'MAIN_Narrative_mp3'
folder_path_3 = 'MAIN_Narrative_mp4'

documents_1 = find_documents(folder_path_1)
documents_2 = find_documents(folder_path_2)
documents_3 = find_documents(folder_path_3)


missing_documents_num = documents_1[0] - documents_2[0] - documents_3[0]
missing_documents = list(set(documents_1[1]) - set(documents_2[1]) - set(documents_3[1]))

print(documents_1[0])
print(documents_2[0])
print(documents_3[0])


print(missing_documents_num)

print(missing_documents)


