import re
import configparser
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
import subprocess

hs_token = "af232f63eb484d59a5c562eff4bb6bd5"
local_android_driver_url = "http://localhost:4723/wd/hub"
local_ios_host = "http://127.0.0.1:4723/wd/hub"
driver_host_ios = f'https://disneyparks-cn-shg-0-proxy-1-mac.wdw.disney.com:7024/v0/{hs_token}/wd/hub'
driver_host_android = f'https://disneyparks-cn-shg-0-proxy-2-lin.wdw.disney.com:7025/v0/{hs_token}/wd/hub'


class AppiumDriver:
    def __init__(self):
        settings = configparser.RawConfigParser()
        settings.read('./settings.ini')
        self.bundle_app = settings['config']['bundle_app']
        self.device_id, self.device_os = self.get_device_id()
        self.bundle_id = self.get_bundle_id()
        print(self.device_id, self.device_os)
        self.capabilities_android = dict(
            platformName=self.device_os,
            deviceName='Android Huawei',
            bundle_id=self.bundle_id
        )
        self.capabilities_ios = dict(
            platformName=self.device_os,
            deviceName='iPhone',
            udid=self.device_id,
            bundle_id=self.bundle_id
        )

    def get_device_id(self):
        ios_command = "ios-deploy -c"
        ios_regex = "Found ([0-9A-Z-]*) "
        process_temp = subprocess.Popen(ios_command, shell=True, stdout=subprocess.PIPE)
        out_ios, err_ios = process_temp.communicate()
        process_temp.terminate()
        ios_device_list = re.findall(ios_regex, out_ios.decode("utf-8"))

        android_command = "adb devices"
        android_regex = "List of devices attached\n([0-9A-Z]*)\tdevice"
        process_temp = subprocess.Popen(android_command, shell=True, stdout=subprocess.PIPE)
        out_android, err_android = process_temp.communicate()
        process_temp.terminate()
        android_device_list = re.findall(android_regex, out_android.decode("utf-8"))
        if len(android_device_list) > 0:
            return android_device_list[0], 'android'
        elif len(ios_device_list) > 0:
            return ios_device_list[0], 'ios'
        else:
            print(f'\033 No Device Found! \033')
            return None

    def get_bundle_id(self):
        ios_command = "ios-deploy --list_bundle_id"
        android_command = "adb shell pm list packages"
        if "ios" in self.device_os:
            command = ios_command
        else:
            command = android_command
        process_temp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        out, err = process_temp.communicate()
        process_temp.terminate()
        bundle_list = out.decode("utf-8").split('\n')
        filtered_expected_bundle_id = [bundle_id for bundle_id in bundle_list if re.match(f".*({self.bundle_app}*)", bundle_id)]
        if len(filtered_expected_bundle_id) > 0:
            return filtered_expected_bundle_id[0].replace("package:", "")
        else:
            print(f'\033 Not Found Any "{self.bundle_app}" APP! \033')
            return None

    def init_driver(self):
        try:
            if 'ios' in self.device_os:
                return webdriver.Remote(local_ios_host,
                                        options=XCUITestOptions().load_capabilities(self.capabilities_ios))
            else:
                return webdriver.Remote(local_android_driver_url,
                                        options=UiAutomator2Options().load_capabilities(self.capabilities_android))
        except:
            print(f'\033Unable connect device {self.device_id} \033')
            print(f'\033Please make sure Appium started...\033')
            print(f'\033Please make sure WDA Running...\033')
        return None

    def close_driver(self, d):
        d.close()


if __name__ == '__main__':
    # driver = AppiumDriver(device_id="00008120-001449400CDB401E", device_os="ios").init_driver()
    print(AppiumDriver().get_bundle_id())
    driver = AppiumDriver().init_driver()
    # print(driver.capabilities['deviceName'] + "_" + driver.capabilities['udid'])
    # bundleID = "com.disney.shanghaidisneyland"
    # for x in range(0, 3):
    #     start_time = str(datetime.datetime.now()).replace(" ", "_")
    #     video_path = f"video_{start_time}.mkv"
    #     time.sleep(5)
    #     driver.start_recording_screen()
    #     try:
    #         driver.terminate_app(bundleID)
    #     except:
    #         pass
    #     time.sleep(5)
    #     driver.activate_app(bundleID)
    #     time.sleep(10)
    #     driver.terminate_app(bundleID)
    #     video = driver.stop_recording_screen()
    #     with open(video_path, "wb") as fp:
    #         fp.write(base64.b64decode(video))
    #     try:
    #         driver.close()
    #     except:
    #         pass
    #     pass
