import pandas as pd
import pkg_resources

_DATASETS = {
    "quranic": "quranic_benchmark_2000.csv",
    "msa_dailyuse": "msa_dailyuse_benchmark_2000.csv",
    "msa_bibliographic": "msa_bibliographic_benchmark_2000.csv",
    "all": "all_domain_mix_benchmark_6000.csv",
}

def get_available_domains():
    return list(_DATASETS.keys())

def load_dataset(domain: str) -> pd.DataFrame:
    if domain not in _DATASETS:
        raise ValueError(
            f"Invalid domain '{domain}'. "
            f"Available: {get_available_domains()}"
        )

    path = pkg_resources.resource_filename(
        __name__, f"data/{_DATASETS[domain]}"
    )
    return pd.read_csv(path)
