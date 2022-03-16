# import requests
import requests

# import json
import json

# URL for Yahoo Finance API
url = "https://yfapi.net/v6/finance/quote"

# Create querystring to find Apple stock info
querystring = {"symbols":"AAPL"}

# Create headers dictionary with API Key
headers = {
    'x-api-key': "REiSqBThOa9z6bIgDGJ2l4S92jMKXl8O1yRsROBK"
}

# Send request to Yahoo Finance API and store response
response = requests.request("GET", url, headers=headers, params=querystring)

# Print response (debugging)
#print(response.text)

# Load response as a dictionary
dict = json.loads(response.text)

# Get symbol for APPL
#print(dict.get('quoteResponse').get('result')[0].get('symbol'))

# Read in find_stock.html
file = open("find_stock.html")
file_data = file.read()

# Print file_data (debugging)
#print(file_data)

# Close find_stock.html as we only need to manipulate stock.html now
file.close()

# Replace search bar text with the company User searched
file_data = file_data.replace("Enter name of company stock to search...", "Apple")

# Replace Stock Name with actual name of stock User searched
file_data = file_data.replace("Stock Name", dict.get('quoteResponse').get('result')[0].get('symbol'))

# Replace Company with actual name of company User searched
file_data = file_data.replace("Company", dict.get('quoteResponse').get('result')[0].get('displayName'))

# Replace Current Stock Price with actual value
file_data = file_data.replace("Current Stock Price", str(dict.get('quoteResponse').get('result')[0].get('regularMarketPrice')))

# Replace Current plus/minus with actual value
file_data = file_data.replace("Current plus/minus", str(dict.get('quoteResponse').get('result')[0].get('regularMarketChangePercent')))

# Replace 'Stock History (as a visual)' with:
# 1. 52-Week Range
# 2. 50 day average
# 3. 200 day average
# 4. epsCurrentYear
# 5. priceEpsCurrentYear
# 6. averageAnalystRating
new_string = ""
new_string += "52-Week Range: " + dict.get('quoteResponse').get('result')[0].get('fiftyTwoWeekRange') + "<br>"
new_string += "50 Day average: " + str(dict.get('quoteResponse').get('result')[0].get('fiftyDayAverage')) + "<br>"
new_string += " 200 Day Average: " + str(dict.get('quoteResponse').get('result')[0].get('twoHundredDayAverage')) + "<br>"
new_string += " EPS Current Year: " + str(dict.get('quoteResponse').get('result')[0].get('epsCurrentYear')) + "<br>"
new_string += " Price EPS Current Year: " + str(dict.get('quoteResponse').get('result')[0].get('priceEpsCurrentYear')) + "<br>"
new_string += " Average Analyst Rating: " + dict.get('quoteResponse').get('result')[0].get('averageAnalystRating') 
file_data = file_data.replace("Stock History (as a visual)", new_string)

# Wtire file data to output file
output_file = open("updated_find_stock.html", "w")
output_file.write(file_data)
output_file.close()