import customtkinter as ctk
from tkinter import messagebox
import openai

# Set OpenAI API configuration
client = openai.OpenAI(
    api_key = "a329f819-51f4-4953-9ac3-9d36093a7021",
    base_url = "https://api.sambanova.ai/v1"
    )


# Initialize the customtkinter theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class FlightBookingApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Flight Booking System")
        self.geometry("600x400")

        # Creating Frames
        self.main_frame = ct.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20)

        #create frame1
        self.frame1 = ct.CTkFrame(self.main_frame)
        self.frame1.grid(row=0, column=0, padx=20, pady=20)

        # Chatbot Interface inside frame2
        self.chatbox = ct.CTkTextbox(self.frame2, height=300, width=400)
        self.chatbox.grid(row=0, column=0, padx=10, pady=10)
        self.chatbox.insert('3.3','Hey, How can I help you ?\n\n\n')
        self.chatbox.configure(state='disabled')  # Make the chatbox read-only initially
        
        # Take user input
        self.user_input = ct.CTkEntry(self.frame2, width=350)
        self.user_input.grid(row=1, column=0, padx=45, pady=45)
        
        # Flight Selection
        self.flight_label = ctk.CTkLabel(self, text="Select Flight:")
        self.flight_label.pack(pady=5)

        self.flight_options = ["Flight A - $100", "Flight B - $200", "Flight C - $300"]
        self.selected_flight = ctk.StringVar(value=self.flight_options[0])

        self.flight_menu = ctk.CTkOptionMenu(self, variable=self.selected_flight, values=self.flight_options)
        self.flight_menu.pack(pady=5)

        # Passenger Name
        self.name_label = ctk.CTkLabel(self, text="Passenger Name:")
        self.name_label.pack(pady=5)

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Enter your name")
        self.name_entry.pack(pady=5)

        # Contact Number
        self.contact_label = ctk.CTkLabel(self, text="Contact Number:")
        self.contact_label.pack(pady=5)

        self.contact_entry = ctk.CTkEntry(self, placeholder_text="Enter your contact number")
        self.contact_entry.pack(pady=5)

        # Submit Button
        self.submit_button = ctk.CTkButton(self, text="Book Flight", command=self.book_flight)
        self.submit_button.pack(pady=20)

        # Reset Button
        self.reset_button = ctk.CTkButton(self, text="Reset", command=self.reset_form)
        self.reset_button.pack(pady=5)

        # Bind the Enter key to send message
        self.bind("<Return>", self.book_flight)

    def book_flight(self):
        name = self.name_entry.get()
        contact = self.contact_entry.get()
        flight = self.selected_flight.get()

        if not name or not contact:
            messagebox.showerror("Input Error", "Please fill in all fields.")
            return

        confirmation_message = f"Booking Confirmed!\n\nPassenger: {name}\nContact: {contact}\nFlight: {flight}"
        messagebox.showinfo("Booking Confirmation", confirmation_message)


    def reset_form(self):
        self.name_entry.delete(0, ctk.END)
        self.contact_entry.delete(0, ctk.END)
        self.selected_flight.set(self.flight_options[0])

    def chatbot_response(self, message):
        """Query the LLM API for a response"""
        try:
            prompt = f"Hello how can I help you."
            response = client.chat.completions.create(
                model='Meta-Llama-3.1-8B-Instruct',
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.1,
                top_p=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"


if __name__ == "__main__":
    app = FlightBookingApp()
    app.mainloop()

