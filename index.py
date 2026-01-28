import argparse
from selenium_browserkit import BrowserManager, Node, By, Utility

from googl import Auto as GoogleAuto, Setup as GoogleSetup
PROJECT_URL = "https://www.edgen.tech"

class Setup:
    def __init__(self, node: Node, profile) -> None:
        self.node = node
        self.profile = profile
        self.google_setup = GoogleSetup(node=node, profile=profile)
        self.run()

    def run(self):
        self.google_setup.run()
        self.node.new_tab(f'{PROJECT_URL}/copilot')
        Utility.wait_time(10)

class Auto:
    def __init__(self, node: Node, profile: dict) -> None:
        self.driver = node._driver
        self.node = node
        self.google_auto = GoogleAuto(node=node, profile=profile)

        self.profile_name = profile.get('profile_name')
        self.email = profile.get('email')
        self.pwd_email = profile.get('pwd_email')

        self.run()

    def check_login(self):
        if self.node.find(By.XPATH, '//button//img'):
            self.node.log('✅ Đã đăng nhập')
            return True
        else:
            if self.node.find(By.XPATH, '//button[contains(text(),"Log in")]'):
                self.node.log('⚠️ Chưa đăng nhập')
                return False
            else:
                self.node.log('❌ Không xác định lỗi đăng nhập')
                return None

    def login(self):
        is_login = self.check_login()
        if is_login == False:
            if not self.google_auto.run():
                self.node.log('⚠️ Chưa đăng nhập tài khoản Google')
                return False
            self.node.close_tab()
            self.node.switch_tab(PROJECT_URL)
            self.node.find_and_click(By.XPATH, '//button[contains(text(),"Log in")]')
            button_gg = self.node.find_in_shadow([(By.CSS_SELECTOR, 'login-modal'),(By.CSS_SELECTOR, '[data-method="GOOGLE"]')])
            if not button_gg:
                self.node.log('Không tìm thấy phương thức đăng nhập Google')
                return None 
            
            self.node.click(button_gg)
            self.google_auto.confirm_login()
            return self.check_login()

        # True và None đc return
        return is_login

    def go_to_task(self):
        self.node.find_and_click(By.XPATH, '//p[contains(., "credits")]')
        self.node.find_and_click(By.XPATH, '//span[contains(., "Go")]')
        url_task= self.node.get_url()
        if self.node.find(By.XPATH, '//p[contains(text(),"Check-in Rewards")]'):
            self.node.log('✅ Đang trang Task nhiệm vụ')
            return True
        
        self.node.log('❌ Không xác định được đang ở trang nào')
        return None

    def check_in(self):
        button_checkin = self.node.find(By.XPATH, '//p[contains(text(),"Check-in Rewards")]/../..//button')
        if not button_checkin:
            self.node.log(f'❌ Không tìm thấy nút check-in')
            return None

        is_disabled = button_checkin.get_attribute("disabled")
        if is_disabled is not None:
            self.node.log(f'⚠️ Đã check-in lần trước')
            return False
        else:
            self.node.click(button_checkin)
            self.node.log(f'✅ Đã click check-in')
            return True
    def task_position(self):
        if self.node.find(By.XPATH, '//div[@id="Daily Missions"]//span[contains(text(),"Edggy")]/../../..//button'):
            self.node.new_tab(f'{PROJECT_URL}/copilot/cio')
            if not self.node.find_and_click(By.XPATH, '//span[contains(text(),"Generate")]'):
                self.node.log(f'⚠️ Không tìm thấy nút Tạo bài AI')
            
            self.node.close_tab()
            self.node.switch_tab(f'{PROJECT_URL}/task')
            self.node.reload_tab()
            
            buttons_claim = self.node.finds(By.XPATH, '//button[contains(text(),"Claim")]')
            if buttons_claim:
                for button in buttons_claim:
                    self.node.click(button)
                return True
            else:
                self.node.log('❌ Không tìm thấy nút Claim sau khi làm nv')
                return None
        else:
            self.node.log('⚠️ Không có nhiệm vụ')
            return False

    def run(self):
        completed = []
        self.node.new_tab(f'{PROJECT_URL}/copilot', method="get")
        if not self.login():
            self.node.snapshot(f'❌ Login thất bại')
        if not self.go_to_task():
            self.node.snapshot(f'❌ Không xác định được đang ở trang nào')
        
        if self.check_in():
            completed.append('check-in')
        if self.task_position():
            completed.append('positions')
        self.node.snapshot(f'Hoàn thành công việc: {completed}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto', action='store_true', help="Chạy ở chế độ tự động")
    parser.add_argument('--headless', action='store_true', help="Chạy trình duyệt ẩn")
    parser.add_argument('--disable-gpu', action='store_true', help="Tắt GPU")
    args = parser.parse_args()

    profiles = Utility.read_data('profile_name', 'email', 'pwd_email')
    max_profiles = Utility.read_config('MAX_PROFLIES')

    if not profiles:
        print("Không có dữ liệu để chạy")
        exit()

    browser_manager = BrowserManager(auto_handler=Auto, setup_handler=Setup)
    browser_manager.update_config(
                        headless=args.headless,
                        disable_gpu=args.disable_gpu,
                        use_tele=True
                    )
    browser_manager.run_menu(
        profiles=profiles,
        max_concurrent_profiles=max_profiles,
        auto=args.auto
    )