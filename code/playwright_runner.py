from threading import Thread
from tkinter import messagebox
from playwright.sync_api import sync_playwright
import copy
import re
import datetime


class PlaywrightRunner:
    def __init__(self, app):
        self.app = app
        self.playwright_thread = None
        self.stop_threads = False

    def run_playwright_in_thread(self, username, password):
        self.playwright_thread = Thread(
            target=self.run_playwright, args=(username, password)
        )
        self.playwright_thread.start()

    def run_playwright(self, username, password):
        try:
            # Playwright 脚本逻辑
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()

                page.goto(
                    "https://sso.buaa.edu.cn/login?service=https://cgyy.buaa.edu.cn/venue-server/sso/manageLogin"
                )
                iframe_locator = page.frame_locator("#loginIframe")

                # 填写用户名和密码并登录
                iframe_locator.get_by_role("textbox", name="请输入学工号").click()
                iframe_locator.get_by_role("textbox", name="请输入学工号").fill(
                    username
                )

                iframe_locator.get_by_placeholder("请输入密码").click()
                iframe_locator.get_by_placeholder("请输入密码").fill(password)

                iframe_locator.get_by_role("button", name="登录").click()

                # 检查是否成功登录，通过判断是否跳转到其他页面或显示登录后的内容
                page.wait_for_timeout(2000)  # 等待页面加载

                # 通过检查页面上的某个登录后特有的元素判断登录是否成功
                if page.url != "https://cgyy.buaa.edu.cn/venue/home":
                    # 如果登录后URL没有变化，则说明登录失败
                    error_message = (
                        "Login failed. Please check your username and password."
                    )
                    self.app.root.after(
                        0, lambda: messagebox.showerror("Login Error", error_message)
                    )
                    return  # 直接返回，不继续执行

                # 登录成功后显示场馆空闲信息
                self.app.root.after(
                    0, lambda: self.app.show_venue_frame()
                )  # 在主线程中显示场馆信息框

                # 获取场馆信息的逻辑...
                page.locator("div").filter(
                    has_text=re.compile(
                        r"^学院路校区羽毛球学院路校区羽毛球沙河校区游泳馆沙河校区羽毛球沙河校区台球厅$"
                    )
                ).get_by_role("img").first.click()

                weekdays = [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]
                current_date = datetime.date.today()
                tomorrow_date = current_date + datetime.timedelta(days=1)
                day_after_tomorrow_date = current_date + datetime.timedelta(days=2)

                current_str = weekdays[current_date.weekday()] + " " + str(current_date)
                tomorrow_str = (
                    weekdays[tomorrow_date.weekday()] + " " + str(tomorrow_date)
                )
                day_after_tomorrow_str = (
                    weekdays[day_after_tomorrow_date.weekday()]
                    + " "
                    + str(day_after_tomorrow_date)
                )

                site_list = {
                    current_str: {},
                    tomorrow_str: {},
                    day_after_tomorrow_str: {},
                }

                while not self.stop_threads:
                    page.get_by_role("button", name="关闭").click()

                    site_list_new = {
                        current_str: {},
                        tomorrow_str: {},
                        day_after_tomorrow_str: {},
                    }

                    for i, date_str in enumerate(
                        [current_str, tomorrow_str, day_after_tomorrow_str]
                    ):
                        if page.locator(f'div[style="order: {i};"]').count() <= 0:
                            break
                        page.locator(f'div[style="order: {i};"]').click()
                        page.wait_for_timeout(500)

                        while True:
                            rows = page.query_selector_all("tbody.ivu-table-tbody tr")
                            time_elements = page.query_selector_all("thead tr td")
                            times = [element.inner_text() for element in time_elements]

                            for row in rows:
                                site_id = row.query_selector(
                                    "td div.ivu-table-cell"
                                ).inner_text()
                                tds = row.query_selector_all("td div.reserveBlock")
                                for index, td in enumerate(tds):
                                    if td.get_attribute(
                                        "class"
                                    ) and "free" in td.get_attribute("class"):
                                        free_time = times[index + 1]
                                        site_list_new[date_str].setdefault(
                                            site_id, []
                                        ).append(free_time)

                            if (
                                page.locator(
                                    "thead tr td i.ivu-icon-ios-arrow-forward"
                                ).count()
                                > 0
                            ):
                                page.locator(
                                    "thead tr td i.ivu-icon-ios-arrow-forward"
                                ).click()
                                page.wait_for_timeout(500)
                            else:
                                break

                    if site_list_new != site_list:
                        site_list = copy.deepcopy(site_list_new)
                        self.app.root.after(
                            0, lambda: self.app.update_venue_info(site_list)
                        )  # 在主线程中更新场馆信息

                    page.reload()

        except Exception as e:
            # 捕获其他任何异常，并在主线程中弹出错误框
            self.app.root.after(0, lambda: messagebox.showerror("Error", str(e)))

    def stop_playwright_thread(self):
        self.stop_threads = True
        if self.playwright_thread is not None:
            self.playwright_thread.join()
