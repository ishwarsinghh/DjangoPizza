# Django Pizza Store 🍕

A fully functional, data-driven e-commerce web application built with the Django Web Framework. This project serves as a complete digital storefront for a pizza restaurant, featuring a session-based shopping cart, a secure checkout pipeline, and a modernized administrative dashboard.

## 🚀 Features

* **Dynamic Product Catalog:** Users can browse pizzas, utilize category filters (e.g., Vegan, Meat), and navigate through a paginated interface.
* **Session-Based Cart:** Implements Django's `session_key` to allow anonymous users to add items, modify quantities, and remove products from their cart without requiring an account.
* **Secure Checkout Pipeline:** Features dual-layer form validation (client-side HTML attributes and server-side Python verification) to ensure data integrity before order creation.
* **User Authentication & Dashboards:** Secure login/signup flow with role-based access control. Authenticated customers have access to a private dashboard to view past order history.
* **Modernized Admin Panel:** Integrates `django-jazzmin` to transform the default Django admin into a highly responsive, professional dashboard for managing products, categories, and order statuses.

## 🛠️ Tech Stack

* **Backend:** Python 3, Django 
* **Database:** SQLite (Development)
* **Frontend:** HTML5, CSS3, JavaScript
* **Admin Interface:** Django-Jazzmin

