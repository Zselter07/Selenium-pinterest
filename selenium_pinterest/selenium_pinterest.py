from typing import List, Dict, Optional
import time, json

from selenium_firefox.firefox import Firefox, By, Keys

from .url_creator import UrlCreator

PT_URL = "https://www.pinterest.com/"

class Pinterest:
    def __init__(
        self,
        cookies_folder_path: str,
        extensions_folder_path: str,
        host: Optional[str] = None,
        port: Optional[int] = None
    ):
        self.browser = Firefox(cookies_folder_path, extensions_folder_path, host=host, port=port)
        self.url_creator = UrlCreator()
        
        try:
            self.browser.get(PT_URL)
            time.sleep(1.5)

            if self.browser.has_cookies_for_current_website():
                self.browser.load_cookies()
                time.sleep(1.5)
                self.browser.refresh()
            else:
                input('Log in then press enter')
                self.browser.get(PT_URL)
                time.sleep(1.5)
                self.browser.save_cookies()
        except Exception as e:
            print(e)
            self.browser.driver.quit()

            raise

    def follow(self, user_name: str):
        self.browser.get(self.url_creator.user_url(user_name))
        user = self.browser.find(By.XPATH, "//div[contains(@class, 'tBJ dyH iFc yTZ erh tg7 mWe')]")
        time.sleep(0.5)
        if user != None and user.text == "Follow":
            user.click()
            time.sleep(0.5)
        else:
            return False
            
        user = self.browser.find(By.XPATH, "//div[contains(@class, 'tBJ dyH iFc yTZ erh tg7 mWe')]") or self.browser.find(By.XPATH, "//div[contains(@class, 'tBJ dyH iFc yTZ pBj tg7 mWe')]")
        
        if user.text != None:
            return user.text == "Following"

    def unfollow(self, user_name: str):
        self.browser.get(self.url_creator.user_url(user_name))
        user = self.browser.find(By.XPATH, "//div[contains(@class, 'tBJ dyH iFc yTZ erh tg7 mWe')]")
        time.sleep(0.5)
        if user != None and user.text == "Following":
            user.click()
            time.sleep(0.5)
        else:
            return False
            
        user = self.browser.find(By.XPATH, "//div[contains(@class, 'tBJ dyH iFc yTZ erh tg7 mWe')]") or self.browser.find(By.XPATH, "//div[contains(@class, 'tBJ dyH iFc yTZ pBj tg7 mWe')]")
        
        if user.text != None:
            return user.text == "Follow"

    def repin(self, pin_id: str, board_name: str):
        self.browser.get(self.url_creator.pin_url(pin_id))
        time.sleep(1)

        board_dropdown = self.browser.find(By.XPATH, "//div[contains(@class, 'tBJ dyH iFc _yT pBj DrD IZT swG z-6')]", timeout=3)
        if board_dropdown != None:
            board_dropdown.click()
        else:
            self.__create_and_save_to_board(board_name)
            return

        boards = self.browser.find_all(By.XPATH, "//div[contains(@class, 'tBJ dyH iFc yTZ pBj DrD IZT mWe z-6')]", timeout=5)

        for board in boards:
            if board.text == board_name:
                board.click()
                break
        else:
            self.browser.find(By.XPATH, "//div[contains(@class, 'rDA wzk zI7 iyn Hsu')]").click() # create board button
            text_tag = self.browser.find(By.XPATH, "//input[contains(@id, 'boardEditName')]")
            text_tag.send_keys(board_name)
            time.sleep(0.5)
            self.browser.find(By.XPATH, "//button[contains(@class, 'RCK Hsu USg Vxj aZc Zr3 hA- GmH adn Il7 Jrn hNT iyn BG7 NTm KhY')]").click() # create_button

            return

        time.sleep(1)
        edit_button = self.browser.find(By.XPATH, "//div[contains(@class, 'Eqh Shl s7I zI7 iyn Hsu')]")

        if edit_button:
            return True
        else:
            return False
    
    def __create_and_save_to_board(self, board_name: str):
        self.browser.find(By.XPATH, "//div[contains(@class, 'tBJ dyH iFc MF7 erh DrD IZT mWe')]").click() # save button
        self.browser.find(By.XPATH, "//div[contains(@class, 'Umk fte zI7 iyn Hsu')]").click() # create_board_button
        text_tag = self.browser.find(By.XPATH, "//input[contains(@id, 'boardEditName')]")
        text_tag.send_keys(board_name)
        time.sleep(0.5)
        self.browser.find(By.XPATH, "//button[contains(@class, 'RCK Hsu USg Vxj aZc Zr3 hA- GmH adn Il7 Jrn hNT iyn BG7 NTm KhY')]").click() # create_button
        
    def get_board_followers(self, 
        user_name: str,
        board_name: str,
        full_board_url: str = None,
        number_of_users_to_follow: int = 100, 
        ignored_users: List[str] = []
    ):
        if full_board_url != None:
            self.browser.get(full_board_url)
        else:
            self.browser.get(self.url_creator.board_url(user_name, board_name))

        time.sleep(1)
        followers_container = self.browser.find(By.XPATH, "/html/body/div[1]/div[1]/div[3]/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div/div[1]/div/div[2]/div[2]/div[2]/div/button", timeout=1) or self.browser.find(By.XPATH, "/html/body/div[1]/div[1]/div[3]/div/div/div/div[1]/div/div[1]/div/div[4]/div[1]/div/button/div/span", timeout=1)

        if followers_container != None:
            followers_container.click()

        saved_users = 0
        final_users = []

        while number_of_users_to_follow >= saved_users:
            users_list = self.browser.find_all(By.XPATH, "//div[contains(@class, 'Module User hasText thumb medium boardFollower')]")
            users_length_before = len(final_users)

            for user_container in users_list:
                user_url = self.browser.find(By.CSS_SELECTOR, 'a', user_container).get_attribute('href')
                user_name = user_url.split('.com/')[1].split('/')[0]

                if user_name in ignored_users:
                    continue

                ignored_users.append(user_name)
                final_users.append(user_name)
                saved_users += 1
                print(saved_users, ':', user_name)

                if saved_users == number_of_users_to_follow:
                    return final_users
            
            users_length_after = len(final_users)
            see_more_button = self.browser.find(By.XPATH, "//div[contains(@class, 'tBJ dyH iFc yTZ pBj tg7 mWe')]", timeout=1.5)
            
            if see_more_button is None or users_length_before == users_length_after:
                return final_users
            
            see_more_button.click()
            time.sleep(0.5)

    def search_pinterest_boards(self, search_term: str, number_of_boards_to_get: int):
        self.browser.get(self.url_creator.search_board_url(search_term))
        time.sleep(1)

        if not self.browser.find(By.XPATH, "//div[contains(@class, 'noResults')]"):
            board_names_container = self.browser.find_all(By.XPATH, "//div[contains(@class, 'Yl- MIw Hb7')]")
            number_of_saved_boards = 0
            board_urls = []

            while True:
                before_scroll = self.browser.current_page_offset_y()

                for board_name_element in board_names_container:
                    full_board_url = self.browser.find(By.CSS_SELECTOR, 'a', board_name_element).get_attribute('href')
                    board_info = full_board_url.split('.com/')[1]
                    user_name = board_info.split('/')[0]
                    board_name = board_info.split('/')[1]

                    if (user_name, board_name) in board_urls:
                        continue

                    board_urls.append((user_name, board_name))
                    number_of_saved_boards += 1

                    if number_of_boards_to_get == number_of_saved_boards:
                        return board_urls
                    
                self.browser.scroll(500)
                time.sleep(0.5)
                after_scroll = self.browser.current_page_offset_y()

                if after_scroll == before_scroll:
                    return board_urls
    
    def get_pins_from_home_feed(self):
        self.browser.get(self.url_creator.home_feed_url())
        time.sleep(1)

        home_pins = []
        home_pin_containers = self.browser.find_all(By.XPATH, "//div[contains(@class, 'Yl- MIw Hb7')]")
        for pin in home_pin_containers:
            full_url = self.browser.find(By.CSS_SELECTOR, 'a', pin).get_attribute('href')

            if 'pinterest.com' not in full_url:
                continue

            pin_id = full_url.split('pin/')[1]
            home_pins.append(pin_id)
        
        return home_pins

    def post_pin(self, 
        file_path: str,
        title_text: str,
        board_name: str,
        about_text: str = None,
        destination_link_text: str = None
        ):
        self.browser.get(self.url_creator.pin_builder_url())
        time.sleep(1)

        select_board_button = self.browser.find(By.XPATH, "/html/body/div[1]/div[1]/div[3]/div/div/div/div[2]/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div")
        if select_board_button != None:
            select_board_button.click()
        
        boards = self.browser.find_all(By.XPATH, "//div[contains(@class, 'tBJ dyH iFc yTZ pBj DrD IZT mWe z-6')]")

        if boards != None: 
            for board in boards:
                if board.text == board_name:
                    board.click()
                    break
        
        title_box = self.browser.find(By.XPATH, "//div[contains(@class, 'CDp xcv L4E zI7 iyn Hsu')]")
        if title_box != None:
            title = self.browser.find(By.CSS_SELECTOR, "textarea", title_box)
            title.send_keys(title_text)
        
        if about_text != None:
            about_box = self.browser.find(By.XPATH, "//div[contains(@class, 'Jea Tte ujU xcv L4E zI7 iyn Hsu')]")
            if about_box != None:
                about = self.browser.find(By.CSS_SELECTOR, "textarea", about_box)
                about.send_keys(about_text)

        if destination_link_text != None:
            destination_link_box = self.browser.find(By.XPATH, "//div[contains(@data-test-id, 'pin-draft-link')]")
            if destination_link_box != None:
                destination_link = self.browser.find(By.CSS_SELECTOR, "textarea", destination_link_box)
                destination_link.send_keys(destination_link_text)
        
        image_box = self.browser.find(By.XPATH, "//div[contains(@class, 'DUt XiG zI7 iyn Hsu')]")
        if image_box != None:
            image = self.browser.find(By.CSS_SELECTOR, 'input', image_box)
            image.send_keys(file_path)
        
        save_button = self.browser.find(By.XPATH, "//div[contains(@class, 'tBJ dyH iFc yTZ erh DrD IZT mWe')]")
        if save_button != None:
            save_button.click()
        
        time.sleep(1.5)
    
        return self.browser.find(By.XPATH, "//div[contains(@data-test-id, 'seeItNow')]") != None
