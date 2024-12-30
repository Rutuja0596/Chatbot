import json
import openai

# Your LLM client initialization
openai.api_key = "a329f819-51f4-4953-9ac3-9d36093a7021"

class FlightBookingChatbot:
    def __init__(self):
        self.user_data = {
            "name": None,
            "contact": None,
            "boarding_city": None,
            "destination_city": None,
        }
        self.current_step = "name"

    def handle_user_response(self, user_message):
        # Update user data and query LLM for the next response
        if self.current_step == "name":
            self.user_data["name"] = user_message
            bot_message = self.query_llm(
                f"The user's name is {user_message}. Ask for the contact number."
            )
            self.current_step = "contact"

        elif self.current_step == "contact":
            if user_message.isdigit() and len(user_message) == 10:  # Basic validation
                self.user_data["contact"] = user_message
                bot_message = self.query_llm(
                    f"The user's contact number is {user_message}. Ask for the boarding city."
                )
                self.current_step = "boarding_city"
            else:
                bot_message = "Please enter a valid 10-digit contact number."

        elif self.current_step == "boarding_city":
            self.user_data["boarding_city"] = user_message
            bot_message = self.query_llm(
                f"The user's boarding city is {user_message}. Ask for the destination city."
            )
            self.current_step = "destination_city"

        elif self.current_step == "destination_city":
            self.user_data["destination_city"] = user_message
            bot_message = self.query_llm(
                f"The destination city is {user_message}. Generate a flight booking summary "
                f"with the following details: {json.dumps(self.user_data)}."
            )
            self.current_step = "confirm_booking"

        elif self.current_step == "confirm_booking":
            if user_message.lower() == "yes":
                bot_message = self.finalize_booking()
            elif user_message.lower() == "no":
                bot_message = self.query_llm("User canceled the booking. Respond accordingly.")
                self.restart_chat()
            else:
                bot_message = "Invalid input. Please type 'yes' or 'no'."

        return bot_message

    def query_llm(self, prompt):
        try:
            # Query the LLM for a response
            response = openai.ChatCompletion.create(
                model="Meta-Llama-3.1-8B-Instruct",
                messages=[
                    {"role": "system", "content": "You are a flight booking assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                top_p = 0.1
            )
            return response.choices[0].message["content"]
        except Exception as e:
            return f"Error while querying LLM: {e}"

    def finalize_booking(self):
        # Generate confirmation and save booking data
        booking_id = f"FB-{self.user_data['boarding_city'][:3]}-{self.user_data['destination_city'][:3]}-001"
        save_status = self.save_booking_to_json(self.user_data)
        return (
            f"Your flight has been successfully booked!\n"
            f"Booking ID: {booking_id}\n"
            f"{save_status}"
        )

    def save_booking_to_json(self, booking_data, filename="flight_bookings.json"):
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

    def restart_chat(self):
        # Reset user data and current step
        self.user_data = {key: None for key in self.user_data}
        self.current_step = "name"
