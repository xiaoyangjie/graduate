# coding=utf-8

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, NoSuchWindowException,TimeoutException
import time
from multiprocessing.dummy import Pool
from multiprocessing import Queue
from pymongo.errors import DuplicateKeyError
import logging
import logging.config
from Redis import Redis
from Configure import *
from DataStorage import DataStorage
from Parse import Parse
from WebAction import WebAction

def login():
    """
    使用账户名和密码进行登录
    :param email:
    :param password:
    :return:登录成功返回true
    """
    email = '1019177406@qq.com'
    password = 'yj15923365092'
    driver = webdriver.Chrome()
    driver.get('https://www.linkedin.com/uas/login')
    WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.CLASS_NAME, "inner-wrapper")))
    driver.find_element_by_id('session_key-login').send_keys(email)
    driver.find_element_by_id('session_password-login').send_keys(password)
    driver.find_element_by_css_selector('input#btn-primary.btn-primary').click()
    # WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, "nav-item__china-logo")))
    driver.get('https://www.linkedin.com/in/AlexisMadrigal/')
    ActionChains(driver).send_keys(Keys.END).perform()  # 拉到底
    time.sleep(2)
    print driver.page_source

# login()
a = [1,2,1,1]
a.remove(a[0])
print a
