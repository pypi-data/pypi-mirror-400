import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from PIL import Image
from PIL import ImageFilter
import imagehash
from os import walk
import pandas as pd
import subprocess
import os
file_dir = str(__file__).replace(str(__file__).split("/")[-1], "")


class make_curve:

    def __init__(self):
        pass

    def mk_folder(self, dir):
        try:
            os.stat(dir)
        except:
            os.makedirs(dir)

    def convert_video_to_screenshot(self, video_file, dir):
        screenshot_path = dir + "/%04d.jpg"
        command = "ffmpeg -i " + video_file + "  -vf fps=10 " + screenshot_path
        print(command)
        process_temp = subprocess.Popen(command, shell=True)
        process_temp.communicate()

    def cut_video(self, device_name, size, different_allow):
        video_path = file_dir + "/recorded_videoes/" + device_name + "/video/"
        screen_path = file_dir + "/recorded_videoes/" + device_name + "/screenshot/"
        video_list = []
        for (dirpath, dirnames, filenames) in walk(video_path):
            video_list.extend(filenames)
            break
        try:
            video_list.remove(".DS_Store")
        except:
            pass
        for video in video_list:
            self.mk_folder(screen_path + video.replace(".mkv", ""))
            self.mk_folder(screen_path + video.replace(".mkv", "") + "/converted/")
            self.convert_video_to_screenshot(video_path + video, screen_path + video.replace(".mkv", ""))
            self.crop_image(screen_path + video.replace(".mkv", ""), size)
        self.show(device_name=device_name, different_allow=different_allow)

    def crop_image(self, dir, size):
        f = []
        for (dirpath, dirnames, filenames) in walk(dir):
            f.extend(filenames)
            break
        for file in f:
            command = "convert " + dir + "/" + file + " -gravity center  -crop "+size+" +repage " + dir + "/converted/" + file
            process_temp = subprocess.Popen(command, shell=True)
            process_temp.communicate()

    def show(self, device_name, different_allow):
        video_path = file_dir + "/recorded_videoes/"+device_name+"/screenshot/"
        for (dirpath_parent, dirnames_parent, filenames_parent) in walk(video_path):
            break
        differences = {}
        data = {}
        start_point = 0
        end_point = 0
        end_point_rule = 10
        for line in dirnames_parent:
            dir = dirpath_parent + line + "/converted/"
            print(dir)
            file = []
            difference = []
            for (dirpath, dirnames, filenames) in walk(dir):
                file.extend(filenames)
            file.sort()
            file_num = 0
            for f in file:
                img1 = Image.open(dir + f)
                img2 = Image.open(dir + file[file_num + 1])
                img1 = img1.filter(ImageFilter.BoxBlur(radius=3))
                img2 = img2.filter(ImageFilter.BoxBlur(radius=3))
                phashvalue = imagehash.phash(img1) - imagehash.phash(img2)
                ahashvalue = imagehash.average_hash(img1) - imagehash.average_hash(img2)
                totalaccuracy = phashvalue + ahashvalue
                if totalaccuracy < different_allow:
                    totalaccuracy = 0
                difference.append(totalaccuracy)
                print(f + " and " + file[file_num + 1] + " : " + str(totalaccuracy))
                file_num += 1
                if file_num == len(file) - 1:
                    break
            differences[line] = difference
        differences = self.mend_list(differences)
        xarray = []
        total_time = 0
        for diff in differences:
            start_point = 0
            end_point = 0
            for i in range(0, len(differences[diff])):
                if differences[diff][i] > 0 and start_point == 0:
                    start_point = 0.2 * i
                    break
            for j in range(0, len(differences[diff])):
                if differences[diff][-(j + end_point_rule)] > 0:
                    end_point = 0.2 * (len(differences[diff]) - 10 - j)
                    break
            launch_time = end_point - start_point
            data[diff.split('.')[-1] + ": " + str(round(launch_time, 2)) + "(s)"] = differences[diff]
            total_time += launch_time

        for diff in differences:
            for i in range(0, len(differences[diff])):
                xarray.append(0.2 * i)
            break
        df = pd.DataFrame(data, index=xarray)
        df.plot()
        plt.title("App Launch time in " + device_name + ": " + str(round(total_time/len(differences), 2)))
        plt.xlabel("App bblt image actions change")
        plt.ylabel("Launch time")
        plt.show()

    def mend_list(self, li):
        len_list = []
        for item in li:
            len_list.append(len(li[item]))
        max_len = max(len_list)
        for item in li:
            for i in range(0, max_len-len(li[item])):
                li[item].append(0)
        return li

    def debug(self):
        dir = "/Users/miaog001/PycharmProjects/pythonProject3/recorded_videoes/huawei/screenshot/video_2021-12-01_11:14:28.160709/converted/"
        img1 = Image.open(dir + "0029.jpg")
        img2 = Image.open(dir + "0030.jpg")
        img1 = img1.filter(ImageFilter.BoxBlur(radius=3))
        img2 = img2.filter(ImageFilter.BoxBlur(radius=3))
        phashvalue = imagehash.phash(img1) - imagehash.phash(img2)
        ahashvalue = imagehash.average_hash(img1) - imagehash.average_hash(img2)
        totalaccuracy = phashvalue + ahashvalue
        print(totalaccuracy)


if __name__ == '__main__':
      # make_curve().convert_video_to_screenshot("/Users/miaog001/PycharmProjects/bblt/bblt/recorded_videoes/DCO-AL00/video/video_2024-12-17_16:33:21.224312.mkv",
      #                                          "/Users/miaog001/PycharmProjects/bblt/bblt/recorded_videoes/DCO-AL00/screenshot/")
      # make_curve().convert_video_to_screenshot("/Users/miaog001/Documents/AutoProjects/bblt/bblt/recorded_videoes/iPhone14promax_00008120-001449400CDB401E/video/test.mkv",
      #                                          "/Users/miaog001/Documents/AutoPsrojects/bblt/bblt/recorded_videoes/iPhone14promax_00008120-001449400CDB401E/screenshot/test/")
      # make_curve().convert_video_to_screenshot("/Users/miaog001/Downloads/1-1nologin_cache.mp4",
      #                                          "/Users/miaog001/Downloads/1-1")
      # make_curve().convert_video_to_screenshot("/Users/miaog001/Downloads/1-2nologin_cache.mp4",
      #                                          "/Users/miaog001/Downloads/1-2")
      # make_curve().convert_video_to_screenshot("/Users/miaog001/Downloads/1-3nologin_cache.mp4",
      #                                          "/Users/miaog001/Downloads/1-3")
      # make_curve().convert_video_to_screenshot("/Users/miaog001/Downloads/2-1.mp4",
      #                                          "/Users/miaog001/Downloads/2-1")
      # make_curve().convert_video_to_screenshot("/Users/miaog001/Downloads/2-2.mp4",
      #                                          "/Users/miaog001/Downloads/2-2")
      # make_curve().convert_video_to_screenshot("/Users/miaog001/Downloads/2-3.mp4",
      #                                          "/Users/miaog001/Downloads/2-3")
      # make_curve().convert_video_to_screenshot("/Users/miaog001/Downloads/3-1loginwithcache.mp4",
      #                                          "/Users/miaog001/Downloads/3-1")
      # make_curve().convert_video_to_screenshot("/Users/miaog001/Downloads/3-2loginwithcache.mp4",
      #                                          "/Users/miaog001/Downloads/3-2")
      # make_curve().convert_video_to_screenshot("/Users/miaog001/Downloads/3-3loginwithcache.mp4",
      #                                          "/Users/miaog001/Downloads/3-3")
      # make_curve().convert_video_to_screenshot("/Users/miaog001/Downloads/4-1loginnocache.mp4",
      #                                          "/Users/miaog001/Downloads/4-1")
      # make_curve().convert_video_to_screenshot("/Users/miaog001/Downloads/4-2loginnocache.mp4",
      #                                          "/Users/miaog001/Downloads/4-2")
      # make_curve().convert_video_to_screenshot("/Users/miaog001/Downloads/4-3loginnocache.mp4",
      #                                          "/Users/miaog001/Downloads/4-3")
      make_curve().convert_video_to_screenshot("/Users/miaog001/Downloads/test.mp4",
                                               "/Users/miaog001/Downloads/3")
      # 3-1loginwithcache.mp4
      # make_curve().cut_video("LYA-AL00", "380x780+710+50", 10)
#     make_curve().cut_video("NOH-AN00", "380x780+710+50", 10)
#     # cut_video("huawei_p40_pro", "380x780+710+50", 10)
#     # cut_video("cepheus", "380x780+710+50", 10)
#     # cut_video("huawei_p30_pro", "380x780+710+50", 10)
#     # cut_video("LYA-AL00", "700x1440+1280+50", 10) #test for local screen
#     # cut_video("20220211110056", "700x1440+1280+50", 10)
#     # cut_video("iPhonexr", "600x910+780+30", 10)
#     # cut_video("iPhone12", "600x910+780+30", 10)
#     # cut_video("iPhoneX", "600x910+780+30", 10)
#     # cut_video("iPhone13ProMax", "600x910+780+30", 10)
#     # HUAWEI_P30_PRO
#     # debug()