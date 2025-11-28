import json

def find_age_code(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source = "".join(cell['source'])
            if 'age' in source:
                print("--- Cell ---")
                print(source)
                print("------------")

if __name__ == "__main__":
    find_age_code(r"c:\Users\Siddhant Sahu\Desktop\Data\College Assignments\Sem - 5 TY-Btech\EDA-PEC\Project\eda.ipynb")
