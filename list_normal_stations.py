import re

import pandas
from selenium import webdriver
from selenium.common import ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from dotenv import load_dotenv
from os import getenv

if __name__ == "__main__":
    load_dotenv()
    keyword = "川崎市"
    filename = "kawasaki-normal.csv"
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    driver.get("https://share.timescar.jp/")
    driver.find_element(By.LINK_TEXT, "予約・ログイン").click()
    driver.find_element(By.ID, "cardNo1").send_keys(getenv("TIMES_CAR_ID1"))
    driver.find_element(By.ID, "cardNo2").send_keys(getenv("TIMES_CAR_ID2"))
    driver.find_element(By.ID, "tpPassword").send_keys(getenv("TIMES_CAR_PASSWORD"))
    driver.find_element(By.ID, "doLoginForTp").click()
    try:
        driver.find_elements(By.CLASS_NAME, "s_agree")[-1].click()
    except ElementNotInteractableException:
        pass
    try:
        driver.find_elements(By.CLASS_NAME, "s_agree")[0].click()
    except ElementNotInteractableException:
        pass
    driver.find_element(By.LINK_TEXT, "予約・ステーション検索").click()
    driver.find_element(By.ID, "nameAdr-s").send_keys([keyword, Keys.ENTER])
    stations, addresses, classes, cars, comments = [], [], [], [], []
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
            row.find_element(By.ID, "goDetail").click()
            WebDriverWait(driver, 30).until(
                expected_conditions.number_of_windows_to_be(2)
            )
            driver.switch_to.window(driver.window_handles[1])
            for car_info in driver.find_elements(By.ID, "carInfo:rendered"):
                class_name = car_info.find_element(By.ID, "carClassName:rendered").text
                car_name = car_info.find_element(By.ID, "carName:rendered").text
                car_comments = car_info.find_element(By.ID, "carComments:rendered").text
                print(station, address, class_name, car_name, car_comments)
                stations.append(station)
                addresses.append(address)
                classes.append(class_name)
                cars.append(car_name)
                comments.append(car_comments)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        if driver.find_elements(By.ID, "goNext"):
            driver.find_element(By.ID, "goNext").click()
        else:
            break
    pandas.DataFrame(
        {
            "ステーション名": stations,
            "住所": addresses,
            "クラス": classes,
            "車種": cars,
            "コメント": comments,
        }
    ).to_csv(filename, index=False)
