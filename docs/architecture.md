# Architecture

## Overview
The portfolio uses a microservices architecture with a frontend built using React.js and a backend API built with Node.js/Express. The database is MongoDB, and Docker is used for containerization.

## Components
- Frontend: React application with TypeScript
- Backend: Express server with RESTful API
- Database: MongoDB for data storage
- Deployment: Docker containers for consistent environment

## Diagram
```
   [Client]
      |
      v
[React Frontend] --(API Calls)--> [Node.js Backend]
      |
      v
   [MongoDB]
```
