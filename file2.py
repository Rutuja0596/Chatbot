import customtkinter as ct
import tiktoken
import time
import openai

# Set OpenAI API configuration
client = openai.OpenAI(
    api_key = "a329f819-51f4-4953-9ac3-9d36093a7021",
    base_url = "https://api.sambanova.ai/v1"
    )

ct.set_appearance_mode("dark")

class App(ct.CTk):
    def __init__(self):
        super().__init__()

        self.title('AI Chatbot')
        self.geometry("600x650")  # Frame size
        self.user_query = [] #Create list

        # Grid manager for layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Creating Frames
        self.main_frame = ct.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20)

        self.frame1 = ct.CTkFrame(self.main_frame)
        self.frame1.grid(row=0, column=0, padx=20, pady=20)

        self.frame2 = ct.CTkFrame(self.main_frame)
        self.frame2.grid(row=0, column=0, padx=20, pady=20)

        # Creating button to switch frames
        button = ct.CTkButton(self.frame1, text="Let's Chat", command=self.show_frame2)
        button.grid(row=0, column=0, padx=20, pady=20)
        button.configure(width=100, height=50)

        # Show frame1 initially
        self.show_frame1()

        # Chatbot Interface inside frame2
        self.chatbox = ct.CTkTextbox(self.frame2, height=300, width=400)
        self.chatbox.grid(row=0, column=0, padx=10, pady=10)
        self.chatbox.insert('3.3','Hey, How can I help you ?\n\n\n')
        self.chatbox.configure(state='disabled')  # Make the chatbox read-only initially

        self.user_input = ct.CTkEntry(self.frame2, width=350)
        self.user_input.grid(row=1, column=0, padx=45, pady=45)

        self.submit_button = ct.CTkButton(self.frame2, text="Send", command=self.send_message)
        self.submit_button.grid(row=2, column=0, padx=10, pady=10)

        # Bind the Enter key to send message
        self.user_input.bind("<Return>", self.enter_key_send)

    def show_frame1(self):
        """Show frame1 and hide frame2"""
        self.frame2.grid_forget()
        self.frame1.grid(row=0, column=0, padx=20, pady=20)

    def show_frame2(self):
        """Show frame2 and hide frame1"""
        self.frame1.grid_forget()
        self.frame2.grid(row=0, column=0, padx=50, pady=50)

    def send_message(self):
        """Handle sending a message"""
        user_message = self.user_input.get()
        if user_message != "":
            start_time = time.time()
            self.chatbox.configure(state='normal')  # Allow editing the chatbox
            self.chatbox.insert('end', "You: " + user_message + '\n')  # Add user's message
            self.user_input.delete(0, 'end')  # Clear the input field

            token_count1 = self.count_tokens_openai(user_message)

            # Bot message
            bot_msg, prompt_token_count = self.chatbot_response(user_message)#we used prompt_len in chatbot response so we have to mention here along with bot_msg
            bot_token_count = self.count_tokens_openai(bot_msg) if isinstance(bot_msg,str) else 0#Ensures that it is a string and not non-string.
            self.chatbox.insert('end', f"Bot: {bot_msg}")

            self.chatbox.insert('end',f'\nPrompt Token Length: {prompt_token_count}')
            #self.chatbox.insert('end', f"\n\nUser Query: " + user_message)
            self.chatbox.insert('end', f"\nUser Token Count: {token_count1}")  # Display token count in the chatbox

            #self.chatbox.insert('end', f'\n\nBot Response: {bot_msg}')
            self.chatbox.insert('end', f"\nResponse Token count: {bot_token_count}")  # Bot's response

            total_token = token_count1 + bot_token_count

            end_time = time.time()
            elapsed_time = end_time - start_time

            #self.chatbox.insert('end', f'\n\n***  Total Token Count ***\n')
            self.chatbox.insert('end', f'\nTotal Token Count : {total_token}')
            self.chatbox.insert('end', f"\nTime Taken : {elapsed_time:.2f} seconds\n\n")

            self.user_query.append(user_message)
            if len(self.user_query) > 4:
                self.user_query.pop(0)#Removes the oldest

            #self.chatbox.insert('end','\nStored Chats : ')
            print("Last 4 Stored Chats: ")
            for i,chat in enumerate(self.user_query):
                print(f'{i+1}:{chat}')

            #self.chatbox.insert('end',f'\nPrompt Token Length: {prompt_token_count}\n')
            
            self.chatbox.configure(state='disabled')  # Make chatbox read-only again
            self.chatbox.yview('end')  # Scroll to the bottom

    def count_tokens_openai(self, message):
        encoder = tiktoken.get_encoding("cl100k_base")  # Using the encoding used by GPT models
        tokens = encoder.encode(message)  # Tokenize the query
        return len(tokens)

    def enter_key_send(self, event=None):
        self.send_message()

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
            #print(response)


            total_latency = response.usage.total_latency
            print(f"Total Latency: {total_latency} seconds")
            return total_latency,prompt_token_count,rol
            
        except Exception as e:
            return f"Error: {str(e)}"

if __name__ == "__main__":
    app = App()
    app.mainloop()

