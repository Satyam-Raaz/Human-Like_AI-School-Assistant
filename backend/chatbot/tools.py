import math
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from Service.LongTermMemoryService import LongTermMemoryService
import requests
from typing import Any
import os
from Service.StudentService import StudentService
from database import SessionLocal
from models.parent import Parent
from pydantic import BaseModel, Field
from typing import Optional
from langchain_groq import ChatGroq
from langgraph.types import interrupt
from typing import Dict, Any






load_dotenv()


CURRENT_THREAD_ID = "default"
CURRENT_USER_ID = 1
CURRENT_ROLE="student"
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
STOCK_API_KEY= os.getenv("STOCK_API_KEY")
GROQ_API_KEY= os.getenv("GROQ_API_KEY")





def set_current_thread_id(thread_id: str):
    global CURRENT_THREAD_ID
    CURRENT_THREAD_ID = thread_id
    
def set_current_user_id(user_id: int):
    global CURRENT_USER_ID
    CURRENT_USER_ID = user_id  
    
    
def set_current_role(role: str):
    global CURRENT_ROLE
    CURRENT_ROLE=role
    
class StudentQuery(BaseModel):
    student_name: Optional[str] = Field(
        default=None,
        description="Name of the student mentioned by the user"
    )

    class_name: Optional[str] = Field(
        default=None,
        description="Class of the student mentioned by the user"
    )    
        
    
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=GROQ_API_KEY
)

structured_llm = llm.with_structured_output(StudentQuery)    


def extract_student_details(query: str):

    prompt = f"""

Extract the following information from the user's query:

1. student_name
2. class_name

Rules:
- Extract only information explicitly mentioned or clearly stated.
- Do not invent a student name.
- Do not invent a class.
- If the student name is missing, return null.
- If the class is missing, return null.
- Return only the structured fields.

User query:
{query}
"""

    result = structured_llm.invoke(prompt)

    return result


web_search = TavilySearch(
    max_results=5,
    topic="general",
    search_depth="advanced"
)


@tool
def calculator(expression: str) -> str:
    """
    Useful for simple math calculations.
    Input should be a valid math expression.
    Example: 2 + 2, math.sqrt(16), 10 * 5
    """

    try:
        allowed = {
            "math": math,
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum
        }

        result = eval(expression, {"__builtins__": {}}, allowed)
        return str(result)

    except Exception as e:
        return f"Calculation error: {str(e)}"
    
@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={STOCK_API_KEY}"
    r = requests.get(url)
    return r.json() 



@tool
def get_current_weather(location: str) -> str:
    """
    Get the current real-time weather for a given city or location.

    Args:
        location: City or location name, for example:
                  "Dhaka", "London, UK", or "New York, US".

    Returns:
        A formatted current weather report.
    """

    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return (
            "Weather API key is missing. "
            "Set the OPENWEATHER_API_KEY environment variable."
        )

    try:
        # Step 1: Convert the location name into latitude and longitude
        geocoding_url = "https://api.openweathermap.org/geo/1.0/direct"

        geocoding_params = {
            "q": location,
            "limit": 1,
            "appid": api_key,
        }

        geo_response = requests.get(
            geocoding_url,
            params=geocoding_params,
            timeout=10,
        )
        geo_response.raise_for_status()

        locations: list[dict[str, Any]] = geo_response.json()

        if not locations:
            return f"Could not find the location: {location}"

        latitude = locations[0]["lat"]
        longitude = locations[0]["lon"]
        resolved_name = locations[0].get("name", location)
        country = locations[0].get("country", "")
        state = locations[0].get("state", "")

        # Step 2: Get current weather using latitude and longitude
        weather_url = "https://api.openweathermap.org/data/2.5/weather"

        weather_params = {
            "lat": latitude,
            "lon": longitude,
            "appid": api_key,
            "units": "metric",
        }

        weather_response = requests.get(
            weather_url,
            params=weather_params,
            timeout=10,
        )
        weather_response.raise_for_status()

        weather_data = weather_response.json()

        temperature = weather_data["main"]["temp"]
        feels_like = weather_data["main"]["feels_like"]
        humidity = weather_data["main"]["humidity"]
        pressure = weather_data["main"]["pressure"]
        description = weather_data["weather"][0]["description"]
        wind_speed = weather_data.get("wind", {}).get("speed", "N/A")
        visibility_meters = weather_data.get("visibility")

        visibility_km = (
            round(visibility_meters / 1000, 1)
            if visibility_meters is not None
            else "N/A"
        )

        location_parts = [resolved_name]

        if state:
            location_parts.append(state)

        if country:
            location_parts.append(country)

        display_location = ", ".join(location_parts)

        return (
            f"Current weather in {display_location}:\n"
            f"- Condition: {description.title()}\n"
            f"- Temperature: {temperature}°C\n"
            f"- Feels like: {feels_like}°C\n"
            f"- Humidity: {humidity}%\n"
            f"- Pressure: {pressure} hPa\n"
            f"- Wind speed: {wind_speed} m/s\n"
            f"- Visibility: {visibility_km} km"
        )

    except requests.Timeout:
        return "The weather service request timed out. Please try again."

    except requests.HTTPError as error:
        status_code = error.response.status_code if error.response else "unknown"

        if status_code == 401:
            return "The OpenWeather API key is invalid or inactive."

        return f"Weather API returned an HTTP error: {status_code}"

    except requests.RequestException as error:
        return f"Could not connect to the weather service: {error}"

    except (KeyError, TypeError, ValueError) as error:
        return f"Unexpected weather API response: {error}"    
    






@tool
def remember_this(memory: str) -> str:
    """
    Save an important user preference or fact into long-term memory.
    Use this when the user asks you to remember something.
    """

    return LongTermMemoryService.save_memory(
        thread_id=CURRENT_THREAD_ID,
        memory=memory
    )



@tool
def recall_memory(query: str) -> str:
    """
    Recall saved long-term memories about the user or this conversation.
    """

    return LongTermMemoryService.search_memory(
        thread_id=CURRENT_THREAD_ID,
        query=query
    )
    

@tool
def get_student_details(student_name: str, class_name:str) -> str:
    """
    if user is student do not need student name and student id for fetch attendence
    if user is parent do not need student name and student id for fetch attendence
    if user is teacher then llm directly fetch student name and class from query to fetch student attendence

    """
    if CURRENT_ROLE=="student":
        std = StudentService.get_student(student_id=CURRENT_USER_ID)
        return f"You get total attendance percentage is {(std.attendance/250)*100}"
    
    if CURRENT_ROLE=="parent":
        db=SessionLocal()
        parent = db.query(Parent).filter(
            Parent.id == CURRENT_USER_ID
        ).first()    
        
        std = StudentService.get_student_by_id(student_id=parent.student_id)
        return f"Your child  {std.name} get total attendance percentage is {(std.attendance/250)*100}"
      
      
    if CURRENT_ROLE=="teacher":
        std =  StudentService.get_student_by_name_and_class(student_name,class_name)
        return f"student name {std.name} get total attendance percentage is {(std.attendance/250)*100}"
    
    
    
             
        
        
        
        
    
    

@tool
def mark_student_attendence(student_name: str, class_name:str) -> Dict[str, Any]:
        
    """
    Mark attendance of a student.

    Steps:
    1. Extract student name and class from the query.
    2. Ask human for confirmation.
    3. Update attendance in database.
    """

    # Validate extracted information
    if not student_name or not class_name:
        return {
            "status": "failed",
            "message": "Student name and class are required."
        }
        
    # Human-in-the-loop confirmation
    decision = interrupt(
        f"Approve marking attendance for student "
        f"{student_name} from class {class_name}? (yes/no)"
    )
    
        
    # Human rejected
    if not (isinstance(decision, str) and decision.lower() == "yes"):
        return {
            "status": "Not marking attendance",
            "message": (
                f"Attendance for {student_name} from class "
                f"{class_name} was declined by human."
            )
        }    
        
    
    
    if CURRENT_ROLE=="teacher":
        updated_student = StudentService.update_student_by_name_and_class(student_name,class_name)
        
        
        # Student not found / update failed
        if not updated_student:
            return {
                "status": "failed",
                "message": (
                    f"Student {student_name} from class "
                    f"{class_name} was not found."
                )
            }

        return {
            "status": "Marked attendance",
            "message": (
                f"Attendance for {student_name} from class "
                f"{class_name} was successfully marked."
            )
        }
        
        
@tool
def parent_connect_teacher() -> Dict[str, Any]:
    """
    Request a meeting between a parent and the child's teacher.
    No teacher name, teacher ID, student name, or class is required.
    """

    decision = interrupt(
        "Approve request to connect with your child's teacher for a meeting? (yes/no)"
    )

    if not (
        isinstance(decision, str)
        and decision.strip().lower() == "yes"
    ):
        return {
            "status": "cancelled",
            "message": "The parent cancelled the teacher meeting request."
        }

    return {
        "status": "success",
        "message": "The teacher meeting request was successfully confirmed."
    }
        
        
           
        
            
            
             
                
        

    
        
    
        
           
        
      
        
        
          

    

    
    





tools = [
    calculator,
    remember_this,
    recall_memory,
    web_search,
    get_current_weather,
    get_stock_price,
    get_student_details,
    mark_student_attendence,
    parent_connect_teacher
]