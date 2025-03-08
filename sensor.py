"""
Mauritius Weather Component for Home Assistant
https://github.com/Abdur-rahmaanJ/meteomoris

For more information about Home Assistant custom components, visit:
https://developers.home-assistant.io/docs/creating_component_index
"""
import logging
import voluptuous as vol
from datetime import timedelta

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import (
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    UnitOfTemperature,
)
SPEED_KILOMETERS_PER_HOUR = 'km/h'
import homeassistant.helpers.config_validation as cv

# Import the meteomoris library
try:
    from meteomoris import (
        get_main_message,
        get_special_weather_bulletin,
        get_weekforecast,
        get_cityforecast,
        get_moonphase,
        get_sunrisemu,
        get_tides,
        get_latest,
        get_uvindex,
        get_today_moonphase,
        get_today_sunrise,
        get_today_forecast,
        get_today_tides,
    )
except ImportError:
    logging.getLogger(__name__).error("Failed to import meteomoris. Make sure it's installed with pip install meteomoris")

DOMAIN = "mauritius_weather"
DEFAULT_NAME = "Mauritius Weather"
DEFAULT_SCAN_INTERVAL = timedelta(minutes=30)

# Configuration schema
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period,
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Mauritius Weather sensor platform."""
    name = config.get(CONF_NAME)
    
    try:
        # Create various sensors
        sensors = [
            MauritiusSpecialBulletin(name, "warning"),
            MauritiusWeatherForecast(name, "forecast"),
            MauritiusWeatherUVIndex(name, "uv_index"),
            MauritiusWeatherTides(name, "tides"),
            MauritiusWeatherSunrise(name, "sunrise"),
            MauritiusWeatherMoonPhase(name, "moon_phase"),
            MauritiusWeatherWind(name, "wind"),
            MauritiusWeatherRainfall(name, "rainfall"),
            MauritiusMainMessage(name, 'message')
        ]
        
        add_entities(sensors, True)
    except Exception as e:
        logging.getLogger(__name__).error(f"Error setting up Mauritius Weather component: {e}")


class MauritiusWeatherBase(SensorEntity):
    """Base class for Mauritius Weather sensors."""
    
    def __init__(self, name, sensor_type):
        """Initialize the sensor."""
        self._name = name
        self._sensor_type = sensor_type
        self._state = None
        self._attributes = {}
    
    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name} {self._sensor_type.replace('_', ' ').title()}"
    
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes
    
    @property
    def should_poll(self):
        """Device should be polled."""
        return True


class MauritiusSpecialBulletin(MauritiusWeatherBase):
    """Representation of a Mauritius weather warning sensor."""
    
    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:alert-circle"
    
    def update(self):
        """Fetch new state data for the sensor."""
        try:
            # Get the main warning message
            warning = get_special_weather_bulletin()
            self._state = warning if warning else "No special bulletin"
            

        except Exception as e:
            logging.getLogger(__name__).error(f"Error updating warning sensor: {e}")
            self._state = "Error"
            self._attributes = {"error": str(e)}


class MauritiusWeatherForecast(MauritiusWeatherBase):
    """Representation of a Mauritius weather forecast sensor."""
    
    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:weather-partly-cloudy"
    
    def update(self):
        """Fetch new state data for the sensor."""
        try:
            # Get today's forecast
            today = get_today_forecast()
            self._state = today.get("condition", "Unknown")
            
            # Get week forecast
            week_forecast = get_weekforecast()
            
            # Get city forecasts
            city_forecasts = get_cityforecast()
            
            self._attributes = {
                "today": today,
                "week_forecast": week_forecast[:5],  # Show next 5 days
                "city_forecasts": city_forecasts,
            }
        except Exception as e:
            logging.getLogger(__name__).error(f"Error updating forecast sensor: {e}")
            self._state = "Error"
            self._attributes = {"error": str(e)}


class MauritiusWeatherUVIndex(MauritiusWeatherBase):
    """Representation of a Mauritius UV index sensor."""
    
    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:weather-sunny-alert"
    
    def update(self):
        """Fetch new state data for the sensor."""
        try:
            # Get UV index
            uv_data = get_uvindex()
            
            # Use Port Louis as the main UV index if available
            if "port-louis" in uv_data:
                self._state = f'port-louis: {uv_data["port-louis"]}'
            else:
                self._state = next(iter(uv_data.values()), "Unknown")
            
            self._attributes = {
                "uv_index_by_location": uv_data,
            }
        except Exception as e:
            logging.getLogger(__name__).error(f"Error updating UV index sensor: {e}")
            self._state = "Error"
            self._attributes = {"error": str(e)}


class MauritiusMainMessage(MauritiusWeatherBase):
    """Representation of a Mauritius UV index sensor."""
    
    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:email-outline"
    
    def update(self):
        """Fetch new state data for the sensor."""
        try:
            # Get UV index
            message = get_main_message()
            
            self._state = message

        except Exception as e:
            logging.getLogger(__name__).error(f"Error updating UV index sensor: {e}")
            self._state = "Error"
            self._attributes = {"error": str(e)}

class MauritiusWeatherTides(MauritiusWeatherBase):
    """Representation of a Mauritius tides sensor."""
    
    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:wave"
    
    def update(self):
        """Fetch new state data for the sensor."""
        try:
            # Get today's tides
            tides = get_today_tides()
            
            if tides and len(tides) >= 8:
                # Convert tide data to more readable format
                high_tide_1_time = tides[0]
                high_tide_1_height = tides[1]
                high_tide_2_time = tides[2]
                high_tide_2_height = tides[3]
                low_tide_1_time = tides[4]
                low_tide_1_height = tides[5]
                low_tide_2_time = tides[6]
                low_tide_2_height = tides[7]
                
                self._state = f"{high_tide_1_time}@{high_tide_1_height}cm {high_tide_2_time}@{high_tide_2_height}cm {low_tide_1_time}@{low_tide_1_height}cm {low_tide_2_time}@{low_tide_2_height}cm"
                
                self._attributes = {
                    "high_tide_1": {
                        "time": high_tide_1_time,
                        "height_cm": high_tide_1_height,
                    },
                    "high_tide_2": {
                        "time": high_tide_2_time,
                        "height_cm": high_tide_2_height,
                    },
                    "low_tide_1": {
                        "time": low_tide_1_time,
                        "height_cm": low_tide_1_height,
                    },
                    "low_tide_2": {
                        "time": low_tide_2_time,
                        "height_cm": low_tide_2_height,
                    },
                }
            else:
                self._state = "No Data"
                self._attributes = {}
        except Exception as e:
            logging.getLogger(__name__).error(f"Error updating tides sensor: {e}")
            self._state = "Error"
            self._attributes = {"error": str(e)}


class MauritiusWeatherSunrise(MauritiusWeatherBase):
    """Representation of a Mauritius sunrise/sunset sensor."""
    
    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:weather-sunset-up"
    
    def update(self):
        """Fetch new state data for the sensor."""
        try:
            # Get today's sunrise/sunset for Mauritius
            sunrise_data = get_today_sunrise("mu")
            
            if sunrise_data and "rise" in sunrise_data and "set" in sunrise_data:
                self._state = f"{sunrise_data['rise']} - {sunrise_data['set']}"
                
                self._attributes = {
                    "sunrise": sunrise_data["rise"],
                    "sunset": sunrise_data["set"],
                }
            else:
                self._state = "No Data"
                self._attributes = {}
        except Exception as e:
            logging.getLogger(__name__).error(f"Error updating sunrise sensor: {e}")
            self._state = "Error"
            self._attributes = {"error": str(e)}


class MauritiusWeatherMoonPhase(MauritiusWeatherBase):
    """Representation of a Mauritius moon phase sensor."""
    
    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:moon-waxing-crescent"
    
    def update(self):
        """Fetch new state data for the sensor."""
        try:
            # Get today's moon phase
            moon_phase = get_today_moonphase()
            
            if moon_phase and "title" in moon_phase:
                self._state = moon_phase["title"].title()
                
                self._attributes = {
                    "time": f"{moon_phase.get('hour', '00')}:{moon_phase.get('minute', '00').zfill(2)}",
                    "full_data": moon_phase,
                }
            else:
                # Get current month's moon phases
                current_moon_phases = get_moonphase()
                if current_moon_phases:
                    self._state = "No phase today"
                    # Get the first month's data
                    first_month = next(iter(current_moon_phases.values()))
                    self._attributes = {
                        "upcoming_phases": first_month
                    }
                else:
                    self._state = "No Data"
                    self._attributes = {}
        except Exception as e:
            logging.getLogger(__name__).error(f"Error updating moon phase sensor: {e}")
            self._state = "Error"
            self._attributes = {"error": str(e)}


class MauritiusWeatherWind(MauritiusWeatherBase):
    """Representation of a Mauritius wind and temperature sensor."""
    
    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:weather-windy-variant"
    
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return SPEED_KILOMETERS_PER_HOUR
    
    def update(self):
        """Fetch new state data for the sensor."""
        try:
            # Get latest wind data
            latest_data = get_latest()
            
            if latest_data and "wind" in latest_data and "data" in latest_data["wind"]:
                wind_data = latest_data["wind"]["data"]
                
                # Use Vacoas data as the main reading if available
                if "Vacoas" in wind_data and wind_data["Vacoas"]:
                    self._state = f'Vacoas: {wind_data["Vacoas"]}'
                else:
                    # Find the first non-empty wind reading
                    for location, speed in wind_data.items():
                        if speed:
                            self._state = f'{location}:{speed}'
                            break
                    else:
                        self._state = "No Data"
                
                self._attributes = {
                    "wind_by_location": wind_data,
                    "wind_info": latest_data["wind"].get("info", ""),
                }
                
                # Add temperature data if available
                if "minmaxtemp" in latest_data and "data" in latest_data["minmaxtemp"]:
                    temp_data = latest_data["minmaxtemp"]["data"]
                    temp_info = latest_data["minmaxtemp"].get("info", "")
                    self._attributes.update({
                        "temperature_by_location": temp_data,
                        "temperature_info": temp_info,
                    })
            else:
                self._state = "No Data"
                self._attributes = {}
        except Exception as e:
            logging.getLogger(__name__).error(f"Error updating wind and temperature sensor: {e}")
            self._state = "Error"
            self._attributes = {"error": str(e)}


class MauritiusWeatherRainfall(MauritiusWeatherBase):
    """Representation of a Mauritius rainfall sensor."""
    
    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:weather-rainy"
    
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "mm"
    
    def update(self):
        """Fetch new state data for the sensor."""
        try:
            # Get latest rainfall data
            latest_data = get_latest()
            
            if (latest_data and "rainfall24h" in latest_data and 
                    "data" in latest_data["rainfall24h"]):
                rain_data = latest_data["rainfall24h"]["data"]
                
                # Use Vacoas data as the main reading if available
                if "Vacoas" in rain_data and rain_data["Vacoas"]:
                    self._state = f'Vacoas: {rain_data["Vacoas"]}'
                else:
                    # Find the first non-empty rainfall reading
                    for location, amount in rain_data.items():
                        if amount:
                            self._state = f'{location}: {amount}'
                            break
                    else:
                        self._state = "0mm"
                
                self._attributes = {
                    "rainfall_24h_by_location": rain_data,
                    "rainfall_24h_info": latest_data["rainfall24h"].get("info", ""),
                }
                
                # Add 3-hour rainfall data if available
                if "rainfall3hrs" in latest_data and "data" in latest_data["rainfall3hrs"]:
                    rain3h_data = latest_data["rainfall3hrs"]["data"]
                    rain3h_info = latest_data["rainfall3hrs"].get("info", "")
                    self._attributes.update({
                        "rainfall_3h_by_location": rain3h_data,
                        "rainfall_3h_info": rain3h_info,
                    })
                
                # Add humidity data if available
                if "humidity" in latest_data and "data" in latest_data["humidity"]:
                    humidity_data = latest_data["humidity"]["data"]
                    humidity_info = latest_data["humidity"].get("info", "")
                    self._attributes.update({
                        "humidity_by_location": humidity_data,
                        "humidity_info": humidity_info,
                    })
            else:
                self._state = "0"
                self._attributes = {}
        except Exception as e:
            logging.getLogger(__name__).error(f"Error updating rainfall sensor: {e}")
            self._state = "Error"
            self._attributes = {"error": str(e)}