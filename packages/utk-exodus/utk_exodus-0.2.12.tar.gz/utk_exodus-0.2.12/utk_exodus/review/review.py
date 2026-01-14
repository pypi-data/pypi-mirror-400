from requestium import Session, Keys
import os
import requests
from requests.auth import HTTPBasicAuth
from tqdm import tqdm


class ExistingImport:
    def __init__(
            self,
            import_ids,
            output_dir,
            initial_auth=None,
            hyku_instance='https://dc.utk-hyku-production.notch8.cloud',
            webdriver_path='/usr/local/bin/chromedriver',
    ):
        self.import_ids = import_ids
        self.output = output_dir
        self.s = Session(
            webdriver_path=webdriver_path,
            browser='chrome',
            default_timeout=15,
            webdriver_options={'arguments': ['headless']}
        )
        self.hyku_instance = hyku_instance
        self.initial_auth = initial_auth
        if initial_auth is not None:
            self.s.driver.get(
                f'https://{initial_auth[0]}:{initial_auth[1]}@{hyku_instance.replace("https://", "")}/users/sign_in?locale=en'
            )

    def sign_in_to_hyku(self, username, password):
        print('\nSigning in to Hyku\n')
        self.s.driver.ensure_element_by_xpath("//input[@id='user_email']").send_keys(username, Keys.ENTER)
        self.s.driver.ensure_element_by_xpath("//input[@id='user_password']").send_keys(password, Keys.ENTER)
        return

    def transfer_cookies_to_requests(self):
        self.requests_session = requests.Session()
        for cookie in self.s.driver.get_cookies():
            cookie_dict = {cookie['name']: cookie['value']}
            self.requests_session.cookies.update(cookie_dict)
        self.requests_session.auth = HTTPBasicAuth(self.initial_auth[0], self.initial_auth[1])

    def export_errors(self):
        self.transfer_cookies_to_requests()
        for import_id in tqdm(self.import_ids):
            url = f'{self.hyku_instance}/importers/{import_id}/export_errors'
            response = self.requests_session.get(url)
            if response.status_code == 200:
                file_path = os.path.join(os.getcwd(), self.output,  f'export_errors_{import_id}.csv')
                with open(f"{file_path}", 'wb') as file:
                    file.write(response.content)
        return
