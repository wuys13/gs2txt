# Custom Enrichment

Implement custom pathway enrichment methods.

## Base Class

All enrichment methods must implement `BaseEnrichment`:

```python
from gs2txt.enrichment import BaseEnrichment
import pandas as pd
from typing import List

class BaseEnrichment:
    def enrich(self, genes: List[str], **kwargs) -> pd.DataFrame:
        """
        Perform enrichment analysis.

        Args:
            genes: List of gene symbols
            **kwargs: Additional parameters

        Returns:
            DataFrame with 'Term' and 'Adjusted P-value' columns
        """
        raise NotImplementedError
```

## Required Output Format

The `enrich()` method must return a DataFrame with:

| Column | Type | Description |
|--------|------|-------------|
| `Term` | `str` | Pathway/term name |
| `Adjusted P-value` | `float` | Statistical significance |

## Creating Custom Enrichment

### Basic Implementation

```python
from gs2txt.enrichment import BaseEnrichment
import pandas as pd
from typing import List
import requests

class MyEnrichment(BaseEnrichment):
    def __init__(self, database: str = "GO"):
        self.database = database
        self.api_url = "https://api.myservice.com/enrichment"

    def enrich(self, genes: List[str], **kwargs) -> pd.DataFrame:
        # Call external API
        response = requests.post(
            self.api_url,
            json={
                "genes": genes,
                "database": self.database
            }
        )
        response.raise_for_status()
        data = response.json()

        # Convert to required format
        return pd.DataFrame({
            "Term": data["pathway_names"],
            "Adjusted P-value": data["pvalues"]
        })
```

### Usage

```python
from gs2txt import GeneSetAnnotator

my_enrichment = MyEnrichment(database="Reactome")

annotator = GeneSetAnnotator(
    llm_provider=provider,
    enrichment_method=my_enrichment
)

result = annotator.annotate(deg_df)
```

## Advanced Examples

### Enrichment with Local Database

```python
import sqlite3
from scipy import stats

class LocalDBEnrichment(BaseEnrichment):
    def __init__(self, db_path: str):
        self.db_path = db_path

    def enrich(self, genes: List[str], **kwargs) -> pd.DataFrame:
        conn = sqlite3.connect(self.db_path)

        # Get pathway-gene associations
        query = """
            SELECT pathway_name, gene_symbol
            FROM pathway_genes
            WHERE gene_symbol IN ({})
        """.format(",".join("?" * len(genes)))

        df = pd.read_sql(query, conn, params=genes)
        conn.close()

        # Calculate enrichment (Fisher's exact test)
        results = []
        for pathway in df["pathway_name"].unique():
            pathway_genes = set(df[df["pathway_name"] == pathway]["gene_symbol"])
            overlap = len(set(genes) & pathway_genes)

            # Perform statistical test
            _, pvalue = stats.fisher_exact([
                [overlap, len(genes) - overlap],
                [len(pathway_genes), 20000 - len(pathway_genes)]
            ])

            results.append({
                "Term": pathway,
                "Adjusted P-value": pvalue
            })

        result_df = pd.DataFrame(results)

        # Adjust p-values (Benjamini-Hochberg)
        result_df["Adjusted P-value"] = self._adjust_pvalues(
            result_df["Adjusted P-value"].values
        )

        return result_df.sort_values("Adjusted P-value")

    def _adjust_pvalues(self, pvalues):
        from statsmodels.stats.multitest import multipletests
        return multipletests(pvalues, method="fdr_bh")[1]
```

### Enrichment with Caching

```python
import hashlib
import pickle
from pathlib import Path

class CachedEnrichment(BaseEnrichment):
    def __init__(self, base_enrichment: BaseEnrichment, cache_dir: str = ".cache"):
        self.base = base_enrichment
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def enrich(self, genes: List[str], **kwargs) -> pd.DataFrame:
        cache_key = self._make_key(genes)
        cache_file = self.cache_dir / f"{cache_key}.pkl"

        if cache_file.exists():
            return pd.read_pickle(cache_file)

        result = self.base.enrich(genes, **kwargs)
        result.to_pickle(cache_file)

        return result

    def _make_key(self, genes: List[str]) -> str:
        gene_str = ",".join(sorted(genes))
        return hashlib.md5(gene_str.encode()).hexdigest()
```

### Combined Enrichment (Multiple Sources)

```python
class CombinedEnrichment(BaseEnrichment):
    def __init__(self, enrichers: List[BaseEnrichment]):
        self.enrichers = enrichers

    def enrich(self, genes: List[str], **kwargs) -> pd.DataFrame:
        all_results = []

        for enricher in self.enrichers:
            try:
                result = enricher.enrich(genes, **kwargs)
                all_results.append(result)
            except Exception as e:
                print(f"Warning: {enricher.__class__.__name__} failed: {e}")

        if not all_results:
            return pd.DataFrame(columns=["Term", "Adjusted P-value"])

        # Combine and deduplicate
        combined = pd.concat(all_results, ignore_index=True)
        combined = combined.drop_duplicates(subset=["Term"])

        return combined.sort_values("Adjusted P-value").reset_index(drop=True)

# Usage
combined = CombinedEnrichment([
    GOEnrichment(),
    KEGGEnrichment(),
    ReactomeEnrichment()
])
```

## Using Pre-computed Results

### CustomEnrichment Adapter

For pre-computed enrichment results:

```python
from gs2txt.enrichment.custom import CustomEnrichment

# From list of terms
pathways = ["T cell activation", "Immune response", "Cytokine signaling"]
custom = CustomEnrichment(terms=pathways)

# From DataFrame
df = pd.DataFrame({
    "Term": ["Apoptosis", "Cell cycle"],
    "Adjusted P-value": [0.001, 0.005]
})
custom = CustomEnrichment(dataframe=df)

annotator = GeneSetAnnotator(
    llm_provider=provider,
    enrichment_method=custom
)
```

### Direct Pathway Passing

Skip enrichment entirely:

```python
annotator = GeneSetAnnotator(
    llm_provider=provider,
    enrichment_method=None
)

result = annotator.annotate(
    deg_df,
    pathways=["DNA damage response", "p53 signaling"],
    compute_enrichment=False
)
```

## Integration with External Tools

### Using DAVID

```python
import requests

class DAVIDEnrichment(BaseEnrichment):
    def __init__(self, email: str):
        self.email = email
        self.base_url = "https://david.ncifcrf.gov/api.jsp"

    def enrich(self, genes: List[str], **kwargs) -> pd.DataFrame:
        # Upload gene list
        response = requests.post(
            self.base_url,
            params={
                "type": "OFFICIAL_GENE_SYMBOL",
                "ids": ",".join(genes),
                "tool": "chartReport",
                "annot": "GOTERM_BP_DIRECT"
            }
        )

        # Parse results
        # ... implementation details

        return pd.DataFrame({
            "Term": terms,
            "Adjusted P-value": pvalues
        })
```

### Using Enrichr

```python
import requests
import json

class EnrichrEnrichment(BaseEnrichment):
    def __init__(self, gene_set_library: str = "GO_Biological_Process_2021"):
        self.library = gene_set_library

    def enrich(self, genes: List[str], **kwargs) -> pd.DataFrame:
        # Submit gene list
        response = requests.post(
            "https://maayanlab.cloud/Enrichr/addList",
            files={"list": (None, "\n".join(genes))}
        )
        user_list_id = response.json()["userListId"]

        # Get enrichment results
        response = requests.get(
            f"https://maayanlab.cloud/Enrichr/enrich",
            params={
                "userListId": user_list_id,
                "backgroundType": self.library
            }
        )

        data = response.json()[self.library]

        return pd.DataFrame({
            "Term": [row[1] for row in data],
            "Adjusted P-value": [row[6] for row in data]
        })
```

## Best Practices

1. **Always return required columns** - `Term` and `Adjusted P-value`
2. **Sort by p-value** - helps with downstream filtering
3. **Handle errors gracefully** - return empty DataFrame on failure
4. **Implement caching** for expensive computations
5. **Log enrichment results** for reproducibility

```python
def enrich(self, genes: List[str], **kwargs) -> pd.DataFrame:
    try:
        result = self._perform_enrichment(genes)
        return result.sort_values("Adjusted P-value")
    except Exception as e:
        print(f"Enrichment failed: {e}")
        return pd.DataFrame(columns=["Term", "Adjusted P-value"])
```
