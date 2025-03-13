from flask import Flask, request, render_template, jsonify, session
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import random
import json
import os
import uuid
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from forex_simulator import Currency, ForexMarket, Simulation

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', str(uuid.uuid4()))

# Store active simulations
simulations = {}

@app.route('/')
def index():
    """Display the main simulation interface"""
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_simulation():
    """Initialize a new simulation"""
    num_rounds = int(request.form.get('num_rounds', 10))
    
    # Create unique simulation ID
    sim_id = str(uuid.uuid4())
    
    # Initialize simulation
    sim = Simulation()
    sim.setup()
    
    # Store in simulations dictionary
    simulations[sim_id] = {
        'simulation': sim,
        'current_round': 0,
        'max_rounds': num_rounds
    }
    
    # Get initial exchange rates
    rates_html = rates_to_html_table(sim.market.exchange_rates)
    
    return jsonify({
        'simulation_id': sim_id,
        'current_round': 0,
        'max_rounds': num_rounds,
        'rates_table': rates_html,
        'currencies': list(sim.market.currencies.keys()),
        'factors': sim.common_factors
    })

@app.route('/update_round', methods=['POST'])
def update_round():
    """Process a round of the simulation with provided factors"""
    data = request.json
    sim_id = data.get('simulation_id')
    
    if sim_id not in simulations:
        return jsonify({'error': 'Invalid simulation ID'}), 400
    
    sim_data = simulations[sim_id]
    sim = sim_data['simulation']
    
    # Extract factors from request
    factor_inputs = data.get('factors', {})
    
    # Update the market
    sim.market.update_market(factor_inputs)
    sim_data['current_round'] += 1
    
    # Generate plots as base64 images
    strength_plot = plot_to_base64(sim.market.plot_currency_strength, return_img=True)
    heatmap_plot = plot_to_base64(sim.market.plot_rate_heatmap, return_img=True)
    
    # Check if simulation is complete
    is_complete = sim_data['current_round'] >= sim_data['max_rounds']
    
    # If complete, clean up the simulation
    if is_complete:
        # In a production environment, you might want to schedule cleanup
        # rather than immediately removing the simulation
        pass
    
    return jsonify({
        'current_round': sim_data['current_round'],
        'max_rounds': sim_data['max_rounds'],
        'rates_table': rates_to_html_table(sim.market.exchange_rates),
        'strength_plot': strength_plot,
        'heatmap_plot': heatmap_plot,
        'is_complete': is_complete
    })

def rates_to_html_table(rates_df):
    """Convert rates DataFrame to HTML table"""
    return rates_df.round(4).to_html(classes='table table-striped table-sm')

def plot_to_base64(plot_function, return_img=False):
    """Convert a matplotlib plot function to a base64 encoded image"""
    # Create a BytesIO object to store the plot
    img = io.BytesIO()
    
    # Call the plot function and save the result
    plt.figure(figsize=(10, 6))
    if return_img:
        plot_function()
    else:
        plot_function()
    
    plt.savefig(img, format='png', bbox_inches='tight')
    plt.close()
    
    # Convert to base64 string
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)