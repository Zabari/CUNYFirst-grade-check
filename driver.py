import time
import smtplib
import filecmp
import configparser
import os
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options


# Sends an email, from you to yourself, with the message:
# "An update has been made to your grades."
def send_email():
    # Parse config file.
    config = configparser.ConfigParser()
    config.read('config.ini')
    # Load gmail credentials.
    gmail_user = config["gmail_credentials"]["username"]
    gmail_password = config["gmail_credentials"]["password"]
    # Secure server.
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    # Identify yourself to server (this may not be necessary).
    server.ehlo()
    # Login.
    server.login(gmail_user, gmail_password)
    message = "An update has been made to your grades."
    # Send message.
    server.sendmail(gmail_user, [gmail_user], message)


# Takes a screenshot of the page your grades are on.
def screenshot_grades():
    # Parse config file.
    config = configparser.ConfigParser()
    config.read('config.ini')
    # Load chrome, chromedrivers, and options.
    CHROME_PATH = config["chrome"]["chrome_path"]
    CHROMEDRIVER_PATH = config["chrome"]["chromedriver_path"]
    WINDOW_SIZE = "1920,1080"
    chrome_options = Options()
    # Chrome will run in background, and not in a window.
    chrome_options.add_argument("--headless")
    # Set a "virtual" window size.
    chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
    chrome_options.binary_location = CHROME_PATH
    # Pass options and driver to webdriver.
    driver = webdriver.Chrome(
                        executable_path=CHROMEDRIVER_PATH,
                        chrome_options=chrome_options
    )
    # Should set a timeout time of ten seconds.
    driver.implicitly_wait(10)
    # Load CUNYFirst credentials.
    CUNY_FIRST_USERNAME = config["cuny_first_credentials"]["username"]
    CUNY_FIRST_PASSWORD = config["cuny_first_credentials"]["password"]
    # Go to the CUNYFirst homepage.
    driver.get('https://home.cunyfirst.cuny.edu/psp/cnyepprd/EMPLOYEE/EMPL/h/')
    # Find and insert username and password.
    username_box = driver.find_element_by_id('CUNYfirstUsernameH')
    # Clear the suffix @login.cuny.edu
    username_box.clear()
    password_box = driver.find_element_by_id('CUNYfirstPassword')
    username_box.send_keys(CUNY_FIRST_USERNAME)
    password_box.send_keys(CUNY_FIRST_PASSWORD)
    # Submit.
    login_button = driver.find_element_by_id('submit')
    login_button.click()
    # Go to student center.
    student_center_button = (
        driver.find_element_by_id('crefli_HC_SSS_STUDENT_CENTER')
    )
    student_center_button.click()
    # A little hacky, but it seems that the section with the dropdown is like a
    # page within a page. I found this URL which gets you the more important
    # parts and allows you to access what you need.
    driver.get(
        "https://hrsa.cunyfirst.cuny.edu/psc/cnyhcprd/EMPLOYEE/HRMS/c/" +
        "SA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL?FolderPath=" +
        "PORTAL_ROOT_OBJECT.HC_SSS_STUDENT_CENTER&IsFolder=false&" +
        "IgnoreParamTempl=FolderPath%2cIsFolder&PortalActualURL=" +
        "https%3a%2f%2fhrsa.cunyfirst.cuny.edu%2fpsc%2fcnyhcprd%2fEMPLOYEE" +
        "%2fHRMS%2fc%2fSA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL&Portal" +
        "ContentURL=https%3a%2f%2fhrsa.cunyfirst.cuny.edu%2fpsc%2fcnyhcprd" +
        "%2fEMPLOYEE%2fHRMS%2fc%2fSA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL" +
        "&PortalContentProvider=HRMS&PortalCRefLabel=Student%20Center" +
        "&PortalRegistryName=EMPLOYEE&PortalServletURI=https%3a%2f%2f" +
        "home.cunyfirst.cuny.edu%2fpsp%2fcnyepprd%2f&PortalURI=https%3a" +
        "%2f%2fhome.cunyfirst.cuny.edu%2fpsc%2f" +
        "cnyepprd%2f&PortalHostNode=EMPL&NoCrumbs=yes&PortalKeyStruct=yes"
    )
    # Get the selector.
    selector = driver.find_element_by_id("DERIVED_SSS_SCL_SSS_MORE_ACADEMICS")
    select = Select(selector)
    # For right now at least, "Grades" is the 12th index.
    select.select_by_index(12)
    # Go.
    go_button = driver.find_element_by_id('DERIVED_SSS_SCL_SSS_GO_1')
    go_button.click()
    # Change semesters (assuming this is not your last.)
    term_button = (
        driver.find_element_by_id("win0divDERIVED_SSS_SCT_SSS_TERM_LINK")
    )
    term_button.click()
    # Choose the first one down (this should roughly work until your last
    # semester), CUNY adds the next semester pretty early on, and you're
    # trying to get your grades from "last" semester.
    term = driver.find_element_by_id("SSR_DUMMY_RECV1$sels$1$$0")
    term.click()
    # Go.
    go_button = driver.find_element_by_id("DERIVED_SSS_SCT_SSR_PB_GO")
    go_button.click()
    # I couldn't find a better way to do this, given the implicit wait above,
    # and you can't combine implicit and explicit waits. Wait until page loads
    # before taking a screenshot (sleep for 2 seconds).
    time.sleep(10)
    # Save a screenshot.
    driver.save_screenshot("./tmp.png")
    # Close browser.
    driver.quit()


if __name__ == "__main__":
    # Run forever.
    while True:
        # The try/except is because there may be timeout errors naturally,
        # and just because it times out doesn't mean we want to stop running.
        try:
            screenshot_grades()
            print("File saved.")
            # If there is already a file called "grades.png" in the folder.
            if (os.path.exists("./grades.png")):
                # If the new file just saved is not the same as the old.
                if(filecmp.cmp("./tmp.png", "./grades.png") is False):
                    # Send email.
                    send_email()
                    # Replace old file with new file.
                    os.replace("./tmp.png", "./grades.png")
            # If there exists no file called "grades.png".
            else:
                # Make the new file your reference, and send an email.
                os.rename("./tmp.png", "./grades.png")
                send_email()
        except Exception as E:
            # Print out the error if any occured.
            print(E)
            print("There was an error, trying again...")
        # Sleep for 5 minutes, this gives time to ctrl-c as well.
        time.sleep(300)
