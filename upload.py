import re
from time import sleep

from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def upload_file(driver: WebDriver, video_path: str, title: str, des: str, playlist: str, tags: str = "", kids: bool = False,
                thumbnail_path: str = None):
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "ytcp-button#create-icon"))).click()
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//tp-yt-paper-item[@test-id="upload-beta"]'))).click()
    video_input = driver.find_element(By.XPATH, '//input[@type="file"]')
    video_input.send_keys(video_path)

    _set_basic_settings(driver, title, des, playlist, kids, thumbnail_path)
    _set_advanced_settings(driver, tags)

    # Go to 'Video elements' tab
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "next-button"))).click()
    _set_endcard(driver)

    # Go to 'Visibility' tab
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "next-button"))).click()
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "next-button"))).click()

    _wait_for_processing(driver)

    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
        (By.XPATH, '//tp-yt-paper-radio-button[@name="PUBLIC"]')
    )).click()

    sleep(1)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "done-button"))).click()

    # Wait for the dialog to disappear
    sleep(5)
    print("Upload is complete")


def _wait_for_processing(driver):
    # Wait for processing to complete
    progress_label: WebElement = driver.find_element_by_css_selector("span.progress-label")
    pattern = re.compile(r"(finished processing)|(processing hd.*)|(check.*)")
    current_progress = progress_label.get_attribute("textContent")
    last_progress = None
    while not pattern.match(current_progress.lower()):
        if last_progress != current_progress:
            print(f'Current progress: {current_progress}')
        last_progress = current_progress
        sleep(5)
        current_progress = progress_label.get_attribute("textContent")


def _set_basic_settings(driver: WebDriver, title: str, description: str, playlist: str, isKids, thumbnail_path: str):
    # Title
    title_input: WebElement = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//ytcp-mention-textbox[@label="Title"]//div[@id="textbox"]',))
    )
    title_input.clear()
    title_input.send_keys(title)

    # Descriptions
    description_input: WebElement = driver.find_element(By.XPATH, '//ytcp-mention-textbox[@label="Description"]//div[@id="textbox"]')
    description_input.send_keys(description)

    # Playlist
    driver.find_element(By.XPATH, '//ytcp-video-metadata-playlists/ytcp-text-dropdown-trigger/ytcp-dropdown-trigger').click()
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
        (By.XPATH, f'//ytcp-checkbox-group[@id="playlists-list"]//ytcp-checkbox-lit[@test-id="{playlist}"]')
    )).click()
    driver.find_element(By.XPATH, '//ytcp-playlist-dialog//ytcp-button[@label="Done"]').click()

    # Made for kids
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
        (By.NAME, "VIDEO_MADE_FOR_KIDS_MFK" if isKids else "VIDEO_MADE_FOR_KIDS_NOT_MFK")
    )).click()

    # Thumbnail
    thumbnail_input: WebElement = driver.find_element(By.CSS_SELECTOR, "input#file-loader")
    if thumbnail_path:
        thumbnail_input.send_keys(thumbnail_path)


def _set_advanced_settings(driver: WebDriver, tags: str):
    # Press button 'SHOW MORE'
    driver.find_element(By.ID, "toggle-button").click()

    tags_input: WebElement = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'text-input')))
    tags_input.send_keys(tags)


def _set_endcard(driver: WebDriver):
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
        (By.ID, 'endscreens-button')
    )).click()

    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
        (By.ID, 'import-endscreen-from-video-button')
    )).click()

    save_button: WebElement = driver.find_element(By.ID, 'save-button')
    for i in range(1, 20):
        try:
            # Select endcard type from last video or first suggestion if no prev. video
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
                (By.XPATH, f'//*[@id="dialog"]/div[2]/div/div/div/ytcp-entity-card[{i}]')
            )).click()
            sleep(1)
            if save_button.get_attribute("disabled") is None:
                break
        except (NoSuchElementException, ElementNotInteractableException):
            print("Couldn't find endcard button. Retry in 3s!")
            sleep(3)
    save_button.click()
