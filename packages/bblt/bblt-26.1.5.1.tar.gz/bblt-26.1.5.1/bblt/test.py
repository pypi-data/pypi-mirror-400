import time
import unittest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

capabilities = dict(
    platformName='Android',
    deviceName='Android',
    bundle_id='com.disney.shanghaidisneyland_goo')

appium_server_url = "http://127.0.0.1:4723/wd/hub"

if __name__ == '__main__':
    driver = webdriver.Remote(appium_server_url, options=UiAutomator2Options().load_capabilities(capabilities))
    driver.activate_app("com.disney.shanghaidisneyland_goo")
    driver.wait_activity('com.disney.wdpro.park.activities.FinderActivity', 180, 1)
    driver.tap([(952, 391)])