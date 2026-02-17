# 🏠 Buffalo Housing Data Pipeline

## 📌 Project Overview
Designed and implemented an end-to-end data pipeline to collect, clean, and standardize rental listing data from multiple real estate platforms in Buffalo, NY.

The project focuses on transforming semi-structured web data into a structured, analysis-ready dataset.

## ⚙️ Key Contributions
* **Developed web scrapers** using `Python`, `BeautifulSoup`, and `requests` to extract 750+ rental listings.
* **Designed a standardized schema** to unify inconsistent data structures across platforms.
* **Implemented data transformation and cleaning logic** using `pandas` and `regex` to:
  * Normalize currency formats
  * Extract structured min/max price ranges
  * Parse bedroom ranges into numeric features
* **Engineered derived features** (`min_price`, `max_price`, `min_bedrooms`, `max_bedrooms`) for analytical querying.
* **Improved data quality** by removing unreliable data sources.
* **Structured cleaned datasets** for downstream analytics and visualization workflows.

## 🛠️ Technologies Used
* **Languages:** Python
* **Libraries:** BeautifulSoup, requests, pandas, Regular Expressions (re)
* **Tools:** Git, Jupyter Notebooks

## 🎯 Skills Demonstrated
* Data ingestion from heterogeneous web sources
* Schema normalization & feature engineering
* Cleaning and transforming semi-structured data
* Data quality validation
* Reproducible project structuring and version control
