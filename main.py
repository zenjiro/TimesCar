import re

import chromedriver_binary
import pandas
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

if __name__ == "__main__":
    keyword = "川崎市"
    filename = "kawasaki.csv"
    try:
        driver = webdriver.Chrome()
        driver.implicitly_wait(10)
        driver.get("https://share.timescar.jp/")
        driver.find_element(By.LINK_TEXT, "予約・ログイン").click()
        driver.find_element(By.ID, "cardNo1").send_keys("会員カード番号（ハイフンの前）")
        driver.find_element(By.ID, "cardNo2").send_keys("会員カード番号（ハイフンの後）")
        driver.find_element(By.ID, "tpPassword").send_keys("パスワード")
        driver.find_element(By.ID, "doLoginForTp").click()
        driver.find_elements(By.CLASS_NAME, "s_agree")[-1].click()
        driver.find_elements(By.CLASS_NAME, "s_agree")[0].click()
        driver.find_element(By.LINK_TEXT, "予約・ステーション検索").click()
        driver.find_element(By.ID, "monthAdvanceBooking").click()
        driver.find_element(By.ID, "optionNarrowWord").send_keys([keyword, Keys.ENTER])
        stations, addresses, models = [], [], []
        while True:
            rows = driver.find_element(
                By.XPATH, "//*[@id='d_search']/table"
            ).find_elements(By.TAG_NAME, "tr")[1:]
            for i in range(len(rows)):
                row = driver.find_element(
                    By.XPATH, "//*[@id='d_search']/table"
                ).find_elements(By.TAG_NAME, "tr")[1:][i]
                cols = row.find_elements(By.TAG_NAME, "td")
                station = re.sub("\n.+", "", cols[0].text)
                address = cols[2].text
                row.find_element(By.ID, "goReserve").click()
                driver.find_element(By.ID, "dateEndSearch").send_keys(Keys.DOWN)
                driver.find_element(By.XPATH, "//img[@alt='検索']").click()
                WebDriverWait(driver, 10).until(
                    expected_conditions.text_to_be_present_in_element(
                        (
                            By.XPATH,
                            '//*[@id="searchResultsArea"]/div[1]/table/tbody/tr[1]/td[1]',
                        ),
                        "車種おまかせ",
                    )
                )
                for button in driver.find_elements(By.CLASS_NAME, "searchResultBtn")[
                    1:
                ]:
                    button.click()
                    WebDriverWait(driver, 10).until(
                        expected_conditions.text_to_be_present_in_element(
                            (
                                By.XPATH,
                                '//*[@id="carspecify_popup"]/div[2]/div/table[2]/tbody[1]/tr/th',
                            ),
                            "車種",
                        )
                    )
                    for row2 in driver.find_element(
                        By.ID, "modelAvailResults"
                    ).find_elements(By.TAG_NAME, "tr"):
                        model = row2.find_element(By.TAG_NAME, "td").text
                        print(station, address, model)
                        stations.append(station)
                        addresses.append(address)
                        models.append(model)
                    driver.find_element(By.CLASS_NAME, "bottomBtn").click()
                driver.back()
            if driver.find_elements(By.ID, "goNext"):
                driver.find_element(By.ID, "goNext").click()
            else:
                break
        pandas.DataFrame({"ステーション名": stations, "住所": addresses, "車種": models}).to_csv(
            filename, index=False
        )
    finally:
        driver.quit()
