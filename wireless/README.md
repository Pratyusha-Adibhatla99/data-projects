# 📡 Wireless Research Data Hub

A full-stack Data Engineering platform designed to ingest, manage, and analyze large-scale wireless research datasets (CSV, PCD, and MAT). The system utilizes a Medallion Architecture (Bronze Layer) to handle raw data ingestion into the cloud.

## 🏗️ System Architecture
- **Frontend:** HTML5, CSS3, and Vanilla JavaScript with a responsive dashboard and dynamic analysis modals.
- **Backend:** Flask (Python) with a modular processor design.
- **Cloud Storage:** Azure Blob Storage for raw data (Bronze Layer).
- **Database:** Azure SQL Database for metadata, user management, and data lineage.

## 🚀 Key Features
- **Multi-tenant Ingestion:** Automatic user-based partitioning (e.g., `/aditya/dataset_name/file.csv`).
- **Smart Analysis:** Lightweight metadata extraction for 1GB+ files without memory overflow.
- **Data Lineage:** Automated tracking of who uploaded what, at what time (PST), and from which source.
- **Jupyter Integration:** Direct launching of research notebooks for data exploration.

## 📂 Project Structure
- `backend/services/`: Cloud ingestion logic and database management.
- `backend/processors/`: Specialized handlers for .csv, .mat, and .pcd files.
- `frontend/`: Interactive research dashboard.
