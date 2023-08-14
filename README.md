# purplepricer-discord
 
purplepricer-discord is a script that connect's to my pricer's SSE server and sends price updates to provided discord webhooks.

## Requirements
+ Python 3.10+

## Installation

+ Clone the repository to your local machine:
    
    ```bash
    git clone git@github.com:purplebarber/purplepricer-discord.git
    ```
+ Install the required dependencies while inside the project directory:

    ```bash
    pip install -r requirements.txt
    ```
+ Update the config.json file with your specific settings and preferences

+ Run the main.py script:
    ```bash
    python main.py
    ```

+ To run with PM2:
    ```bash
    pm2 start main.py --interpreter python3.10 --name purplepricer-discord --time --cron '0 */6 * * *'
    ```
