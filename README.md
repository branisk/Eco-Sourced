# Eco-Sourced
A database, visualization, and overview of environmental research topics through available sources

## What is this?
The goal for this project is to aggregate a large amount of Environmental research papers, and organize them for simplicity at understanding the domain of Environmental Sciences.  This will aid in answering questions such as:
- What Environmental Science fields are being studied?
- What Environmental Science research has already been done?
- What Environmental Science topics can I contribute to?
- What Environmental Science topics need to be worked on?
- What are the most densely worked on topics?

#### Relevent Papers:
- Literature Clustering Algorithm: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9420566/
- Hierarchical classification of Web content: https://dl.acm.org/doi/abs/10.1145/345508.345593
- Hierarchical Classification across multiple domains: https://link.springer.com/article/10.1007/s10618-010-0175-9
- Semantic Hierarchy in DOT: https://arxiv.org/pdf/2105.00101.pdf
- Research Taxonomy: https://brieflands.com/articles/apid-112456.html

#### Relevent Sources:
- ArXiv bulk research papers from Amazon S3: https://info.arxiv.org/help/bulk_data_s3.html



### Technical Flowchart
```mermaid

classDiagram
    class ArXiv_AWS_S3 {
        5.6 TB
        Updates Monthly
    }
    class PDF_ACCESS {
        2.7 TB
        +100 GB/month
    }
    class SOURCE_ACCESS {
        2.9 TB
    }
    class Dask {
        Preprocessing
    }
    ArXiv_AWS_S3 -- PDF_ACCESS
    ArXiv_AWS_S3 -- SOURCE_ACCESS
    PDF_ACCESS --> PyMuPDF: PDF to text
    SOURCE_ACCESS --> text_from_TEX_EXTRACTOR
    SOURCE_ACCESS --> other_EXTRACTOR
    text_from_TEX_EXTRACTOR --> ECOSOURCED_S3
    PyMuPDF --> ECOSOURCED_S3
    other_EXTRACTOR --> ECOSOURCED_S3
    ECOSOURCED_S3 --> Dask
    Dask --> Vaex: Visualization
    Dask --> HDBSCAN: Hierarchical Clustering
    HDBSCAN --> Vaex: Visualization
    HDBSCAN --> Categorization
    Categorization --> Vaex: Visualization
    Categorization --> AWS_RDS
    AWS_RDS --> Query
```

Contributions are very welcomed! Please submit a pull request, or feel free to reach out at branisk@protonmail.com.
