import json

def extract_headers(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    headers = []
    for cell in nb['cells']:
        if cell['cell_type'] == 'markdown':
            for line in cell['source']:
                if line.strip().startswith('#'):
                    headers.append(line.strip())
    
    return headers

if __name__ == "__main__":
    headers = extract_headers(r"c:\Users\Siddhant Sahu\Desktop\Data\College Assignments\Sem - 5 TY-Btech\EDA-PEC\Project\eda.ipynb")
    for h in headers:
        print(h)
