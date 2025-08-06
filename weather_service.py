import requests
from typing import Dict, Any, Optional
from config import Config

class WeatherService:
    """Weather service using OpenWeatherMap API"""
    
    def __init__(self):
        """Initialize weather service with API key"""
        self.api_key = Config.OPENWEATHER_API_KEY
        self.base_url = Config.WEATHER_BASE_URL
        
        # Indian cities with coordinates
        self.indian_cities = {
            "delhi": {"lat": 28.6139, "lon": 77.2090},
            "mumbai": {"lat": 19.0760, "lon": 72.8777},
            "bangalore": {"lat": 12.9716, "lon": 77.5946},
            "chennai": {"lat": 13.0827, "lon": 80.2707},
            "kolkata": {"lat": 22.5726, "lon": 88.3639},
            "hyderabad": {"lat": 17.3850, "lon": 78.4867},
            "pune": {"lat": 18.5204, "lon": 73.8567},
            "ahmedabad": {"lat": 23.0225, "lon": 72.5714},
            "jaipur": {"lat": 26.9124, "lon": 75.7873},
            "lucknow": {"lat": 26.8467, "lon": 80.9462},
            "kanpur": {"lat": 26.4499, "lon": 80.3319},
            "nagpur": {"lat": 21.1458, "lon": 79.0882},
            "indore": {"lat": 22.7196, "lon": 75.8577},
            "thane": {"lat": 19.2183, "lon": 72.9781},
            "bhopal": {"lat": 23.2599, "lon": 77.4126},
            "visakhapatnam": {"lat": 17.6868, "lon": 83.2185},
            "patna": {"lat": 25.5941, "lon": 85.1376},
            "vadodara": {"lat": 22.3072, "lon": 73.1812},
            "ghaziabad": {"lat": 28.6654, "lon": 77.4391},
            "ludhiana": {"lat": 30.9010, "lon": 75.8573}
        }
    
    def get_weather_by_city(self, city: str, country_code: Optional[str] = None) -> Dict[str, Any]:
        """Get weather data for a city"""
        try:
            # Check if it's an Indian city
            city_lower = city.lower()
            if city_lower in self.indian_cities:
                coords = self.indian_cities[city_lower]
                return self.get_weather_by_coordinates(coords["lat"], coords["lon"])
            
            # Build query parameters
            params = {
                'q': f"{city},{country_code}" if country_code else city,
                'appid': self.api_key,
                'units': 'metric'  # Use metric units
            }
            
            # Make API request
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant information
            weather_info = {
                'city': data['name'],
                'country': data['sys']['country'],
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind'].get('deg', 'N/A'),
                'visibility': data.get('visibility', 'N/A'),
                'sunrise': data['sys']['sunrise'],
                'sunset': data['sys']['sunset']
            }
            
            return weather_info
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Weather API request failed: {str(e)}")
        except KeyError as e:
            raise Exception(f"Unexpected weather data format: {str(e)}")
        except Exception as e:
            raise Exception(f"Error getting weather data: {str(e)}")
    
    def get_weather_by_coordinates(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get weather data by coordinates"""
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            weather_info = {
                'city': data['name'],
                'country': data['sys']['country'],
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind'].get('deg', 'N/A'),
                'visibility': data.get('visibility', 'N/A'),
                'sunrise': data['sys']['sunrise'],
                'sunset': data['sys']['sunset']
            }
            
            return weather_info
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Weather API request failed: {str(e)}")
        except KeyError as e:
            raise Exception(f"Unexpected weather data format: {str(e)}")
        except Exception as e:
            raise Exception(f"Error getting weather data: {str(e)}")
    
    def get_aqi_info(self, city: str) -> Dict[str, Any]:
        """Get AQI information for a city (Note: OpenWeatherMap doesn't provide AQI)"""
        try:
            # For AQI, you would need a different API like AirVisual or WAQI
            # This is a placeholder implementation
            city_lower = city.lower()
            if city_lower in self.indian_cities:
                coords = self.indian_cities[city_lower]
                weather_data = self.get_weather_by_coordinates(coords["lat"], coords["lon"])
                
                # Add AQI placeholder (you would need to integrate with AQI API)
                aqi_info = {
                    'city': weather_data['city'],
                    'weather_data': weather_data,
                    'aqi_note': 'AQI data requires separate API integration',
                    'suggested_aqi_apis': [
                        'AirVisual API',
                        'WAQI (World Air Quality Index)',
                        'OpenWeatherMap Air Pollution API'
                    ]
                }
                return aqi_info
            else:
                return {
                    'error': f'City {city} not found in Indian cities database',
                    'available_cities': list(self.indian_cities.keys())
                }
                
        except Exception as e:
            return {'error': f'Error getting AQI data: {str(e)}'}
    
    def format_weather_response(self, weather_data: Dict[str, Any]) -> str:
        """Format weather data into a readable response"""
        try:
            response = f"""
🌤️ Weather Report for {weather_data['city']}, {weather_data['country']}

🌡️ Temperature: {weather_data['temperature']}°C (feels like {weather_data['feels_like']}°C)
💧 Humidity: {weather_data['humidity']}%
🌪️ Wind: {weather_data['wind_speed']} m/s
📊 Pressure: {weather_data['pressure']} hPa
👁️ Visibility: {weather_data['visibility']} meters
☁️ Conditions: {weather_data['description'].title()}
            """.strip()
            
            return response
            
        except Exception as e:
            return f"Error formatting weather response: {str(e)}"
    
    def get_indian_cities_list(self) -> list:
        """Get list of available Indian cities"""
        return list(self.indian_cities.keys()) 