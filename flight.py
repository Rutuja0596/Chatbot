import customtkinter as ctk
import random
from datetime import datetime
import requests


# Initialize the customtkinter theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class FlightBookingChatbot(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Flight Booking Chatbot with LLM")
        self.geometry("600x600")
        self.user_query = []  # Create list to store user inputs
        self.flight_id = None  # Store the flight ID after booking

        # Chatbot interface
        self.chat_frame = ctk.CTkFrame(self)
        self.chat_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Chat display
        self.chatbox = ctk.CTkTextbox(self.chat_frame, height=300, width=550)
        self.chatbox.pack(padx=10, pady=10)
        self.chatbox.insert("end", "Bot: Welcome!\n\n")
        self.chatbox.configure(state="disabled")  # Read-only chatbox

        # User input
        self.user_input = ctk.CTkEntry(self.chat_frame, placeholder_text="Type your response here...")
        self.user_input.pack(padx=10, pady=10, fill="x")
        self.user_input.bind("<Return>", self.handle_user_response)

        # Flight booking data
        self.user_data = {
            "name": None,
            "boarding_city": None,
            "destination_city": None,
            "travel_date": None,
        }

        self.current_step = "init"  # Initialize the conversation state

    def handle_user_response(self, event=None):
        user_message = self.user_input.get().strip()
        if not user_message:
            return

        self.add_to_chat(f"You: {user_message}\n\n")

        # Determine how to process the input
        if self.is_general_query(user_message):
            self.answer_general_query(user_message)
        elif self.current_step.startswith("edit_"):
            detail_key = self.current_step.replace("edit_", "")
            new_value = user_message.strip()
            if new_value.lower() == self.user_data.get(detail_key, "").lower():
                self.add_to_chat(f"Bot: The new {detail_key.replace('_', ' ')} matches the existing one. Please provide a different value.\n\n")
            else:
                self.user_data[detail_key] = new_value
                self.add_to_chat(f"Bot: Your {detail_key.replace('_', ' ')} has been updated to {new_value}.\n\n")
                self.show_summary()
        elif "cancel flight" in user_message.lower():
            self.cancel_booking()
        else:
            self.process_booking_workflow(user_message)

        self.user_input.delete(0, ctk.END)

    def is_general_query(self, message):
        """Detect if the user input is a general question or unrelated to booking."""
        keywords = ["boarding city", "destination city", "travel date", "name", "flight id"]
        return any(keyword in message.lower() for keyword in keywords)

    def forward_to_meta_llama(self, message):
        """Send general queries to Meta Llama and display the response."""
        response = self.meta_llama_query(message)
        self.add_to_chat(f"Meta Llama: {response}\n\n")

    def answer_general_query(self, question):
        """Provide answers about stored booking data or handle general queries."""
        if "boarding city" in question.lower():
            self.add_to_chat(f"Bot: Your boarding city is {self.user_data['boarding_city']}.\n\n")
        elif "destination city" in question.lower():
            self.add_to_chat(f"Bot: Your destination city is {self.user_data['destination_city']}.\n\n")
        elif "travel date" in question.lower():
            self.add_to_chat(f"Bot: Your travel date is {self.user_data['travel_date']}.\n\n")
        elif "name" in question.lower():
            self.add_to_chat(f"Bot: Your name is {self.user_data['name']}.\n\n")
        elif "flight id" in question.lower():
            if self.flight_id:
                self.add_to_chat(f"Bot: Your flight ID is {self.flight_id}.\n\n")
            else:
                self.add_to_chat("Bot: You have not booked a flight yet.\n\n")
        else:
            self.add_to_chat("Bot: I couldn't understand your query. Please be more specific.\n\n")

    def process_booking_workflow(self, user_message):
        """Manage the flight booking steps."""
        if self.current_step == "init" and "book a flight" in user_message.lower():
            self.add_to_chat("Bot: Sure! What is your name?\n\n")
            self.current_step = "name"
        elif self.current_step == "name":
            self.user_data["name"] = user_message
            self.add_to_chat(f"Bot: Nice to meet you, {user_message}! What is your boarding city?\n\n")
            self.current_step = "boarding_city"
        elif self.current_step == "boarding_city":
            self.user_data["boarding_city"] = user_message
            self.add_to_chat("Bot: What is your destination city?\n\n")
            self.current_step = "destination_city"
        elif self.current_step == "destination_city":
            self.user_data["destination_city"] = user_message
            self.add_to_chat("Bot: What is your travel date? (YYYY-MM-DD)\n\n")
            self.current_step = "travel_date"
        elif self.current_step == "travel_date":
            try:
                travel_date = datetime.strptime(user_message, "%Y-%m-%d").date()
                if travel_date >= datetime.now().date():
                    self.user_data["travel_date"] = str(travel_date)
                    self.show_summary()
                else:
                    self.add_to_chat("Bot: Travel date cannot be in the past. Please enter a valid date.\n\n")
            except ValueError:
                self.add_to_chat("Bot: Please enter the date in the correct format (YYYY-MM-DD).\n\n")
        elif self.current_step == "confirm_booking" and user_message.lower() in ["yes", "no"]:
            if user_message.lower() == "yes":
                self.finalize_booking()
            elif user_message.lower() == "no":
                self.add_to_chat("Bot: Would you like to change any details? Type 'yes' to edit or 'no' to cancel.\n\n")
                self.current_step = "edit_prompt"
        elif self.current_step == "edit_prompt":
            if user_message.lower() == "yes":
                self.add_to_chat("Bot: Which detail would you like to change? (name/boarding city/destination city/travel date)\n\n")
                self.current_step = "edit_details"
            else:
                self.add_to_chat("Bot: Flight booking cancelled. Goodbye!\n\n")
                self.restart_chat()
        else:
            self.add_to_chat("Bot: I'm sorry, I didn't understand that. Please try again.\n\n")

    def show_summary(self):
        """Display booking details and ask for confirmation."""
        self.add_to_chat("Bot: Here's your flight booking summary:\n")
        self.add_to_chat(f"  - Name: {self.user_data['name']}\n")
        self.add_to_chat(f"  - Boarding City: {self.user_data['boarding_city']}\n")
        self.add_to_chat(f"  - Destination City: {self.user_data['destination_city']}\n")
        self.add_to_chat(f"  - Travel Date: {self.user_data['travel_date']}\n")
        self.add_to_chat("Bot: Do you want to confirm the booking? Type 'yes' to confirm, or 'no' to edit or cancel.\n\n")
        self.current_step = "confirm_booking"

    def finalize_booking(self):
        """Generate a flight ID and confirm the booking."""
        self.flight_id = f"FL-{random.randint(1000, 9999)}"
        self.add_to_chat(f"Bot: Your flight has been successfully booked! Your flight ID is {self.flight_id}.\n\n")
        self.restart_chat()

    def cancel_booking(self):
        """Cancel the flight booking and reset the state."""
        self.user_data = {key: None for key in self.user_data}
        self.flight_id = None
        self.add_to_chat("Bot: Your flight booking has been canceled. All your data has been cleared.\n\n")
        self.restart_chat()

    def restart_chat(self):
        """Reset the chatbot but retain booking data for follow-up queries."""
        self.current_step = "init"
        self.add_to_chat("Bot: Let's start again! How can I help you?\n\n")
    
    def generate_response(prompt):
        """Generate a response using the Sambanova API."""
        return None
    
    def extract_flight_details(user_message):
        """Extract flight details from the user message."""
        prompt = f"""activity(hi, book a flight,hello, book a flight, hi book a flight, hello book a flight, book a flight, Book a flight,
        Book a Flight,update flight, edit flight details, cancel flight,fetch flight), Boarding city(look for phrases like 'from <city>'),
        Destination city(look for phrases like 'to <city>'), Travel date(look for phrases like 'on <YYYY-MM-DD>'), Name(look for phrases like 'my name is <name>','I am <name>'),
        Contact number(look for phrases like 'my contact number is <number>','contact number <number>','number is <number>'), Flight ID(look for phrases like 'flight ID is <ID>','ID is <ID>','flight id is <ID>'),
        Update request(look for phrases like 'update <field> to <value>','change <field> to <value>'), Cancel request(look for phrases like 'cancel flight','cancel booking')

    User input:"{user_message}"

    {
        {
            "activity": "<activity>",
            "name" : "<name>",
            "boarding_city": "<city>",
            "destination_city": "<city>",
            "travel_date": "<YYYY-MM-DD>",
            "contact_number": "<number>",
            "flight_id": "<ID>",
            "update_request": {
                "field": "<field>",
                "value": "<value>"
            },
        }
    }"""
        response = generate_response(prompt)
        print("LLM Response",response)
        
    def meta_llama_query(self, query):
        headers: {
        "Authorization" : f"Bearer {SAMBANOVA_API_KEY}",
        "Content-Type" : "application/json"
    }
        payload = {
            "model":'Meta-Llama-3.1-8B-Instruct',
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.1,
                top_p=0.1"
        }

    def add_to_chat(self, message):
        """Append a message to the chat display."""
        self.chatbox.configure(state="normal")
        self.chatbox.insert("end", message)
        self.chatbox.see("end")
        self.chatbox.configure(state="disabled")


if __name__ == "__main__":
    app = FlightBookingChatbot()
    app.mainloop()
