# Disney Plus Home Page Scraper

## Overview
Scrapes the following data from [Disney Plus](www.disneyplus.com) homepage:
- Category
- Movie title
- Image URL
- Movie URL

Outputs results as a JSON file.

# Quickstart

## Usage:
1. Update dl.cfg file to include Disney Plus USERNAME and PASSWORD
2. Run 'disney.py'

## Requirements:
- Disney Plus subscription
- Python3
- Selenium
- ChromeDriver

## Issues:
- Scraper can time out, if load time is too long, or if webpage logs out. However a progress file is created to keep track of what still needs to be completed.
