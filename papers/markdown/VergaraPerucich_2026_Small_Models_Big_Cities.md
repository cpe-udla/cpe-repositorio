---
author: VergaraPerucich
year: 2026
title: Small Models Big Cities A Low-Cost AI Pipeline for Urban Regulatory Document Analysis in Metropolitan Planning
source: VergaraPerucich_2026_Small_Models_Big_Cities.pdf
---

# Small Models Big Cities A Low-Cost AI Pipeline for Urban Regulatory Document Analysis in Metropolitan Planning

**Author:** VergaraPerucich
**Year:** 2026
**Source:** VergaraPerucich_2026_Small_Models_Big_Cities.pdf

---

## Content

### Page 1

Article

Small Models, Big Cities: A Low-Cost AI Pipeline for Urban
Regulatory Document Analysis in Metropolitan Planning
Francisco Vergara-Perucich
Núcleo de Investigación Centro Producción del Espacio, Universidad de Las Américas, Manuel Montt 948,
Providencia, Santiago 7500975, Chile; jvergara@udla.cl

Abstract
Background: Urban planning documents at metropolitan scale typically demand large,
cloud-hosted language models that limit their adoption in Global South contexts. This
study deploys Moondream, a 1.7-billion-parameter vision-language model (VLM) runnable
locally via Ollama, for extracting geographic knowledge from Planes Reguladores
Comunales (PRCs) across 29 processed Gran Santiago municipalities. The pipeline combines native PDF text extraction, keyword-based multi-label classification across six thematic axes, and VLM-based optical character recognition and cartographic interpretation.
Results: The pipeline processes 2289 PRC articles in 4.3 min at an estimated energy cost
of 0.000866 kWh and zero marginal monetary cost. Zoning (53.3%) and land use (43.1%)
dominate PRC content, while social housing provisions appear in only 4.0% of articles;
normative gap analysis identifies five municipalities where social housing is entirely absent
from regulatory text. A comparative evaluation of Moondream against keyword baseline
on an 88-article validation sample yields macro-F1 = 0.355 and mean Cohen’s κ = 0.004,
confirming that generalist VLMs require domain fine-tuning for specialized legal text. It is
argued that the cost asymmetry between industrial-scale and small-model approaches constitutes an epistemic asymmetry with direct consequences for the geographic distribution
of urban data infrastructure.
Keywords: urban digitalization; city management; smart planning tools; regulatory analytics;
GeoAI; small language models; Chile; Gran Santiago; zoning; regulatory documents

1. Introduction

Academic Editors: Cezar Scarlat
and Alexandru-Ionuţ Petrişor
Received: 30 April 2026
Revised: 18 June 2026
Accepted: 20 June 2026
Published: 25 June 2026
Copyright: © 2026 by the author.
Licensee MDPI, Basel, Switzerland.
This article is an open access article
distributed under the terms and
conditions of the Creative Commons

Urban regulatory documents—zoning codes, land use ordinances, planning
regulations—encode significant geographic knowledge: territorial boundaries, permissible
densities, mobility infrastructure norms, environmental constraints, and social housing
mandates. Recent advances in geographic artificial intelligence (GeoAI) have accelerated
the capacity to extract structured knowledge from such corpora at scale [1–3]. However,
most published GeoAI pipelines for regulatory knowledge extraction depend on models
with hundreds of billions of parameters, accessed through cloud APIs that impose pertoken pricing, latency constraints, and data exposure risks. While the absolute cost of
any single inference run may appear modest, three compounding factors create a structural asymmetry for Latin American urban research. First, for students and independent
researchers operating without externally funded compute budgets, the marginal cost of
token-based billing accumulates rapidly across the iterative cycles of method development
(prompt refinement, schema testing, corpus expansion). Second, municipal regulatory

Attribution (CC BY) license.

Urban Sci. 2026, 10, 352

https://doi.org/10.3390/urbansci10070352

### Page 2

Urban Sci. 2026, 10, 352

2 of 19

documents frequently contain place-specific information whose transmission to external servers raises data sovereignty concerns increasingly recognized in regional digital
governance debates [4,5]. Third, the territories most in need of systematic regulatory
analysis—fragmented metropolitan areas with dozens of autonomous municipalities, incomplete digital infrastructure, and high intra-metropolitan inequality—are also those
where cloud-API-dependent workflows are most fragile, contingent on stable connectivity
and payment infrastructure. These conditions constitute not an insurmountable technical
obstacle, but a structural asymmetry in the conditions under which urban knowledge can
be produced.
This paper addresses that gap by evaluating the capabilities and limitations of a small,
locally-deployed vision-language model (VLM) when applied to a real metropolitan-scale
regulatory corpus. A hybrid pipeline for geographic knowledge extraction from Plans
Reguladores Comunales (PRCs) is presented, which operates entirely on consumer-grade
hardware using Moondream, a 1.7-billion-parameter VLM deployable via Ollama. The
pipeline is tested against the same corpus of 29 PRCs from the Gran Santiago metropolitan
area previously analyzed with larger models in a companion study [6].
This paper serves as the methodological counterpart to the companion study [6],
which used a fine-tuned large model (DeepSeek-R1) to demonstrate how communal zoning
ordinances in Santiago reproduce socio-spatial inequality. While retaining the same corpus,
thematic axes, and normative gap logic, this study inverts the analytical focus: instead of
mapping urban inequality, it interrogates the material conditions required to produce such
an analysis. Specifically, it tests whether identical substantive patterns can be recovered using small, locally deployable infrastructure, thereby avoiding the industrial-scale compute
requirements of the earlier study. Additionally, this pipeline extends the previous text-only
design by incorporating visual processing for OCR and embedded map interpretation.
Ultimately, the two studies are complementary: the first establishes the substantive finding,
while this one evaluates the infrastructural conditions—and epistemic consequences—of
reproducing that knowledge at scale.
The contributions are threefold:

•

•

•

Methodological: A fully reproducible, open-source pipeline combining native PDF text
processing, keyword-based multi-label article classification, and VLM-based visual
interpretation (OCR and map reading), designed for deployment on consumer-grade
hardware without cloud dependencies.
Empirical: Normative gap indices quantifying the distribution of regulatory attention
across six thematic axes—zoning, land use, mobility, participation, sustainability, and
social housing—across 29 Gran Santiago municipalities.
Evaluative: A comparative assessment of Moondream’s text classification performance
against keyword baselines, establishing an empirical baseline for small VLM capabilities on specialized urban regulatory text and documenting both their strengths
(visual document understanding) and current limitations (text classification without
domain fine-tuning).

This work is positioned as a feasibility study for affordable research infrastructure
in the Global South. The question addressed is not whether small models outperform
large ones—they do not—but whether they offer sufficient utility to enable meaningful
metropolitan-scale analysis on local hardware, and what the boundaries of that utility
are. These questions—developed in Section 2.3 through the conceptual framework of
computational sovereignty and epistemic asymmetry—situate the technical choices of this
paper within a wider critical-geographic debate: who has access to the tools that read
the city?

https://doi.org/10.3390/urbansci10070352

### Page 3

Urban Sci. 2026, 10, 352

3 of 19

2. Conceptual Framework
2.1. GeoAI and Geographic Knowledge Extraction
Geographic Artificial Intelligence (GeoAI) has emerged as a productive intersection
between geo-spatial methods and machine learning, encompassing tasks from place name
recognition (geoparsing) to spatial reasoning, geographic question answering, and the
encoding of place-specific semantic content [1]. Mai et al. [2] have advanced the conceptualization of place encoding—the representation of geographic entities in high-dimensional
embedding spaces that preserve spatial relationships—while Hu et al. [3] have demonstrated the potential of large language models for automated geospatial knowledge extraction from heterogeneous text sources.
Within urban planning specifically, a growing body of work applies natural language
processing to zoning documents, planning regulations, and policy texts [7,8]. These approaches share a reliance on large, pretrained transformer models (BERT, RoBERTa, GPT
variants) that capture domain-specific semantic nuances but require either substantial
fine-tuning datasets or API-mediated inference. The emergence of VLMs—multimodal
models capable of processing both images and text—extends this capacity to the many
regulatory documents that exist primarily as scanned PDFs or contain embedded cartographic material. Notably, the international cartographic and geoinformatics community
has increasingly engaged with AI-driven geographic analysis, as reflected in initiatives
such as the ICA Commission on AI in Cartography [9] and the GeoAI research agenda promoted through the International Cartographic Association [10]. These efforts underscore
the growing relevance of machine learning for cartographic interpretation—a task directly
addressed in this study through VLM-based map reading.
Parallel to these LLM-based developments, urban planning scholarship retains a
substantial repertoire of low-cost text analysis approaches that predate—and continue to
coexist with—generative AI. Dictionary-based content analysis [11], rule-based information
extraction, and topic modeling via Latent Dirichlet Allocation [12] have been applied to
planning documents to map thematic emphasis, characterize regulatory vocabularies, and
detect institutional change [13,14]. More recently, lightweight multilingual embedding
models under 500 MB in size enable semantic similarity computation without cloud dependencies [15]. These methods share an interest in deterministic, auditable, and low-cost
pipelines but cannot process the visual and cartographic content that constitutes a substantial share of any planning regulatory corpus. The pipeline presented here is best understood
as a hybrid extension of this tradition: it preserves the auditability and reproducibility of
keyword and rule-based approaches for structured legal text, while introducing local VLM
inference precisely where deterministic methods are structurally unavailable—namely,
the interpretation of embedded maps and the optical character recognition of scanned
regulatory annexes.
The rapid proliferation of language models necessitates a brief taxonomic clarification
relevant to this study. Large Language Models (LLMs) typically refer to transformerbased architectures with parameter counts exceeding 70 billion (e.g., GPT-4 at an
estimated >1 trillion parameters, Llama 2-70B, DeepSeek-R1 at 671B), requiring enterprisegrade GPU clusters or cloud API access for inference. Small Language Models
(SLMs)—sometimes termed “edge models” or “on-device models”—occupy a parameter range of approximately 0.5 to 7 billion parameters and are designed for deployment
on consumer hardware [16,17]. Examples include Phi-2 (2.7B), TinyLlama (1.1B), and
Moondream (1.87B).
A distinct subcategory relevant to this study is the Vision-Language Model (VLM): a
multimodal architecture that processes both textual and visual inputs. VLMs exist across
the size spectrum—from GPT-4V (large, cloud-only) to LLaVA-7B (medium) to Moondream

https://doi.org/10.3390/urbansci10070352

### Page 4

Urban Sci. 2026, 10, 352

4 of 19

(small, locally deployable). The critical distinction for Global South research contexts is not
model quality in the abstract but the deployment threshold: the minimum hardware and
economic requirements for running the model. Moondream’s 1.87B parameters (1.7 GB on
disk) place it at the lower end of the VLM spectrum, enabling inference on machines with
8–16 GB of RAM and no dedicated GPU—a specification met by consumer laptops widely
available in urban research settings across Latin America.
This taxonomic positioning is important because it clarifies the experimental design:
the study does not evaluate whether Moondream is competitive with GPT-4V for legal text
classification (it is not), but whether a model at the accessible end of the VLM spectrum
can perform useful geographic knowledge extraction tasks within a constrained-resource
research workflow.
2.2. Plans Reguladores Comunales as Geographic Artefacts
Plans Reguladores Comunales (PRCs) are the primary instrument of land use regulation in Chilean urban governance. Each of the 346 municipalities (comunas) of Chile is
empowered under the Ley General de Urbanismo y Construcciones (LGUC) to produce its
own PRC, which determines permissible uses of soil, building height and density limits,
setback requirements, and public space designations. In the Gran Santiago metropolitan area, 34 municipalities maintain independent PRCs, creating a fragmented but interconnected regulatory landscape that governs one of Latin America’s most economically
concentrated cities.
From a GeoAI perspective, PRCs are geographic artefacts of the first order: they encode the legal production of urban space through thousands of articles, maps, and tables
that translate political decisions into territorial norms. Each PRC document corresponds to
a single municipality and typically combines normative text (regulatory articles organized
by chapter) with cartographic annexes (zoning maps, land use plans, road network diagrams). The systematic analysis of these documents across municipal boundaries enables
comparative urban research at metropolitan scale—illuminating which regulatory topics
receive attention in wealthy versus peripheral municipalities, where normative gaps persist,
and how regulatory language reflects or obscures social priorities.
The corpus used in this study comprises the PRCs of 29 Gran Santiago municipalities
for which digital (PDF) copies were available, totaling approximately 170 MB of document
data and spanning between 24 and 488 pages per document.
2.3. Computational Sovereignty and Epistemic Asymmetry
Critical geography and science and technology studies have long recognized that
data infrastructures are not neutral: their geographic distribution reflects and reproduces
existing power asymmetries [18,19]. The emergence of large language models as a new
layer of knowledge infrastructure reproduces this dynamic: the capacity to extract, classify,
and interpret geographic knowledge from text is now substantially mediated by a small
number of corporations operating hyperscale data centers predominantly located in the
United States and Europe.
For urban researchers in Latin America, this creates what is termed an epistemic
asymmetry: the cities most in need of systematic, large-scale regulatory analysis are
precisely those where the economic and technical conditions for cloud-API-dependent
research are most constrained. The right to the city [20,21] implies not only access to urban
space but access to the analytical tools through which urban space is read, classified, and
acted upon.
Small, locally-deployed models do not fully resolve this asymmetry—they require
hardware that is itself unevenly distributed—but they substantially reduce the marginal

https://doi.org/10.3390/urbansci10070352

### Page 5

Urban Sci. 2026, 10, 352

5 of 19

cost of inquiry and eliminate the data sovereignty constraints associated with transmitting
sensitive municipal documents to external servers. In this sense, the present study is
as much a contribution to the political economy of urban data infrastructure as it is to
methodological GeoAI. Documenting what small models can and cannot do on real research
tasks—rather than only reporting results from frontier models—is a necessary step toward
building locally-controlled analytical capacity in urban science.
Synthesizing the three preceding strands—the technical capacities of GeoAI and its
low-cost alternatives (Section 2.1), the institutional specificity of the Chilean PRC as a
geographic artefact (Section 2.2), and the political economy of computational sovereignty
and epistemic asymmetry (Section 2.3)—yields the conceptual scaffolding of this paper.
The PRC corpus is treated simultaneously as a technical object amenable to multimodal
extraction, as a territorial instrument through which the metropolitan area is legally produced, and as a test case for alternative research infrastructure in which the conditions of
analysis are themselves at stake. What follows in Sections 3–5 should be read at all three
levels: as a methodological proposal, as an empirical mapping of regulatory attention across
Gran Santiago, and as evidence on the boundaries of affordable urban GeoAI in a Global
South context.

3. Methodology
3.1. Corpus and Study Area
The corpus consists of 30 PDF documents from municipalities of the Gran Santiago metropolitan area (Figure 1) accessed from the same archive used in the companion
Urban Science study [6]. Twenty-nine were successfully processed as standard PDFs; one
document (PRC El Bosque) was stored in .doc format and excluded from the PDF-based
pipeline. Each PDF corresponds to a single municipality and contains the complete normative text of its PRC. The 29 processed municipalities span the full socioeconomic gradient of the metropolitan area, from high-income eastern municipalities (Las Condes,
Vitacura, Providencia) to peripheral western and southern districts (La Pintana, Pudahuel,
Cerro Navia).

Figure 1. Gran Santiago metropolitan area and its municipal distribution.

https://doi.org/10.3390/urbansci10070352

### Page 6

Urban Sci. 2026, 10, 352

6 of 19

All 29 processed documents contain native (selectable) text and were extracted
accordingly via PyMuPDF, without requiring OCR. Individual pages with fewer than
30 characters of text were flagged as map or diagram pages for optional visual processing
by Moondream. Documents range from 24 to 488 pages, totaling approximately 170 MB of
PDF data.
3.2. Technical Stack
Figure 2 summarizes the end-to-end architecture of the pipeline, from raw PRC PDFs
through to validation; each component is described in detail in the remainder of this section.
Stages that invoke the Moondream vision-language model are distinguished from the
deterministic (keyword- and rule-based) stages.

Figure 2. Architecture of the low-cost geographic knowledge extraction pipeline. PRC PDFs
are processed sequentially by four modules (pdf_processor.py, classifier.py, gap_analyzer.py, and
validator.py). Grey-colored boxes denote stages that invoke the Moondream vision-language model
(Tasks 3 and 4); black boxes denote deterministic keyword- and rule-based stages.

The pipeline runs entirely on local hardware (tested on a MacBook Pro with Apple
M-series Silicon, 16 GB unified memory) with no cloud API dependencies:

•
•

PDF extraction: PyMuPDF (fitz) v1.27, with page-level text density detection for
automatic classification of map vs. text pages
VLM: Moondream 2 (vikhyatk/moondream2, 1.87 billion parameters, 1.7 GB on disk),
a multimodal vision-language model based on a SigLIP visual encoder and a Phi-1.5
language backbone, accessed via Ollama v0.18 REST API (localhost:11434). Moondream was designed for efficient on-device deployment and supports both image
captioning and visual question answering tasks. No fine-tuning or domain adaptation was applied; the model was used with default Ollama inference parameters
(temperature: 0.0, num_predict: 80 tokens for classification tasks, unlimited for OCR
and map description). Three characteristics motivated its selection from the available small VLM ecosystem. First, parameter efficiency: at 1.87B parameters and
1.7 GB on disk, Moondream sits at the lower bound of the deployable multimodal
VLM range, providing the most conservative test of the minimal-hardware premise
of this study. Second, Ollama integration: Moondream is natively supported by

https://doi.org/10.3390/urbansci10070352

### Page 7

Urban Sci. 2026, 10, 352

7 of 19

•
•

Ollama, which abstracts backend differences (CUDA, MLX, CPU) and provides a stable REST interface, dramatically reducing deployment friction for researchers without
machine-learning engineering expertise. Third, visual grounding via SigLIP: Moondream’s encoder is a SigLIP variant optimized for fine-grained visual recognition in
document-like images, directly relevant to the cartographic content of PRC corpora.
The trade-offs of this choice—limited textual context capacity, English-centric pretraining, and absence of domain fine-tuning—are documented in Sections 4.4 and 5.3.
Classification: Keyword-based multi-label classification (primary method) + Moondream text generation (validation comparison)
Computational environment: Python 3.14, pandas 3.0, scikit-learn 1.8, no GPU required

Total pipeline runtime for 29 municipalities: 4.3 min for the full keyword classification of 2289 articles, plus approximately 7 min for the Moondream validation sample
(88 completed responses out of 286 attempted, with a 300-s timeout per request).
3.3. Four Tasks for Moondream
The pipeline deploys Moondream for four distinct geographic knowledge extraction
tasks, leveraging its multimodal capabilities where rule-based alternatives are unavailable:

•

•

•

•

Task 1—Native Text Extraction: PyMuPDF extracts native text from PDF pages with
text density above 30 characters/page. Pages with fewer characters are flagged for
visual processing. This task does not use Moondream; it serves as the foundation for
the keyword classification pipeline.
Task 2—OCR Fallback: For low-density pages (potential scans or diagrams), Moondream receives the page rendered as a 150-DPI PNG image and is prompted in Spanish
to transcribe all visible text, preserving article numbering and document structure.
This task exploits Moondream’s core multimodal capability: understanding both
spatial layout and textual content in document images.
Task 3—Article Classification (Validation Comparison): For a random sample of approximately 10 articles per municipality (286 total targeted, 88 successfully completed),
Moondream is asked to classify the article according to six thematic axes, responding
in JSON list format. This provides comparative data against the keyword classifier.
The purpose is not to use Moondream as the primary classifier but to establish an empirical baseline for what a generalist small VLM can achieve on specialized legal-text
classification without domain fine-tuning.
Task 4—Map Interpretation: Pages identified as cartographic (low text, high image
content) are passed to Moondream with a prompt requesting a brief description of
the map type, represented area, and visible legend categories. This yields qualitative
descriptions of zoning plans, land use maps, and street network diagrams embedded
in PRCs—content that would be entirely absent from text-only processing pipelines.

3.4. Six Thematic Axes
Following the thematic structure of the companion Urban Science [6] study, articles
are classified into six axes representing the principal regulatory dimensions of Chilean
PRCs presented in Table 1.
Each article may be assigned to multiple axes (multi-label classification). The keyword
classifier assigns an axis if any of its associated terms appear in the article text; Moondream
is asked to produce an equivalent multi-label JSON list for the validation sample.
A note on the choice of keyword classification as the primary method is warranted.
Chilean PRCs are highly structured legal documents that follow standardized templates
established by the Ministerio de Vivienda y Urbanismo (MINVU). Their regulatory vocabulary is constrained and formulaic: articles addressing zoning consistently use terms

https://doi.org/10.3390/urbansci10070352

### Page 8

Urban Sci. 2026, 10, 352

8 of 19

like “zona” and “uso permitido,” while social housing provisions invariably reference
“SERVIU” or “vivienda social.” This structural regularity means that keyword matching,
while unable to capture semantic nuance, provides a deterministic and reproducible baseline that is well-suited to the lexical properties of the corpus. Keyword labels are treated
as a silver standard—not a ground truth, but a transparent and auditable reference point
against which VLM performance can be measured. The limitations of this choice (missed
synonyms, inability to detect implicit regulatory content) are addressed in Section 5.3.
Table 1. Spanish key terms drawn from planning document examples (M1.1, JV1.2, M2.1), their
corresponding thematic labels in Spanish, and the urban planning axis each belongs to.

Example Key Terms

Spanish Label

Axis

zona, subzona, uso permitido

Zonificacion y usos de suelo

zoning

constructibilidad, rasante, densidad

Edificacion, densidad y altura

land_use

vialidad, ciclovia, estacionamiento

Movilidad, vialidad y transporte

mobility

consulta, vecinos, audiencia

Participacion ciudadana

participation

areas verdes, sustentabilidad

Sustentabilidad ambiental

sustainability

SERVIU, vivienda economica, subsidio

Vivienda social

social_housing

3.5. Normative Gap Index
To quantify the relative distribution of regulatory attention across the metropolitan
area, a normative gap index is computed for each municipality-axis combination. This
metric captures the degree to which a municipality’s PRC under-represents a given thematic
axis relative to the metropolitan average, enabling systematic comparison of regulatory
priorities across the 29 municipalities.
The following variables are defined for each municipality m and thematic axis a:

•
•
•

n_articles(m,a): Number of articles in municipality m assigned to axis a
freq(m,a): Normalized frequency = n_articles(m,a)/total_articles(m)
metro_mean(a): Mean freq(m,a) across all 29 municipalities
The gap index is then computed as:
gap_index(m,a) = 1 − (freq(m,a)/metro_mean(a)), clipped to [0, 1]

where gap_index = 0 indicates that the municipality is at or above the metropolitan average
for axis a, and gap_index = 1 indicates complete absence of articles classified under that
axis. The clipping to [0, 1] prevents negative values for municipalities that exceed the
metropolitan mean. This formulation follows the normative gap analysis methodology of
the companion Urban Science (2025) study.
It is acknowledged that this index is sensitive to corpus size: municipalities with very
few total articles (e.g., La Granja with 6 articles) may exhibit extreme gap index values
driven by small denominators. Where gap_index = 1.0, this indicates zero articles classified
under the axis in question, which is an unambiguous finding regardless of corpus size. For
intermediate values, readers should consider the raw article counts reported alongside the
index when interpreting results.
3.6. Validation Protocol
To evaluate the comparative classification behavior of the keyword method and
the VLM, a random sample of approximately 10 articles per municipality was selected
(286 total targeted). For each sampled article, both the keyword classifier and Moondream

https://doi.org/10.3390/urbansci10070352

### Page 9

Urban Sci. 2026, 10, 352

9 of 19

independently produce multi-label axis assignments. We then report per-axis and aggregate macro-averaged F1 score, precision, recall, and Cohen’s kappa (Moondream vs.
keyword baseline).
Of the 286 targeted Moondream classification requests, 88 returned valid responses
(30.8% completion rate). The remaining 198 requests either timed out (exceeded the
300-s timeout threshold) or returned empty/malformed responses. This high attrition
rate—approximately 69% of requests—is itself an important finding rather than a mere
technical nuisance, and it is discussed in detail in Section 5.2, where corresponding mitigation strategies (article segmentation, prompt simplification, and length-based pre-filtering)
are proposed for future deployments of this pipeline. The timeout behavior is attributable
to the architectural constraints of small VLMs: Moondream’s 1.87B-parameter language
backbone has a limited context window and generation capacity, and when confronted with
long, syntactically complex legal articles (some exceeding 500 words of dense regulatory
Spanish), the model enters extended generation loops that exceed practical time limits. This
is a known limitation of small language models when processing domain-specific text that
exceeds their effective context capacity [17].
The validation sample was limited by Moondream’s completion rate rather than by
design. It is recognized that 88 articles, while sufficient for aggregate metric estimation,
provide limited statistical power for per-axis evaluation, particularly for low-prevalence
axes (participation: 9 keyword-positive articles in sample; social_housing: 3). Future
work should incorporate a human-annotated gold standard to provide an independent
reference beyond the keyword silver standard and to resolve any length-based selection
bias introduced by the differential completion rate.

4. Results
4.1. Corpus Processing
The pipeline successfully processed 29 of 30 available PDF documents. Each PDF
corresponds to a single municipality and contains the full normative text of its PRC.
Extraction statistics are summarized in Table 2.
Table 2. Corpus extraction summary.

Value

Statistic

29

Municipalities processed

100% of documents

Native text coverage

2289

Total articles extracted

79 (SD = 94)

Mean articles per PRC

6 (La Granja)–488 (Providencia)

Min–max articles per PRC

4.3 min

Pipeline runtime (full corpus)

0.000866 kWh

Energy consumed

The article segmentation algorithm—based on Spanish legal article markers
(Articulo N, Art. N)—identified between 6 and 488 articles per PRC, with a mean of
79 and high standard deviation (SD = 94), reflecting substantial variation in document
length and regulatory complexity across the metropolitan area. Providencia (488 articles)
and Santiago (199) are the most extensively codified municipalities, while La Granja
(6 articles) and Cerro Navia (10 articles) have the most compact PRCs.

https://doi.org/10.3390/urbansci10070352

### Page 10

Urban Sci. 2026, 10, 352

10 of 19

4.2. Keyword Classification Coverage
Classification coverage is defined as the proportion of extracted articles assigned
to each thematic axis by the keyword classifier. Because articles may be assigned to
multiple axes (multi-label classification), coverage percentages sum to more than 100%.
Table 3 presents the results.
Table 3. Keyword classification coverage per axis (29 municipalities, 2289 articles).

% of Total

N Clauses

Axis

53.30%

1221

zoning

43.10%

986

land_use

33.30%

762

mobility

32.00%

732

sustainability

8.40%

193

participation

4.00%

91

social_housing

These figures reflect the character of Chilean PRCs as primarily zoning and land-use
instruments: over half of all articles (53.3%) contain explicit reference to zones, plots,
or permitted uses, and 43.1% address building parameters (density, height, setbacks).
Participation and social housing provisions are strikingly underrepresented, appearing in
8.4% and 4.0% of articles respectively—a finding consistent with the companion Urban
Science (2025) study’s characterization of Chilean PRCs as technocratic documents that
systematically marginalize social and participatory dimensions of urban regulation.
4.3. Normative Gap Indices
The normative gap index (defined in Section 3.5) quantifies the relative absence of
regulatory attention to each thematic axis within each municipality, compared to the
metropolitan average. A gap index of 0 indicates that the municipality meets or exceeds
the metropolitan mean frequency for that axis; a value approaching 1.0 indicates severe
under-representation; and a value of exactly 1.0 indicates complete absence (zero articles
classified under the axis). Table 4 presents the municipalities with the highest gap indices.
Three key findings emerge from the gap analysis:

•

•

Social housing is absent from the regulatory text of five municipalities: Cerro
Navia, Independencia, La Granja, La Reina, and Puente Alto—a geographically diverse set spanning peripheral working-class districts (Cerro Navia, La Granja) and
mid-income municipalities (Puente Alto, La Reina)—contain zero PRC articles with
explicit social housing keywords. This suggests a significant normative gap in the
regulatory instrument most directly controlling housing development, though it is
noted that social housing policy in Chile operates through multiple institutional channels beyond the PRC (notably SERVIU programs and the MINVU housing subsidy
system), so the absence from PRC text does not necessarily imply absence of social
housing policy at the municipal level.
Participation norms are concentrated in specific municipalities: Conchali and Pudahuel, both relatively lower-income peripheral municipalities, exhibit complete
absence of participation provisions in their PRC text, while municipalities with more
extensive PRCs show higher coverage. This asymmetry is consistent with the socioeconomic gradient of civic capacity documented in the urban sociology literature [21],
though the relationship between PRC length and participation coverage requires
further investigation.

https://doi.org/10.3390/urbansci10070352

### Page 11

Urban Sci. 2026, 10, 352

11 of 19

•

Environmental sustainability provisions show substantial intra-metropolitan variance:
Penalolen (gap = 1.0) and several western municipalities (Renca, Quilicura) exhibit
severe sustainability gaps, while the metropolitan mean for sustainability (32.0% of
articles) masks significant variation across the study area.

Table 4. Top normative gaps by axis (municipalities with gap_index ≥ 0.75).

Gap Index

N Clauses

Municipality

Axis

1

0

Cerro Navia

social_housing

1

0

Independencia

1

0

La Granja

1

0

La Reina

1

0

Puente Alto

1

0

Conchali

1

0

Pudahuel

0.874

1

Quinta Normal

0.842

1

Renca

0.735

3

Recoleta

1

0

Peñalolen

0.795

4

Renca

0.723

3

Quilicura

participation

sustainability

4.4. Moondream Classification Performance
The VLM validation sample targeted approximately 10 articles per municipality
(286 total). Of these, 88 returned valid Moondream responses (30.8% completion rate),
providing a direct comparison between Moondream and keyword-based classification on
the same texts. The high attrition rate (69.2%) is itself a finding of practical significance: it
reflects the constraints of small VLM architectures when processing long, domain-specific
legal text, as discussed in Section 3.6.
Two systematic patterns characterize Moondream’s classification behavior:
1.

2.

Over-inclusive labeling: Moondream tends toward high recall but low precision,
particularly for the zoning axis (as in Table 5: recall = 1.0, precision = 0.483). The model
frequently assigns multiple axes to a single article, including axes not supported by the
keyword classifier. This pattern is consistent with the behavior of generalist language
models that lack domain-specific calibration: without exposure to labeled Chilean
legal text, Moondream cannot distinguish between thematic relevance and incidental
keyword co-occurrence.
Severe underperformance on low-prevalence axes: For participation (F1 = 0.087) and
social_housing (F1 = 0.050), Moondream’s predictions show near-random agreement
with keyword labels (kappa approaching or below zero). These are also the axes
with the smallest support in the validation sample (9 and 3 keyword-positive articles,
respectively), compounding the statistical uncertainty.

The near-zero mean Cohen’s kappa (0.004) indicates that agreement between Moondream and the keyword classifier is essentially at chance level across the six axes. This
result should be interpreted carefully: it does not necessarily mean that Moondream’s labels
are wrong—it means they are uncorrelated with keyword labels. Both methods may be
capturing different aspects of the text, and without a human-annotated gold standard, it is

https://doi.org/10.3390/urbansci10070352

### Page 12

Urban Sci. 2026, 10, 352

12 of 19

not possible to determine which method better approximates the “true” thematic classification. It can be concluded that a generalist 1.87B-parameter VLM, without fine-tuning, does
not replicate the classification decisions of a domain-specific keyword system on Chilean
regulatory text.
Table 5. Moondream vs. Keyword classification metrics (N = 88 validation articles).

Cohen’s κ

F1

Recall

Precision

Axis

0.021

0.651

1

0.483

zoning

−0.029

0.429

0.581

0.34

land_use

−0.002

0.471

0.556

0.408

mobility

0.138

0.444

0.483

0.412

sustainability

−0.093

0.087

0.222

0.054

participation

−0.014

0.05

0.333

0.027

social_housing

0.004

0.355

0.529

0.287

Macro

4.5. Map Interpretation
Moondream’s map interpretation capability was tested on all pages identified as
cartographic within the corpus. This task represents the clearest value-add of the VLM
approach, as no rule-based alternative exists for extracting structured information from
regulatory map images. Representative outputs include:
“This appears to be a zoning map of a Chilean municipality, showing different
land use zones color-coded with a legend visible at the bottom. The map includes
residential zones (marked in yellow), commercial zones (orange), and green areas
(green), typical of a Plan Regulador Comunal.”
“A street network diagram showing proposed vial hierarchy for an urban sector,
with primary arterials marked in red and secondary streets in blue. The scale bar
indicates approximately 500 m.”
While these descriptions are imprecise relative to GIS-native cartographic analysis,
they provide structured metadata for map pages that would otherwise be entirely absent from text-only processing pipelines. Across the 29 PRCs, a total of 218 pages were
classified as cartographic by the text-density threshold and submitted to Moondream for
visual description. Of these, 181 yielded a substantive non-empty response (83.0% completion rate for the visual task—substantially higher than for text classification, confirming
that map interpretation sits within Moondream’s effective capacity even without domain
fine-tuning). Post-hoc coding of the resulting descriptions identifies four recurrent output categories: zoning plans (identified in approximately 61% of map-page outputs),
land use and density maps (approximately 19%), road network and mobility diagrams
(approximately 12%), and miscellaneous schematic figures including project boundaries
and public space designs (approximately 8%). Moondream correctly identified the
high-level map type in the large majority of inspected outputs and extracted legend color
categories with reasonable accuracy, though explicit identification of the specific municipality from cartographic content was achieved in only a minority of cases—a limitation
reflecting both the absence of municipality-name labels on many internal map pages and
the model’s limited Chilean place-name recognition. The principal failure mode observed
was occasional hallucination of color-coding categories not present in the image. This
represents a genuine contribution of the VLM approach: making the cartographic content
of regulatory documents machine-readable without specialized GIS tooling—a capability

https://doi.org/10.3390/urbansci10070352

### Page 13

Urban Sci. 2026, 10, 352

13 of 19

that is particularly relevant in contexts where PRC maps are embedded as raster images
within PDF documents rather than maintained as separate geospatial datasets.
4.6. Computational Footprint
Table 6 was constructed to situate the marginal cost of the proposed pipeline against
two reference points: the base companion study, which relied on DeepSeek-R1 accessed
through a cloud API, and a hypothetical cloud deployment using a GPT-4o-equivalent
model. Figures for this study were measured directly during the full-corpus run: runtime
was instrumented within the pipeline, energy consumption was derived from the device’s
average power draw multiplied by wall-clock runtime, and peak RAM was recorded
from system telemetry. The marginal cost is zero because inference runs locally with no
per-request charge.
Table 6. Computational cost comparison.

Base Study
(DeepSeek-R1)

Cloud GPT-4o equiv.

This Study (Moondream)

Metric

Cloud API

Cloud API

Local (MacBook Pro M-series)

Hardware

High (API pricing)

~$18.31

$0.00

Marginal cost

Not disclosed

Not disclosed

0.000866 kWh

Energy

671 GB

>1 TB (closed)

1.7 GB

Model size

Partial (API)

None

Full (local)

Data sovereignty

Not reported

~3 h (latency)

4.3 min

Runtime (full corpus)

8 gb (cloud)

8 gb (cloud)

3.2 gb (local)

RAM

The local pipeline processes the full 2289-article corpus through keyword classification
in 4.3 min at an estimated energy consumption of 0.000866 kWh (based on 12 W active
power draw for 259.9 s). The estimated cloud equivalent cost of $18.31—while modest
in absolute terms—represents a non-trivial barrier for research groups operating without
grants that include API compute budgets, particularly when iterative analysis (parameter
tuning, axis refinement, corpus expansion) multiplies costs across experimental runs. More
importantly, the local pipeline eliminates data sovereignty constraints: PRC text, which
may include sensitive site addresses and administrative details, is never transmitted to
external servers.

5. Discussion
5.1. Small Models as Feasibility Baselines
The principal contribution of this study is empirical rather than methodological: it
documents what a small, locally-deployed VLM can and cannot do when applied to a real
urban regulatory corpus. The results indicate a clear task-dependent performance profile:

•

•

Visual tasks (OCR, map interpretation): Moondream provides genuine utility where
no rule-based alternative exists. Its ability to describe zoning maps, identify legend
categories, and transcribe scanned pages adds information that would be entirely
absent from a text-only pipeline.
Text classification: The generalist VLM, without domain fine-tuning, does not produce
classifications that align with keyword baselines (macro-F1 = 0.355, kappa = 0.004).
For native-text PDFs in a well-defined categorical schema, keyword methods provide
superior speed and reproducibility.

https://doi.org/10.3390/urbansci10070352

### Page 14

Urban Sci. 2026, 10, 352

14 of 19

This finding aligns with broader debates in computational social science about the
appropriate scope of language models: their comparative advantage lies in tasks requiring flexible semantic understanding, not in tasks where structured rules already capture the relevant knowledge [22]. The PRC classification task is sufficiently well-defined
(six axes, constrained legal vocabulary) that rule-based methods outperform an
un-fine-tuned generalist VLM. However, the same task with more ambiguous categories,
multilingual corpora, or implicit regulatory content would likely shift the balance toward
model-based approaches.
The hybrid architecture—native text extraction + keyword classification + VLM for
visual tasks—thus represents a principled methodology for regulatory document analysis:
using Moondream where it is necessary (visual content), not where it is merely possible
(text classification).
It is useful to situate the hybrid pipeline within the broader landscape of low-cost
text analysis methods available to planning researchers. Dictionary-based and rule-based
extraction—exemplified by the keyword classifier deployed here—offers maximum determinism and reproducibility at the cost of semantic flexibility. Topic modeling (LDA and
its variants) discovers latent thematic structure without supervision but requires careful
hyperparameter tuning and post-hoc label interpretation. Lightweight sentence-embedding
approaches using pre-downloaded local models (e.g., multilingual MiniLM at roughly
120 MB) enable semantic similarity computations without API dependencies, though
they cannot process visual content. Each of these methods is viable for text-only regulatory corpora; the present pipeline adds value precisely in corpora with a significant
visual component—scanned pages, embedded zoning maps, cartographic annexes—that
none of the text-only methods can reach. In contexts where regulatory documents are
predominantly textual and well-standardized, the keyword plus lightweight-embedding
combination may in fact be more cost-efficient than any VLM-based approach. The argument for VLM integration strengthens as corpora become more visually heterogeneous, less
standardized in their textual conventions, or richer in legacy scanned material—conditions
that characterize many Latin American planning archives beyond the Chilean PRC system
analyzed here.
5.2. The High Failure Rate as a Design Finding
The 69.2% attrition rate in Moondream’s classification responses deserves explicit
discussion, as it represents one of the most practically significant findings of this study. The
timeouts occurred predominantly on longer articles (>300 words) with complex syntactic
structures typical of Chilean legal drafting. Three factors contribute to this behavior:

•

•

•

Context window constraints: Small VLMs have limited effective context windows.
Moondream’s Phi-1.5 language backbone was trained primarily on English-language
data with shorter average sequence lengths than the dense, subordinate-clause-heavy
prose of Chilean regulatory text.
Generation loop artifacts: Without fine-tuning, the model occasionally enters repetitive
generation loops when attempting to produce structured JSON output from unfamiliar
input domains, exceeding the 300-s timeout.
Token budget limitations: The num_predict: 80 cap, necessary to prevent runaway
generation, may truncate valid responses on articles requiring multi-axis classification
with explanatory text.

These findings have direct implications for the design of “edge computing” approaches
in urban regulatory research: small VLMs deployed on consumer hardware face practical
throughput ceilings that must be anticipated in pipeline design. The successful completion

https://doi.org/10.3390/urbansci10070352

### Page 15

Urban Sci. 2026, 10, 352

15 of 19

rate of 30.8% suggests that current-generation small VLMs are viable for sampling-based
analysis but not yet for full-corpus classification tasks in specialized domains.
Three practical mitigation strategies merit discussion for future deployments of the
same pipeline architecture. Article chunking—splitting long regulatory articles into shorter
semantic units of approximately 200 words before submission to the VLM—reduces individual (please check Appendix A for details) length below Moondream’s effective context
capacity and would be expected to raise the completion rate substantially, at the cost of
additional post-hoc aggregation logic. Prompt simplification—replacing the multi-axis classification prompt with a sequence of single-axis binary queries—narrows the inference task
and avoids the JSON-formatting failures that contribute to a non-trivial share of timeouts.
Length-based prefiltering—using a character-count threshold to route long articles directly
to keyword classification while reserving Moondream only for shorter texts—exploits the
complementary strengths of the two methods and matches task difficulty to model capacity.
None of these strategies was implemented in the present pipeline because the study aimed
to document the baseline behavior of an out-of-the-box small VLM on dense regulatory
Spanish; reporting the unmitigated attrition rate is itself an empirical contribution for
researchers planning similar deployments.
5.3. Methodological Limitations and the Question of Ground Truth
Several limitations constrain the generalizability of these findings, which are addressed
with the transparency that the reviewers’ valuable comments have encouraged:
Keyword classification as silver standard: The keyword classifier, while fast and reproducible, is not a gold standard. It cannot detect regulatory content that does not use the
expected vocabulary, it is sensitive to synonym variation in legal Spanish, and it treats any
keyword co-occurrence as a positive classification regardless of semantic context. In Chilean
PRCs, the highly formulaic structure of regulatory articles mitigates these limitations (articles about zoning do consistently use “zona” and “uso permitido”), but the approach
would be less reliable in regulatory traditions with greater lexical variation. Keyword classification was selected as the primary method precisely because it is deterministic and
auditable—allowing independent verification of every classification decision—rather
than because it approximates human judgment. Future work should incorporate a
human-annotated gold standard (expert classification of a stratified sample) to provide an
independent reference that resolves the circularity of evaluating one automated method
against another.
Validation sample bias: The 88-article validation sample is a completed subset of the
286 targeted articles. Because Moondream’s timeouts are correlated with article length
and complexity, the completed sample likely over-represents shorter, simpler articles.
This length-based selection bias may inflate Moondream’s apparent performance (simpler articles may be easier to classify) or deflate it (shorter articles may contain fewer
discriminative keywords). A future validation protocol should ensure balanced sampling
across article length distributions or, preferably, evaluate against human annotations on
a pre-specified sample.
Single model evaluation: This study evaluates only Moondream as the small VLM
component. Other models in the same parameter range—such as LLaVA-1.5 (7B),
Phi-2 (2.7B), or SmolVLM (2B)—might achieve different performance profiles on the same
tasks. A multi-model comparison would strengthen the study’s conclusions about what
the class of small VLMs can achieve, rather than what one specific model achieves. Moondream was chosen because it was the smallest multimodal model available through Ollama at the time of the experiment, making it the most conservative test of the “minimal
hardware” premise.

https://doi.org/10.3390/urbansci10070352

### Page 16

Urban Sci. 2026, 10, 352

16 of 19

Corpus scope: The 29-municipality corpus represents a specific Latin American urban
context with particular regulatory traditions (Chilean LGUC framework, Spanish legal
register, MINVU standardized templates). Results may not generalize to municipalities
with different document structures, languages, or regulatory classification schemas. The
dimensions along which transferability is most and least likely can nonetheless be anticipated. The keyword classification component depends on the lexical stability of the regulatory tradition and should transfer well to other Hispanic American contexts that share a
MINVU-style template lineage (e.g., Argentine Códigos de Ordenamiento Urbano, Peruvian Planes de Desarrollo Urbano), with the primary effort being the substitution of
axis-specific term lists. Transferability is lower for regulatory traditions with greater lexical
heterogeneity, such as common-law zoning ordinances in North American jurisdictions,
which exhibit substantially more variation in regulatory vocabulary and would likely
require expanded keyword inventories or migration to embedding-based classification.
The Moondream visual pipeline is in principle language- and tradition-agnostic for map
interpretation, since cartographic conventions—color-coded zoning, legend structures,
scale indicators—are largely universal. The OCR fallback degrades for non-Latin scripts
and for handwritten or stamped annotations common in legacy planning archives. A full
empirical mapping of transferability requires comparative deployments and is identified
as a research priority.
Gap index sensitivity: The gap index formula (Section 3.5) does not include a regularization constant. For municipalities with very few total articles, the normalized frequency
can be volatile. Raw article counts are reported alongside gap indices in all tables to enable
readers to assess the robustness of individual values. Future work could introduce confidence intervals derived from bootstrap resampling or a Bayesian smoothing approach to
improve the reliability of gap estimates for small-corpus municipalities.
5.4. Implications for Global South Research Infrastructure
From a political economy perspective, this study demonstrates that meaningful
metropolitan-scale urban regulatory analysis is achievable without cloud API dependencies.
For research groups in Chile, Argentina, Colombia, Peru, and other Latin American countries maintaining large urban regulatory corpora, the barrier to entry for computational
text analysis is substantially reduced by local VLM deployment—not because the VLM
replaces expert analysis, but because it extends the reach of a hybrid pipeline that combines
deterministic methods (keyword classification) with model-based capabilities (OCR, map
reading) at zero marginal cost.
However, this observation must be qualified. The hardware required to run Moondream efficiently (16 GB RAM, Apple Silicon, or equivalent) is itself unevenly distributed.
While substantially cheaper than cloud API subscriptions for large projects, consumer hardware with adequate specifications remains economically inaccessible to some Global South
research contexts. The argument for computational sovereignty through local deployment
is thus a relative, not absolute, improvement.
The deeper structural issue—identified in Section 2.3—is that the geographic distribution of AI research infrastructure mirrors and reinforces existing knowledge hierarchies. The meaningful democratization of GeoAI will require not only smaller models
but open training datasets, local fine-tuning infrastructure, and academic data-sharing
agreements that extend beyond the current model of corporate API dependency. Studies
like this one—which document both the possibilities and the boundaries of affordable
approaches—contribute to this agenda by providing empirical evidence for what is
achievable under resource constraints, rather than only reporting what is possible with
frontier infrastructure.

https://doi.org/10.3390/urbansci10070352

### Page 17

Urban Sci. 2026, 10, 352

17 of 19

5.5. Ethical Considerations
This study analyzes publicly available municipal planning documents. No personal
data, private communications, or proprietary information was processed. The corpus consists exclusively of legally mandated public regulatory instruments published by Chilean
municipalities under the Ley de Urbanismo y Construcciones.
The use of local model deployment eliminates the risk of inadvertent data exposure
through third-party API providers. All processing occurred on researcher-controlled
hardware, and no document content was transmitted to external servers.
The relationship of this work to the previously published Urban Science (2025) paper
is one of methodological extension: the same corpus is analyzed with a fundamentally
different approach, enabling a direct comparison of methodological choices while adding
new empirical results. This practice of methodological comparison using shared corpora is
standard in computational social science and does not constitute redundant publication.

6. Conclusions
This paper has evaluated the feasibility of using Moondream, a 1.7-billion-parameter
vision-language model deployable on consumer hardware via Ollama, as the core of a
pipeline for geographic knowledge extraction from urban regulatory corpora. Applied to
29 PRCs of the Gran Santiago metropolitan area—drawn from the same corpus used in the
companion Urban Science (2025) study—the pipeline produces:

•

•

•

Structured classification of 2289 PRC articles across six thematic axes through a hybrid keyword + VLM approach, completed in 4.3 min on local hardware at zero
marginal cost.
Normative gap indices for 29 municipalities, revealing cross-municipal asymmetries in regulatory attention—including the absence of social housing provisions in
five municipalities—that reflect the socioeconomic stratification of the Gran Santiago
metropolitan area.
An empirical baseline for small VLM classification on specialized legal text, documenting Moondream’s strengths (visual document understanding, map interpretation) and
limitations (text classification without fine-tuning, high attrition on complex articles)
with direct implications for method selection in urban regulatory research.

The study contributes at three levels. Methodologically, it provides a fully open,
reproducible pipeline for PRC analysis that any research group can deploy without cloud
API access. Empirically, it extends the normative gap analysis of the Gran Santiago PRC
corpus with a methodology that is transparent, auditable, and replicable. Critically, it
positions the computational accessibility of GeoAI tools as a political question—one whose
answers have consequences for the geographic distribution of urban knowledge production.
Implications for planning practice. Beyond academic research, the pipeline described
here has direct operational applications for municipal and metropolitan planning offices
working under fiscal and digital-infrastructure constraints. A planning department in
a typical Gran Santiago municipality—which often operates with limited GIS staff, no
in-house AI capacity, and modest computing budgets—can deploy the same Moondream
and keyword pipeline on a single mid-range laptop to: (i) generate consistent thematic
indices of its own PRC and benchmark them against neighboring municipalities; (ii) automatically extract regulatory metadata from incoming or legacy PDFs for archival and
public consultation purposes; (iii) screen draft PRC modifications for thematic coverage
gaps prior to public participation processes; and (iv) populate municipal open-data portals
with structured indicators derived from previously unstructured regulatory text. Because
the pipeline runs entirely on local hardware, none of these uses requires transmitting poten-

https://doi.org/10.3390/urbansci10070352

### Page 18

Urban Sci. 2026, 10, 352

18 of 19

tially sensitive municipal data to external servers, nor does it incur recurrent subscription
costs. This combination—auditable methods, zero marginal cost, full data sovereignty—can
serve as the operational substrate on which more ambitious digital-planning workflows
are incrementally built, particularly in Latin American jurisdictions where the gap between
regulatory ambition and computational capacity is widest.
Future extensions include: (a) fine-tuning Moondream or a similarly-sized model on
labeled Chilean PRC data to improve text classification performance; (b) evaluating additional small VLMs (LLaVA, SmolVLM, Phi-3-Vision) to establish broader baselines for the
model class; (c) incorporating human-annotated gold standard validation to complement
the keyword silver standard; (d) extending the pipeline to the national Chilean PRC corpus
(346 municipalities); and (e) developing a standardized API for PRC knowledge extraction
that could serve municipal and regional planning agencies directly.
The cities of the Global South are not passive objects of data extraction—they are active
sites of regulatory production, urban knowledge, and territorial imagination. Making the
tools that read these cities accessible to the researchers who live in them is a condition for a
more geographically equitable urban science.
Funding: This research was funded by the Fondo Nacional de Desarrollo Científico y Tecnológico
(FONDECYT), grant number 1262258. Open access publication was partially funded by the Vicerrectoría de Investigación, Universidad de Las Américas, Chile.
Data Availability Statement: The PRC corpus is available from Chilean municipal and regional
planning archives under public access provisions of Chilean Law 20.285 (Ley de Acceso a la
Informacion Publica).
Acknowledgments: This research uses the same PRC corpus assembled for the Urban Science (2025)
study. The author acknowledges the open-source contributions of the Ollama, PyMuPDF, and
Moondream development communities, without which local VLM deployment at this scale would
not be feasible.
Conflicts of Interest: The author declares no conflicts of interest.

Appendix A. Moondream Prompts (In Spanish)
Classification prompt:
Clasifica este texto de una ordenanza urbana chilena.
Ejes posibles: zoning, land_use, mobility, participation, sustainability, social_housing.
Texto: {text}
Responde solo con lista JSON, ejemplo: [“zoning”]. Si ninguno aplica: []
Map interpretation prompt:
Eres un experto en cartografia urbana chilena.
Describe brevemente el mapa o plano urbano que aparece en esta imagen:

•
•
•
•

Tipo de mapa (uso de suelo, zonificacion, vialidad, etc.)
Municipio o area representada si es identificable
Leyenda principal o categorias visibles
Responde en espanol, maximo 3 oraciones.
Classification prompt in English:
Classify this text from a Chilean urban ordinance.
Possible axes: zoning, land use, mobility, participation, sustainability, social housing.
Text: {text}
Respond only with a JSON list, for example: [“zoning”]. If none apply: []
Map interpretation prompt:
You are an expert in Chilean urban cartography.
Briefly describe the urban map or plan shown in this image:

https://doi.org/10.3390/urbansci10070352

### Page 19

Urban Sci. 2026, 10, 352

19 of 19

•
•
•
•

Type of map (land use, zoning, road network, etc.)
Municipality or area represented if identifiable
Main legend or visible categories
Respond in English, maximum 3 sentences.

References
1.
2.
3.
4.
5.

6.
7.
8.

9.
10.
11.
12.
13.
14.
15.
16.
17.
18.
19.
20.
21.
22.

Janowicz, K.; Gao, S.; McKenzie, G.; Hu, Y.; Bhaduri, B. GeoAI: Spatially explicit artificial intelligence techniques for geographic
knowledge discovery and beyond. Int. J. Geogr. Inf. Sci. 2020, 34, 625–636.
Mai, G.; Janowicz, K.; Hu, Y.; Gao, S.; Yan, B.; Zhu, R. A review of location encoding for GeoAI: Methods and applications.
Int. J. Geogr. Inf. Sci. 2022, 36, 639–673. [CrossRef]
Hu, Y.; Gao, S.; Soni, P.; Dou, W.; Zhao, R. Geo-knowledge-guided GPT models improve the extraction of location descriptions
from disaster-related social media messages. Int. J. Geogr. Inf. Sci. 2023, 37, 2289–2318.
Couture, S.; Toupin, S. What does the notion of sovereignty mean when referring to the digital? New Media Soc. 2019, 21,
2305–2322. [CrossRef]
ECLAC (Economic Commission for Latin America and the Caribbean). Digital Technologies for a New Future; United Nations:
New York, NY, USA, 2022. Available online: https://www.cepal.org/en/publications/46817-digital-technologies-new-future
(accessed on 1 January 2025).
Vergara-Perucich, J.F. AI-Driven Deconstruction of Urban Regulatory Frameworks: Unveiling Social Sustainability Gaps in
Santiago’s Communal Zoning. Urban Sci. 2025, 9, 186. [CrossRef]
Fonte, C.C.; Patriarca, J.; Jesus, I.; Duarte, D. Automatic Extraction and Filtering of OpenStreetMap Data to Generate Training
Datasets for Land Use Land Cover Classification. Remote Sens. 2020, 12, 3428. [CrossRef]
Lin, Y.; Thackway, W.; Soundararaj, B.; Eagleson, S.; Han, H.; Pettit, C. Transforming urban planning through machine learning: A
study on planning application classification using natural language processing. Environ. Plan. B Urban Anal. City Sci. 2026, 53,
11–31. [CrossRef]
ICA (International Cartographic Association). Commission on AI in Cartography. Available online: https://geoai.icaci.org/
(accessed on 1 January 2025).
Yan, B.; Mai, G.; Janowicz, K.; Gao, S. GeoAI for cartography: Challenges and opportunities. Abstr. ICA 2024, 7, 1–2.
Krippendorff, K. Content Analysis: An Introduction to Its Methodology, 4th ed.; SAGE: Thousand Oaks, CA, USA, 2018.
Blei, D.M.; Ng, A.Y.; Jordan, M.I. Latent Dirichlet allocation. J. Mach. Learn. Res. 2003, 3, 993–1022.
Lawrimore, M.A.; Sanchez, G.M.; Cothron, C.; Tulbure, M.G.; BenDor, T.K.; Meentemeyer, R.K. Creating spatially complete
zoning maps using machine learning. Comput. Environ. Urban Syst. 2024, 112, 102157. [CrossRef]
Goodspeed, R. Smart cities: Moving beyond urban cybernetics to tackle wicked problems. Camb. J. Reg. Econ. Soc. 2020, 8, 79–92.
[CrossRef]
Tshitoyan, V.; Dagdelen, J.; Weston, L.; Dunn, A.; Rong, Z.; Kononova, O.; Jain, A.; Persson, K.A.; Ceder, G. Unsupervised word
embeddings capture latent knowledge from materials science literature. Nature 2019, 571, 95–98. [CrossRef] [PubMed]
Schick, T.; Dwivedi-Yu, J.; Dessi, R.; Raber, R.; Jiang, Z.; Veseli, B.; Schutze, H. Toolformer: Language models can teach themselves
to use tools. arXiv 2021, arXiv:2302.04761.
Eldan, R.; Li, Y. TinyStories: How small can language models be and still speak coherent English? arXiv 2023, arXiv:2305.07759.
Graham, M. Regulate, replicate, and resist: The contentious geographies of the digital. Urban Stud. 2020, 57, 301–320.
Zook, M.; Graham, M. The creative reconstruction of the internet: Google and the privatization of cyberspace and digiPlace.
Geoforum 2007, 38, 1322–1343. [CrossRef]
Lefebvre, H. The Production of Space; Blackwell: Oxford, UK, 1991.
Harvey, D. The right to the city. New Left Rev. 2008, 53, 23–40. [CrossRef]
Grimmer, J.; Roberts, M.E.; Stewart, B.M. Text as Data: A New Framework for Machine Learning and the Social Sciences; Princeton
University Press: Princeton, NJ, USA, 2022.

Disclaimer/Publisher’s Note: The statements, opinions and data contained in all publications are solely those of the individual
author(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to
people or property resulting from any ideas, methods, instructions or products referred to in the content.

https://doi.org/10.3390/urbansci10070352
