import json
import datetime
from PIL import Image, ImageDraw, ImageFont
import os
import ctypes
import logging
import math

def load_json(file_path):
    """
    读取JSON文件并返回内容
    :param file_path: JSON文件路径
    :return: 解析后的JSON内容
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def get_today_birthdays(birthdays):
    """
    获取今天生日的名单
    :param birthdays: 所有生日数据
    :return: 今天生日的名单
    """
    today = datetime.date.today()
    today_birthdays = [entry for entry in birthdays if datetime.datetime.strptime(entry['birthday'], '%Y-%m-%d').date().replace(year=today.year) == today]
    return today_birthdays

def get_upcoming_weekend_birthdays(birthdays):
    """
    获取周末生日的名单（如果今天是周五）
    :param birthdays: 所有生日数据
    :return: 周末生日的名单
    """
    today = datetime.date.today()
    weekend_birthdays = []
    if today.weekday() == 4:  # 如果今天是周五
        for entry in birthdays:
            birthday = datetime.datetime.strptime(entry['birthday'], '%Y-%m-%d').date().replace(year=today.year)
            if today < birthday <= today + datetime.timedelta(days=2):
                weekend_birthdays.append(entry)
    return weekend_birthdays

def create_birthday_image(config, today_birthdays, weekend_birthdays):
    """
    在模板图片上添加生日祝福文字
    :param config: 配置数据
    :param today_birthdays: 今天生日的名单
    :param weekend_birthdays: 周末生日的名单
    :return: 生成的图片
    """
    # 打开模板图片
    image = Image.open(config['template_image_path'])
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(config['font_path'], config['font_size'])
    
    width, height = image.size
    y_text = int(height * ((3 - math.sqrt(5)) / 2))
    
    # 添加今天生日的祝福文字
    if today_birthdays:
        names = '、'.join([entry['name'] for entry in today_birthdays])
        age = datetime.date.today().year - datetime.datetime.strptime(today_birthdays[0]['birthday'], '%Y-%m-%d').year
        text = f"{names} {age}岁生日快乐"
        draw.text((width // 2, y_text), text, font=font, fill=config['font_color'], anchor='mm')
        y_text += config['font_size'] * 2

    # 添加周末生日的祝福文字
    if weekend_birthdays:
        for entry in weekend_birthdays:
            name = entry['name']
            age = datetime.date.today().year - datetime.datetime.strptime(entry['birthday'], '%Y-%m-%d').year
            text = f"提前祝{name} {age}岁生日快乐("+ str(datetime.datetime.strptime(entry['birthday'], '%Y-%m-%d').month) + "." +str(datetime.datetime.strptime(entry['birthday'], '%Y-%m-%d').day)+")"
            draw.text((width // 2, y_text), text, font=font, fill=config['font_color'], anchor='mm')
            y_text += config['font_size'] * 2
    
    return image

def set_desktop_background(image_path):
    """
    设置桌面背景图片(适用于Windows系统)
    :param image_path: 图片路径
    """
    im = Image.open(image_path).convert('RGB')
    im.save(image_path.replace(".png",".jpg"))
    picPath = os.getcwd()+"\\"+image_path.replace(".png",".jpg")
    logging.info(f"Trying to set {picPath} as desktop background.")
    ctypes.windll.user32.SystemParametersInfoW(20, 0, picPath, 3)

def main():
    # 设置日志
    logging.basicConfig(filename='BirthdayWisher.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # 加载配置文件
    try:
        config = load_json('config.json')
    except Exception as e:
        logging.error(f"Failed to load config: {e}")
        return

    # 加载生日信息sssss
    try:
        birthdays += load_json(config['json_path'])
    except Exception as e:
        logging.error(f"Failed to load birthdays: {e}")
        return
    
    # print(birthdays)

    # 获取今天生日和周末生日名单
    today_birthdays = get_today_birthdays(birthdays)
    weekend_birthdays = get_upcoming_weekend_birthdays(birthdays)

    logging.info("Happy birthday "+', '.join([entry['name'] for entry in today_birthdays + weekend_birthdays]))

    # 判断是否需要生成生日祝福图片
    if today_birthdays or weekend_birthdays:
        try:
            image = create_birthday_image(config, today_birthdays, weekend_birthdays)
            output_path = os.path.join(os.path.dirname(config['template_image_path']), 'birthday_background.png')
            image.save(output_path)
            set_desktop_background(output_path)
            logging.info(f"Birthday image set as desktop background: {output_path}")
        except Exception as e:
            logging.error(f"Failed to create or set birthday image: {e}")
            logging.exception(e)
    else:
        try:
            set_desktop_background(config['default_background_path'])
            logging.info("No birthdays today. Default background set.")
        except Exception as e:
            logging.error(f"Failed to set default background: {e}")

if __name__ == "__main__":
    main()