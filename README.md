# smart-pharmacy-system
💊 A Flask-based AI-powered pharmacy management system for handling drug inventory, sales and pharmacy monitoring. Each subscriber have the access to only one pharmacy account that he is able to add 5 pharmacist at maximum.

# Project Architecture
The project consist of three main app, each one of them has its own beneficieries, and the apps are:
    1- The Pharmacists app: this app is responsible for providing a simple interface for the pharmacists to:
    - Adding new drug or just increase the the quantity.
    - Handle drugs selling.
    - Searching for drugs and check selling prices, availability (Remaining in shelves and stock), validity, location on shelves.
    - View daily sold and returned drugs.
    - Creating weekly reports.
    - Handle returning sales.
    - Creates timestamps for the pharmacists login and logout times.

    2- The Manager app: this app is providing detailed view for the pharmacy, that help the manager in:
    a- Checking login and logout times for every pharmacist and check online and offline pharmacists.
    b- Provide options like:
        - View Pharmacists weekly reports.
        - Add new pharmacist.
        - Adding new drug.
        - Calculate daily and monthly income.
        - View daily and monthly sold and returned drugs.

    3- The Control app: this app is for the developer provide overview for the system growth and number of pharmacies in the system allowing for future upgradings, will contain:
    1- View totlal number of pharmacies subscribed to the service.
    2- Monitoring the space of the database storage.
