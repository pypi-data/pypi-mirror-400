"""Hand-curated search queries for BHSA latency benchmarks.

These queries are validated for syntactic correctness and cover
a range of complexities:
- Lexical: Simple word-level feature queries
- Structural: Phrase and clause queries
- Quantified: Queries with /with/ and /without/ conditions
- Complex: Multi-level hierarchical queries

All queries use actual BHSA feature values.
"""

from __future__ import annotations

from cfabric_benchmarks.models.latency import SearchQuery


def get_bhsa_queries() -> list[SearchQuery]:
    """Return 100 hand-curated BHSA search queries."""
    return [
        # ===========================================
        # LEXICAL QUERIES (1-30): Simple word queries
        # ===========================================

        # Part of speech searches
        SearchQuery(
            id="lex_001",
            category="lexical",
            template="word sp=verb",
            description="All verbs",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_002",
            category="lexical",
            template="word sp=subs",
            description="All substantives (nouns)",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_003",
            category="lexical",
            template="word sp=prep",
            description="All prepositions",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_004",
            category="lexical",
            template="word sp=conj",
            description="All conjunctions",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_005",
            category="lexical",
            template="word sp=nmpr",
            description="All proper nouns",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_006",
            category="lexical",
            template="word sp=art",
            description="All articles",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_007",
            category="lexical",
            template="word sp=adjv",
            description="All adjectives",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_008",
            category="lexical",
            template="word sp=advb",
            description="All adverbs",
            expected_complexity="low",
        ),

        # Verb tense searches
        SearchQuery(
            id="lex_009",
            category="lexical",
            template="word vt=perf",
            description="Perfect tense verbs",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_010",
            category="lexical",
            template="word vt=impf",
            description="Imperfect tense verbs",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_011",
            category="lexical",
            template="word vt=wayq",
            description="Wayyiqtol verbs",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_012",
            category="lexical",
            template="word vt=impv",
            description="Imperative verbs",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_013",
            category="lexical",
            template="word vt=ptca",
            description="Active participles",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_014",
            category="lexical",
            template="word vt=infc",
            description="Infinitive construct",
            expected_complexity="low",
        ),

        # Verb stem searches
        SearchQuery(
            id="lex_015",
            category="lexical",
            template="word vs=qal",
            description="Qal stem verbs",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_016",
            category="lexical",
            template="word vs=piel",
            description="Piel stem verbs",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_017",
            category="lexical",
            template="word vs=hif",
            description="Hiphil stem verbs",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_018",
            category="lexical",
            template="word vs=nif",
            description="Niphal stem verbs",
            expected_complexity="low",
        ),

        # Gender/number searches
        SearchQuery(
            id="lex_019",
            category="lexical",
            template="word gn=m",
            description="Masculine words",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_020",
            category="lexical",
            template="word gn=f",
            description="Feminine words",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_021",
            category="lexical",
            template="word nu=sg",
            description="Singular words",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_022",
            category="lexical",
            template="word nu=pl",
            description="Plural words",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_023",
            category="lexical",
            template="word nu=du",
            description="Dual words",
            expected_complexity="low",
        ),

        # Combined lexical features
        SearchQuery(
            id="lex_024",
            category="lexical",
            template="word sp=verb vt=perf",
            description="Perfect verbs",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_025",
            category="lexical",
            template="word sp=verb vs=qal",
            description="Qal verbs",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_026",
            category="lexical",
            template="word sp=subs gn=m nu=pl",
            description="Masculine plural nouns",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_027",
            category="lexical",
            template="word sp=subs gn=f nu=sg",
            description="Feminine singular nouns",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_028",
            category="lexical",
            template="word sp=verb vt=impv gn=m",
            description="Masculine imperatives",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_029",
            category="lexical",
            template="word sp=verb vs=hif vt=perf",
            description="Hiphil perfects",
            expected_complexity="low",
        ),
        SearchQuery(
            id="lex_030",
            category="lexical",
            template="word language=Aramaic",
            description="Aramaic words",
            expected_complexity="low",
        ),

        # ===========================================
        # STRUCTURAL QUERIES (31-60): Phrase/clause
        # ===========================================

        # Phrase function searches
        SearchQuery(
            id="struct_001",
            category="structural",
            template="phrase function=Pred",
            description="Predicate phrases",
            expected_complexity="low",
        ),
        SearchQuery(
            id="struct_002",
            category="structural",
            template="phrase function=Subj",
            description="Subject phrases",
            expected_complexity="low",
        ),
        SearchQuery(
            id="struct_003",
            category="structural",
            template="phrase function=Objc",
            description="Object phrases",
            expected_complexity="low",
        ),
        SearchQuery(
            id="struct_004",
            category="structural",
            template="phrase function=Cmpl",
            description="Complement phrases",
            expected_complexity="low",
        ),
        SearchQuery(
            id="struct_005",
            category="structural",
            template="phrase function=Adju",
            description="Adjunct phrases",
            expected_complexity="low",
        ),
        SearchQuery(
            id="struct_006",
            category="structural",
            template="phrase function=Time",
            description="Time phrases",
            expected_complexity="low",
        ),
        SearchQuery(
            id="struct_007",
            category="structural",
            template="phrase function=Loca",
            description="Location phrases",
            expected_complexity="low",
        ),

        # Phrase type searches
        SearchQuery(
            id="struct_008",
            category="structural",
            template="phrase typ=VP",
            description="Verbal phrases",
            expected_complexity="low",
        ),
        SearchQuery(
            id="struct_009",
            category="structural",
            template="phrase typ=NP",
            description="Noun phrases",
            expected_complexity="low",
        ),
        SearchQuery(
            id="struct_010",
            category="structural",
            template="phrase typ=PP",
            description="Prepositional phrases",
            expected_complexity="low",
        ),
        SearchQuery(
            id="struct_011",
            category="structural",
            template="phrase typ=CP",
            description="Conjunction phrases",
            expected_complexity="low",
        ),
        SearchQuery(
            id="struct_012",
            category="structural",
            template="phrase typ=AdvP",
            description="Adverb phrases",
            expected_complexity="low",
        ),

        # Clause searches
        SearchQuery(
            id="struct_013",
            category="structural",
            template="clause kind=VC",
            description="Verbal clauses",
            expected_complexity="low",
        ),
        SearchQuery(
            id="struct_014",
            category="structural",
            template="clause kind=NC",
            description="Nominal clauses",
            expected_complexity="low",
        ),
        SearchQuery(
            id="struct_015",
            category="structural",
            template="clause domain=Q",
            description="Quotation clauses",
            expected_complexity="low",
        ),
        SearchQuery(
            id="struct_016",
            category="structural",
            template="clause domain=N",
            description="Narrative clauses",
            expected_complexity="low",
        ),
        SearchQuery(
            id="struct_017",
            category="structural",
            template="clause typ=Way0",
            description="Wayyiqtol clauses",
            expected_complexity="low",
        ),
        SearchQuery(
            id="struct_018",
            category="structural",
            template="clause typ=NmCl",
            description="Nominal clauses",
            expected_complexity="low",
        ),
        SearchQuery(
            id="struct_019",
            category="structural",
            template="clause typ=InfC",
            description="Infinitive clauses",
            expected_complexity="low",
        ),

        # Embedded structures
        SearchQuery(
            id="struct_020",
            category="structural",
            template="""
clause
  phrase function=Subj
""",
            description="Clauses with subject phrases",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="struct_021",
            category="structural",
            template="""
clause
  phrase function=Pred
""",
            description="Clauses with predicate phrases",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="struct_022",
            category="structural",
            template="""
clause kind=VC
  phrase function=Objc
""",
            description="Verbal clauses with objects",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="struct_023",
            category="structural",
            template="""
phrase typ=NP
  word sp=subs
""",
            description="Noun phrases with substantives",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="struct_024",
            category="structural",
            template="""
phrase typ=VP
  word sp=verb
""",
            description="Verb phrases with verbs",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="struct_025",
            category="structural",
            template="""
phrase typ=PP
  word sp=prep
""",
            description="Prepositional phrases with prepositions",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="struct_026",
            category="structural",
            template="""
clause
  phrase function=Subj
  phrase function=Pred
""",
            description="Clauses with both subject and predicate",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="struct_027",
            category="structural",
            template="""
clause
  phrase function=Pred
  phrase function=Objc
""",
            description="Clauses with predicate and object",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="struct_028",
            category="structural",
            template="""
sentence
  clause
""",
            description="Sentences containing clauses",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="struct_029",
            category="structural",
            template="""
verse
  clause kind=VC
""",
            description="Verses with verbal clauses",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="struct_030",
            category="structural",
            template="""
clause
  phrase
    word sp=verb vt=wayq
""",
            description="Clauses with wayyiqtol verbs",
            expected_complexity="medium",
        ),

        # ===========================================
        # QUANTIFIED QUERIES (61-80): with/without
        # ===========================================

        SearchQuery(
            id="quant_001",
            category="quantified",
            template="""
clause
/with/
  phrase function=Subj
/-/
""",
            description="Clauses with subject phrases",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="quant_002",
            category="quantified",
            template="""
clause kind=VC
/with/
  phrase function=Objc
/-/
""",
            description="Verbal clauses with objects",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="quant_003",
            category="quantified",
            template="""
clause
/without/
  phrase function=Subj
/-/
""",
            description="Clauses without explicit subjects",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="quant_004",
            category="quantified",
            template="""
phrase typ=NP
/with/
  word sp=art
/-/
""",
            description="Noun phrases with articles",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="quant_005",
            category="quantified",
            template="""
phrase typ=NP
/without/
  word sp=art
/-/
""",
            description="Noun phrases without articles",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="quant_006",
            category="quantified",
            template="""
clause
/with/
  phrase function=Time
/-/
""",
            description="Clauses with time phrases",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="quant_007",
            category="quantified",
            template="""
clause
/with/
  phrase function=Loca
/-/
""",
            description="Clauses with location phrases",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="quant_008",
            category="quantified",
            template="""
phrase function=Pred
/with/
  word vt=perf
/-/
""",
            description="Predicate phrases with perfect verbs",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="quant_009",
            category="quantified",
            template="""
phrase function=Pred
/with/
  word vt=impf
/-/
""",
            description="Predicate phrases with imperfect verbs",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="quant_010",
            category="quantified",
            template="""
clause domain=Q
/with/
  phrase function=Voct
/-/
""",
            description="Quotations with vocatives",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="quant_011",
            category="quantified",
            template="""
clause
/with/
  phrase function=Nega
/-/
""",
            description="Clauses with negation",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="quant_012",
            category="quantified",
            template="""
phrase typ=NP
/with/
  word sp=adjv
/-/
""",
            description="Noun phrases with adjectives",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="quant_013",
            category="quantified",
            template="""
clause kind=NC
/with/
  phrase function=PreC
/-/
""",
            description="Nominal clauses with predicative complements",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="quant_014",
            category="quantified",
            template="""
verse
/with/
  clause domain=Q
/-/
""",
            description="Verses containing quotations",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="quant_015",
            category="quantified",
            template="""
sentence
/with/
  clause kind=VC
  clause kind=NC
/-/
""",
            description="Sentences with both verbal and nominal clauses",
            expected_complexity="high",
        ),
        SearchQuery(
            id="quant_016",
            category="quantified",
            template="""
phrase function=Subj
/with/
  word sp=nmpr
/-/
""",
            description="Subject phrases with proper nouns",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="quant_017",
            category="quantified",
            template="""
clause
/with/
  phrase function=Subj
  phrase function=Objc
/-/
""",
            description="Clauses with both subject and object",
            expected_complexity="high",
        ),
        SearchQuery(
            id="quant_018",
            category="quantified",
            template="""
clause
/without/
  phrase function=Objc
/-/
""",
            description="Intransitive clauses (no object)",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="quant_019",
            category="quantified",
            template="""
phrase typ=VP
/with/
  word vs=hif
/-/
""",
            description="Verb phrases with hiphil verbs",
            expected_complexity="medium",
        ),
        SearchQuery(
            id="quant_020",
            category="quantified",
            template="""
clause
/with/
  phrase function=Cmpl
/-/
""",
            description="Clauses with complements",
            expected_complexity="medium",
        ),

        # ===========================================
        # COMPLEX QUERIES (81-100): Multi-level
        # ===========================================

        SearchQuery(
            id="complex_001",
            category="complex",
            template="""
clause kind=VC
  phrase function=Subj
    word sp=nmpr
  phrase function=Pred
    word vt=perf
""",
            description="Verbal clauses: proper noun subject + perfect predicate",
            expected_complexity="high",
        ),
        SearchQuery(
            id="complex_002",
            category="complex",
            template="""
clause kind=VC
  phrase function=Pred
    word vt=wayq
  phrase function=Objc
""",
            description="Wayyiqtol clauses with objects",
            expected_complexity="high",
        ),
        SearchQuery(
            id="complex_003",
            category="complex",
            template="""
sentence
  clause kind=VC
    phrase function=Subj
    phrase function=Pred
      word vt=perf
""",
            description="Sentences with subject + perfect verb clauses",
            expected_complexity="high",
        ),
        SearchQuery(
            id="complex_004",
            category="complex",
            template="""
clause domain=Q
  phrase function=Pred
    word sp=verb
  phrase function=Objc
    word sp=subs
""",
            description="Quotations with verb + noun object",
            expected_complexity="high",
        ),
        SearchQuery(
            id="complex_005",
            category="complex",
            template="""
verse
  clause kind=VC
    phrase function=Pred
      word vs=qal vt=perf
""",
            description="Verses with qal perfect verbs",
            expected_complexity="high",
        ),
        SearchQuery(
            id="complex_006",
            category="complex",
            template="""
clause
  phrase function=Subj
    word sp=subs gn=m nu=sg
""",
            description="Clauses with masculine singular noun subjects",
            expected_complexity="high",
        ),
        SearchQuery(
            id="complex_007",
            category="complex",
            template="""
clause
  phrase function=Pred
  phrase function=Subj
  phrase function=Objc
""",
            description="Transitive clauses (pred + subj + obj)",
            expected_complexity="high",
        ),
        SearchQuery(
            id="complex_008",
            category="complex",
            template="""
clause kind=NC
  phrase function=Subj
  phrase function=PreC
""",
            description="Nominal clauses with subject and predicate complement",
            expected_complexity="high",
        ),
        SearchQuery(
            id="complex_009",
            category="complex",
            template="""
sentence
  clause
    phrase typ=PP
      word sp=prep
""",
            description="Sentences with prepositional phrases",
            expected_complexity="high",
        ),
        SearchQuery(
            id="complex_010",
            category="complex",
            template="""
clause
  phrase function=Pred
    word sp=verb vt=impv
""",
            description="Imperative clauses",
            expected_complexity="high",
        ),
        SearchQuery(
            id="complex_011",
            category="complex",
            template="""
clause
/with/
  phrase function=Subj
    word sp=nmpr
/-/
  phrase function=Pred
""",
            description="Clauses: proper noun subject with predicate",
            expected_complexity="high",
        ),
        SearchQuery(
            id="complex_012",
            category="complex",
            template="""
clause kind=VC
/with/
  phrase function=Time
/-/
  phrase function=Pred
    word vt=perf
""",
            description="Verbal clauses with time phrase + perfect",
            expected_complexity="high",
        ),
        SearchQuery(
            id="complex_013",
            category="complex",
            template="""
clause domain=N
  phrase function=Pred
    word vt=wayq vs=qal
""",
            description="Narrative wayyiqtol qal verbs",
            expected_complexity="high",
        ),
        SearchQuery(
            id="complex_014",
            category="complex",
            template="""
verse
  clause
    phrase function=Subj
    phrase function=Pred
    phrase function=Objc
""",
            description="Verses with full transitive clauses",
            expected_complexity="high",
        ),
        SearchQuery(
            id="complex_015",
            category="complex",
            template="""
clause
  phrase function=Pred
    word sp=verb vs=piel
  phrase function=Objc
""",
            description="Piel verbs with objects",
            expected_complexity="high",
        ),
        SearchQuery(
            id="complex_016",
            category="complex",
            template="""
clause
/with/
  phrase function=Adju
/-/
  phrase function=Pred
  phrase function=Subj
""",
            description="Clauses with adjuncts, predicate, and subject",
            expected_complexity="high",
        ),
        SearchQuery(
            id="complex_017",
            category="complex",
            template="""
sentence
  clause kind=VC
  clause kind=VC
""",
            description="Sentences with multiple verbal clauses",
            expected_complexity="high",
        ),
        SearchQuery(
            id="complex_018",
            category="complex",
            template="""
chapter
/with/
  verse
    clause domain=Q
/-/
""",
            description="Chapters containing quotations",
            expected_complexity="high",
        ),
        SearchQuery(
            id="complex_019",
            category="complex",
            template="""
clause
  phrase function=Pred
    word sp=verb gn=m nu=sg ps=p3
""",
            description="3rd person masculine singular verbs",
            expected_complexity="high",
        ),
        SearchQuery(
            id="complex_020",
            category="complex",
            template="""
clause kind=VC domain=N
  phrase function=Pred
    word vt=wayq
  phrase function=Subj
    word sp=nmpr
""",
            description="Narrative wayyiqtol with proper noun subject",
            expected_complexity="high",
        ),
    ]


# Dictionary mapping corpus names to query functions
CORPUS_QUERIES: dict[str, callable] = {
    "bhsa": get_bhsa_queries,
}


def get_queries_for_corpus(corpus_name: str) -> list[SearchQuery]:
    """Get curated queries for a corpus.

    Args:
        corpus_name: Name of the corpus

    Returns:
        List of SearchQuery objects

    Raises:
        ValueError: If no queries are available for the corpus
    """
    if corpus_name not in CORPUS_QUERIES:
        available = ", ".join(CORPUS_QUERIES.keys())
        raise ValueError(
            f"No curated queries for corpus '{corpus_name}'. "
            f"Available: {available}"
        )
    return CORPUS_QUERIES[corpus_name]()
