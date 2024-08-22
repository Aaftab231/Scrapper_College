# College Scraper

This Python script scrapes data from [HTCampus](http://www.htcampus.com/) and stores categories, subcategories, and college information into a MongoDB database. The scraper extracts details such as college names, locations, brochures, logos, and additional highlights.

## Features

- Scrapes main categories, subcategories, and colleges.
- Fetches detailed information from each college's page.
- Handles pagination while scraping multiple pages.
- Utilizes MongoDB for storing scraped data.
- Includes error handling and logging for better tracking.

## Requirements

- Python 3.7+
- MongoDB
- Python packages listed in `requirements.txt`

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/college-scraper.git
    cd college-scraper
    ```

2. **Set up a virtual environment (optional but recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Start MongoDB:**  
   Ensure your MongoDB server is running locally on port `27017`.

## Usage

1. **Configure MongoDB:**
   - Ensure MongoDB is installed and running on your local machine.
   - The script connects to MongoDB on `localhost:27017` by default. If your MongoDB instance is running on a different host or port, update the connection settings in `scraper.py`.

2. **Run the Scraper:**

    ```bash
    python scraper.py
    ```

    This command will initiate the scraping process. The script will:
    - Fetch main categories from HTCampus.
    - Scrape subcategories and colleges.
    - Extract detailed information about each college.
    - Save all data to MongoDB collections.

3. **Check Logs:**
   - During execution, the script logs its progress and any errors encountered.
   - Logs are output to the console, and you can adjust the logging level or format by modifying the `logging` configuration in `scraper.py`.

4. **Database Schema:**

    - **Categories Collection (`categories`):** Stores main categories and subcategories.
    - **Colleges Collection (`colleges`):** Stores detailed information about colleges.

5. **Modify and Extend:**
   - You can customize the script to scrape additional data, change target URLs, or adjust the data storage format.
   - For advanced usage, consider implementing features like parallel processing, rate limiting, or enhanced error handling.

## Project Structure

```plaintext
.
├── scraper.py               # Main script for scraping
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies
└── ...

Logging
The script uses Python’s built-in logging module to track progress and errors. Logs include:

Status of fetching URLs.
Whether a category, subcategory, or college is already saved in the database.
Information on saving new entries to MongoDB.
Customizing the Script
You can modify the script to change:

The MongoDB connection settings.
The specific details scraped from each college page.
The logging levels or format.
Potential Improvements
Parallelization: Implement parallel scraping for faster execution.
Batch Insertion: Although batch insertion is ready, you can enhance the efficiency by grouping MongoDB insert operations.
Rate Limiting: Implement rate limiting or sleep intervals to avoid overloading the target site.
License
This project is licensed under the MIT License. See the LICENSE file for details.

Contributions
Contributions are welcome! If you find any issues or have suggestions, please open an issue or submit a pull request.
