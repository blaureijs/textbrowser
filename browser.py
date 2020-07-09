import sys
import os
from collections import deque
import requests
from bs4 import BeautifulSoup
import colorama
colorama.init()


class Browser:

    def url_is_valid(self):
        if '.' in self.url:
            return True
        elif self.url in self.hotkeys:
            return True
        elif self.url in self.saved_tabs.keys():
            self.url = self.quick_links[self.url]  # Convert 'bloomberg' to 'https://bloomberg.com/'
            return True
        return False

    def check_https(self):
        if self.url in self.hotkeys:
            pass
        elif not self.url.startswith('https://'):
            self.url = 'https://' + self.url

    def https_response(self):
        response = requests.get(self.url)
        if response:
            self.soup = BeautifulSoup(response.content, 'html.parser')
            return response.text, response.encoding
        else:
            return None

    def navigate(self):
        if self.url == 'exit':
            self.browsing = False
        elif self.url == 'back':
            try:
                self.history.pop()  # pop current page
                self.url = self.history.pop()  # set url to second pop (previous page)
                self.current_html, self.current_encoding = self.https_response()
                self.current_content = self.strip_tags()  # Print stripped html content
                print(*self.current_content, sep='/n')
            except IndexError:  # No more history pages
                pass
        else:
            self.current_html, self.current_encoding = self.https_response()
            self.current_content = self.strip_tags()  # Print stripped html content
            for line in self.current_content:
                print(line.decode("ansi"))

    def page_name(self):
        part_tld = self.url.split('.')[0]
        if part_tld.startswith('https://'):
            name = part_tld.split('://')[1]
            return name
        return part_tld

    def save_tab(self):
        site = self.page_name()
        file_name = site + '.txt'
        file_path = os.path.join(self.save_path, file_name)
        with open(file_path, 'w', encoding=self.current_encoding) as page:
            print(*self.current_content, sep='\n', file=page)
            self.saved_tabs[site] = file_path
            self.quick_links[site] = self.url

    def log_history(self):
        if self.url in self.quick_links.keys():
            self.history.append(self.quick_links[self.url])
        else:
            self.history.append(self.url)

    def strip_tags(self):
        tag_search = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'ul', 'ol', 'li']
        all_tags = self.soup.find_all(tag_search)
        links = self.soup.find_all('a')
        stripped = list()
        for element in all_tags:
            if element in links:
                stripped.append((colorama.Fore.BLUE +
                                 element.get_text() +
                                 colorama.Style.RESET_ALL).encode('ansi', 'ignore'))
            else:
                stripped.append(element.get_text().encode('ansi', 'ignore'))
        return stripped

    def __init__(self, save_path):
        self.save_path = os.path.join(os.getcwd(), save_path)
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        self.hotkeys = ['back']
        self.saved_tabs = dict()
        self.quick_links = dict()
        self.history = deque()
        self.current_html = ''
        self.current_encoding = ''
        self.current_content = ''
        self.soup = None
        self.browsing = True

        while self.browsing:
            self.url = input()
            if self.url == 'exit':
                self.browsing = False
            elif self.url_is_valid():
                self.check_https()
                self.navigate()
                if self.url not in self.hotkeys:
                    self.save_tab()  # Don't save the page again if url input was 'back'
                self.log_history()
            else:
                print('Error: Incorrect URL')


save_dir = sys.argv[1]
browser = Browser(save_dir)






