def test_devices():
    lcd_ok = False
    rfid_ok = False

    try:
        from LCD1602 import LCD1602
        LCD1602(16, 2)
        lcd_ok = True
        print("LCD1602: PASSED")
    except Exception as e:
        print("LCD1602: FAILED")
        print(f"LCD1602 Error: {e}")

    try:
        from mfrc522 import WS1850S
        WS1850S()
        rfid_ok = True
        print("MFRC522: PASSED")
    except Exception as e:
        print("MFRC522: FAILED")
        print(f"MFRC522 Error: {e}")

    try:
        buzzer.on()
        time.sleep(0.1)
        buzzer.off()
        led.on()
        time.sleep(1)
        led.off()
        print("Tested light and buzzer")
    except:
        print("Light or buzzer failed - please check wiring")

    # Distance sensor
    # 

    return lcd_ok and rfid_ok

def process_card_with_lcd(card_uid, card_dict, lcd, buzzer_pin=20, led_pin=16, audit_file='card_audit.csv'):
    """
    Process a card read: lookup user, display on LCD, and log to audit file.
    
    Args:
        card_uid (str): Card UID as hex string
        card_dict (dict): Dictionary mapping card UIDs to usernames
        lcd (LCD1602): LCD1602 object instance
        buzzer_pin (int): GPIO pin for buzzer
        led_pin (int): GPIO pin for LED
        audit_file (str): Audit log filename
    
    Returns:
        str: Username if found, None otherwise
    """
    from gpiozero import Buzzer, LED
    import time
    
    try:
        buzzer = Buzzer(buzzer_pin)
        led = LED(led_pin)
        
        # Look up username
        username = card_dict.get(card_uid)
        
        if username:
            print(f"Card UID: {card_uid} -> User: {username}")
            
            # Display on LCD
            display_user_on_lcd(username, lcd)
            
            # Log to audit file
            log_card_audit(f"{card_uid},{username}", audit_file)
            
            # Beep and flash LED
            buzzer.on()
            time.sleep(0.1)
            buzzer.off()
            led.on()
            time.sleep(1)
            led.off()
            
            return username
        else:
            print(f"Card UID: {card_uid} -> Unknown card")
            
            # Display error on LCD
            lcd.clear()
            lcd.setCursor(0, 0)
            lcd.printout("Unknown Card")
            lcd.setCursor(0, 1)
            lcd.printout(card_uid[:16])
            
            # Log unknown card
            log_card_audit(f"{card_uid},UNKNOWN", audit_file)
            
            return None
    
    except Exception as e:
        print(f"Error processing card: {e}")
        return None

def log_card_audit(card_uid, filename='card_audit.csv'):
    """
    Write an audit log entry for a card read with timestamp.
    
    Args:
        card_uid (str): Card UID as hex string (e.g., "FF AA BB CC")
        filename (str): CSV file to log to (default 'card_audit.csv')
    
    Returns:
        bool: True if log was written successfully, False otherwise
    """
    from datetime import datetime
    import os
    
    try:
        # Get current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if file exists to determine if we need to write headers
        file_exists = os.path.isfile(filename)
        
        # Write to CSV file
        with open(filename, 'a') as f:
            # Write header if file is new
            if not file_exists:
                f.write("Timestamp,Card UID\n")
            
            # Write audit entry
            f.write(f"{timestamp},{card_uid}\n")
        
        print(f"Audit logged: {timestamp} - {card_uid}")
        return True
    
    except Exception as e:
        print(f"Error writing audit log: {e}")
        return False

def detect_person():
    pass

def get_username_from_card(card_uid, card_dict):
    """
    Look up username from card UID using a dictionary.
    
    Args:
        card_uid (str): Card UID as hex string (e.g., "FF AA BB CC")
        card_dict (dict): Dictionary mapping card UIDs to usernames
    
    Returns:
        str: Username if card found, None if not found
    """
    username = card_dict.get(card_uid)
    
    if username:
        print(f"Card UID: {card_uid} -> User: {username}")
        return username
    else:
        print(f"Card UID: {card_uid} -> Unknown card")
        return None

def display_user_on_lcd(username, lcd):
    """
    Display username and current date/time on LCD1602 display.
    
    Args:
        username (str): Username to display
        lcd (LCD1602): LCD1602 object instance
    
    Returns:
        bool: True if successful, False otherwise
    """
    from datetime import datetime
    import time
    
    try:
        # Get current date and time
        now = datetime.now()
        date_str = now.strftime("%m/%d %H:%M")  # Format: MM/DD HH:MM
        
        # Truncate username to 16 characters (LCD width)
        username_display = username[:16].ljust(16)
        date_display = date_str[:16].ljust(16)
        
        # Clear display
        lcd.clear()
        
        # Display username on row 0
        lcd.setCursor(0, 0)
        lcd.printout(username_display)
        
        # Display date/time on row 1
        lcd.setCursor(0, 1)
        lcd.printout(date_display)
        
        print(f"LCD Display - User: {username} | Time: {date_str}")
        return True
    
    except Exception as e:
        print(f"Error displaying on LCD: {e}")
        return False


def add_card(card_uid, username, card_dict):
    """
    Add a new card to the dictionary.
    
    Args:
        card_uid (str): Card UID as hex string (e.g., "FF AA BB CC")
        username (str): Username to associate with card
        card_dict (dict): Card dictionary to update
    
    Returns:
        dict: Updated dictionary
    """
    if card_uid in card_dict:
        print(f"Card {card_uid} already exists: {card_dict[card_uid]}")
        return card_dict
    
    card_dict[card_uid] = username
    print(f"✓ Added: {card_uid} -> {username}")
    return card_dict


def update_card(card_uid, username, card_dict):
    """
    Update an existing card in the dictionary.
    
    Args:
        card_uid (str): Card UID as hex string
        username (str): New username
        card_dict (dict): Card dictionary to update
    
    Returns:
        dict: Updated dictionary
    """
    if card_uid not in card_dict:
        print(f"Card {card_uid} not found")
        return card_dict
    
    old_username = card_dict[card_uid]
    card_dict[card_uid] = username
    print(f"✓ Updated: {card_uid} from {old_username} to {username}")
    return card_dict


def delete_card(card_uid, card_dict):
    """
    Delete a card from the dictionary.
    
    Args:
        card_uid (str): Card UID as hex string
        card_dict (dict): Card dictionary to update
    
    Returns:
        dict: Updated dictionary
    """
    if card_uid not in card_dict:
        print(f"Card {card_uid} not found")
        return card_dict
    
    username = card_dict[card_uid]
    del card_dict[card_uid]
    print(f"✓ Deleted: {card_uid} ({username})")
    return card_dict


def view_cards(card_dict):
    """
    Display all cards in the dictionary.
    
    Args:
        card_dict (dict): Card dictionary
    """
    if not card_dict:
        print("No cards in dictionary")
        return
    
    print("\n" + "="*40)
    print("Registered Cards")
    print("="*40)
    
    for card_uid, username in card_dict.items():
        print(f"{card_uid:<15} -> {username}")
    
    print("="*40 + "\n")

def audit_log_to_html(csv_file='card_audit.csv', html_file='card_audit.html'):
    """
    Convert audit log CSV to HTML format.
    
    Args:
        csv_file (str): Input CSV file (default 'card_audit.csv')
        html_file (str): Output HTML file (default 'card_audit.html')
    
    Returns:
        bool: True if successful, False otherwise
    """
    import os
    from datetime import datetime
    
    try:
        # Check if CSV file exists
        if not os.path.isfile(csv_file):
            print(f"Error: {csv_file} not found")
            return False
        
        # Read CSV file
        with open(csv_file, 'r') as f:
            lines = f.readlines()
        
        if len(lines) < 1:
            print("Error: CSV file is empty")
            return False
        
        # Create HTML content
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Card Audit Log</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        th {
            background-color: #4CAF50;
            color: white;
            padding: 12px;
            text-align: left;
            border: 1px solid #ddd;
        }
        td {
            padding: 12px;
            border: 1px solid #ddd;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #f0f0f0;
        }
        .footer {
            margin-top: 20px;
            color: #666;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <h1>Card Audit Log</h1>
"""
        
        # Add table
        html_content += "    <table>\n"
        html_content += "        <tr>\n"
        
        # Add header row
        header = lines[0].strip().split(',')
        for col in header:
            html_content += f"            <th>{col}</th>\n"
        
        html_content += "        </tr>\n"
        
        # Add data rows
        for line in lines[1:]:
            if line.strip():
                html_content += "        <tr>\n"
                cols = line.strip().split(',')
                for col in cols:
                    html_content += f"            <td>{col}</td>\n"
                html_content += "        </tr>\n"
        
        html_content += "    </table>\n"
        
        # Add footer
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html_content += f"""
    <div class="footer">
        <p>Generated: {now}</p>
        <p>Total records: {len(lines) - 1}</p>
    </div>
</body>
</html>
"""
        
        # Write HTML file
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        print(f"✓ HTML file created: {html_file}")
        return True
    
    except Exception as e:
        print(f"Error converting to HTML: {e}")
        return False


if __name__ == "__main__":
    result = test_devices()
    print("All devices working:", result)

    """
    #Usage
from LCD1602 import LCD1602

# Initialize LCD
lcd = LCD1602(16, 2)

# Your card dictionary
cards = {
    'FF AA BB CC': 'john_smith',
    'DD EE FF 11': 'jane_doe',
    '12 34 56 78': 'bob_jones'
}

# Process card and display on LCD
card = read_rfid_with_audit(timeout=30)
if card:
    process_card_with_lcd(card, cards, lcd)


    # Define your cards dictionary
cards = {
    'FF AA BB CC': 'john_smith',
    'DD EE FF 11': 'jane_doe'
}

# Add a new card
cards = add_card('12 34 56 78', 'bob_jones', cards)

# Update a card
cards = update_card('FF AA BB CC', 'john_smith_updated', cards)

# Delete a card
cards = delete_card('12 34 56 78', cards)

# View all cards
view_cards(cards)

# Use with RFID
card = read_rfid_with_audit(timeout=30)
if card:
    process_card_with_lcd(card, cards, lcd)

def generate_audit_report():
   
    Generate an HTML audit report from the CSV log.
    
    csv_file = 'card_audit.csv'
    html_file = 'card_audit.html'
    
    if audit_log_to_html(csv_file, html_file):
        print(f"Report saved to {html_file}")
        print("Open in browser to view")
    else:
        print("Failed to generate report")

# Run it
generate_audit_report()
    """
