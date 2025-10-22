# 📈 Graph Anomaly Detection Platform

A production-grade platform designed to detect complex anomalies like fraud, social media bots, and e-commerce abuse by analyzing the connections and relationships within data. Instead of just looking at individual events, this system builds a "detective's corkboard" (a graph) to spot suspicious patterns and coordinated group activity in real-time.

---

## ✨ Key Features

-   **Graph-Based Detection:** Uses the power of graph algorithms (like centrality and cycle detection) to find sophisticated anomalies that simple rule engines would miss.
-   **Real-Time & Scalable:** Built with FastAPI for high-performance, asynchronous request handling, making it suitable for real-time data streams.
-   **Modular by Design:** Easily extend the platform to new use-cases (e.g., social networks, e-commerce) by adding new "Domain Processors" without changing the core logic.
-   **Persistent Memory:** Integrated with **Neo4j**, a native graph database, to store and query the complex relationships between entities.
-   **Ready for Production:** Comes with **Docker** support for easy deployment and **Prometheus** metrics for monitoring system health and performance.

---

## 🛠️ Tech Stack

-   **Backend:** Python 3.10+
-   **API Framework:** FastAPI
-   **Graph Analytics:** NetworkX
-   **Database:** Neo4j (Graph Database)
-   **Deployment:** Docker, Uvicorn
-   **Monitoring:** Prometheus

---

## 🚀 Getting Started

Follow these steps to get the platform running on your local machine.

### Prerequisites

-   Git
-   [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
-   Python 3.10+ and `pip`.

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/dibyanshu-8/Graph-Anomaly-Detection.git](https://github.com/dibyanshu-8/Graph-Anomaly-Detection.git)
    cd Graph-Anomaly-Detection
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    # Create the environment
    python -m venv .venv

    # Activate it (Windows)
    .\.venv\Scripts\Activate.ps1
    # Activate it (Mac/Linux)
    # source .venv/bin/activate

    # Install required packages
    pip install -r requirements.txt
    ```

3.  **Start the database:**
    Make sure Docker Desktop is running. Then, start the Neo4j database container.
    ```bash
    docker-compose -f docker-compose-db.yml up -d
    ```
    *Wait about 60 seconds for the database to initialize the first time you run this.*

4.  **Run the application:**
    ```bash
    python -m src.api.main
    ```
    The server should now be running!

---

## 💡 How to Use

Once the server is running, you can interact with the API using the automatically generated documentation.

1.  **Open your browser** and go to:
    **[http://localhost:8000/docs](http://localhost:8000/docs)**

2.  **Test the main analysis endpoint:**
    -   Expand the `POST /v1/{domain}/analyze` endpoint.
    -   Click "Try it out".
    -   Set the `domain` to `fraud`.
    -   Use the following JSON as the `Request body` to detect a transaction ring:
        ```json
        {
          "domain": "fraud",
          "data": [
            {
              "transaction_id": "txn_101",
              "sender": "user_A",
              "receiver": "user_B",
              "amount": 150.75,
              "timestamp": "2025-10-23T10:00:00Z"
            },
            {
              "transaction_id": "txn_102",
              "sender": "user_B",
              "receiver": "user_C",
              "amount": 200.00,
              "timestamp": "2025-10-23T10:01:00Z"
            },
            {
              "transaction_id": "txn_103",
              "sender": "user_C",
              "receiver": "user_A",
              "amount": 50.25,
              "timestamp": "2025-10-23T10:02:00Z"
            }
          ],
          "incremental": false
        }
        ```
    -   Click "Execute" to see the analysis results!

---

## 📜 License

This project is licensed under the MIT License.
