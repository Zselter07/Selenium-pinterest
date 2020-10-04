from typing import List, Dict, Optional, Tuple
import time, json, traceback

from selenium_firefox.firefox import Firefox, By, Keys
from kcu import rand

from .url_creator import UrlCreator

PT_URL = "https://www.pinterest.com/"

class Pinterest:
    def __init__(
        self,
        cookies_folder_path: str,
        extensions_folder_path: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
        headless: bool = False
    ):
        self.browser = Firefox(cookies_folder_path, extensions_folder_path, host=host, port=port, headless=headless)

        try:
            self.browser.get(PT_URL)
            time.sleep(1.5)

            if self.browser.has_cookies_for_current_website():
                self.browser.load_cookies()
                time.sleep(1.5)
                self.browser.refresh()
                time.sleep(0.5)
            else:
                input('Log in then press enter')
                self.browser.get(PT_URL)
                time.sleep(1.5)
                self.browser.save_cookies()
        except:
            traceback.print_exc()
            self.browser.driver.quit()

            raise
        
    def follow(self, user_name: str) -> bool:
        try:
            self.browser.get(UrlCreator.user_url(user_name))
            rand.sleep(0.5, 1)

            follow_container = self.browser.find(By.XPATH, "//div[contains(@data-test-id, 'user-follow-button')]", timeout=2.5)

            if follow_container:
                follow_button = self.browser.find(By.XPATH, "//div[contains(@class, 'tBJ dyH iFc yTZ erh tg7 mWe')]", follow_container)

                if follow_button is not None and follow_button.text == "Follow":
                    follow_button.click()
                    rand.sleep(0.5, 1)
                else:
                    return False

                follow_buttons_updated = self.browser.find_all(By.XPATH, "//div[contains(@class, 'tBJ dyH iFc yTZ pBj tg7 mWe')]")

                for elem in follow_buttons_updated:
                    if elem.text == "Following":
                        print('user.text', elem.text)

                        return True
                        
            elif follow_container is None: 
                user = self.browser.find(By.XPATH, "//div[contains(@class, 'tBJ dyH iFc yTZ erh tg7 mWe')]")

                if user.text == "Follow":
                    user.click()
                    rand.sleep(1, 1.5)

                user_updated = self.browser.find(By.XPATH, "//div[contains(@class, 'tBJ dyH iFc yTZ erh tg7 mWe')]")

                return user_updated.text == "Following"
        except:
            traceback.print_exc()

            return False

    def unfollow(self, user_name: str) -> bool:
        try:
            self.browser.get(UrlCreator.user_url(user_name))
            rand.sleep(1, 2)
            user_container = self.browser.find(By.XPATH, "//div[contains(@data-test-id, 'user-unfollow-button')]")

            if user_container is not None:
                user_element = self.browser.find(By.XPATH, "//button[contains(@class, 'RCK Hsu USg Vxj aZc Zr3 hA- GmH adn a_A gpV hNT iyn BG7 NTm KhY')]", user_container)
                user_element.click()
                rand.sleep(0.5, 1)
                
                return self.browser.find_by('button', attributes={'class': 'RCK Hsu USg Vxj aZc Zr3 hA- GmH adn Il7 Jrn hNT iyn BG7 NTm KhY', 'type': 'button'}) is not None
            else:
                user = self.browser.find(By.XPATH, "//div[contains(@class, 'tBJ dyH iFc yTZ pBj tg7 mWe')]")

                if user.text == "Following":
                    user.click()
                    rand.sleep(1, 1.5)

                user_updated = self.browser.find(By.XPATH, "//div[contains(@class, 'tBJ dyH iFc yTZ erh tg7 mWe')]")

                return user_updated.text == "Follow"     
        except:
            traceback.print_exc()

            return False

    def repin(self, pin_id: str, board_name: str, needs_repin_id: bool=False) -> Tuple[bool, Optional[str]]:
        try:
            self.browser.get(UrlCreator.pin_url(pin_id))
            rand.sleep(0.7, 1.2)

            board_dropdown = self.browser.find(By.XPATH, "//div[contains(@class, 'tBJ dyH iFc _yT pBj DrD IZT swG z-6')]", timeout=3)

            if board_dropdown is not None:
                board_dropdown.click()
                rand.sleep(0.1, 0.5)
            else:
                if self.__create_and_save_to_board(board_name) and needs_repin_id:
                    return True, self.__get_link_to_repinned_post()
                elif self.__create_and_save_to_board(board_name) and needs_repin_id is False:
                    return True, None

                return False, None

            boards = self.browser.find_all(By.XPATH, "//div[contains(@class, 'tBJ dyH iFc yTZ pBj DrD IZT mWe z-6')]", timeout=5)

            for board in boards:
                if board.text == board_name:
                    board.click()
                    rand.sleep(0.2,0.5)

                    break
            else:
                self.browser.find(By.XPATH, "//div[contains(@class, 'rDA wzk zI7 iyn Hsu')]").click() # create board button
                text_tag = self.browser.find(By.XPATH, "//input[contains(@id, 'boardEditName')]")
                text_tag.send_keys(board_name)
                rand.sleep(0.5, 1)
                self.browser.find(By.XPATH, "//button[contains(@class, 'RCK Hsu USg Vxj aZc Zr3 hA- GmH adn Il7 Jrn hNT iyn BG7 NTm KhY')]").click() # create_button
                
                if needs_repin_id:
                    return True, self.__get_link_to_repinned_post()
                else:
                    return self.browser.find(By.XPATH, "//div[contains(@class, 'Eqh Shl s7I zI7 iyn Hsu')]") is not None, None

            rand.sleep(0.5, 1)

            if needs_repin_id:
                return self.browser.find(By.XPATH, "//div[contains(@class, 'Eqh Shl s7I zI7 iyn Hsu')]") is not None, self.            __get_link_to_repinned_post()
            else:
                return self.browser.find(By.XPATH, "//div[contains(@class, 'Eqh Shl s7I zI7 iyn Hsu')]") is not None, None
        except:
            traceback.print_exc()

            return False, None

    def __get_link_to_repinned_post(self) -> Optional[str]:
        try:
            saved_to_button = self.browser.find(By.XPATH, "//div[contains(@class, 'Shl ujU zI7 iyn Hsu')]", timeout=3)
            full_link = self.browser.find(By.CSS_SELECTOR, 'a', saved_to_button).get_attribute('href')

            self.browser.get(full_link)
            print(full_link)
            rand.sleep(2.5, 3)

            latest_image_box = self.browser.find(By.XPATH, "//div[contains(@class, 'Yl- MIw Hb7')]", timeout=5)
            pin_id = self.browser.find(By.XPATH, "//div[contains(@data-test-id, 'pin')]", latest_image_box).get_attribute('data-test-pin-id')
            rand.sleep(0.1, 0.3)

            return pin_id
        except:
            traceback.print_exc()

            return None
    
    def __create_and_save_to_board(self, board_name: str) -> bool:
        try:
            print('I am in the __create_and_save_to_board func')
            self.browser.find(By.XPATH, "//div[contains(@class, 'tBJ dyH iFc MF7 erh DrD IZT mWe')]").click() # save button
            self.browser.find(By.XPATH, "//div[contains(@class, 'Umk fte zI7 iyn Hsu')]").click() # create_board_button
            text_tag = self.browser.find(By.XPATH, "//input[contains(@id, 'boardEditName')]")
            text_tag.send_keys(board_name)
            rand.sleep(0.5, 0.8)
            self.browser.find(By.XPATH, "//button[contains(@class, 'RCK Hsu USg Vxj aZc Zr3 hA- GmH adn Il7 Jrn hNT iyn BG7 NTm KhY')]").click() # create_button
            rand.sleep(1, 1.5)

            return self.browser.find(By.XPATH, "//button[contains(@class, 'RCK Hsu USg Vxj aZc Zr3 hA- GmH adn Il7 Jrn hNT iyn BG7 NTm KhY')]", timeout=3) is None
        except:
            traceback.print_exc()

            return False
        
    def get_board_followers(
        self, 
        user_name: str,
        board_name: str,
        ignored_users: List[str],
        number_of_users_to_follow, 
        full_board_url: str = None
    ) -> Optional[Tuple[List[str], List[str]]]:
        try:
            if full_board_url is not None:
                self.browser.get(full_board_url)
            else:
                self.browser.get(UrlCreator.board_url(user_name, board_name))

            rand.sleep(1, 1.5)
            followers_container = self.browser.find(By.XPATH, "//div[contains(@class, 'rLK iyn eEj FTD L4E DI9 BG7')]")

            if followers_container is not None:
                followers_container.click()
                rand.sleep(1, 1.5)

            saved_users = 0
            final_users = []

            while number_of_users_to_follow >= saved_users:
                try:
                    users_list = self.browser.find_all(By.XPATH, "//div[contains(@class, 'Module User hasText thumb medium')]")
                    users_length_before = len(final_users)

                    for user_container in users_list:
                        try:
                            print(user_container.text)
                            print('im in the for')
                            user_url = self.browser.find(By.CSS_SELECTOR, 'a', user_container).get_attribute('href')
                            user_name = user_url.split('.com/')[1].split('/')[0]

                            if user_name in ignored_users:
                                continue

                            ignored_users.append(user_name)
                            final_users.append(user_name)
                            saved_users += 1
                            print(saved_users, ':', user_name)

                            if saved_users == number_of_users_to_follow:
                                return (final_users, ignored_users)
                        except:
                            traceback.print_exc()
                except:
                    traceback.print_exc()
                
                users_length_after = len(final_users)
                see_more_button = self.browser.find(By.XPATH, "//div[contains(@class, 'tBJ dyH iFc yTZ pBj tg7 mWe')]", timeout=1.5)
                
                if see_more_button is None or users_length_before == users_length_after:
                    return (final_users, ignored_users)
                
                see_more_button.click()
                rand.sleep(1, 1.5)

        except:
            traceback.print_exc()

            return None

    def search_pinterest_boards(self, search_term: str, number_of_boards_to_get: int=35) -> Optional[List[Tuple[str, str]]]:
        try:
            self.browser.get(UrlCreator.search_board_url(search_term))
            rand.sleep(1, 1.5)

            if self.browser.find(By.XPATH, "//div[contains(@class, 'noResults')]"):
                return None

            board_names_container = self.browser.find_all(By.XPATH, "//div[contains(@class, 'Yl- MIw Hb7')]")
            number_of_saved_boards = 0
            board_urls = []

            while True:
                before_scroll = self.browser.current_page_offset_y()

                for board_name_element in board_names_container:
                    try:
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
                    except:
                        traceback.print_exc()

                self.browser.scroll(1000)
                rand.sleep(0.5, 1.5)
                after_scroll = self.browser.current_page_offset_y()

                if after_scroll == before_scroll:
                    return board_urls
        except:
            traceback.print_exc()

            return None

    def get_pins_from_home_feed(self) -> Optional[List[str]]:
        try:
            self.browser.get(UrlCreator.home_feed_url())
            rand.sleep(1, 1.5)

            home_pins = []
            home_pin_containers = self.browser.find_all(By.XPATH, "//div[contains(@class, 'Yl- MIw Hb7')]")

            for pin in home_pin_containers:
                try:
                    full_url = self.browser.find(By.CSS_SELECTOR, 'a', pin).get_attribute('href')

                    if 'pinterest.com' not in full_url:
                        continue
                    
                    if 'pin/' in full_url:
                        pin_id = full_url.split('pin/')[1]
                        home_pins.append(pin_id)
                except:
                    traceback.print_exc()
                    
            return home_pins
        except:
            traceback.print_exc()

            return None
    
    def post_pin(
        self, 
        image_path: str,
        board_name: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        url: Optional[str] = None
    ) -> Optional[str]:
        try:
            self.browser.get(UrlCreator.pin_builder_url())
            rand.sleep(1, 1.5)

            image_box = self.browser.find_by('div', class_='DUt XiG zI7 iyn Hsu')

            if not image_box:
                raise 'did not find image_box'

            image_input = self.browser.find(By.CSS_SELECTOR, 'input', image_box)

            if not image_input:
                raise 'did not find image_input'

            image_input.send_keys(image_path)
            rand.sleep(1, 1.5)

            select_board_button = self.browser.find_by('button', attributes={'data-test-id': 'board-dropdown-select-button'})
            select_board_button.click()
            rand.sleep(1, 1.5)
            board_search_field = self.browser.find_by('input', id_='pickerSearchField')
            self.browser.send_keys_delay_random(board_search_field, board_name)
            rand.sleep(1, 1.5)
            boards = self.browser.find_all_by('div', class_='tBJ dyH iFc yTZ pBj DrD IZT mWe z-6', timeout=2.5)

            exists_board = False

            if boards and len(boards) > 0:
                for board in boards:
                    if board.text == board_name:
                        exists_board = True
                        board.click()
                        rand.sleep(0.1, 0.5)

                        break

            if not exists_board:
                dropdown_boards = self.browser.find_by('div', class_='DUt qJc sLG zI7 iyn Hsu')
                create_board = self.browser.find_by('div', class_='rDA wzk zI7 iyn Hsu', in_element=dropdown_boards)

                if create_board is not None:
                    create_board.click()
                    rand.sleep(0.1, 0.5)

                board_name_textfield = self.browser.find_by('input', id_='boardEditName', timeout=2)

                if board_name_textfield.get_attribute('value') != board_name:
                    while len(board_name_textfield.get_attribute('value')) > 0:
                        board_name_textfield.send_keys(Keys.BACK_SPACE)
                        board_name_textfield = self.browser.find_by('input', id_='boardEditName', timeout=2)

                    self.browser.send_keys_delay_random(board_name_textfield, board_name)
                    rand.sleep(0.5, 1)

                create_board_button = self.browser.find_by('button', class_='RCK Hsu USg adn CCY czT F10 xD4 fZz hUC Il7 Jrn hNT BG7 NTm KhY', timeout=2.5) or self.browser.find_by('button', {'type':'submit'}, timeout=2.5)
                create_board_button.click()
                rand.sleep(0.5, 1)
                just_created_board_save_button = self.browser.find_by('div', class_='tBJ dyH iFc yTZ erh DrD IZT mWe')
                just_created_board_save_button.click()
                rand.sleep(0.5, 1.5)

            if title:
                title_box = self.browser.find_by('div', class_='CDp xcv L4E zI7 iyn Hsu')

                if title_box:
                    title_textfield = self.browser.find(By.CSS_SELECTOR, "textarea", title_box)

                    if title_textfield:
                        self.browser.send_keys_delay_random(title_textfield, title)
                        rand.sleep(0.5, 1.5)

            if description:
                about_box = self.browser.find_by('div', class_='Jea Tte ujU xcv L4E zI7 iyn Hsu', timeout=2)

                if about_box:
                    about_textfield = self.browser.find_by('div', class_='notranslate public-DraftEditor-content', in_element=about_box, timeout=2)

                    if about_textfield:
                        self.browser.send_keys_delay_random(about_textfield, description)
                        rand.sleep(0.5, 1.5)

            if url:
                url_box = self.browser.find_by('div', {'data-test-id':'pin-draft-link'})

                if url_box:
                    url_textfield = self.browser.find(By.CSS_SELECTOR, "textarea", url_box)

                    if url_textfield:
                        self.browser.send_keys_delay_random(url_textfield, url)
                        rand.sleep(0.5, 1.5)
            
            save_button = self.browser.find_by('button', {'data-test-id':'board-dropdown-save-button'})
            save_button.click()

            rand.sleep(0.1, 0.5)
            see_it_now = self.browser.find_by('div', {'data-test-id':'seeItNow'})
            full_pin_url = self.browser.find(By.CSS_SELECTOR, 'a', see_it_now).get_attribute('href')

            return full_pin_url.split('pin/')[1]
        except:
            traceback.print_exc()

            return None