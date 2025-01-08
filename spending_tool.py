import streamlit as st
import numpy as np
import pandas as pd

# Corrected Ticket Sales Model
def calculate_tickets_sold(event_rating, production_spending, arena_size):
    """Corrected model for tickets sold."""
    intercept = 1216.66
    coef_event_rating = 22.31
    coef_production_values = -0.00014
    coef_arena_size = -0.04
    tickets_sold = coef_event_rating * event_rating + coef_production_values * production_spending + coef_arena_size * arena_size + intercept
    return max(0, min(arena_size, tickets_sold))  # Cap at arena size

# Refined models for spending
def calculate_ad_spending(event_rating):
    """Non-linear model for ad spending."""
    return 1_745_787.68 * np.log(0.00125 * event_rating + 1) + 2_452.16

def calculate_production_spending(per_seat_spending, arena_size):
    """Capped linear model for production spending."""
    capped_per_seat = min(per_seat_spending, 4.37)
    return capped_per_seat * arena_size

def calculate_merchandising_revenue(tickets_sold, average_merch_spending=15):
    """Estimate merchandising revenue."""
    return tickets_sold * average_merch_spending

def calculate_food_drink_revenue(tickets_sold, average_food_spending=20):
    """Estimate food & drink revenue."""
    return tickets_sold * average_food_spending

def calculate_ppv_purchases(event_rating, ad_spending, ppv_length_hours):
    """Refined PPV purchases model with scaling for event length."""
    intercept = 157501.78
    coef_event_rating = 1420.70
    coef_ad_spending = -0.90
    # Non-linear scaling for length (e.g., diminishing returns)
    length_multiplier = 1 + (0.2 * ppv_length_hours) - (0.05 * ppv_length_hours**2)
    base_purchases = max(0, coef_event_rating * event_rating + coef_ad_spending * ad_spending + intercept)
    return base_purchases * max(0, length_multiplier)  # Ensure multiplier is non-negative

def calculate_ppv_revenue(ppv_purchases):
    """Calculate gross PPV revenue."""
    return ppv_purchases * 35  # $35 per PPV purchase

def calculate_ppv_profit(ppv_revenue):
    """Calculate the profit contribution from PPV revenue (50% only)."""
    return ppv_revenue * 0.5  # Only 50% contributes to profits

# Streamlit app
st.title("Event Spending Optimization Tool (With Adjusted PPV Profit)")

# Inputs
st.header("Input Event Details")
event_rating = st.slider("Event Rating (0-1000)", min_value=0, max_value=1000, value=500)
arena_size = st.number_input("Arena Size (Number of Seats)", min_value=0, value=20000)
ppv_length_hours = st.selectbox("PPV Length (Hours)", [0, 1, 2, 3], index=3)
commentators_cost = st.selectbox("Commentator Level (Cost)", [10_000, 50_000, 100_000], index=0)
cameras_cost = st.slider("Number of Cameras (Cost)", min_value=1, max_value=10, value=1) * 10_000
ad_budget = st.number_input("Ad Budget (Optional)", min_value=0, value=0)
prod_budget = st.number_input("Production Budget (Optional)", min_value=0, value=0)

# Calculations
recommended_ad_spending = calculate_ad_spending(event_rating)
recommended_prod_spending = calculate_production_spending(4.37, arena_size)

tickets_sold = calculate_tickets_sold(event_rating, recommended_prod_spending, arena_size)
ticket_revenue = tickets_sold * 75  # Assume $75 average ticket price
merchandising_revenue = calculate_merchandising_revenue(tickets_sold)
food_drink_revenue = calculate_food_drink_revenue(tickets_sold)

# Handle PPV Revenue
if ppv_length_hours == 0:
    ppv_purchases = 0
    ppv_revenue = 0
    ppv_profit = 0
else:
    ppv_purchases = calculate_ppv_purchases(event_rating, recommended_ad_spending, ppv_length_hours)
    ppv_revenue = calculate_ppv_revenue(ppv_purchases)
    ppv_profit = calculate_ppv_profit(ppv_revenue)

# Total Revenue and Costs
total_revenue = ticket_revenue + merchandising_revenue + food_drink_revenue + ppv_revenue
total_costs = recommended_ad_spending + recommended_prod_spending + commentators_cost + cameras_cost
profit = (ticket_revenue + merchandising_revenue + food_drink_revenue + ppv_profit) - total_costs

# Outputs
st.header("Revenue Breakdown")
st.write(f"**Tickets Sold:** {tickets_sold:,.0f}")
st.write(f"**Ticket Revenue:** ${ticket_revenue:,.2f}")
st.write(f"**Merchandising Revenue:** ${merchandising_revenue:,.2f}")
st.write(f"**Food & Drink Revenue:** ${food_drink_revenue:,.2f}")
st.write(f"**PPV Purchases:** {ppv_purchases:,.0f}")
st.write(f"**PPV Revenue (Gross):** ${ppv_revenue:,.2f}")
st.write(f"**PPV Profit Contribution:** ${ppv_profit:,.2f}")
st.write(f"**Total Revenue:** ${total_revenue:,.2f}")

st.header("Cost Breakdown")
st.write(f"**Ad Spending:** ${recommended_ad_spending:,.2f}")
st.write(f"**Production Spending:** ${recommended_prod_spending:,.2f}")
st.write(f"**Commentators Cost:** ${commentators_cost:,.2f}")
st.write(f"**Cameras Cost:** ${cameras_cost:,.2f}")
st.write(f"**Total Costs:** ${total_costs:,.2f}")

st.header("Profit Calculation")
st.write(f"**Profit:** ${profit:,.2f}")

# Create DataFrames for Visualization
revenue_data = pd.DataFrame({
    "Category": ["Tickets", "Merchandising", "Food & Drink", "PPV"],
    "Amount": [ticket_revenue, merchandising_revenue, food_drink_revenue, ppv_profit]
})

cost_data = pd.DataFrame({
    "Category": ["Ad Spending", "Production Spending", "Commentators", "Cameras"],
    "Amount": [recommended_ad_spending, recommended_prod_spending, commentators_cost, cameras_cost]
})

# Visualization
st.header("Revenue Breakdown Chart")
st.bar_chart(revenue_data.set_index("Category"))

st.header("Cost Breakdown Chart")
st.bar_chart(cost_data.set_index("Category"))
