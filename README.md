# CUNYFirst_grade_check
Use the CUNYFirst system? Check your grades every five minutes? Now you don't have to!
This script will send you an email whenever there is an update to your grades. It checks every 5 minutes.

## How to use:
Rename example.ini to config.ini. Then, fill it out with your information.

Here's the link to find the proper chromedriver for you: http://chromedriver.chromium.org/

If you use 2FA on gmail, do not despair: https://support.google.com/accounts/answer/185833?hl=en

Assuming you have a virtual environment, or some other way you use pip:

    pip install -r requirements.txt
    python3 driver.py

This will never stop running, you can use ctrl-c or some other kill method to stop it.
I recommend running it once, and taking a look at the generated file "grades.png". Make sure it's looking at the right page.
Then continue running it. You should get an email the first time you properly run the script.

Good luck!
