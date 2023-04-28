# Eco-Sourced
A database, visualization, and overview of environmental research topics through available sources

Relevent Papers:
- Literature Clustering Algorithm: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9420566/
- Hierarchical classification of Web content: https://dl.acm.org/doi/abs/10.1145/345508.345593
- Hierarchical Classification across multiple domains: https://link.springer.com/article/10.1007/s10618-010-0175-9
- Semantic Hierarchy in DOT: https://arxiv.org/pdf/2105.00101.pdf
- Research Taxonomy: https://brieflands.com/articles/apid-112456.html

Relevent Sources:
- ArXiv bulk research papers from Amazon S3

```mermaid
classDiagram
    participant ArXivAPI
    participant AWS_S3
    participant AWS_RDS
    participant Dask
    participant Vaex
    participant Preprocessing
    participant Feature_Extraction
    participant HDBSCAN
    participant Query
    participant Visualization
    ArXivAPI --> AWS_S3: Stream Data to AWS S3
    AWS_S3 --> Dask: Load Data using Dask
    Dask --> Preprocessing: Preprocess Data
    Preprocessing --> Vaex: Lazy Evaluation & Data Manipulation
    Vaex --> Feature_Extraction: Extract Relevant Features
    Feature_Extraction --> HDBSCAN: Perform Hierarchical Clustering
    HDBSCAN --> AWS_RDS: Store Categorized Database
    AWS_RDS --> Query: Query Data for Analysis
    Query --> Visualization: Visualize & Explore Data
```
