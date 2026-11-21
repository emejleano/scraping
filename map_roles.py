# map_roles.py
import pandas as pd

df = pd.read_csv("data/corpus_jobs.csv")

# Petakan lowongan 'network_qa' berdasarkan kata kunci di job_title
def map_role(row):
    role = row['role_group']
    if role == 'network_qa':
        title = str(row['job_title']).lower()
        if any(k in title for k in ['qa', 'quality', 'tester', 'test', 'sqa']):
            return 'qa_tester'
        return 'network'
    return role

df['role_group'] = df.apply(map_role, axis=1)
df.to_csv("data/corpus_jobs.csv", index=False, encoding="utf-8-sig")

print("=== DISTRIBUSI PERAN FINAL (8 BIDANG IT) ===")
print(df['role_group'].value_counts())
print("\n=== PIVOT PERAN X BAHASA ===")
print(pd.crosstab(df['role_group'], df['language'], margins=True))