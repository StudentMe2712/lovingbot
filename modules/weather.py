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
                        return f"❌ Не удалось получить погоду. Код: {resp.status}"
                    data = await resp.json()
                    now = datetime.now()
                    target_date = now.date()
                    forecast = None
                    min_diff = float('inf')
                    for item in data["list"]:
                        dt = datetime.fromtimestamp(item["dt"])
                        if dt.date() == target_date:
                            diff = abs((dt - now).total_seconds())
                            if diff < min_diff:
                                min_diff = diff
                                forecast = item
                    if not forecast and data["list"]:
                        forecast = data["list"][0]
                    if not forecast:
                        logging.error(f"Weather: нет прогноза в ответе: {data}")
                        return "Нет данных о погоде."
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
                    emoji = "☀️" if "ясно" in desc else ("🌧️" if "дожд" in desc else "☁️")
                    msg = (
                        f"{emoji} <b>{city}</b> <i>({dt_txt})</i>\n"
                        f"Температура: <b>{temp}°C</b> (ощущается как {feels}°C)\n"
                        f"Описание: <b>{desc}</b>\n"
                    )
                    if icon_url:
                        msg += f'<a href="{icon_url}">&#8205;</a>'
                    msg += (
                        f"Влажность: {humidity}%\n"
                        f"Ветер: {wind} м/с\n"
                        f"Облачность: {clouds}%\n"
                        f"Давление: {pressure} гПа"
                    )
                    logging.info(f"[WeatherModule] get_weather result for {city}: {msg}")
                    return msg
        except aiohttp.ClientError as e:
            logging.exception(f"Weather: ClientError при запросе погоды для {city}: {e}")
            return f"Ошибка сети при получении погоды: {e}"
        except Exception as e:
            logging.exception(f"Weather: исключение при запросе погоды для {city}")
            return f"Ошибка при получении погоды: {e}" 