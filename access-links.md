# 🚀 Laiqa Growth Agent Access Links

This file contains the local links to access your agent's services. Note that **Docker Desktop** must be running for these links to work.

### 🧠 Main Dashboard (n8n)
*   **Link:** [http://localhost:5678](http://localhost:5678)
*   **Purpose:** The "brain" of your agent. This is where you import workflows, monitor execution, and approve actions.
*   **Initial Setup:** You will be asked to create an owner account on your first visit.

### 🛡️ Privacy Sanitiser (Service)
*   **Health Check:** [http://localhost:8001/health](http://localhost:8001/health)
*   **Purpose:** Automatically redacts names, emails, and phone numbers from your ad data before sending it to the AI (Gemini).

### 📚 Vector Bridge (Service)
*   **Health Check:** [http://localhost:8002/health](http://localhost:8002/health)
*   **Purpose:** The bridge between your data and the Gemini Embedding model. It stores your "knowledge base" (brand guidelines, past campaign results) in ChromaDB.

### 🗄️ Databases (Backend Only)
*   **Vector DB (Chroma):** [http://localhost:8000](http://localhost:8000) (API only)
*   **Postgres DB:** `localhost:5432` (Requires a database tool like DBeaver or pgAdmin to view).

---

### 🛠️ Maintenance Commands

*   **Start the Agent:** `docker-compose up -d`
*   **Stop the Agent:** `docker-compose down`
*   **Check Status:** `docker-compose ps`
*   **View Logs:** `docker-compose logs -f n8n`
