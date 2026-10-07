# Plant CYP450 Structural \& Docking Analysis

Computational structural and docking analysis of plant CYP450 enzymes involved in secondary
metabolite biosynthesis, extended to a pharmacogenomics classifier for human drug metabolism
prediction. Developed as a computational extension of wet-lab molecular cloning work performed
at CSIR-Central Drug Research Institute (CDRI), Lucknow, during an INSA-NASI Summer Research
Fellowship (2025) under Dr. Vineeta Tripathi, Principal Scientist.


## Working sequence: CYP76AH1 (ferruginol synthase) from *Salvia miltiorrhiza*
(UniProt S4UX02; GenBank JX422213 / protein AGN04215.1), selected for its functional and
phylogenetic similarity to the *Eclipta prostrata* CYP450 characterised during the fellowship.

## Background
During the fellowship, a CYP450 gene from *Eclipta prostrata* — involved in wedelolactone
biosynthesis — was sub-cloned into pYES2-NTB (yeast) and pCAMBIA1302 (plant/Agrobacterium)
expression vectors. The actual gene sequence belongs to an ongoing PhD project at the lab and
is not publicly available prior to publication. CYP76AH1 from *Salvia miltiorrhiza* was chosen
as a public working sequence for this computational extension because it belongs to the same
CYP76 family involved in terpenoid secondary metabolite biosynthesis, produces bioactive
compounds (tanshinones) with an analogous pharmacological profile to wedelolactone, and has
extensive published structural and docking literature available for validation.


## Phase 1 — Phylogenetics

**Sequence retrieval** The CYP76AH1 protein sequence was retrieved from NCBI Protein
(AGN04215.1), with identity cross-confirmed against UniProt (S4UX02).

**Homology search.** BLASTp was run against the full NCBI non-redundant (nr) protein database.
Eleven homologs were selected to maximise taxonomic and sequence-identity diversity (rather than
top-score alone), spanning 72–99.6% identity across the Lamiaceae family:


| Accession | Species | % Identity |

|---|---|---|

| AJD25181.1 | *S.miltiorrhiza* | 99.6% |

| KAL1532387.1 | *S. divinorum* | 85.4% |

| WEQ50542.1 | *S. officinalis* | 82.9% |

| AJQ30188.1 | *S. rosmarinus* | 81.5% |

| AMZ03392.1 | *Plectranthus barbatus* | 81.7% |

| A0A1Z3GBS4.1 | *Isodon rubescens* | 80.3% |

| BFV54790.1 | *Isodon japonicus* | 79.1% |

| CAN8716041.1 | *Dracocephalum ruyschiana* | 81.3% |

| UXG91340.1 | *Callicarpa americana* | 75.9% |

| WCR39967.1 | *Scutellaria barbata* | 72.8% |



Note: an *Artemisia annua* homolog was considered per the original project outline but excluded —
A. annua's characterised CYP450s (e.g. CYP71AV1) belong to the CYP71 family, not CYP76, and
returned no meaningful BLASTp hits against this query.


**Multiple sequence alignment.** Performed in Clustal Omega (EBI) on the query plus 11 homologs
(12 sequences total, default parameters).

**Phylogenetic tree.** A Neighbour-Joining tree was constructed in MEGA 12 (1000 bootstrap
replicates, Poisson correction, pairwise deletion), rooted at the most divergent taxon
(*Callicarpa americana*). Topology is biologically consistent: the three *S. miltiorrhiza*
sequences cluster tightly (bootstrap 86–100%), followed by a broader *Salvia* clade
(bootstrap 78–98%), with *Scutellaria* and *Callicarpa* as the most divergent outgroup pair.

![Phylogenetic tree](figures/phylogenetic_tree.png)


**Conserved heme-binding motif.** The canonical cytochrome P450 heme-ligand signature
(FxxGxxxCxG) was located at residues 430–439 of the query (`FGSGRRVCPG`), with the
heme-ligating cysteine at residue 437. This motif — and the cysteine in particular — is
100% conserved across all 12 sequences despite up to \~40% overall sequence divergence,
consistent with strong purifying selection on this catalytically essential residue.

![Heme-binding motif conservation](figures/heme_binding_motif.png)

**Specificity-residue analysis (D301 / V479).** Mao et al. (2020) showed that mutating two
residues in CYP76AH1 — D301→E and V479→F — shifts product specificity from pure ferruginol
toward the broader product profile of its paralog CYP76AH3. Checking these two positions across
the alignment:



| Accession | Species | Residue 301 | Residue 479 |

|---|---|---|---|

| AGN04215.1 (query) | *S. miltiorrhiza* | D | V |

| S4UX02.1 | *S. miltiorrhiza* | D | V |

| AJD25181.1 | *S. miltiorrhiza* | D | V |

| BFV54790.1 | *Isodon japonicus* | D | V |

| AJQ30188.1 | *S. rosmarinus* | E | F |

| WEQ50542.1 | *S. officinalis* | E | L |

| KAL1532387.1 | *S. divinorum* | E | L |

| WCR39967.1 | *Scutellaria barbata* | E | L |

| UXG91340.1 | *Callicarpa americana* | E | L |

| CAN8716041.1 | *Dracocephalum ruyschiana* | E | L |

| A0A1Z3GBS4.1 | *Isodon rubescens* | E | L |

| AMZ03392.1 | *Plectranthus barbatus* | E | L |

![Position 301 alignment across homologs](figures/position_301_alignment.png)
![Position 479 alignment across homologs](figures/position_479_alignment.png)

D301 and V479 co-occur perfectly across the dataset with zero exceptions: only the three
*S. miltiorrhiza* sequences and one *Isodon japonicus* homolog retain both wild-type residues,
while every other genus — including close *Salvia* relatives — has independently drifted to
the alternate pair at both positions simultaneously. This suggests the two residues co-evolve
as a functional unit, and that strict single-product (ferruginol-only) specificity may be
restricted to a narrow clade within the broader CYP76 family.


## Phase 2 — Structure Prediction & Validation (ColabFold/PyMOL)

**Structure prediction.** The CYP76AH1 sequence was submitted to ColabFold (AlphaFold2, MMseqs2
MSA mode) for 3D structure prediction. The top-ranked model achieved high confidence:
**pLDDT = 90.7, pTM = 0.89** (averaged across 3 recycles), with per-residue pLDDT mostly in the
80-95 range across all 5 generated models — indicating a reliably folded core structure, with
only isolated flexible loop regions dropping to lower confidence (50-60).

![ColabFold per-residue confidence (pLDDT)](figures/CYP76AH1_de1fa_plddt.png)
![ColabFold predicted alignment error (PAE)](figures/CYP76AH1_de1fa_pae.png)
![ColabFold MSA sequence coverage](figures/CYP76AH1_de1fa_coverage.png)

**Validation against experimental structures.** The predicted structure was aligned in PyMOL
against two published crystal structures of CYP76AH1 from *Salvia miltiorrhiza*: PDB 5YLW
(apo form) and PDB 7CB9 (in complex with heme and its natural substrate, miltiradiene). The
AlphaFold2 prediction superimposed with excellent agreement onto both:

| Reference structure | RMSD | Atoms aligned |
|---|---|---|
| 5YLW (apo) | 0.919 Å | 3015 |
| 7CB9 (substrate-bound) | 0.908 Å | 2993 |

Sub-1 Å RMSD against both experimental structures confirms the predicted model is structurally
reliable for downstream analysis.

![Structure alignment: ColabFold prediction vs. crystal structures](figures/structure_alignment_colabfold_vs_crystal.png)

**Active site visualization.** Using the substrate-bound structure (7CB9), the heme group
(HEM) and bound miltiradiene substrate (ligand code J6C) were visualized alongside the two
specificity-determining residues identified in Phase 1 (D301, V479). Both residues were
confirmed, by direct residue identity check in PyMOL, to retain the same numbering as the
query sequence (no offset between crystal structure and UniProt/GenBank numbering). Both
residues sit at the edge of the substrate-binding pocket, immediately adjacent to the bound
miltiradiene — a direct structural explanation for why mutating either position
(D301E/V479F) alters the enzyme's product specificity (Mao et al., 2020).

![Active site: heme, substrate, and D301/V479](figures/active_site_D301_V479_heme_substrate.png)


## Phase 3 — Molecular Docking (CB-Dock2)

Three ligands were docked against the AlphaFold2-predicted CYP76AH1 structure using CB-Dock2's
Structure-based Blind Docking mode (AutoDock Vina scoring, automatic cavity detection — no
pocket location specified in advance). Ligand structures were sourced from PubChem as 3D SDF
files.
- **Tanshinone IIA** (PubChem CID 164676) — a downstream pathway product of CYP76AH1
- **Cryptotanshinone** (PubChem CID 160254) — a related tanshinone pathway intermediate
- **Wedelolactone** (PubChem CID 5281813) — the bioactive compound from *Eclipta prostrata*
  linked to the original CDRI wet-lab work

**Headline finding:** all three ligands, docked independently, converged on the exact same
binding cavity (CurPocket C1, volume 6911 Å³) — the same pocket already confirmed in Phase 2
to contain the heme group. This cavity's contact residues include both specificity-determining
residues from Phase 1 (**C437**, the heme-ligating cysteine, and **V479**), plus residues
immediately flanking D301 (D294, T302, N303). This is independent confirmation, via a
completely different computational method, of the active site located structurally in Phase 2.

---

### Tanshinone IIA (PubChem CID 164676)

CYP76AH1's own downstream pathway product. Docked with the **strongest affinity of the three**
ligands tested: **-10.2 kcal/mol**, into CurPocket C1 (volume 6911 Å³), directly contacting
C437 and V479.

![Tanshinone IIA — all detected cavities](docking/results/tanshinone_IIA_all_cavities.png)
![Tanshinone IIA — docking pose in the active site](figures/tanshinone_IIA_docking_pose.png)
![Tanshinone IIA — C1 contact residues](docking/results/tanshinone_IIA_C1_contacts.png)

---

### Cryptotanshinone (PubChem CID 160254)

A related intermediate in the same tanshinone biosynthetic pathway. Docked into the identical
C1 pocket, with Vina score **-9.1 kcal/mol** — intermediate between tanshinone IIA and
wedelolactone, consistent with its structural similarity to tanshinone IIA.

![Cryptotanshinone — all detected cavities](docking/results/cryptotanshinone_all_cavities.png)
![Cryptotanshinone — docking pose in the active site](figures/cryptotanshinone_docking_pose.png)
![Cryptotanshinone — C1 contact residues](docking/results/cryptotanshinone_C1_contacts.png)

---

### Wedelolactone (PubChem CID 5281813)

The bioactive compound from *Eclipta prostrata* connected to the original CDRI wet-lab cloning
work this project extends. Despite originating from a structurally unrelated CYP450 pathway in
a different plant species, wedelolactone still docked into the same C1 pocket, contacting C437
and V479 — but with the **weakest affinity of the three**, **-8.7 kcal/mol**. This is consistent
with wedelolactone being accommodated by the pocket without being a native substrate for this
specific enzyme.

![Wedelolactone — all detected cavities](docking/results/wedelolactone_all_cavities.png)
![Wedelolactone — docking pose in the active site](figures/wedelolactone_docking_pose.png)
![Wedelolactone — C1 contact residues](docking/results/wedelolactone_C1_contacts.png)

---

### Summary

| Ligand | Vina score (kcal/mol) | Cavity volume (Å³) | C437 contact | V479 contact |
|---|---|---|---|---|
| Tanshinone IIA | **-10.2** | 6911 | ✓ | ✓ |
| Cryptotanshinone | **-9.1** | 6911 | ✓ | ✓ |
| Wedelolactone | **-8.7** | 6911 | ✓ | ✓ |

Binding affinity follows a biologically sensible gradient: native pathway compounds
(tanshinone IIA, cryptotanshinone) bind more tightly than a bioactive compound from an
unrelated biosynthetic pathway (wedelolactone), while all three engage the same authentic
catalytic pocket identified independently in Phase 2.




## Status

[x] Phase 1: Phylogenetics

[x] Phase 2: Structure prediction (ColabFold) and comparison to experimental structures

&#x20;     (PDB 5YLW, 7CB9)

[x] Phase 3: Molecular docking (tanshinone IIA, wedelolactone, cryptotanshinone)

[ ] Phase 4: Pharmacogenomics — CYP2D6 metaboliser-phenotype classifier



## References
1.Mao, Y. et al. (2020). Functional Integration of Two CYP450 Genes Involved in
   Biosynthesis of Tanshinones for Improved Diterpenoid Production by Synthetic Biology.
   *ACS Synthetic Biology*, 9(7). https://doi.org/10.1021/acssynbio.0c00136.
2. UniProt: S4UX02 (CYPH1\_SALMI)
3. NCBI: JX422213 / AGN04215.1

