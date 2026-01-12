# Based on EQ test norms (simulated data for demonstration)
BENCHMARK_DATA = {
    "age_groups": {
        "Under 18": {"avg_score": 28, "std_dev": 6, "sample_size": 1200},
        "18-25": {"avg_score": 32, "std_dev": 7, "sample_size": 2500},
        "26-35": {"avg_score": 34, "std_dev": 6, "sample_size": 3200},
        "36-50": {"avg_score": 36, "std_dev": 5, "sample_size": 2800},
        "51-65": {"avg_score": 38, "std_dev": 4, "sample_size": 1800},
        "65+": {"avg_score": 35, "std_dev": 6, "sample_size": 900}
    },
    "global": {
        "avg_score": 34,
        "std_dev": 6,
        "sample_size": 12500,
        "percentiles": {
            10: 24,
            25: 29,
            50: 34,
            75: 39,
            90: 42
        }
    },
    "professions": {
        "Student": {"avg_score": 31, "std_dev": 7},
        "Professional": {"avg_score": 36, "std_dev": 5},
        "Manager": {"avg_score": 38, "std_dev": 4},
        "Healthcare": {"avg_score": 39, "std_dev": 3},
        "Education": {"avg_score": 37, "std_dev": 4},
        "Technology": {"avg_score": 33, "std_dev": 6},
        "Creative": {"avg_score": 35, "std_dev": 5}
    }
}
