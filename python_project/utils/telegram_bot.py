import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler, CallbackContext

import sys
sys.path.append('/Users/a39328/Desktop/IOT_PRJ/Light-Tracking-for-Plants/Light-Tracking-for-Plants/python_project/data_proxy')
from configs import *
from plant_manager import PlantLightManager

# Define states for the conversation
ADDING_PLANT, MODIFY_PLANT, DELETING_PLANT = 1, 2, 3
ADDING_POSITION, MODIFY_POSITION, DELETING_POSITION = 4, 5, 6

# Helper functions to handle file reading/writing
def read_json_file(file_path):
    """Read and return the content of a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def write_json_file(file_path, data):
    """Write data to a JSON file."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

# ---------------------------- Start Command ----------------------------
async def start(update: Update, context: CallbackContext):
    """Display the main menu with plant and position management options."""
    keyboard = [
        [InlineKeyboardButton("Manage Plants", callback_data='manage_plants')],
        [InlineKeyboardButton("Manage Positions", callback_data='manage_positions')],
        [InlineKeyboardButton("Utility", callback_data='utility')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Welcome to the Plant and Position Management Bot!', reply_markup=reply_markup)

# ---------------------------- Plant UTILITY ----------------------------
async def utility(update: Update, context: CallbackContext):
    """Show plant management options."""
    keyboard = [
        [InlineKeyboardButton("Suggest position change", callback_data='suggest_change')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text('Choose an action for plants:', reply_markup=reply_markup)

async def suggest_change(update: Update, context: CallbackContext):
    """Suggest a position change for a plant based on light data."""
    plant_manager = PlantLightManager()
    #I ant to concatenate the string with the plant_manager.suggest_position() result
    suggestions = "".join(f"- {el}\n" for el in plant_manager.suggest_position())
    if suggestions:
        await update.callback_query.edit_message_text(suggestions)
    else:
        await update.callback_query.edit_message_text("No suggestions available at the moment.")
    await start(update, context)
    return ConversationHandler.END

# ---------------------------- Plant Management ----------------------------
async def manage_plants(update: Update, context: CallbackContext):
    """Show plant management options."""
    keyboard = [
        [InlineKeyboardButton("Add Plant", callback_data='add_plant')],
        [InlineKeyboardButton("Modify Plant", callback_data='modify_plant')],
        [InlineKeyboardButton("Delete Plant", callback_data='delete_plant')],
        [InlineKeyboardButton("Back", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text('Choose an action for plants:', reply_markup=reply_markup)

async def add_plant(update: Update, context: CallbackContext):
    print("add_plant")
    """Start adding a new plant."""
    await update.callback_query.edit_message_text('Enter plant details (name, code, optimal light, position, sensor):')
    print("returning ADDING_PLANT")
    return ADDING_PLANT

async def modify_plant(update: Update, context: CallbackContext):
    """Start modifying an existing plant."""
    template = "Available plants: \n" + str(read_json_file(CONFIG_PLANT_FILE)) + "\n"
    await update.callback_query.edit_message_text(template + 'Enter plant details to modify the plant with the same code (name, code, optimal light, position, sensor):')
    return MODIFY_PLANT

async def delete_plant(update: Update, context: CallbackContext):
    """Start deleting a plant."""
    template = "Available plants: \n" + str(read_json_file(CONFIG_PLANT_FILE)) + "\n"
    await update.callback_query.edit_message_text(template + 'Enter the ID of the plant to delete:')
    return DELETING_PLANT

# ---------------------------- Position Management ----------------------------
async def manage_positions(update: Update, context: CallbackContext):
    """Show position management options."""
    keyboard = [
        [InlineKeyboardButton("Add Position", callback_data='add_position')],
        [InlineKeyboardButton("Modify Position", callback_data='modify_position')],
        [InlineKeyboardButton("Delete Position", callback_data='delete_position')],
        [InlineKeyboardButton("Back", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text('Choose an action for positions:', reply_markup=reply_markup)

async def add_position(update: Update, context: CallbackContext):
    """Start adding a new position."""
    await update.callback_query.edit_message_text('Enter position details (name, ID, description, sensor):')
    return ADDING_POSITION

async def modify_position(update: Update, context: CallbackContext):
    """Start modifying an existing position."""
    template = "Available positions: \n" + str(read_json_file(CONFIG_POSITION_FILE)) + "\n"
    await update.callback_query.edit_message_text(template + 'Enter position details to modify position with same ID (name, ID, description, sensor):')
    return MODIFY_POSITION

async def delete_position(update: Update, context: CallbackContext):
    """Start deleting a position."""
    template = "Available positions: \n" + str(read_json_file(CONFIG_POSITION_FILE)) + "\n"
    await update.callback_query.edit_message_text(template + 'Enter the ID of the position to delete:')
    return DELETING_POSITION

# ---------------------------- Data Handling ----------------------------
async def handle_adding_plant(update: Update, context: CallbackContext):
    print("handle_adding_plant")
    """Handle adding a plant."""
    try:
        plant_details = update.message.text.split(',')
        if len(plant_details) != 5:
            await update.message.reply_text("Please provide the plant details in the correct format: name, code, optimal light, position, sensor.")
            return ADDING_PLANT  # Stay in the ADDING_PLANT state to capture valid input
        
        plant = {
            "name": plant_details[0].strip(),
            "code": int(plant_details[1].strip()),
            "optimal_light_amount": int(plant_details[2].strip()),
            "position": plant_details[3].strip(),
            "sensor": plant_details[4].strip()
        }

        plants = read_json_file(CONFIG_PLANT_FILE)
        plants.append(plant)
        write_json_file(CONFIG_PLANT_FILE, plants)
        await update.message.reply_text("Plant added successfully!")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
    await start(update, context)
    return ConversationHandler.END

async def handle_modifying_plant(update: Update, context: CallbackContext):
    """Handle modifying a plant."""
    try:
        plant_details = update.message.text.split(',')
        if len(plant_details) != 5:
            await update.message.reply_text("Please provide the plant details in the correct format: name, code, optimal light, position, sensor.")
            return MODIFY_PLANT  # Stay in the ADDING_PLANT state to capture valid input
        #delete plant with the same code
        plants = read_json_file(CONFIG_PLANT_FILE)
        plants = [p for p in plants if p['code'] != int(plant_details[1].strip())]
        #add the new plant
        plant = {
            "name": plant_details[0].strip(),
            "code": int(plant_details[1].strip()),
            "optimal_light_amount": int(plant_details[2].strip()),
            "position": plant_details[3].strip(),
            "sensor": plant_details[4].strip()
        }
        plants.append(plant)
        write_json_file(CONFIG_PLANT_FILE, plants)
        await update.message.reply_text("Plant modified successfully!")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
    await start(update, context)
    return ConversationHandler.END

async def handle_deleting_plant(update: Update, context: CallbackContext):
    """Handle deleting a plant."""
    try:
        plant_code = update.message.text.strip()
        plants = read_json_file(CONFIG_PLANT_FILE)
        plant_to_delete = next((p for p in plants if p['code'] == int(plant_code)), None)
        if plant_to_delete:
            plants = [p for p in plants if p['code'] != int(plant_code)]
            write_json_file(CONFIG_PLANT_FILE, plants)
            await update.message.reply_text(f"Plant with code {plant_code} deleted successfully!")
        else:
            await update.message.reply_text(f"No plant found with code {plant_code}. Please try again.")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
    await start(update, context)
    return ConversationHandler.END

# Handling adding, modifying, and deleting positions
async def handle_adding_position(update: Update, context: CallbackContext):
    """Handle adding a position."""
    try:
        position_details = update.message.text.split(',')
        if len(position_details) != 4:
            await update.message.reply_text("Please provide the position details in the correct format: name, ID, description, sensor.")
            return ADDING_POSITION  # Stay in the ADDING_POSITION state to capture valid input

        position = {
            "name": position_details[0].strip(),
            "ID": int(position_details[1].strip()),
            "description": position_details[2].strip(),
            "sensor": position_details[3].strip()
        }

        positions = read_json_file(CONFIG_POSITION_FILE)
        positions.append(position)
        write_json_file(CONFIG_POSITION_FILE, positions)        
        await update.message.reply_text("Position added successfully!")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
    await start(update, context)    
    return ConversationHandler.END

async def handle_modifying_position(update: Update, context: CallbackContext):
    """Handle modifying a plant."""
    try:
        position_details = update.message.text.split(',')
        if len(position_details) != 4:
            await update.message.reply_text("Please provide the position details in the correct format: name, ID, description, sensor.")
            return MODIFY_POSITION  # Stay in the ADDING_POSITION state to capture valid input
        #delete position with the same ID
        positions = read_json_file(CONFIG_POSITION_FILE)
        positions = [p for p in positions if p['ID'] != int(position_details[1].strip())]
        #add the new plant
        position = {
            "name": position_details[0].strip(),
            "ID": int(position_details[1].strip()),
            "description": position_details[2].strip(),
            "sensor": position_details[3].strip()
        }
        positions.append(position)
        write_json_file(CONFIG_PLANT_FILE, positions)
        await update.message.reply_text("Position modified successfully!")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
    await start(update, context)
    return ConversationHandler.END

async def handle_deleting_position(update: Update, context: CallbackContext):
    """Handle deleting a position."""
    try:
        position_id = int(update.message.text.strip())
        positions = read_json_file(CONFIG_POSITION_FILE)
        positions = [p for p in positions if p['ID'] != position_id]
        write_json_file(CONFIG_POSITION_FILE, positions)
        await update.message.reply_text("Position deleted successfully!")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
    await start(update, context)
    return ConversationHandler.END

# ---------------------------- Main Flow ----------------------------
def main():
    """Start the bot and set up the conversation handler."""
    application = Application.builder().token(TELEGRAM_BOT).build()
    # Set up the ConversationHandler with states and transitions
    conversation_handler = ConversationHandler(
        entry_points=[
            #CommandHandler('start', start),
            CallbackQueryHandler(start, pattern='^start$'),
            CallbackQueryHandler(add_plant, pattern='^add_plant$'),
            CallbackQueryHandler(modify_plant, pattern='^modify_plant$'),
            CallbackQueryHandler(delete_plant, pattern='^delete_plant$'),
            CallbackQueryHandler(add_position, pattern='^add_position$'),
            CallbackQueryHandler(modify_position, pattern='^modify_position$'),
            CallbackQueryHandler(delete_position, pattern='^delete_position$'),
            CallbackQueryHandler(suggest_change, pattern='^suggest_change$'),
            CallbackQueryHandler(start, pattern='^back$')
            ],
        states={
            ADDING_PLANT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_adding_plant),  # Capture user input for adding plant
            ],
            MODIFY_PLANT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_modifying_plant)],
            DELETING_PLANT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_deleting_plant)],
            ADDING_POSITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_adding_position)],
            MODIFY_POSITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_modifying_position)],
            DELETING_POSITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_deleting_position)],
        },
        fallbacks=[CommandHandler('start', start)],  # Reset to start if conversation ends or user cancels
    )
    application.add_handler(conversation_handler)
    # Add callback query handler to handle inline button presses    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(manage_plants, pattern='^manage_plants$'))
    application.add_handler(CallbackQueryHandler(manage_plants, pattern='^manage_plants$'))
    application.add_handler(CallbackQueryHandler(manage_positions, pattern='^manage_positions$'))
    application.add_handler(CallbackQueryHandler(add_plant, pattern='^add_plant$'))
    application.add_handler(CallbackQueryHandler(modify_plant, pattern='^modify_plant$'))
    application.add_handler(CallbackQueryHandler(delete_plant, pattern='^delete_plant$'))
    application.add_handler(CallbackQueryHandler(add_position, pattern='^add_position$'))
    application.add_handler(CallbackQueryHandler(modify_position, pattern='^modify_position$'))
    application.add_handler(CallbackQueryHandler(delete_position, pattern='^delete_position$'))
    application.add_handler(CallbackQueryHandler(utility, pattern='^utility$'))
    application.add_handler(CallbackQueryHandler(suggest_change, pattern='^suggest_change$'))
    
    application.add_handler(CallbackQueryHandler(start, pattern='^back$'))  # Handle 'Back' button press

    application.run_polling()

if __name__ == '__main__':
    main()