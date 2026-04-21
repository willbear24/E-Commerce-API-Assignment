# Relational Databases & API Rest Development Project | Building an E-commerce API with Flask, SQLAlchemy, Marshmallow, and MySQL

## About
This was a project completed for Coding Temple as part of the Software Engineering curriculum. The project description was as follows:
In this assignment, you will create a fully functional e-commerce API using Flask, Flask-SQLAlchemy, Flask-Marshmallow, and MySQL. The API will manage Users, Orders, and Products with proper relationships, including One-to-Many and Many-to-Many associations. You will also learn to set up a MySQL database, define models, implement serialization with Marshmallow, and develop RESTful CRUD endpoints.

## Key Learnings

### Learning Objectives
- Database Design: Create models with relationships in SQLAlchemy and MySQL.
- API Development: Develop a RESTful API with CRUD operations using Flask.
- Serialization: Use Marshmallow schemas for input validation and data serialization.
- Testing: Ensure the API is fully functional using Postman and MySQL Workbench.

### What I Built
- A Flask API backed by MySQL for three core resources:
	- Users
	- Orders
	- Products
- SQLAlchemy models using:
	- One-to-Many relationship: `User -> Order`
	- Many-to-Many relationship: `Order <-> Product` through an association table
- Marshmallow schemas for:
	- Request validation
	- Response serialization
	- Nested output for order/product relationships

### API Skills I Practiced
- Building REST endpoints for create, read, update, and delete operations.
- Designing routes for relationship operations, including:
	- Adding a product to an order
	- Removing a product from an order
	- Retrieving all orders for a user
	- Retrieving all products for an order
- Returning consistent status codes and validation messages for common failure cases.

### Database Design Lessons
- A many-to-many relationship does not require a direct `product_id` column on `orders`.
- Instead, the link is stored in a join table (`order_product`) with foreign keys.
- Relationship behavior can appear broken if schemas do not expose related fields in serialized output.

### Serialization Lessons
- Marshmallow schema configuration matters as much as model configuration.
- Foreign key fields may need explicit inclusion (for example, `include_fk = True`).
- Nested schema fields are useful for making relationship updates visible in API responses.

### Testing and Debugging Lessons
- Postman helped verify route paths, HTTP methods, payload shape, and status codes.
- MySQL Workbench helped confirm that records and association table rows were actually created/updated.
- A `400` response often indicated validation issues (schema mismatch, missing fields, invalid IDs), not server crashes.

### Biggest Takeaways
- Data modeling decisions directly shape API route design.
- Clean validation and clear error responses make debugging much faster.
- Keeping schema, models, and endpoints aligned is key to avoiding hidden relationship bugs.

### Tools Used
- Python
- Flask
- Flask-SQLAlchemy
- Flask-Marshmallow
- Marshmallow-SQLAlchemy
- MySQL
- MySQL Workbench
- Postman

