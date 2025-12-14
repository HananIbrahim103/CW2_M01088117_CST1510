# Multi-Domain Intelligence Platform

**Student Name:** Fathima Hanan Ibrahim  
**Student ID:** M01088117  
**Course:** Cybersecurity and Digital Forensics  
**Module:** CST1510 Coursework 2  
****
## System Architecture
**Entry & navigation**  
`Home.py` handles login/registration and routes to:  
- `1_Incidents_Dashboard.py`  
- `2_Datasets_Dashboard.py`  
- `3_IT_Tickets_Dashboard.py`  
- `4_Settings.py`  

using `st.switch_page(...)`.

**Dashboard Pages**  
`1_Incidents_Dashboard.py`, `2_Datasets_Dashboard.py`, and `3_IT_Tickets_Dashboard.py`each implement the Streamlit UI and call into their own data modules for CRUD and analytics.`4_Settings.py`  lets users manage account details, like change passwords and logout.

**Data and persistence layer**  
`db.py` and `database_manager.py` provide a shared SQLite connection and helpers, while `schema.py1 defines the database structure.

Domain  modules (`users.py`, `incidents.py`, `datasets.py`, `it_tickets.py`) encapsulates all queries for their respective tables.

**Authentication and session state**  
`auth_manager.py` handles password hashing, validation, redistration, login, working with `users.py`. Login status is stored in `st.session_state` and checked on each dashboard before rendering.

**AI assistants**  
Each dashboard includes an AI tab that tahes an OpenAI API key, uses a domain-specific system prompt, and streams responses. Chat history is stored per page in st.session_state.

***
## Key Features  

- **Secure authentication and roles**  
  - User registration and login with hashed passwords, plus a role field for basic access control.  

- **Three operational dashboards**  
  - Incidents, Datasets, and IT Tickets dashboards with CRUD operations, filtering, and performance analytics for each domain.  

- **Integrated AI assistants**  
  - Domain-specific AI assistant tab on every dashboard that can answer questions, explain metrics, and help troubleshoot issues.  

- **Unified navigation**  
  - Single landing page that routes users to all dashboards and the Settings page for profile management.  

## Technical Implementation  

- **Framework and UI**  
  - Built with Streamlit multi-page architecture (`Home.py` + `pages/`), using tabs, forms, charts, and session state for a responsive dashboard UI.  

- **Database layer**  
  - SQLite backend accessed through `db.py` and `database_manager.py`, with domain-specific data modules (`users.py`, `incidents.py`, `datasets.py`, `it_tickets.py`) to keep queries encapsulated.  

- **Authentication service**  
  - `auth_manager.py` uses bcrypt for password hashing and verification, plus validation helpers for usernames and passwords.  

- **LLM integration**  
  - OpenAI Python client with streaming chat completions; each dashboard uses a different system prompt and its own `st.session_state` key so conversations remain isolated per page.  

****
## Running the app
1) Register and Login in Home.
2) Choose a Dashboard from the dropdown after Login.
3) On any dashboard’s AI tab, paste your OpenAI API key and start chatting; each page keeps its own conversation history
