# 🚌 CTS Bus Tracking System: Real-Time IoT Data Ingestion Platform

### *A High-Frequency GPS Telemetry System for University Transit*

![Java](https://img.shields.io/badge/Backend-Spring%20Boot-red) ![Angular](https://img.shields.io/badge/Frontend-Angular%2014-orange) ![Database](https://img.shields.io/badge/Database-MySQL%20%7C%20H2-blue) ![Role](https://img.shields.io/badge/Focus-Data%20Engineering-yellow)

## 📖 Project Overview
The **CTS Bus Tracking System** is an end-to-end IoT platform designed to handle **high-frequency GPS telemetry data**. While functioning as a user-facing transit app, the core architecture is built to solve data engineering challenges: **ingesting**, **validating**, and **normalizing** real-time location streams from moving assets.

---

## 🛠️ Technical Architecture & Data Flow

### **1. Data Ingestion Layer **
* **Source:** Simulated IoT GPS trackers sending high-frequency updates (1-5 second intervals).
* **Protocol:** RESTful API (`POST /bus/update/gps`) handling concurrent requests.
* **Payload:** Raw telemetry including `latitude`, `longitude`, `route_id`, and `timestamp`.

### **2. Data Processing & Validation **
Before storage, raw data passes through a custom Java-based **Validation Service** to ensure data integrity:
* **Null-Island Filtering:** Automatically rejects invalid `(0.0, 0.0)` coordinates often caused by sensor cold-starts.
* **Geofence Validation:** filters out outliers falling outside the operational bounds (e.g., coordinates outside New York State).
* **Precision Normalization:** Standardizes floating-point GPS data to 6 decimal places for consistent storage and spatial querying.

### **3. Storage & Serving **
* **Operational Store:** MySQL / H2 Database for persisting current state and historical route data.
* **Frontend Visualization:** Angular dashboard polling the normalized data to render real-time movement on an interactive map.

---

### **✅ High-Frequency Data Ingestion API**
Designed a specialized endpoint to handle rapid-fire location updates from multiple buses simultaneously.
```java
// Controller: Accepts raw telemetry stream
@PostMapping(value = "/update/gps")
public String updateGpsLocation(@RequestParam("routeId") int routeId,
                                @RequestParam("lat") String lat,
                                @RequestParam("lon") String lon) {
    service.updateBusLocation(routeId, lat, lon); // Triggers ETL process
    return "Telemetry Ingested";
}
```
### Defensive programming to reduce inconsistent tracking records
```
// Service: The "Transformation" step in ETL
public void updateBusLocation(int routeNo, String latStr, String lonStr) {
    // 1. REJECT 'Null Island' (Sensor Failures)
    if (latitude == 0.0 && longitude == 0.0) return;

    // 2. NORMALIZE Precision (Standardization)
    double normalizedLat = Math.round(latitude * 1000000.0) / 1000000.0;
    
    // 3. LOAD into Database
    repository.save(route);
}
```
### Category,Technologies
Backend / Processing,"Java, Spring Boot, REST APIs"
Database / Storage,"MySQL, H2 (In-Memory for testing)"
Frontend / Viz,"Angular, TypeScript, Leaflet Maps"
Tools & DevOps,"Git, Maven, Postman (API Testing)"
### **🔧 How to Run Locally**
1. Clone the Repository
```
git clone [https://github.com/YOUR_USERNAME/data_projects.git](https://github.com/YOUR_USERNAME/data_projects.git)
```
2. Start the Backend (Ingestion Engine)
```
cd "CTS bus tracking/new final project/Nbackend"
mvn spring-boot:run
```
3. Start the Frontend (Dashboard)
```
cd "CTS bus tracking/new final project/Nfrontend"
npm start
```
4. Simulate GPS Data Stream
Used curl to mimic a bus sensor sending data:
```
curl -X POST "http://localhost:10090/bus/update/gps?routeId=101&lat=42.8864&lon=-78.8784"
```

