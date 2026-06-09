# Django Pizza Store 🍕

A full-stack, data-driven e-commerce web application built with the Django Web Framework. This project serves as a complete digital storefront for a pizza restaurant, featuring a session-based shopping cart, a secure checkout pipeline, a modernized administrative dashboard, and a custom-built, fault-tolerant AI customer service chatbot.

## 🚀 Key Features

### Core E-Commerce Pipeline
* **Dynamic Product Catalog:** Users can browse the menu, utilize category filters (e.g., Vegan, Meat), and navigate through a fast, paginated interface.
* **Session-Based Cart:** Implements Django's `session_key` to allow anonymous users to add items, modify quantities, and remove products without requiring an account.
* **Secure Checkout:** Features dual-layer form validation (client-side HTML attributes and server-side Python verification) to ensure data integrity before database insertion.
* **User Authentication & Dashboards:** Secure login/signup flow with role-based access control. Authenticated customers have access to a private dashboard to view past order history and real-time statuses.
* **Modernized Admin Panel:** Integrates `django-jazzmin` to transform the default Django admin into a highly responsive, professional dashboard for managing products, categories, FAQs, and order fulfillment.

### Advanced AI Customer Support Engine
* **Deterministic NLP Routing:** Utilizes `RapidFuzz` for typo-tolerant string matching, allowing the backend to instantly intercept and answer common queries (e.g., "cheapest items", "delivery fee", "cancel order") without unnecessary API latency.
* **Context-Aware RAG Pipeline:** Dynamically queries the Django ORM to inject real-time product inventory, user-specific order statuses, and Admin FAQs into the local LLM's system prompt context.
* **State-Aware Security Guardrails:** The chatbot evaluates `request.user.is_authenticated` to securely block anonymous users from querying sensitive order tracking information while maintaining open conversational paths for general inquiries.
* **Fault-Tolerant Architecture:** Engineered with strict execution timeouts and `try/except` fallback mechanisms. If the local LLM server stalls or crashes, the backend safely intercepts the failure and falls back to a deterministic customer support message, preventing UI freezes.

## 🛠️ Tech Stack

* **Backend:** Python 3, Django
* **Database:** SQLite (Development)
* **AI & NLP:** `openai` (Python SDK), `RapidFuzz`, Local LLM Inference (LM Studio)
* **Frontend:** HTML5, CSS3, JavaScript
* **Admin Interface:** Django-Jazzmin
