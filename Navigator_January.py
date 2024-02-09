import logging
import subprocess
import pyautogui
import time
import random
import cv2
import numpy as np
import math
from humancursor import SystemCursor
from humancursor.utilities.human_curve_generator import HumanizeMouseTrajectory
import pytweening
from PIL import ImageChops
import numpy as np
from bs4 import BeautifulSoup
import os
import json


issue_folder_path = "/home/..."  # Replace with your directory path
html_file_path = "/home/..."  # Replace with your directory path
json_save_path = "/home/..."  # Replace with your directory path
formatted_date = "2022-01-01"  # Replace with your date

# Configuration
PATH_TO_SCREENSHOT_CUTOUT = '/home/...'
CONTENT = '/home/...'
CONTENT_GREY = '/home/...'
SAVE = '/home/...'
DOWNLOAD = '/home/...'
CONTENT_CLICKED = '/home/...'

save_directory = "/home/..." # Replace with your directory path

page = 1

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ChromeController:

    def open_new_chrome_window(self, url):
        try:
            subprocess.Popen(["chromium-browser","--disable-gpu", url])
            print(f"Opened Chromium")
        except Exception as e:
            logging.error(f"Error opening new Chromium window: {e}")


    def activate_chrome(self):
        try:
            print(f"Trying to activate Chromium")
            window_id = subprocess.check_output(["xdotool", "search", "--onlyvisible", "--name", "Chromium"])
            subprocess.run(["xdotool", "windowactivate", window_id.strip()])
            logging.info("Chromium activated successfully.")
        except Exception as e:
            logging.error(f"Error activating Chromium: {e}")

    def make_chrome_full_screen(self):
        try:
            print(f"Trying to fullscreen")
            window_id = subprocess.check_output(["xdotool", "search", "--onlyvisible", "--name", "Chromium"])
            subprocess.run(["xdotool", "key", "--window", window_id.strip(), "F11"])
            logging.info("Made Chromium full screen.")
        except Exception as e:
            logging.error(f"Error making Chromium full screen: {e}")


    def close_chrome_window(self):
        try:
            print(f"Trying to close")
            window_id = subprocess.check_output(["xdotool", "search", "--onlyvisible", "--name", "Chromium"])
            subprocess.run(["xdotool", "windowclose", window_id.strip()])
            logging.info("Closed Chromium window.")
        except Exception as e:
            logging.error(f"Error closing Chromium window: {e}")
    
    def get_current_url(self):
        try:
            # Focus the address bar
            subprocess.run(['xdotool', 'key', 'ctrl+l'])
            # Copy the URL
            subprocess.run(['xdotool', 'key', 'ctrl+c'])
            # Get clipboard content
            result = subprocess.run(['xclip', '-o', '-selection', 'clipboard'], capture_output=True, text=True)
            print(result.stdout.strip())
            return result.stdout.strip()
        except Exception as e:
            logging.error(f"Error getting current URL: {e}")
            return None
    
    def navigate_to_url(self, url):
        try:
            # Focus the address bar
            subprocess.run(['xdotool', 'key', 'ctrl+l'])
            # Type the URL
            subprocess.run(['xdotool', 'type', url])
            # Press Enter
            subprocess.run(['xdotool', 'key', 'Return'])
            logging.info(f"Navigated to {url}")
        except Exception as e:
            logging.error(f"Error navigating to URL {url}: {e}")

class NavigateCursor:    

    def point_dist(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def move_cursor_with_duration(self, target_x, target_y):
        cursor = SystemCursor()
        start_point = pyautogui.position()
        end_point = [target_x, target_y]

        # Calculate distance between start and end points
        distance = ((end_point[0] - start_point[0]) ** 2 + (end_point[1] - start_point[1]) ** 2) ** 0.5

        # Use helper point only if distance is at least 300 pixels
        use_helper_point = distance >= 300
        if use_helper_point:
            diff_x, diff_y = end_point[0] - start_point[0], end_point[1] - start_point[1]
            helper_point = [end_point[0] - min(200, abs(diff_x)) * (1 if diff_x > 0 else -1),
                            end_point[1] - min(200, abs(diff_y)) * (1 if diff_y > 0 else -1)]

        # Adjust curve parameters based on distance
        curve_strength = max(0.1, 1 - distance / 1000)  # Adjust this formula as needed
        offset_boundary = max(10, 50 * curve_strength)
        distortion = max(0.5, 1.5 * curve_strength)

        # Define HumanizeMouseTrajectory parameters
        curve_params = {
            'offset_boundary_x': offset_boundary,
            'offset_boundary_y': offset_boundary,
            'knots_count': 1 if use_helper_point else 0,  # Less knots for shorter distances
            'distortion_mean': distortion,
            'distortion_st_dev': distortion,
            'distortion_frequency': 0.8,
            'tween': pytweening.easeInOutQuad,
            'target_points': 100
        }

        # Move to Helper Point (if applicable)
        if use_helper_point:
            helper_curve = HumanizeMouseTrajectory(from_point=start_point, to_point=helper_point, **curve_params)
            cursor.move_to(helper_point, duration=0.05, human_curve=helper_curve, steady=False)
            time.sleep(0.2)  # Adjust pause duration as needed

        # Move to End Point
        end_curve_params = curve_params.copy()
        end_curve_params['target_points'] = 150  # More points for smoother movement
        end_curve = HumanizeMouseTrajectory(from_point=helper_point if use_helper_point else start_point, 
                                            to_point=end_point, **end_curve_params)
        cursor.move_to(end_point, duration=0.1, human_curve=end_curve, steady=False)


    def find_and_click(self, template_image_path, click, i):   # i is the delay, click = 1 means it will lick, other number just hover

        time.sleep(i)
        # Take a screenshot of the entire screen
        logging.info("Taking a screenshot of the entire screen.")
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)  # Convert to a numpy array
        screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)

        # Read the template image
        logging.info("Reading the template image.")
        template_image = cv2.imread(template_image_path, 0)  # Read in grayscale

        # Template matching
        logging.info("Performing template matching.")
        res = cv2.matchTemplate(screenshot_gray, template_image, cv2.TM_CCOEFF_NORMED)

        # Threshold for detection
        threshold = 0.8

        # Get the locations where the matching is above the threshold
        loc = np.where(res >= threshold)

        if np.any(res >= threshold):
            logging.info("Match found, preparing to click.")
        else:
            logging.warning("No match found. Exiting.")
            return False

        # Assuming you want to click the first match
        for pt in zip(*loc[::-1]):  # Switch columns and rows
            # Adjust for scaling
            adjusted_x = pt[0] + 10
            adjusted_y = pt[1] + 5

            logging.info(f"Moving to coordinates: ({adjusted_x}, {adjusted_y}) and clicking.")
            # Use the custom function for moving the cursor
            self.move_cursor_with_duration(adjusted_x, adjusted_y)
            if click == 1:
                pyautogui.click()

            # Break after the first match to avoid multiple clicks
            break

        return True

class Screenshot:

    def screen_save(self, page, z):
        save_directory = os.path.join(issue_folder_path, str(page))

        start_time = time.time()
        while True:
            screenshot = pyautogui.screenshot()
            has_blue = self.preprocess_blue(screenshot)
            cropped_screenshot = self.preprocess_grey(screenshot, z)
            has_grey, _ = self.find_grey(cropped_screenshot, (51, 51, 51), 50, 50, 0.9)

            if not has_blue and not has_grey:
                filename = os.path.join(save_directory, f"{z}.png")
                screenshot.save(filename)
                logging.info(f"Screenshot saved as {filename}")
                z += 1
                break
            else:
                if time.time() - start_time > 10:
                    error_message = f"Timeout on page {page}. "
                    if has_blue and has_grey:
                        error_message += "Both blue and grey pixel checks failed."
                    elif has_blue:
                        error_message += "Blue pixel check failed."
                    else:
                        error_message += "Grey pixel check failed."
                    print(error_message)
                    return 'error', page, z  # Return a tuple indicating error, current page, and z value

                time.sleep(0.5)  # Wait for 0.5 seconds before rechecking

        return 'success', page, z

    def compare_screenshots(self, img1, img2):
        # Convert images to grayscale
        img1 = img1.convert('L')
        img2 = img2.convert('L')

        # Compute the difference and calculate the percentage of similarity
        diff = ImageChops.difference(img1, img2)
        np_diff = np.array(diff)
        percentage = (np_diff < 50).sum() / np_diff.size

        return percentage
    
    def preprocess_grey(self, screenshot, x):
        screen_width, screen_height = screenshot.size
        if x % 2 != 0:  # Left screenshot
            search_area = (175, 268, screen_width - 35, screen_height - 35)
        else:  # Right screenshot
            search_area = (0, 268, screen_width - 160, screen_height - 35)

        cropped_img = screenshot.crop(search_area)
        return cropped_img
    
    def find_grey(self, screenshot, target_color, width, height, match_threshold=0.9):
        np_screenshot = np.array(screenshot)
        target_color_np = np.array(target_color)

        for y in range(0, np_screenshot.shape[0] - height + 1, height):
            for x in range(0, np_screenshot.shape[1] - width + 1, width):
                cropped_area = np_screenshot[y:y+height, x:x+width]
                cropped_area_rgb = cropped_area[:, :, :3]  # Slicing to exclude the alpha channel
                matches = np.all(cropped_area_rgb == target_color_np, axis=-1)
                match_percentage = np.sum(matches) / (width * height)

                if match_percentage >= match_threshold:
                    return True, (x, y, x + width, y + height)
        
        return False, None
    
    def find_blue(self, screenshot, area, main_color, deviation_color, threshold):
        cropped_img = screenshot.crop((area[0], area[1], area[0] + area[2], area[1] + area[3]))
        np_image = np.array(cropped_img)
        match_count = np.sum(np.all(np_image == main_color, axis=-1))
        match_count += np.sum(np.all(np_image == deviation_color, axis=-1))
        total_pixels = area[2] * area[3]
        match_percentage = (match_count / total_pixels) * 100
        return match_percentage >= threshold

    def preprocess_blue(self, screenshot):
        screen_width, screen_height = screenshot.size
        area = (screen_width - 61, screen_height - 98, 60, 60)
        main_color = (147, 168, 207)
        deviation_color = (141, 161, 198)
        return self.find_blue(screenshot, area, main_color, deviation_color, 2)

class MovementController:
    def move_right(self, steps=12):
        for _ in range(steps):
            pyautogui.press('right')
            time.sleep(0.5)

    def move_left(self, steps=12):
        for _ in range(steps):
            pyautogui.press('left')
            time.sleep(0.5)

    def move_down(self, steps=7):
        for _ in range(steps):
            pyautogui.press('down')
            time.sleep(0.5)

    def move_up(self, steps=7):
        for _ in range(steps):
            pyautogui.press('up')
            time.sleep(0.5)

def random_sleep(center_duration):
    min_duration = max(center_duration - 0.5, 0.1)
    max_duration = center_duration + 0.5
    sleep_time = random.uniform(min_duration, max_duration)
    time.sleep(sleep_time)

class HtmlFolder:

    def parse_html(self, file_path, json_save_path):
        with open(file_path, 'r') as file:
            content = file.read().replace("=3D", "=")  # Replace =3D with =
            soup = BeautifulSoup(content, 'html.parser')
            toc_items = soup.find_all('li', class_='toc_item')

            data = []
            format_correct = True
            for item in toc_items:
                href = item.find('a', class_='toc_link')
                title = item.find('span', class_='toc_chapter')
                page = item.find('span', class_='toc_page-number')

                if href and title and page:
                    data.append({
                        'href': href['href'],
                        'title': title.get_text(strip=True),
                        'page': page['data-page']
                    })
                else:
                    format_correct = False
                    break

            # Save the data to JSON in the specified path
            with open(json_save_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)

            # Print statement about the data format
            if format_correct:
                print(f"Data extracted in the expected format and saved to {json_save_path}")
            else:
                print(f"Warning: Data in {file_path} did not have the expected format.")

            return format_correct

def main(page):
    # Create an instance of ChromeController
    chrome_controller = ChromeController()

    # Modify the URL if webpage_nr is a number, otherwise use the default logic
    
    url = "your/url/here"
    chrome_controller.open_new_chrome_window(url)
    print(f"Opened new tab, waiting now...")
    time.sleep(10)  # Wait for browser to open
    print(f"Wait complete")
    
    
    cursor_navigator = NavigateCursor()
    content = cursor_navigator.find_and_click(CONTENT, 1, 1)

    if not content:
        print("Did not find normal content, try grey_content")
        content_grey = cursor_navigator.find_and_click(CONTENT_GREY, 1, 1)
        if content_grey:
            print("Clicked Content Grey")
    
    time.sleep(2)

    # Simulate pressing 'Ctrl+S' to open the save dialog
    pyautogui.hotkey('ctrl', 's')  # adjust based on your OS
    save = cursor_navigator.find_and_click(SAVE, 1, 2)

    cursor_navigator.find_and_click(DOWNLOAD, 1, 3) 
    

    content_clicked = cursor_navigator.find_and_click(CONTENT_CLICKED, 1, 1)
    if content_clicked:
        print("clicked content close")
    else:
        print("failed to click content close")
        time.sleep(1)
    
    # Parse the HTML, Save the data to JSON, and create the folders   
    html_folder = HtmlFolder()
    data = html_folder.parse_html(html_file_path, json_save_path)
    max_pages = html_folder.find_relevant_page(data)
    html_folder.create_folders(formatted_date, max_pages)

    


if __name__ == "__main__":
    main(page)
