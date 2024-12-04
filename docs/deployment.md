# Deployment Guide

## Prerequisites

- Python 3.8 or higher

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/shankypedia/CloverAI.git
   cd CloverAI
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Your Environment**:
   ```bash
   cp config/example.yaml config/config.yaml
   # Edit config.yaml with your settings
   ```

## Running the Framework

1. **Run Locally**:
   ```bash
   python main.py
   ```

2. **Run with Custom Configuration**:
   ```bash
   python main.py --config path/to/config.yaml
   ```
