import customtkinter as ctk
from tkinter import messagebox
import openai
import json
import random
import requests

# Amadeus API details
AMADEUS_API_KEY = "TPpQ6AIxCAKA03eFGe5Jx68yGzu817Z6"
AMADEUS_API_URL = "https://test.api.amadeus.com/v1/shopping/flight-offers"

# Initialize OpenAI API key
openai.api_key = "a329f819-51f4-4953-9ac3-9d36093a7021"

# Initialize the customtkinter theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class FlightBookingChatbot(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Flight Booking Chatbot")
        self.geometry("600x600")

        # Chatbot interface
        self.chat_frame = ctk.CTkFrame(self)
        self.chat_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Chat display
        self.chatbox = ctk.CTkTextbox(self.chat_frame, height=300, width=550)
        self.chatbox.pack(padx=10, pady=10)
        self.chatbox.insert("end", "Welcome to the Flight Booking Chatbot!\n\n")
        self.chatbox.configure(state="disabled")  # Read-only chatbox

        # User input
        self.user_input = ctk.CTkEntry(self.chat_frame, placeholder_text="Type your response here...")
        self.user_input.pack(padx=10, pady=10, fill="x")
        self.user_input.bind("<Return>", self.handle_user_response)

        # Flight booking data
        self.user_data = {
            "name": None,
            "contact": None,
            "boarding_city": None,
            "destination_city": None,
        }

        self.current_step = "name"  # Track which question is being asked
        self.final_confirmed = False

        self.add_to_chat("Bot: What is your name?\n\n")

    def handle_user_response(self, event=None):
        # Get user's input
        user_message = self.user_input.get().strip()
        if not user_message:
            return

        # Display user message in chatbox
        self.add_to_chat(f"You: {user_message}\n\n")

        # Process the input based on the current step
        if self.current_step == "name":
            self.user_data["name"] = user_message
            self.add_to_chat(f"Bot: Nice to meet you, {user_message}! What's your contact number?\n\n")
            self.current_step = "contact"

        elif self.current_step == "contact":
            if user_message.isdigit() and len(user_message) == 10:  # Basic validation
                self.user_data["contact"] = user_message
                self.add_to_chat("Bot: Got it! What's your boarding city?\n\n")
                self.current_step = "boarding_city"
            else:
                self.add_to_chat("Bot: Please enter a valid 10-digit contact number.\n\n")

        elif self.current_step == "boarding_city":
            self.user_data["boarding_city"] = user_message
            self.add_to_chat("Bot: And where are you flying to (destination city)?\n\n")
            self.current_step = "destination_city"

        elif self.current_step == "destination_city":
            self.user_data["destination_city"] = user_message
            self.show_summary()

        elif self.current_step == "confirm_booking":
            if user_message.lower() == "yes":
                self.finalize_booking()
            elif user_message.lower() == "no":
                self.add_to_chat("Bot: Flight booking cancelled. Goodbye!\n\n")
                self.restart_chat()
            else:
                self.add_to_chat("Bot: Please type 'yes' to confirm or 'no' to cancel.\n\n")

        elif self.current_step == "update_details":
            if user_message in self.user_data:
                self.current_step = user_message
                self.add_to_chat(f"Bot: Please provide the updated value for {user_message}.\n\n")
            else:
                self.add_to_chat("Bot: Invalid field. Please type a valid field to update (name, contact, boarding_city, destination_city).\n\n")

        elif self.current_step in self.user_data:
            self.user_data[self.current_step] = user_message
            self.add_to_chat(f"Bot: {self.current_step} updated successfully!\n\n")
            self.show_summary()
    # Bot message
        bot_msg= self.chatbot_response(user_message)#we used prompt_len in chatbot response so we have to mention here along with bot_msg
        
        self.chatbox.insert('end', f"Bot: {bot_msg}")

        # Clear user input
        self.user_input.delete(0, ctk.END)

    def show_summary(self):
        # Display booking details
        self.add_to_chat("Bot: Here's your flight booking summary:\n")
        self.add_to_chat(f"  - Name: {self.user_data['name']}\n")
        self.add_to_chat(f"  - Contact: {self.user_data['contact']}\n")
        self.add_to_chat(f"  - Boarding City: {self.user_data['boarding_city']}\n")
        self.add_to_chat(f"  - Destination City: {self.user_data['destination_city']}\n")
        self.add_to_chat("Bot: Do you want to confirm the booking? Type 'yes' to confirm, 'no' to cancel, or 'update' to modify details.\n\n")
        self.current_step = "confirm_booking"

    def finalize_booking(self):
        # Save booking details to JSON
        save_message = save_booking_to_json(self.user_data)
        self.add_to_chat(f"Bot: {save_message}\n\n")
        self.generate_flight_id()

    def generate_flight_id(self):
        flight_id = f"FL-{random.randint(1000, 9999)}"
        self.add_to_chat(f"Bot: Your flight has been successfully booked! Your flight ID is {flight_id}.\n\n")
        self.fetch_flight_options()

    def fetch_flight_options(self):
        # Fetch flight options from Amadeus API
        try:
            response = requests.get(
                AMADEUS_API_URL,
                headers={"Authorization": f"Bearer {AMADEUS_API_KEY}"},
                params={
                    "originLocationCode": self.user_data["boarding_city"],
                    "destinationLocationCode": self.user_data["destination_city"],
                    "departureDate": "2024-12-30",
                    "adults": 1,
                },
            )
            if response.status_code == 200:
                flights = response.json().get("data", [])
                if flights:
                    self.add_to_chat("Bot: Here are the available flights:\n")
                    for idx, flight in enumerate(flights[:5], start=1):
                        self.add_to_chat(f"  {idx}. {flight['itineraries'][0]['segments'][0]['carrierCode']} - ${flight['price']['total']}\n")
                    self.add_to_chat("Bot: Please type the number of the flight you want to book.\n\n")
                else:
                    self.add_to_chat("Bot: No flights available for your route.\n\n")
            else:
                self.add_to_chat(f"Bot: Error fetching flight options: {response.status_code}\n\n")
        except Exception as e:
            self.add_to_chat(f"Bot: Failed to fetch flight options: {e}\n\n")

    def restart_chat(self):
        # Reset the chatbot
        self.user_data = {key: None for key in self.user_data}
        self.current_step = "name"
        self.add_to_chat("Bot: Let's start again! What's your name?\n\n")

    def add_to_chat(self, message):
        # Add messages to the chatbox
        self.chatbox.configure(state="normal")
        self.chatbox.insert("end", f"{message}")
        self.chatbox.configure(state="disabled")
        self.chatbox.see("end")


def save_booking_to_json(booking_data, filename="flight_bookings.json"):
    """Save the booking data to a JSON file."""
    try:
        # Load existing data if file exists
        try:
            with open(filename, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = []

        # Append new booking
        data.append(booking_data)

        # Save updated data
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
        return "Booking saved successfully!"
    except Exception as e:
        return f"Error saving booking: {e}"

    def chatbot_response(self, message):
        """Query the LLM API for a response"""
        try:
            prompt = f"You are a helpful assistant and here are my previous chat history {self.user_query}"
            prompt_token_count = self.count_tokens_openai(prompt)
            response = client.chat.completions.create(
                model='Meta-Llama-3.1-8B-Instruct',
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.1,
                top_p=0.1
            )
            bot_res = response.choices[0].message.content


if __name__ == "__main__":
    app = FlightBookingChatbot()
    app.mainloop()
