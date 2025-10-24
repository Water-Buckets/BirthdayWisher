import json, datetime, os, ctypes, logging, PIL.Image, PIL.ImageDraw, PIL.ImageFont

if __name__ == "__main__":
    logging.basicConfig(filename='BirthdayWisher.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
    try: config = json.load(open('config.json', 'r', encoding='utf-8'))
    except Exception as e: logging.exception(f"Failed to load config: {e}"); exit()
    try: birthdays = json.load(open(config['birthdays_path'], 'r', encoding='utf-8'))
    except Exception as e: logging.exception(f"Failed to load birthdays: {e}"); exit()
    try: dates_config = json.load(open(config['dates_config_path'], 'r', encoding='utf-8'))
    except Exception as e: logging.exception(f"Failed to load dates config: {e}"); exit()
    today_birthdays, weekend_birthdays = [entry for entry in birthdays if datetime.datetime.strptime(entry['birthday'], '%Y-%m-%d').date().replace(year=datetime.date.today().year) == datetime.date.today()], [entry for entry in birthdays if datetime.date.today() < datetime.datetime.strptime(entry['birthday'], '%Y-%m-%d').date().replace(year=datetime.date.today().year) <= datetime.date.today() + datetime.timedelta(days=2)] if datetime.date.today().weekday() == 4 else []
    try:
        days_remaining = (datetime.date(2026, 6, 7) - datetime.date.today()).days
        logging.info(f"Days remaining until 2026-06-07: {days_remaining}")

        if today_birthdays or weekend_birthdays:
            logging.info("Happy birthday " + ', '.join([entry['name'] for entry in today_birthdays + weekend_birthdays]))
            image = PIL.Image.open(config['template_image_path'])
            width, height = image.size
            draw = PIL.ImageDraw.Draw(image)
            draw.text((width // 2, height // 2), ('' if not today_birthdays else f"祝{'、'.join([entry['name'] for entry in today_birthdays])} {datetime.date.today().year - datetime.datetime.strptime(today_birthdays[0]['birthday'], '%Y-%m-%d').year} 岁生日快乐!") + ('' if not weekend_birthdays else ('' if not today_birthdays else '\n\n') + "\n\n".join([f"提前祝{entry['name']} {datetime.date.today().year - datetime.datetime.strptime(entry['birthday'], '%Y-%m-%d').year} 岁生日快乐! ("+ str(datetime.datetime.strptime(entry['birthday'], '%Y-%m-%d').month) + "." +str(datetime.datetime.strptime(entry['birthday'], '%Y-%m-%d').day)+")" for entry in weekend_birthdays])), font=PIL.ImageFont.truetype(config['font_path'], config['font_size']), fill=config['font_color'], anchor='mm')
            draw.text((width - 40, 40), f"以防你不知道\n\n{'\n\n'.join([f"距离{date_entry['name']}还有{'约' if date_entry.get('approximate', False) else ''}{(datetime.datetime.strptime(date_entry['date'], '%Y-%m-%d').date() - datetime.date.today()).days}天" for date_entry in dates_config['dates']])}", font=PIL.ImageFont.truetype(config['font_path'], config['font_size']//2), fill=config['font_color'], anchor='ra', align='right')
            draw.text((40, height - 40), f"自2025.01.02以来第{((datetime.date.today() - datetime.date(2025, 1, 2)).days + (datetime.date(2025, 1, 2).weekday() - 3) % 7) // 7 + 1}个星期四" if datetime.date.today().weekday() == 3 else "", font=PIL.ImageFont.truetype(config['font_path'], config['font_size'] // 3), fill=config['font_color'], anchor='lb')
            image.save(os.path.join(os.path.dirname(config['template_image_path']), 'birthday_background.png'))
            ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(os.path.join(os.path.dirname(config['template_image_path']), 'birthday_background.png')), 3)
            logging.info(f"Birthday image set as desktop background: {os.path.join(os.path.dirname(config['template_image_path']), 'birthday_background.png')}")
        else:
            image = PIL.Image.open(config['default_background_path'])
            width, height = image.size
            draw = PIL.ImageDraw.Draw(image)
            draw.text((width - 40, 40), f"以防你不知道\n\n{'\n\n'.join([f"距离{date_entry['name']}还有{'约' if date_entry.get('approximate', False) else ''}{(datetime.datetime.strptime(date_entry['date'], '%Y-%m-%d').date() - datetime.date.today()).days}天" for date_entry in dates_config['dates']])}", font=PIL.ImageFont.truetype(config['font_path'], config['font_size']//2), fill=config['font_color'], anchor='ra', align='right')
            draw.text((40, height - 40), f"自2025.01.02以来第{((datetime.date.today() - datetime.date(2025, 1, 2)).days + (datetime.date(2025, 1, 2).weekday() - 3) % 7) // 7 + 1}个星期四" if datetime.date.today().weekday() == 3 else "", font=PIL.ImageFont.truetype(config['font_path'], config['font_size'] // 3), fill=config['font_color'], anchor='lb')
            image.save(os.path.join(os.path.dirname(config['template_image_path']), 'birthday_background.png'))
            ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(os.path.join(os.path.dirname(config['template_image_path']), 'birthday_background.png')), 3)
            logging.info("No birthdays today. Default background set with days remaining info.")
    except Exception as e: logging.exception(f"Failed to create or set birthday image or default background: {e}")
