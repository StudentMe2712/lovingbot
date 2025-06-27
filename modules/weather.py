import aiohttp
from datetime import datetime, timedelta
import logging

CITIES = ["Астана", "Семей"]

class WeatherModule:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_weather(self, city: str):
        logging.info(f"[WeatherModule] get_weather called for city: {city}")
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={self.api_key}&units=metric&lang=ru"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        logging.error(f"Weather: ошибка {resp.status}, ответ: {text}")
                        return f"Не удалось получить погоду. Код: {resp.status}", None
                    data = await resp.json()
                    now = datetime.now()
                    target_date = now.date()
                    # Найти ближайший прогноз к текущему времени дня
                    forecast = None
                    min_diff = float('inf')
                    for item in data["list"]:
                        dt = datetime.fromtimestamp(item["dt"])
                        if dt.date() == target_date:
                            diff = abs((dt - now).total_seconds())
                            if diff < min_diff:
                                min_diff = diff
                                forecast = item
                    # Если нет прогноза на сегодня — взять ближайший вообще
                    if not forecast and data["list"]:
                        forecast = data["list"][0]
                    if not forecast:
                        logging.error(f"Weather: нет прогноза в ответе: {data}")
                        return "Нет данных о погоде.", None
                    temp = forecast['main']['temp']
                    feels = forecast['main'].get('feels_like', '-')
                    desc = forecast['weather'][0]['description']
                    icon = forecast['weather'][0].get('icon', '')
                    humidity = forecast['main'].get('humidity', '-')
                    wind = forecast['wind'].get('speed', '-')
                    clouds = forecast.get('clouds', {}).get('all', '-')
                    pressure = forecast['main'].get('pressure', '-')
                    dt_txt = forecast.get('dt_txt', '')
                    icon_url = f"https://openweathermap.org/img/wn/{icon}@2x.png" if icon else ''
                    msg = (
                        f"{city} ({dt_txt}):\n"
                        f"Температура: {temp}°C (ощущается как {feels}°C)\n"
                        f"Описание: {desc}"
                    )
                    if icon_url:
                        msg += f"\n[ ]({icon_url})"
                    msg += (
                        f"\nВлажность: {humidity}%"
                        f"\nВетер: {wind} м/с"
                        f"\nОблачность: {clouds}%"
                        f"\nДавление: {pressure} гПа"
                    )
                    logging.info(f"[WeatherModule] get_weather result for {city}: {msg}")
                    return msg, None
        except aiohttp.ClientError as e:
            logging.exception(f"Weather: ClientError при запросе погоды для {city}: {e}")
            return f"Ошибка сети при получении погоды: {e}", None
        except Exception as e:
            logging.exception(f"Weather: исключение при запросе погоды для {city}")
            return f"Ошибка при получении погоды: {e}", None 