import json
import datetime
from PIL import Image, ImageDraw, ImageFont
import os
import ctypes
import logging

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def get_today_birthdays(birthdays):
    today = datetime.date.today()
    today_birthdays = [entry for entry in birthdays if datetime.datetime.strptime(entry['birthday'], '%Y-%m-%d').date().replace(year=today.year) == today]
    return today_birthdays

def get_upcoming_weekend_birthdays(birthdays):
    today = datetime.date.today()
    weekend_birthdays = []
    if today.weekday() == 4: #Friday.
        for entry in birthdays:
            birthday = datetime.datetime.strptime(entry['birthday'], '%Y-%m-%d').date().replace(year=today.year)
            if today < birthday <= today + datetime.timedelta(days=2):
                weekend_birthdays.append(entry)
    return weekend_birthdays

def create_birthday_image(config, today_birthdays, weekend_birthdays):
    # 打开模板图片
    image = Image.open(config['template_image_path'])

    width, height = image.size

    # 字符串拼接
    wish = ('' if not today_birthdays else f"祝{'、'.join([entry['name'] for entry in today_birthdays])} {datetime.date.today().year - datetime.datetime.strptime(today_birthdays[0]['birthday'], '%Y-%m-%d').year} 岁生日快乐!") + ('' if not weekend_birthdays else "\n\n" + "\n\n".join([f"提前祝{entry['name']} {datetime.date.today().year - datetime.datetime.strptime(entry['birthday'], '%Y-%m-%d').year} 岁生日快乐! ("+ str(datetime.datetime.strptime(entry['birthday'], '%Y-%m-%d').month) + "." +str(datetime.datetime.strptime(entry['birthday'], '%Y-%m-%d').day)+")" for entry in weekend_birthdays]))

    ImageDraw.Draw(image).text((width // 2, height // 2), wish, font=ImageFont.truetype(config['font_path'], config['font_size']), fill=config['font_color'], anchor='mm')

    return image

def set_desktop_background(image_path):
    ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(image_path), 3)

def main():
    # 设置日志
    logging.basicConfig(filename='BirthdayWisher.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')

    # 加载配置文件
    try:
        config = load_json('config.json')
    except Exception as e:
        logging.error(f"Failed to load config: {e}")
        logging.exception(e)
        return

    # 加载生日信息
    try:
        birthdays = load_json(config['json_path'])
    except Exception as e:
        logging.error(f"Failed to load birthdays: {e}")
        logging.exception(e)
        return
    
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
            logging.exception(e)

if __name__ == "__main__":
    main()
