import re

import pandas
from selenium import webdriver
from selenium.common import ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
from os import getenv

if __name__ == "__main__":
    load_dotenv()
    keyword = "川崎市"
    filename = "kawasaki-options.csv"
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    driver.get("https://share.timescar.jp/")
    # トップページ
    driver.find_element(By.LINK_TEXT, "予約・ログイン").click()
    # 会員専用マイページログイン
    driver.find_element(By.ID, "cardNo1").send_keys(getenv("TIMES_CAR_ID1"))
    driver.find_element(By.ID, "cardNo2").send_keys(getenv("TIMES_CAR_ID2"))
    driver.find_element(By.ID, "tpPassword").send_keys(getenv("TIMES_CAR_PASSWORD"))
    driver.find_element(By.ID, "doLoginForTp").click()
    # タイムズカーマイページ
    try:
        driver.find_elements(By.CLASS_NAME, "s_agree")[-1].click()
    except ElementNotInteractableException:
        pass
    try:
        driver.find_elements(By.CLASS_NAME, "s_agree")[0].click()
    except ElementNotInteractableException:
        pass
    driver.find_element(By.LINK_TEXT, "予約・ステーション検索").click()
    # ステーションを探す
    driver.find_element(By.ID, "monthAdvanceBooking").click()
    driver.find_element(By.ID, "optionNarrowWord").send_keys(keyword + Keys.ENTER)
    # ステーション一覧
    stations, addresses, models = [], [], []
    while True:
        rows = driver.find_element(By.XPATH, "//*[@id='d_search']/table").find_elements(
            By.TAG_NAME, "tr"
        )[1:]
        for i in range(len(rows)):
            row = driver.find_element(
                By.XPATH, "//*[@id='d_search']/table"
            ).find_elements(By.TAG_NAME, "tr")[1:][i]
            cols = row.find_elements(By.TAG_NAME, "td")
            station = re.sub("\n.+", "", cols[0].text)
            address = cols[2].text
            row.find_element(By.ID, "goReserve").click()
            driver.find_element(By.ID, "useCarModel").click()
            # 予約登録（入力）
            for car_model in driver.find_element(By.ID, "carModel").find_elements(
                By.TAG_NAME, "option"
            )[1:]:
                model = car_model.text
                print(station, address, model)
                stations.append(station)
                addresses.append(address)
                models.append(model)
            driver.back()
        # ステーション一覧
        if driver.find_elements(By.ID, "goNext"):
            driver.find_element(By.ID, "goNext").click()
        else:
            break
    pandas.DataFrame(
        {"ステーション名": stations, "住所": addresses, "車種": models}
    ).to_csv(filename, index=False)
