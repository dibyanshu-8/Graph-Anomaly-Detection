# Graph Anomaly Detection Platform

A production-grade platform designed to detect complex anomalies like fraud by analyzing the connections and relationships within data. Instead of just looking at individual events, this system builds a graph to spot suspicious patterns and coordinated group activity in real-time.

---

## Key Features

-   **Graph-Based Detection:** Uses the power of graph algorithms (like centrality and cycle detection) to find sophisticated anomalies that simple rule engines would miss.
-   **Real-Time & Scalable:** Built with FastAPI for high-performance, asynchronous request handling, making it suitable for real-time data streams.
-   **Modular by Design:** Easily extend the platform to new use-cases (e.g., social networks, e-commerce) by adding new "Domain Processors" without changing the core logic.
-   **Persistent Memory:** Integrated with **Neo4j**, a native graph database, to store and query the complex relationships between entities.
-   **Ready for Production:** Comes with **Docker** support for easy deployment and **Prometheus** metrics for monitoring system health and performance.

---

## Tech Stack

-   **Backend:** Python 3.12.10
-   **API Framework:** FastAPI
-   **Graph Analytics:** NetworkX
-   **Database:** Neo4j (Graph Database)
-   **Deployment:** Docker, Uvicorn
-   **Monitoring:** Prometheus

---

