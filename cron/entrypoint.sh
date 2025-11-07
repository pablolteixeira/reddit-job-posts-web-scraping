#!/bin/bash

# Copy crontab file to the cron.d directory
cp /etc/cron.d/scraper-cron /etc/cron.d/scraper-cron-active

# Give execution rights on the cron job
chmod 0644 /etc/cron.d/scraper-cron-active

# Apply cron job
crontab /etc/cron.d/scraper-cron-active

# Create the log file to be able to run tail
touch /var/log/cron.log

# Run the scraper immediately on startup
echo "Running scraper on startup..."
cd /app && python src/scraper.py 2>&1 | tee -a /var/log/cron.log
if [ $? -eq 0 ]; then
    echo "Initial scraper run completed. Cron will handle subsequent runs every 2 hours."
else
    echo "ERROR: Initial scraper run failed with exit code $?. Check logs above."
fi

# Start cron in foreground and tail the log
cron && tail -f /var/log/cron.log
