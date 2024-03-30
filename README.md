# Phonepe Pulse Analysis Dashboard

## Overview
Phonepe Pulse Analysis Dashboard is a web application built using Streamlit that allows users to explore and analyze transaction and user data from the Phonepe Pulse dataset. The dashboard provides interactive visualizations and insights to understand transaction trends, user demographics, and top transaction categories across different states and time periods in India.

## Features
- **Data Analysis**: Analyze transaction and user data for India, states, and top transaction categories.
- **Insights Generation**: Generate basic insights through pre-defined queries and visualizations.
- **Interactive Visualizations**: Utilize interactive charts, maps, and tables for data exploration and visualization.
- **Database Integration**: Connects to a MySQL database to fetch and analyze real-time data.
- **Customization**: Customize data filters and options to tailor the analysis based on specific requirements.

## Usage
1. **Installation**:
   - Clone the repository:
     ```
     git clone https://github.com/your_username/phonepe-pulse-analysis.git
     cd phonepe-pulse-analysis
     ```
   - Install dependencies:
     ```
     pip install -r requirements.txt
     ```

2. **Database Configuration**:
   - Update the `get_database_connection()` function in `app.py` with your database credentials.
   - Ensure that the required tables (`aggregated_transaction`, `user_by_map`, `trans_by_map`) exist in your MySQL database.

3. **Running the Application**:
   ```
   streamlit run app.py
   ```

4. **Usage**:
   - Navigate to the desired section (Analysis or Insights) using the navigation tabs.
   - Select filters and options to customize data visualization and analysis.
   - Interact with the charts, maps, and tables to explore detailed information.

## Data Sources
- The transaction and user data are sourced from the Phonepe Pulse dataset, which provides insights into the digital payments landscape in India.

## Contributors
- Sarvan Kumar M
- Linkedin : www.linkedin.com/in/sarvan-kumar-m
- Email : soulsarvankumar007@gmail.com

## License
This project is licensed under the MIT License.

## Acknowledgements
- We acknowledge the support and contributions of the Phonepe Pulse team for providing the dataset and valuable insights.
- Special thanks to the Streamlit community for their open-source contributions and support.
