import requests as req
# Using DEMO_KEY,  which shall be sufficient for our needs:
    ## Hourly Limit: 30 requests per IP address per hour
    ## Daily Limit: 50 requests per IP address per day
# The data available is: img_url, HD_img_url, 'title', 'explanation', etc
data = eval(req.get('https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY').text)
keys = data.keys()

url = None
media_type = None
title = None
explanation = None

# Data we require:
if 'url' in keys:
    url = data['url'] # Not storing the HD image since it may take a lot of time to load
else:
    url = 'https://apod.nasa.gov/apod/image/2007/DSC7590-Leutenegger.jpg'

if 'media_type' in keys: # Takes the value 'video' when APOD is a video, url will be YT link
    media_type = data['media_type']
else:
    media_type = 'image'

if 'title' in keys:
    title = data['title']
else:
    title = 'MAGIC NEOWISE'

if 'explanation' in keys:
    explanation = data['explanation']
else:
    explanation = "The multi-mirror, 17 meter-diameter MAGIC telescopes reflect this starry night sky from the Roque de los Muchachos European Northern Observatory on the Canary Island of La Palma. MAGIC stands for Major Atmospheric Gamma Imaging Cherenkov and the telescopes can see the brief flashes of optical light produced in particle air showers as high-energy gamma rays impact the Earth's upper atmosphere. On July 20, two of the three telescopes in view were looking for gamma rays from the center of our Milky Way galaxy. In reflection they show the bright stars of Sagittarius and Scorpius near the galactic center to the southeast. Beyond the segmented-mirror arrays, above the northwest horizon and below the Big Dipper is Comet NEOWISE. NEOWISE stands for Near Earth Object Wide-field Infrared Survey Explorer. That's the Earth-orbiting satellite used to discover the comet designated C/2020 F3, but you knew that."
