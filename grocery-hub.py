import streamlit as st
from datetime import datetime
import urllib.parse

# Page configuration
st.set_page_config(
    page_title="Grocery Hub",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
def load_css(theme="light"):
    if theme == "dark":
        st.markdown("""
        <style>
        .main {
            background-color: #1e1e1e;
        }
        .stApp {
            background-color: #1e1e1e;
        }
        h1, h2, h3 {
            color: #00d4ff;
        }
        .category-card {
            background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
            padding: 20px;
            border-radius: 15px;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0, 212, 255, 0.1);
            border: 1px solid #00d4ff;
        }
        .item-card {
            background-color: #2a2a2a;
            padding: 15px;
            border-radius: 10px;
            margin: 5px 0;
            border-left: 4px solid #00d4ff;
        }
        .cart-summary {
            background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
            padding: 20px;
            border-radius: 15px;
            border: 2px solid #00d4ff;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .main {
            background-color: #f5f7fa;
        }
        .stApp {
            background-color: #f5f7fa;
        }
        h1 {
            color: #2c3e50;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        h2, h3 {
            color: #3498db;
        }
        .category-card {
            background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
            padding: 20px;
            border-radius: 15px;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border: 1px solid #3498db;
        }
        .item-card {
            background-color: #ffffff;
            padding: 15px;
            border-radius: 10px;
            margin: 5px 0;
            border-left: 4px solid #3498db;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .cart-summary {
            background: linear-gradient(135deg, #ffffff 0%, #e8f4f8 100%);
            padding: 20px;
            border-radius: 15px;
            border: 2px solid #3498db;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)

# Initialize session state
if 'cart' not in st.session_state:
    st.session_state.cart = {}

if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Grocery items database
GROCERY_DATA = {
    "🥛 Dairy": {
        "Whole Milk (1L)": 2.99,
        "Skim Milk (1L)": 2.89,
        "Cheddar Cheese (200g)": 4.99,
        "Mozzarella Cheese (250g)": 5.49,
        "Greek Yogurt (500g)": 3.99,
        "Butter (250g)": 3.49,
        "Cream Cheese (227g)": 2.99,
        "Sour Cream (250ml)": 2.49
    },
    "🧹 Cleaning Agents": {
        "Dish Soap (500ml)": 3.99,
        "Laundry Detergent (2L)": 12.99,
        "All-Purpose Cleaner (750ml)": 4.49,
        "Glass Cleaner (500ml)": 3.79,
        "Floor Cleaner (1L)": 5.99,
        "Bleach (1L)": 2.99,
        "Paper Towels (6 rolls)": 8.99,
        "Sponges (5 pack)": 3.49
    },
    "🍎 Fruits": {
        "Apples (1kg)": 3.99,
        "Bananas (1kg)": 1.99,
        "Oranges (1kg)": 4.49,
        "Grapes (500g)": 5.99,
        "Strawberries (500g)": 4.99,
        "Watermelon (each)": 6.99,
        "Mangoes (each)": 2.49,
        "Pineapple (each)": 3.99,
        "Blueberries (250g)": 5.49,
        "Avocado (each)": 1.99
    },
    "🥕 Vegetables": {
        "Carrots (1kg)": 2.49,
        "Broccoli (500g)": 3.49,
        "Tomatoes (1kg)": 3.99,
        "Cucumbers (each)": 1.49,
        "Bell Peppers (each)": 1.99,
        "Onions (1kg)": 2.99,
        "Potatoes (2kg)": 4.99,
        "Lettuce (head)": 2.49,
        "Spinach (bunch)": 2.99,
        "Garlic (bulb)": 0.99
    },
    "🥩 Meats": {
        "Ground Beef (500g)": 8.99,
        "Beef Steak (500g)": 14.99,
        "Pork Chops (500g)": 9.99,
        "Lamb Chops (500g)": 16.99,
        "Bacon (250g)": 6.99,
        "Sausages (6 pack)": 7.49,
        "Ham Slices (200g)": 5.99
    },
    "🍗 Poultry": {
        "Chicken Breast (500g)": 8.49,
        "Chicken Thighs (500g)": 6.99,
        "Whole Chicken (1.5kg)": 12.99,
        "Chicken Wings (1kg)": 9.99,
        "Ground Chicken (500g)": 7.99,
        "Turkey Breast (500g)": 10.99,
        "Chicken Drumsticks (1kg)": 7.49
    },
    "📱 Electronics": {
        "USB Cable (1m)": 9.99,
        "Power Bank (10000mAh)": 29.99,
        "Phone Case": 14.99,
        "Earbuds": 24.99,
        "Screen Protector": 12.99,
        "Phone Charger": 19.99,
        "Memory Card (32GB)": 15.99,
        "HDMI Cable (2m)": 11.99
    },
    "🍿 Snacks": {
        "Potato Chips (200g)": 3.99,
        "Pretzels (250g)": 3.49,
        "Cookies (300g)": 4.99,
        "Chocolate Bar (100g)": 2.49,
        "Popcorn (250g)": 2.99,
        "Nuts Mix (200g)": 6.99,
        "Granola Bars (6 pack)": 5.49,
        "Crackers (250g)": 3.79,
        "Candy Mix (300g)": 4.49,
        "Trail Mix (250g)": 5.99
    }
}

# Functions
def add_to_cart(item, price, category):
    if item in st.session_state.cart:
        st.session_state.cart[item]['quantity'] += 1
    else:
        st.session_state.cart[item] = {
            'price': price,
            'quantity': 1,
            'category': category
        }

def remove_from_cart(item):
    if item in st.session_state.cart:
        del st.session_state.cart[item]

def update_quantity(item, quantity):
    if quantity > 0:
        st.session_state.cart[item]['quantity'] = quantity
    else:
        remove_from_cart(item)

def calculate_total():
    total = 0
    for item_data in st.session_state.cart.values():
        total += item_data['price'] * item_data['quantity']
    return total

def format_cart_for_whatsapp():
    """Format cart items for WhatsApp message"""
    if not st.session_state.cart:
        return "Your cart is empty!"
    
    message = "🛒 *GROCERY HUB - Shopping List*\n"
    message += "═" * 30 + "\n\n"
    
    # Group by category
    categories = {}
    for item, data in st.session_state.cart.items():
        category = data['category']
        if category not in categories:
            categories[category] = []
        categories[category].append((item, data))
    
    # Format by category
    for category, items in categories.items():
        message += f"*{category}*\n"
        for item, data in items:
            message += f"  ▪️ {item} (x{data['quantity']}) - ${data['price'] * data['quantity']:.2f}\n"
        message += "\n"
    
    # Add totals
    subtotal = calculate_total()
    tax = subtotal * 0.08
    total = subtotal + tax
    
    message += "─" * 30 + "\n"
    message += f"*Subtotal:* ${subtotal:.2f}\n"
    message += f"*Tax (8%):* ${tax:.2f}\n"
    message += f"*TOTAL:* ${total:.2f}\n"
    message += "─" * 30 + "\n\n"
    message += f"📅 {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n"
    message += "\nThank you for shopping with Grocery Hub! 🙏"
    
    return message

def send_to_whatsapp(phone_number):
    """Generate WhatsApp link with formatted message"""
    # Clean phone number (remove spaces, dashes, etc.)
    clean_number = ''.join(filter(str.isdigit, phone_number))
    
    # Format message
    message = format_cart_for_whatsapp()
    
    # URL encode the message
    encoded_message = urllib.parse.quote(message)
    
    # Create WhatsApp link
    whatsapp_url = f"https://wa.me/{clean_number}?text={encoded_message}"
    
    return whatsapp_url

def clear_cart():
    st.session_state.cart = {}

# Header
st.title("🛒 Grocery Hub")
st.markdown("### Your One-Stop Shopping Experience")

# Sidebar
with st.sidebar:
    st.markdown("## 🎨 Settings")
    
    # Theme toggle
    theme_option = st.radio(
        "Choose Theme:",
        ["☀️ Light Mode", "🌙 Dark Mode"],
        index=0 if st.session_state.theme == 'light' else 1
    )
    
    if "Dark" in theme_option:
        st.session_state.theme = 'dark'
    else:
        st.session_state.theme = 'light'
    
    st.markdown("---")
    
    # Shopping Cart Summary
    st.markdown("## 🛍️ Shopping Cart")
    
    if st.session_state.cart:
        st.markdown(f"**Items in cart:** {len(st.session_state.cart)}")
        st.markdown(f"**Total items:** {sum(item['quantity'] for item in st.session_state.cart.values())}")
        st.markdown(f"**Total Price:** ${calculate_total():.2f}")
        
        if st.button("🗑️ Clear Cart", use_container_width=True):
            clear_cart()
            st.rerun()
    else:
        st.info("Your cart is empty")
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    st.metric("Categories", len(GROCERY_DATA))
    st.metric("Products", sum(len(items) for items in GROCERY_DATA.values()))

# Apply CSS based on theme
load_css(st.session_state.theme)

# Main content
tab1, tab2 = st.tabs(["🏪 Shop", "🛒 Cart"])

with tab1:
    st.markdown("## Browse Our Products")
    
    # Search functionality
    search_term = st.text_input("🔍 Search for products...", placeholder="Type to search")
    
    # Category filter
    selected_categories = st.multiselect(
        "Filter by categories:",
        list(GROCERY_DATA.keys()),
        default=list(GROCERY_DATA.keys())
    )
    
    st.markdown("---")
    
    # Display categories and items
    for category, items in GROCERY_DATA.items():
        if category not in selected_categories:
            continue
            
        # Filter items by search term
        filtered_items = {k: v for k, v in items.items() 
                         if search_term.lower() in k.lower()} if search_term else items
        
        if not filtered_items:
            continue
        
        st.markdown(f'<div class="category-card">', unsafe_allow_html=True)
        st.markdown(f"### {category}")
        
        # Create columns for items
        cols = st.columns(3)
        
        for idx, (item, price) in enumerate(filtered_items.items()):
            with cols[idx % 3]:
                st.markdown(f'<div class="item-card">', unsafe_allow_html=True)
                st.markdown(f"**{item}**")
                st.markdown(f"💵 ${price:.2f}")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    if st.button(f"Add to Cart", key=f"add_{category}_{item}", use_container_width=True):
                        add_to_cart(item, price, category)
                        st.success(f"Added {item}!")
                        st.rerun()
                
                with col2:
                    if item in st.session_state.cart:
                        st.markdown(f"✓ x{st.session_state.cart[item]['quantity']}")
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("")

with tab2:
    st.markdown("## Your Shopping Cart")
    
    # Custom item addition
    st.markdown("### ➕ Add Custom Item")
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        custom_item_name = st.text_input(
            "Item Name",
            placeholder="Enter custom item name...",
            key="custom_item_name"
        )
    
    with col2:
        custom_item_price = st.number_input(
            "Price ($)",
            min_value=0.01,
            value=1.00,
            step=0.01,
            key="custom_item_price"
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Add Item", key="add_custom", use_container_width=True, type="primary"):
            if custom_item_name.strip():
                add_to_cart(custom_item_name, custom_item_price, "🛍️ Custom Items")
                st.success(f"Added {custom_item_name}!")
                st.rerun()
            else:
                st.error("Please enter an item name")
    
    st.markdown("---")
    
    if st.session_state.cart:
        st.markdown('<div class="cart-summary">', unsafe_allow_html=True)
        
        # Display cart items
        for item, data in st.session_state.cart.items():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{item}**")
                st.markdown(f"*{data['category']}*")
            
            with col2:
                st.markdown(f"${data['price']:.2f}")
            
            with col3:
                quantity = st.number_input(
                    "Qty",
                    min_value=0,
                    value=data['quantity'],
                    key=f"qty_{item}",
                    label_visibility="collapsed"
                )
                if quantity != data['quantity']:
                    update_quantity(item, quantity)
                    st.rerun()
            
            with col4:
                st.markdown(f"**${data['price'] * data['quantity']:.2f}**")
                if st.button("🗑️", key=f"remove_{item}"):
                    remove_from_cart(item)
                    st.rerun()
            
            st.markdown("---")
        
        # Cart totals
        st.markdown("### 💰 Order Summary")
        
        subtotal = calculate_total()
        tax = subtotal * 0.08  # 8% tax
        total = subtotal + tax
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Subtotal:**")
            st.markdown("**Tax (8%):**")
            st.markdown("**Total:**")
        
        with col2:
            st.markdown(f"${subtotal:.2f}")
            st.markdown(f"${tax:.2f}")
            st.markdown(f"**${total:.2f}**")
        
        # Items list without prices
        st.markdown("---")
        st.markdown("### 📋 Items in Your Cart")
        for idx, (item, data) in enumerate(st.session_state.cart.items(), 1):
            st.markdown(f"{idx}. {item} (x{data['quantity']})")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # WhatsApp Share Section
        st.markdown("---")
        st.markdown("### 📱 Send List via WhatsApp")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            phone_number = st.text_input(
                "Enter phone number (with country code)",
                placeholder="e.g., +1234567890 or 1234567890",
                help="Enter phone number with country code (e.g., +1 for US, +92 for Pakistan)"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📤 Send to WhatsApp", use_container_width=True, type="primary"):
                if phone_number:
                    # Add + if not present
                    if not phone_number.startswith('+'):
                        phone_number = '+' + phone_number.strip()
                    
                    whatsapp_url = send_to_whatsapp(phone_number)
                    st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="background-color: #25D366; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%; font-size: 16px; font-weight: bold;">🚀 Open WhatsApp</button></a>', unsafe_allow_html=True)
                    st.success("Click the button above to open WhatsApp!")
                else:
                    st.error("Please enter a phone number")
        
        st.markdown("")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ Clear Cart", use_container_width=True, type="secondary"):
                clear_cart()
                st.rerun()
        
        with col2:
            # Preview message button
            if st.button("👁️ Preview Message", use_container_width=True):
                st.text_area("WhatsApp Message Preview:", format_cart_for_whatsapp(), height=300)
        
        with col3:
            if st.button("✅ Checkout", use_container_width=True, type="primary"):
                st.success(f"Order placed successfully! Total: ${total:.2f}")
                st.balloons()
                clear_cart()
                st.rerun()
    else:
        st.info("Your cart is empty. Start shopping in the Shop tab!")
        st.markdown("### 🎯 Popular Categories")
        
        cols = st.columns(4)
        categories_list = list(GROCERY_DATA.keys())
        
        for idx, category in enumerate(categories_list[:4]):
            with cols[idx]:
                st.markdown(f"### {category}")
                st.markdown(f"{len(GROCERY_DATA[category])} items")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("📞 **Customer Service**")
    st.markdown("1-800-GROCERY")

with col2:
    st.markdown("📧 **Email**")
    st.markdown("support@groceryhub.com")

with col3:
    st.markdown("🕒 **Hours**")
    st.markdown("24/7 Online")

st.markdown(f"<p style='text-align: center; color: gray;'>© 2026 Grocery Hub. All rights reserved. | Last updated: {datetime.now().strftime('%B %d, %Y')}</p>", unsafe_allow_html=True)
