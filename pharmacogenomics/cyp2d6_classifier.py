#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd, numpy as np
from sklearn.model_selection import GroupShuffleSplit

sim = pd.read_csv("data/simulated_population.csv")
sim["dip_key"] = sim.apply(lambda r: "/".join(sorted([r["allele1"], r["allele2"]])), axis=1)

alleles = sorted(set(sim["allele1"]) | set(sim["allele2"]))
X = pd.DataFrame({a: (sim["allele1"] == a).astype(int) + (sim["allele2"] == a).astype(int)
                  for a in alleles})
y = sim["phenotype"]

gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx = next(gss.split(X, y, groups=sim["dip_key"]))
X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

print("Features:", X.shape[1], "| Train:", len(train_idx), "| Test:", len(test_idx))
print("Diplotype overlap:", len(set(sim.iloc[train_idx]["dip_key"]) & set(sim.iloc[test_idx]["dip_key"])))


# In[2]:


from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

print("Test-set diplotypes per class:")
print(sim.iloc[test_idx].groupby("phenotype")["dip_key"].nunique())

rf = RandomForestClassifier(n_estimators=300, class_weight="balanced",
                            random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
pred = rf.predict(X_test)

print()
print("Accuracy:", round(accuracy_score(y_test, pred), 4))
print(classification_report(y_test, pred, digits=3))


# In[3]:


import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay

labels = ["CYP2D6 Poor Metabolizer", "CYP2D6 Intermediate Metabolizer",
          "CYP2D6 Normal Metabolizer", "CYP2D6 Ultrarapid Metabolizer"]
short = ["Poor", "Intermediate", "Normal", "Ultrarapid"]
cm = confusion_matrix(y_test, pred, labels=labels)
print(pd.DataFrame(cm, index=short, columns=short))

fig, ax = plt.subplots(figsize=(6, 5))
ConfusionMatrixDisplay(cm, display_labels=short).plot(ax=ax, cmap="Blues", colorbar=False)
ax.set_title("CYP2D6 phenotype, held-out diplotypes")
plt.tight_layout()
plt.savefig("cyp2d6_confusion_matrix.png", dpi=300)
plt.show()


# In[4]:


fn = pd.read_excel("data/CYP2D6_allele_functionality_reference.xlsx",
                   sheet_name="Allele Function", header=1).iloc[:, [0, 1]]
fn.columns = ["allele", "activity"]
fn["allele"] = fn["allele"].astype(str).str.strip()
fn["act"] = pd.to_numeric(fn["activity"], errors="coerce")

fr = pd.read_excel("data/CYP2D6_frequency_table.xlsx",
                   sheet_name="Allele frequency", header=1)
fr["allele"] = fr.iloc[:, 0].astype(str).str.strip()

used = set(fr["allele"]) & set(fn.loc[fn["act"].notna(), "allele"])
print(len(used), "alleles in the simulation list")
print("Not drawn in the simulation:", sorted(used - set(alleles)))


# In[5]:


test = sim.iloc[test_idx].copy()
test["pred"] = pred
test["correct"] = test["pred"] == test["phenotype"]

top = (test.groupby(["dip_key", "phenotype"])
           .agg(people=("correct", "size"), accuracy=("correct", "mean"))
           .sort_values("people", ascending=False).head(12))
print(top.round(2))
print()
print("Share of test people in the 12 biggest diplotypes:",
      round(top["people"].sum() / len(test), 2))
print()
for a in ["*1", "*2", "*41"]:
    print(a, "| count values in train:", sorted(X_train[a].unique()),
          "| in test:", sorted(X_test[a].unique()))
print()
print("Frequency of *38 in the CPIC table (max over populations):")
print(fr.loc[fr["allele"] == "*38", fr.columns[1:10]].max(axis=1))


# In[6]:


d = (test.groupby("dip_key")
         .agg(people=("correct", "size"), score=("score", "first"),
              truth=("phenotype", "first"), acc=("correct", "mean"))
         .reset_index())
d["truth"] = d["truth"].str.replace("CYP2D6 ", "").str.replace(" Metabolizer", "")

print("Diplotypes:", len(d), "| fully correct:", (d["acc"] == 1).sum(),
      "| fully wrong:", (d["acc"] == 0).sum())
print("Diplotype-level accuracy:", round((d["acc"] > 0.5).mean(), 3))
print()
print("Per class, share of diplotypes correct:")
print(d.groupby("truth")["acc"].agg(["mean", "count"]).round(2))
print()
print("Wrong diplotypes (score, truth):")
print(d[d["acc"] < 0.5].sort_values("people", ascending=False)
        [["dip_key", "score", "truth", "people"]].head(25).to_string(index=False))
print()
print("Scores of wrong diplotypes:", sorted(d[d["acc"] < 0.5]["score"].unique()))


# In[7]:


from sklearn.linear_model import LogisticRegression
from sklearn.metrics import recall_score

classes = ["CYP2D6 Poor Metabolizer", "CYP2D6 Intermediate Metabolizer",
           "CYP2D6 Normal Metabolizer", "CYP2D6 Ultrarapid Metabolizer"]
rows = []
for seed in range(5):
    g = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed)
    tr, te = next(g.split(X, y, groups=sim["dip_key"]))
    for name, model in [
        ("RandomForest", RandomForestClassifier(n_estimators=300, class_weight="balanced",
                                                random_state=42, n_jobs=-1)),
        ("LogisticRegression", LogisticRegression(C=10, class_weight="balanced", max_iter=5000)),
    ]:
        model.fit(X.iloc[tr], y.iloc[tr])
        p = model.predict(X.iloc[te])
        t = sim.iloc[te].assign(ok=(p == y.iloc[te].to_numpy()))
        dip_acc = t.groupby("dip_key")["ok"].mean().gt(0.5).mean()
        rec = recall_score(y.iloc[te], p, labels=classes, average=None, zero_division=0)
        rows.append([seed, name, round((p == y.iloc[te].to_numpy()).mean(), 3),
                     round(dip_acc, 3), *rec.round(3)])

res = pd.DataFrame(rows, columns=["seed", "model", "person_acc", "diplotype_acc",
                                  "recall_Poor", "recall_Inter", "recall_Normal", "recall_Ultra"])
print(res.to_string(index=False))
print()
print(res.groupby("model")[["person_acc", "diplotype_acc", "recall_Poor", "recall_Inter",
                            "recall_Normal", "recall_Ultra"]].agg(["mean", "std"]).round(3).T)
res.to_csv("data/model_comparison_5_splits.csv", index=False)


# In[8]:


from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score

lr = LogisticRegression(C=10, class_weight="balanced", max_iter=5000).fit(X_train, y_train)
p = lr.predict(X_test)
print("Accuracy:", round(accuracy_score(y_test, p), 4))
print(classification_report(y_test, p, digits=3))

test = sim.iloc[test_idx].copy()
test["ok"] = (p == test["phenotype"].to_numpy())
train_counts = X_train.sum()
dd = (test.groupby("dip_key")
          .agg(people=("ok", "size"), acc=("ok", "mean"),
               score=("score", "first"), truth=("phenotype", "first")).reset_index())
dd["rarest_allele_train_rows"] = dd["dip_key"].apply(
    lambda d: min(train_counts[a] for a in d.split("/")))

print("Diplotype-level accuracy:", round((dd["acc"] > 0.5).mean(), 3))
print()
print("Wrong diplotypes:")
print(dd[dd["acc"] <= 0.5].sort_values("people", ascending=False)
        [["dip_key", "score", "truth", "people", "rarest_allele_train_rows"]]
        .head(20).to_string(index=False))
print()
print("Median training rows of the rarest allele, correct vs wrong diplotypes:")
print(dd.groupby(dd["acc"] > 0.5)["rarest_allele_train_rows"].median())


# In[9]:


fn = pd.read_excel("data/CYP2D6_allele_functionality_reference.xlsx",
                   sheet_name="Allele Function", header=1).iloc[:, [0, 1]]
fn.columns = ["allele", "activity"]
fn["allele"] = fn["allele"].astype(str).str.strip()
act_map = dict(zip(fn["allele"], pd.to_numeric(fn["activity"], errors="coerce")))

coef = pd.DataFrame(lr.coef_, index=lr.classes_, columns=X.columns).T
coef["activity"] = [act_map[a] for a in coef.index]
print("Correlation between each class's allele weights and the allele's CPIC activity value:")
print(coef.corr()["activity"].round(2))


# In[10]:


import shap
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression

lr = LogisticRegression(C=10, class_weight="balanced", max_iter=5000).fit(X_train, y_train)

exp = shap.LinearExplainer(lr, X_train)(X_test)
vals = np.array(exp.values)
print("SHAP array shape:", vals.shape, "| classes:", list(lr.classes_))


# In[11]:


import shap
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression

lr = LogisticRegression(C=10, class_weight="balanced", max_iter=5000).fit(X_train, y_train)

exp = shap.LinearExplainer(lr, X_train)(X_test)
vals = np.array(exp.values)
print("SHAP array shape:", vals.shape, "| classes:", list(lr.classes_))


# In[12]:


fn = pd.read_excel("data/CYP2D6_allele_functionality_reference.xlsx",
                   sheet_name="Allele Function", header=1).iloc[:, [0, 1]]
fn.columns = ["allele", "activity"]
fn["allele"] = fn["allele"].astype(str).str.strip()
act_map = dict(zip(fn["allele"], pd.to_numeric(fn["activity"], errors="coerce")))

short = {"CYP2D6 Poor Metabolizer": "Poor", "CYP2D6 Intermediate Metabolizer": "Intermediate",
         "CYP2D6 Normal Metabolizer": "Normal", "CYP2D6 Ultrarapid Metabolizer": "Ultrarapid"}

fig, axes = plt.subplots(1, 4, figsize=(16, 5))
for k, cls in enumerate(lr.classes_):
    m = pd.Series(np.abs(vals[:, :, k]).mean(axis=0), index=X.columns).sort_values(ascending=False).head(8)
    print(short[cls], "- top alleles (mean |SHAP|, CPIC activity):")
    print(pd.DataFrame({"mean_abs_shap": m.round(3), "activity": [act_map[a] for a in m.index]}))
    print()
    m.sort_values().plot.barh(ax=axes[k])
    axes[k].set_title(short[cls])
    axes[k].set_xlabel("mean |SHAP|")
plt.tight_layout()
plt.savefig("cyp2d6_shap_top_alleles.png", dpi=300)
plt.show()


# In[13]:


top = ["*1", "*2", "*10", "*4", "*5", "*41", "*1x2", "*17"]
c = pd.DataFrame(lr.coef_, index=[short[k] for k in lr.classes_], columns=X.columns)[top].round(2)
c.loc["CPIC activity"] = [act_map[a] for a in top]
print(c.T)


# In[ ]:




