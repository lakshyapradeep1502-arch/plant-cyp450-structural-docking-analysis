#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
print(pd.__version__)


# In[2]:


from pathlib import Path
for f in sorted(Path("data").iterdir()):
    print(f.name)


# In[3]:


files = [
    "CYP2D6_allele_definition_table.xlsx",
    "CYP2D6_allele_functionality_reference.xlsx",
    "CYP2D6_Diplotype_Phenotype_Table.xlsx",
    "CYP2D6_frequency_table.xlsx",
]

for name in files:
    xl = pd.ExcelFile("data/" + name)
    print(name)
    print("Sheets:", xl.sheet_names)
    print()



# In[4]:


for name in files:
    df = pd.read_excel("data/" + name)
    print("=====", name, "=====")
    print("Shape (rows, columns):", df.shape)
    print(df.head())
    print()


# In[5]:


pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

func = pd.read_excel(
    "data/CYP2D6_allele_functionality_reference.xlsx",
    sheet_name="Allele Function", header=1
)
print(func.columns.tolist())
print(func.iloc[:, :4].head(10))
print()
print(func.iloc[:, 3].value_counts(dropna=False))


# In[6]:


freq = pd.read_excel(
    "data/CYP2D6_frequency_table.xlsx",
    sheet_name="Allele frequency", header=1
)
print(freq.columns.tolist())
print(freq.head(8))
print(freq.dtypes)


# In[7]:


dp = pd.read_excel("data/CYP2D6_Diplotype_Phenotype_Table.xlsx", sheet_name="Diplotypes")
print(dp.iloc[:, 2].value_counts(dropna=False))


# In[8]:


func = func.iloc[:, [0, 1, 3]].copy()
func.columns = ["allele", "activity", "clinical"]
func["allele"] = func["allele"].astype(str).str.strip()
func["activity_num"] = pd.to_numeric(func["activity"], errors="coerce")

print("Missing activity, by clinical category:")
print(func.groupby("clinical")["activity_num"].apply(lambda s: s.isna().sum()))
print()
print("Text values that are not plain numbers:")
print(func[func["activity_num"].isna() & func["activity"].notna()]["activity"].unique())
print()
usable = func[func["activity_num"].notna()]
print(len(usable), "alleles with a numeric activity value")
print(usable["activity_num"].value_counts().sort_index())


# In[9]:


dp.columns = ["diplotype", "score", "phenotype", "ehr"]


# In[10]:


n_all = len(func)
n_known = func["activity"].notna().sum()
print("Alleles in table:", n_all, "-> pairs:", n_all * (n_all + 1) // 2)
print("Alleles with an activity value:", n_known, "-> pairs:", n_known * (n_known + 1) // 2)
print("Diplotype table rows:", len(dp), "| determinate:", (dp["phenotype"] != "CYP2D6 Indeterminate").sum())


# In[11]:


# activity value of each allele; the two '≥3.0' alleles are read as 3.0 for this test only
act = dict(zip(
    func["allele"],
    pd.to_numeric(func["activity"].astype(str).str.replace("≥", ""), errors="coerce")
))

def split_dip(d):
    return [p.strip() for p in str(d).split("/")]

def total_activity(d):
    parts = split_dip(d)
    if len(parts) != 2 or any((p not in act) or pd.isna(act[p]) for p in parts):
        return None
    return act[parts[0]] + act[parts[1]]

def phenotype(score):
    if score == 0:
        return "CYP2D6 Poor Metabolizer"
    if score < 1.25:
        return "CYP2D6 Intermediate Metabolizer"
    if score <= 2.25:
        return "CYP2D6 Normal Metabolizer"
    return "CYP2D6 Ultrarapid Metabolizer"

det = dp[dp["phenotype"] != "CYP2D6 Indeterminate"].copy()
det["my_score"] = det["diplotype"].apply(total_activity)
det["cpic_score"] = pd.to_numeric(det["score"].astype(str).str.replace("≥", ""), errors="coerce")

print("Could not compute a score for:", det["my_score"].isna().sum())
print(det[det["my_score"].isna()].head())

ok = det.dropna(subset=["my_score"]).copy()
score_bad = ok[(ok["my_score"] - ok["cpic_score"]).abs() > 1e-9]
ok["my_phenotype"] = ok["my_score"].apply(phenotype)
pheno_bad = ok[ok["my_phenotype"] != ok["phenotype"]]

print("Checked:", len(ok))
print("Score mismatches:", len(score_bad))
print("Phenotype mismatches:", len(pheno_bad))
print(score_bad.head())
print(pheno_bad.head())
print()
print(ok.groupby("phenotype")["cpic_score"].agg(["min", "max", "count"]))


# In[12]:


ind = dp[dp["phenotype"] == "CYP2D6 Indeterminate"]
has_unknown = ind["diplotype"].apply(
    lambda d: any((p not in act) or pd.isna(act[p]) for p in split_dip(d))
)
print("Indeterminate rows with at least one allele that has no activity value:",
      has_unknown.sum(), "of", len(ind))


# In[13]:


freq = freq.rename(columns={"CYP2D6 allele": "allele"})
freq["allele"] = freq["allele"].astype(str).str.strip()
pops = [c for c in freq.columns if c != "allele"]


# In[14]:


m2 = freq.merge(func[["allele", "clinical", "activity_num"]], on="allele", how="left")
no_act = m2[m2["activity_num"].isna()].copy()
no_act["max_freq"] = no_act[pops].max(axis=1)

print("Frequency rows without an activity value:", len(no_act))
print(no_act.sort_values("max_freq", ascending=False)[["allele", "clinical", "max_freq"]].head(15))
print()
print(no_act["clinical"].value_counts(dropna=False))
print()
missing = usable[~usable["allele"].isin(freq["allele"])]["allele"].tolist()
print(len(missing), "alleles have an activity value but are not in the frequency table:")
print(missing)


# In[15]:


import numpy as np

rng = np.random.default_rng(42)

# the 72 alleles that have both a numeric activity value and a frequency
alle = freq.merge(usable[["allele", "activity_num"]], on="allele", how="inner").reset_index(drop=True)
print("Alleles used in the simulation:", len(alle))

N_PER_POP = 5000
frames = []
for pop in pops:
    f = alle[pop].fillna(0).to_numpy()   # blank = allele not reported in that group, treated as 0
    p = f / f.sum()                      # rescale so the usable alleles sum to 1
    i1 = rng.choice(len(alle), size=N_PER_POP, p=p)
    i2 = rng.choice(len(alle), size=N_PER_POP, p=p)
    frames.append(pd.DataFrame({
        "population": pop,
        "allele1": alle["allele"].to_numpy()[i1],
        "allele2": alle["allele"].to_numpy()[i2],
        "act1": alle["activity_num"].to_numpy()[i1],
        "act2": alle["activity_num"].to_numpy()[i2],
    }))

sim = pd.concat(frames, ignore_index=True)
sim["score"] = sim["act1"] + sim["act2"]
sim["phenotype"] = sim["score"].apply(phenotype)
sim["diplotype"] = sim["allele1"] + "/" + sim["allele2"]

print(sim.shape)
print(sim["phenotype"].value_counts())
print()
print((pd.crosstab(sim["population"], sim["phenotype"], normalize="index") * 100).round(1))


# In[16]:


lookup = {}
for d, ph in zip(det["diplotype"], det["phenotype"]):
    a, b = split_dip(d)
    lookup[(a, b)] = ph
    lookup[(b, a)] = ph        # CPIC lists each pair in one order only

sim["cpic_phenotype"] = [lookup.get((a, b)) for a, b in zip(sim["allele1"], sim["allele2"])]

print("Not found in CPIC table:", sim["cpic_phenotype"].isna().sum())
print("Phenotype mismatches:", (sim["cpic_phenotype"] != sim["phenotype"]).sum())
print("Unique diplotypes (order ignored):",
      sim.apply(lambda r: tuple(sorted([r["allele1"], r["allele2"]])), axis=1).nunique())

sim.to_csv("data/simulated_population.csv", index=False)


# In[17]:


ph = pd.read_excel("data/CYP2D6_frequency_table.xlsx",
                   sheet_name="Phenotype frequency", header=None)
print(ph.shape)
print(ph.to_string())


# In[18]:


ours = (pd.crosstab(sim["population"], sim["phenotype"], normalize="index") * 100).round(1)
ours.to_csv("data/simulated_phenotype_percentages.csv")


# In[19]:


ph = pd.read_excel("data/CYP2D6_frequency_table.xlsx",
                   sheet_name="Phenotype frequency", header=1)
ph = ph.rename(columns={ph.columns[0]: "score"})
ph["score_num"] = pd.to_numeric(ph["score"].astype(str).str.replace("≥", "", regex=False),
                                errors="coerce")

indet = ph[ph["score_num"].isna()][pops].iloc[0]
ph = ph.dropna(subset=["score_num"]).copy()
ph["phenotype"] = ph["score_num"].apply(phenotype)

cpic = ph.groupby("phenotype")[pops].sum()
cpic_pct = (cpic / cpic.sum() * 100).T.round(1)   # rescaled to exclude Indeterminate

print("CPIC indeterminate share (%):")
print((indet * 100).round(1))
print()
print("CPIC phenotype % (rescaled):")
print(cpic_pct)
print()
print("Ours:")
print(ours)
print()
print("Ours minus CPIC (percentage points):")
print((ours - cpic_pct[ours.columns]).round(1))


# In[ ]:




