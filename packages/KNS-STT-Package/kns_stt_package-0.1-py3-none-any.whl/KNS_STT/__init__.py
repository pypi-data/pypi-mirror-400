from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# 1. SETUP CHROME OPTIONS
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--headless=new")  # Run in headless mode

# --- FIX 1: Disable Headless Mode ---
# Microphone access usually fails in headless mode. 
# We comment this out so the browser opens visibly.
# chrome_options.add_argument("--headless=new") 

# --- FIX 2: Explicitly Allow Microphone Permissions ---
# This ensures the browser doesn't block the site from listening.
prefs = {"profile.default_content_setting_values.media_stream_mic": 1}
chrome_options.add_experimental_option("prefs", prefs)

# Initialize Driver
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

# 2. LOAD WEBSITE
website = "https://allorizenproject1.netlify.app/"
try:
    driver.get(website)
except Exception as e:
    print(f"Error loading website: {e}")
    driver.quit()
    exit()

rec_file = "input.txt"

def listen():
    try:
        print("Waiting for Start button...")
        # Wait for the button to be clickable
        start_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "startButton"))
        )
        
        # --- FIX 3: Robust JavaScript Click ---
        # Sometimes standard .click() fails if elements overlap. JS click is safer.
        driver.execute_script("arguments[0].click();", start_button)
        print("Listening started...")

        last_text = ""

        while True:
            # Wait for output element to exist
            output_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "output"))
            )

            current_text = output_element.text.strip()

            # Check if text is valid and new
            if current_text and current_text != last_text:
                last_text = current_text
                
                # Write to file
                with open(rec_file, "w", encoding="utf-8") as f:
                    f.write(current_text.lower())
                
                print("USER:", current_text)

            # Small delay to prevent CPU spiking
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print("Error during execution:", e)
    finally:
        # --- FIX 4: Cleanup ---
        # Ensure the browser closes if the script crashes
        print("Closing browser...")
        driver.quit()

if __name__ == "__main__":
    listen()