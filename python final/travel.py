import os
import json
from datetime import datetime
from typing import List
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


class TripPlan:
    def __init__(self, location: str, nation: str, start: str, end: str, budget: float, interests: List[str]):
        self.location = location
        self.nation = nation
        self.start = start
        self.end = end
        self.budget = budget
        self.interests = interests

    def __str__(self):
        return f"{self.location}, {self.nation} | {self.start} to {self.end} | Budget: ${self.budget:.2f}"

    def to_dict(self):
        return {
            "location": self.location,
            "nation": self.nation,
            "start": self.start,
            "end": self.end,
            "budget": self.budget,
            "interests": self.interests
        }

    @staticmethod
    def from_dict(data: dict):
        return TripPlan(
            data["location"],
            data["nation"],
            data["start"],
            data["end"],
            data["budget"],
            data["interests"]
        )


class TripStorage:
    def __init__(self, filename="trips.json"):
        self.filename = filename

    def save(self, trips: List[TripPlan]):
        with open(self.filename, "w") as f:
            json.dump([trip.to_dict() for trip in trips], f, indent=4)

    def load(self):
        if not os.path.exists(self.filename):
            return []
        with open(self.filename, "r") as f:
            data = json.load(f)
            return [TripPlan.from_dict(item) for item in data]


class AIPlanner:
    def __init__(self):
            self.client = OpenAI(api_key=api_key)

    def suggest_itinerary(self, trip: TripPlan) -> str:
        
        prompt = (
            f"Create a detailed travel itinerary for {trip.location}, {trip.nation} "
            f"from {trip.start} to {trip.end}. "
            f"Budget: ${trip.budget:.2f}. "
            f"Traveler interests: {', '.join(trip.interests)}"
        )
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert travel assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error fetching itinerary: {e}"

    def generate_budget_tips(self, trip: TripPlan) -> str:
            
        prompt = (
            f"Give budget travel tips for {trip.location}, {trip.nation} "
            f"with a budget of ${trip.budget:.2f}. "
            "Include cheap accommodation, dining, transport, free activities, and best times to visit."
        )
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a budget travel expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error fetching budget tips: {e}"

#Main Menu
class TravelAssistant:
    def __init__(self):
        self.storage = TripStorage()
        self.planner = AIPlanner()
        self.trips = self.storage.load()

    def run(self):
        while True:
            self.show_menu()
            choice = input("Choose option (1-9): ").strip()
            if choice == "1":
                self.add_trip()
            elif choice == "2":
                self.remove_trip()
            elif choice == "3":
                self.update_trip()
            elif choice == "4":
                self.view_all_trips()
            elif choice == "5":
                self.search_trips()
            elif choice == "6":
                self.ai_assistance()
            elif choice == "7":
                self.storage.save(self.trips)
                print("Itinerary saved.")
            elif choice == "8":
                self.trips = self.storage.load()
                print("Itinerary loaded.")
            elif choice == "9":
                self.storage.save(self.trips)
                print("Goodbye! Your itinerary is saved.")
                break
            else:
                print("Invalid option! Please choose between 1-9.")

    def show_menu(self):
        print("\n--- MENU ---")
        print("1. Add Destination")
        print("2. Remove Destination")
        print("3. Update Destination")
        print("4. View All Destinations")
        print("5. Search Destination")
        print("6. AI Travel Assistance")
        print("7. Save Itinerary")
        print("8. Load Itinerary")
        print("9. Exit")

#Add trip
    def add_trip(self):
        print("\nAdd a New Destination")
        location = input("City: ").strip()
        nation = input("Country: ").strip()
        start = input("Start date (YYYY-MM-DD): ").strip()
        end = input("End date (YYYY-MM-DD): ").strip()
        try:
            budget = float(input("Budget (USD): ").strip())
        except ValueError:
            print("Invalid budget input.")
            return
        interests = input("Interests (comma separated): ").strip().split(",")
        interests = [i.strip() for i in interests if i.strip()]
        if not interests:
            print("At least one interest required.")
            return
        trip = TripPlan(location, nation, start, end, budget, interests)
        self.trips.append(trip)
        print("Destination added.")

#Remove trip
    def remove_trip(self):
        self.view_all_trips()
        if not self.trips:
            return
        city = input("Enter city name to remove: ").strip().lower()
        for i, trip in enumerate(self.trips):
            if trip.location.lower() == city:
                removed = self.trips.pop(i)
                print(f"Removed {removed.location}, {removed.nation}.")
                return
        print("City not found.")

#Update trip
    def update_trip(self):
        self.view_all_trips()
        if not self.trips:
            return
        city = input("Enter city name to update: ").strip().lower()
        for trip in self.trips:
            if trip.location.lower() == city:
                print(f"Updating {trip}")
                print("1. Update Budget")
                print("2. Update Interests")
                print("3. Update Dates")
                choice = input("Choose what to update (1-3): ").strip()
                if choice == "1":
                    try:
                        new_budget = float(input("New Budget (USD): ").strip())
                        trip.budget = new_budget
                        print("Budget updated.")
                    except ValueError:
                        print("Invalid budget.")
                elif choice == "2":
                    interests = input("New interests (comma separated): ").strip().split(",")
                    interests = [i.strip() for i in interests if i.strip()]
                    if interests:
                        trip.interests = interests
                        print("Interests updated.")
                    else:
                        print("No interests entered.")
                elif choice == "3":
                    new_start = input("New start date (YYYY-MM-DD): ").strip()
                    new_end = input("New end date (YYYY-MM-DD): ").strip()
                    trip.start = new_start
                    trip.end = new_end
                    print("Dates updated.")
                else:
                    print("Invalid option.")
                return
        print("City not found.")

#View All trips
    def view_all_trips(self):
        if not self.trips:
            print("No destinations found.")
            return
        print("\nYour Destinations:")
        for i, trip in enumerate(self.trips, start=1):
            print(f"{i}. {trip}")

#Search Trip
    def search_trips(self):
        query = input("Search by city, country, or interest: ").strip().lower()
        results = []
        for trip in self.trips:
            if (query in trip.location.lower() or 
                query in trip.nation.lower() or
                any(query in interest.lower() for interest in trip.interests)):
                results.append(trip)
        if results:
            print(f"\nFound {len(results)} result(s):")
            for i, trip in enumerate(results, 1):
                print(f"{i}. {trip}")
        else:
            print("No matches found.")

#AI help and suggestion
    def ai_assistance(self):
        self.view_all_trips()
        if not self.trips:
            return
        try:
            idx = int(input("Select destination number for AI assistance: "))
            trip = self.trips[idx - 1]
            print("\n1. Generate Daily Itinerary")
            print("2. Get Budget Tips")
            choice = input("Choose the options (1-2): ").strip()
            if choice == "1":
                print("\n     AI Generated Itinerary    ")
                print(self.planner.suggest_itinerary(trip))
            elif choice == "2":
                print("\n    AI Budget Tips    ")
                print(self.planner.generate_budget_tips(trip))
            else:
                print("Invalid choice.")
        except (ValueError, IndexError):
            print("Invalid selection.")


if __name__ == "__main__":
    app = TravelAssistant()
    app.run()
