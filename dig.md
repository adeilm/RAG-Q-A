flowchart TD
    START([user query]) --> CI{{"classify_intent<br/>route + sql_filters"}}

    %% direct / conversational branches
    CI -->|direct| DA[direct_answer]
    CI -->|define| DEF[define_node]
    CI -->|clarify| CL[clarify_node]
    CI -->|image| IM[image_node]
    CI -->|cad| CAD[cad_node]
    CI -->|"full-scope: summary"| FD[full_doc_node]
    CI -->|"full-scope: Q&A"| REL[relevance_node]

    %% retrieval routes
    CI -->|"rag / iterative / analytics / transform / graph / report"| RV[retrieve_vector]
    RV --> RG[retrieve_graph]
    RG --> RM[rerank_merge]

    RM -->|no docs in session| DAN[direct_answer_no_docs]
    RM -->|transform| TR[transform_node]
    RM -->|graph| GR[graph_node]
    RM -->|report| REP[report_node]
    RM -->|analytics| AN[analytics_node]
    RM -->|"iterative + low quality"| RW[rewrite_query]
    RM -->|rag| JP[judge_plan]

    RW -.loop.-> RV

    JP --> SY[synthesise]
    SY --> JE{{judge_evaluate}}
    JE -->|retry| SY
    JE -.->|"recover: re-route to another node"| CI
    JE -->|done| END([answer])

    DA --> END
    DAN --> END
    DEF --> END
    CL --> END
    IM --> END
    CAD --> END
    FD --> END
    REL --> END
    TR --> END
    GR --> END
    REP --> END
    AN --> END
