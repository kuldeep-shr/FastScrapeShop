# 🦷 Dental Stall Scraper

Welcome to the **Dental Stall Scraper**! This project is a web scraping tool built with FastAPI, designed to scrape product details from the Dental Stall website and store them efficiently using a caching mechanism. 🚀

## 📋 Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Environment Variables](#environment-variables)
- [Cache Management](#cache-management)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- Scrape product details (title, price, image) from Dental Stall.
- Cache the scraped data to avoid redundant requests.
- Save the scraped data to a JSON file.
- Simple token-based authentication for secure API access.

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- `pip` (Python package installer)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/kuldeep-shr/dental-stall-scraper.git

   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   Create a `.env` file in the root directory with the following content:

   ```ini
   API_TOKEN=your_api_token
   CACHE_HOST=your_cache_host
   CACHE_PORT=your_cache_port
   PROXY=http://your_proxy_server:port
   ```

### Running the Application

1. **Start the FastAPI server:**

   ```bash
   uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ```

2. **Access the API documentation:**

   Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to explore the available endpoints using the interactive Swagger UI.

## 🛠 API Endpoints

### Authentication

All endpoints require a valid `API_TOKEN` passed in the Authorization header.

### Scrape Products

- **POST /api/scrape**

  Scrape products from the Dental Stall website.

  **Request:**

  ```json
  {
    "num_pages": 1
  }
  ```

  **Response:**

  ```json
  {
    "message": "Scraping completed"
  }
  ```

## 🌐 Environment Variables

Ensure you have a `.env` file with the following variables:

```ini
API_TOKEN=your_api_token
CACHE_HOST=your_cache_host
CACHE_PORT=your_cache_port
PROXY=http://your_proxy_server:port
```

## 🔄 Cache Management

The scraper uses a TTL (Time-To-Live) cache to store product data temporarily. This helps reduce redundant requests and speeds up the scraping process.

## 🤝 Contributing

We welcome contributions! Please fork the repository and submit a pull request with your changes.

## Made with ❤️ by Kuldeep

### Notes:

- Replace `yourusername` with your GitHub username.
- Customize the URL for your repository.
- Add any additional information or sections relevant to your project.

This README.md is designed to be informative and engaging, making it easy for others to understand and contribute to your project.
