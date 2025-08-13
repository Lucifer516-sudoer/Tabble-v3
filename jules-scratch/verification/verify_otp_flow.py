from playwright.sync_api import sync_playwright, expect
import time

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    try:
        # Step 1: Navigate to the homepage and open the setup dialog
        page.goto("http://localhost:8000/")
        experience_button = page.get_by_role("button", name="Experience Now")
        expect(experience_button).to_be_visible(timeout=10000)
        experience_button.click()

        # Step 2: Fill out the database and password
        db_selector = page.get_by_label("Database Name")
        expect(db_selector).to_be_visible(timeout=5000)
        db_selector.select_option("tabble_new")

        password_input = page.get_by_label("Database Password")
        expect(password_input).to_be_visible(timeout=5000)
        password_input.fill("myhotel")

        connect_button = page.get_by_role("button", name="Connect to Database")
        connect_button.click()

        # Step 3: Enter the table number
        table_input = page.get_by_label("Table Number")
        expect(table_input).to_be_visible(timeout=5000)
        table_input.fill("10")

        continue_button = page.get_by_role("button", name="Continue")
        continue_button.click()

        # Step 4: We should now be on the login page. Fill the phone number.
        phone_input = page.get_by_label("Phone Number")
        expect(phone_input).to_be_visible(timeout=10000)
        phone_input.fill("+919876543210")

        send_otp_button = page.get_by_role("button", name="Continue with Phone")
        send_otp_button.click()

        # Step 5: Get the OTP from the backend log file
        # It might take a moment for the log to be written
        time.sleep(2)
        with open("backend.log", "r") as f:
            log_content = f.read()

        otp_line = [line for line in log_content.splitlines() if "OTP:" in line][-1]
        otp = otp_line.split("OTP:")[1].strip()

        # Step 6: Enter the OTP
        otp_input = page.get_by_label("Verification Code")
        expect(otp_input).to_be_visible(timeout=5000)
        otp_input.fill(otp)

        verify_button = page.get_by_role("button", name="Verify")
        verify_button.click()

        # Step 7: Assert that the username dialog appears and take a screenshot
        username_dialog_heading = page.get_by_role("heading", name="Create Your Account")
        expect(username_dialog_heading).to_be_visible(timeout=5000)

        page.screenshot(path="jules-scratch/verification/otp_flow_success.png")

        print("Successfully verified the OTP flow.")

    except Exception as e:
        print(f"An error occurred: {e}")
        page.screenshot(path="jules-scratch/verification/error.png")
    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
