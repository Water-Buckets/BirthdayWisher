import json, datetime, os, ctypes, logging, PIL.Image, PIL.ImageDraw, PIL.ImageFont
if __name__ == "__main__":
    logging.basicConfig(filename='BirthdayWisher.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
    try: config = json.load(open('config.json', 'r', encoding='utf-8'))
    except Exception as e: logging.exception(f"Failed to load config: {e}"); exit()
    try: birthdays = json.load(open(config['json_path'], 'r', encoding='utf-8'))
    except Exception as e: logging.exception(f"Failed to load birthdays: {e}"); exit()
    today_birthdays, weekend_birthdays = [entry for entry in birthdays if datetime.datetime.strptime(entry['birthday'], '%Y-%m-%d').date().replace(year=datetime.date.today().year) == datetime.date.today()], [entry for entry in birthdays if datetime.date.today() < datetime.datetime.strptime(entry['birthday'], '%Y-%m-%d').date().replace(year=datetime.date.today().year) <= datetime.date.today() + datetime.timedelta(days=2)] if datetime.date.today().weekday() == 4 else []
    logging.info("Happy birthday "+', '.join([entry['name'] for entry in today_birthdays + weekend_birthdays]))
    try:
        if today_birthdays or weekend_birthdays:
            image = PIL.Image.open(config['template_image_path'])
            width, height = image.size
            wish = ('' if not today_birthdays else f"祝{'、'.join([entry['name'] for entry in today_birthdays])} {datetime.date.today().year - datetime.datetime.strptime(today_birthdays[0]['birthday'], '%Y-%m-%d').year} 岁生日快乐!") + ('' if not weekend_birthdays else "\n\n" + "\n\n".join([f"提前祝{entry['name']} {datetime.date.today().year - datetime.datetime.strptime(entry['birthday'], '%Y-%m-%d').year} 岁生日快乐! ("+ str(datetime.datetime.strptime(entry['birthday'], '%Y-%m-%d').month) + "." +str(datetime.datetime.strptime(entry['birthday'], '%Y-%m-%d').day)+")" for entry in weekend_birthdays]))
            PIL.ImageDraw.Draw(image).text((width // 2, height // 2), wish, font=PIL.ImageFont.truetype(config['font_path'], config['font_size']), fill=config['font_color'], anchor='mm')
            image.save(os.path.join(os.path.dirname(config['template_image_path']), 'birthday_background.png'))
            ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(os.path.join(os.path.dirname(config['template_image_path']), 'birthday_background.png')), 3)
            logging.info(f"Birthday image set as desktop background: {os.path.join(os.path.dirname(config['template_image_path']), 'birthday_background.png')}")
        else: ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(config['default_background_path']), 3); logging.info("No birthdays today. Default background set.")
    except Exception as e: logging.exception(f"Failed to create or set birthday image or default background: {e}")
