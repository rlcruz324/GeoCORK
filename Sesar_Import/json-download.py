# Import necessary libraries/modules
import requests  # this library allows us to make HTTP requests to download data from websites
import json      # this library helps us work with JSON data (a common data format)
import os        # this library helps interact with the operating system (though not used here)

# the script has several functions to download sample data, check for parent samples, and handle user interactions.
# this script allows the user to input an IGSN (a unique identifier for a geological sample),
# retrieves the corresponding sample data from the SESAR web service, and saves it to a JSON file.
# It also checks if the sample has a parent sample and offers the option to download it as well.

#####################################################################################################################################
#functions
def download_sample(igsn):
    """Download a single sample by IGSN and save to JSON file"""
    
    
    #this is the web address (API endpoint) that provides the sample data
    url = "https://app.geosamples.org/webservices/display.php"
    
    #parameters to send with our request
    # # tells the website which sample we want
    params = {"igsn": igsn}
    
    # headers tell the website what format we want the data in JSON format
    headers = {"Accept": "application/json"}
    
    try:  # this is some basic error handling 
        # actually send the request to the website and get the response
        response = requests.get(url, params=params, headers=headers)
        
        # check if the request was successful 
        # if not, this will raise an error
        response.raise_for_status()
        
        # convert the response from JSON format into a Python dictionary
        data = response.json()
        
        # create a filename that's safe to use on any computer
        # replace slashes with underscores since slashes aren't allowed in filenames
        safe_igsn = igsn.replace("/", "_")
        filename = f"sesar_{safe_igsn}.json"
        
        # save the data to a file
        # 'with' ensures the file is properly closed after writing
        with open(filename, "w", encoding="utf-8") as f:  # "w" to write a new file, "utf-8" to support all characters
            json.dump(data, f, indent=2)  # indent=2 makes the JSON file readable
        
        print(f"Saved {igsn} to {filename}")
        return data  # return the data for further processing
        
    except requests.exceptions.RequestException as e:  # If any error occurred in the try block
        print(f"Error downloading {igsn}: {e}")
        return None  # return None to indicate failure

def check_for_parent(data):
    """Check if the sample has a parent and return parent IGSN if exists"""
    try:
        # the data is nested like Russian dolls. We need to navigate through it carefully.
        # first, get the 'sample' section, then within that get 'parents', etc.
        parent_info = data.get("sample", {}).get("parents", {})
        
        # if there is parent information and it contains samples
        if parent_info and "samples" in parent_info:
            samples = parent_info["samples"]
            
            # check if there's a 'sample' field (could be one sample or multiple)
            if "sample" in samples:
                parent = samples["sample"]
                
                # if parent is a dictionary single parent, get its IGSN
                if isinstance(parent, dict) and "igsn" in parent:
                    return parent["igsn"]
                # if parent is a list (multiple parents), get the first one's IGSN
                elif isinstance(parent, list) and len(parent) > 0:
                    return parent[0].get("igsn")
    except (AttributeError, KeyError, TypeError):  # if any of these errors occur, ignore them for now. this needs to be changed to be more specific about what went wrong and how to fix it
        pass
    return None  # no parent found


########################################################################################################################
#main
def main():
    
    # ask the user for an IGSN and remove any extra spaces
    igsn = input("Please enter an IGSN (e.g., 10.58052/IENWUC821): ").strip()
    
    # make sure they actually entered something
    if not igsn:
        print("IGSN cannot be empty. Exiting.")
        return
    
    # download the first sample
    print(f"\nDownloading {igsn}...")
    data = download_sample(igsn)
    
    # If download failed, stop the program
    if not data:
        print("Failed to download initial sample. Exiting.")
        return
    
    # check if this sample has a parent sample
    parent_igsn = check_for_parent(data)
    
    if parent_igsn:  # If there IS a parent
        print(f"\nFound parent sample: {parent_igsn}")
        
        while True:  #keep asking until we get a valid answer
            choice = input("Would you like to download the parent sample? (yes/no): ").strip().lower()
            
            if choice in ['yes', 'y']:  # If they say yes
                print(f"\nDownloading parent {parent_igsn}...")
                parent_data = download_sample(parent_igsn)
                
                if parent_data:  #if parent downloaded successfully
                    # check if this parent has its own parent (grandparent)
                    grandparent_igsn = check_for_parent(parent_data)
                    if grandparent_igsn:
                        print(f"\nFound grandparent sample: {grandparent_igsn}")
                        while True:  #ask about grandparent
                            choice2 = input("Would you like to download the grandparent sample? (yes/no): ").strip().lower()
                            if choice2 in ['yes', 'y']:
                                print(f"\nDownloading grandparent {grandparent_igsn}...")
                                download_sample(grandparent_igsn)
                                break  #exit the grandparent loop
                            elif choice2 in ['no', 'n']:
                                print("Skipping grandparent sample.")
                                break  #exit the grandparent loop
                            else:
                                print("Please enter 'yes' or 'no'.")
                break  #exit the parent loop
                
            elif choice in ['no', 'n']:  # If they say no
                print("Skipping parent sample.")
                break  # exit the loop
                
            else:  # If they type something else
                print("Please enter 'yes' or 'no'.")
    else:  # If there's NO parent
        print("No parent sample found for this IGSN.")
    
    print("\nDone!")


if __name__ == "__main__":
    main()


#If there a parent as if they want to switch to parent
#If there is a parent if they want to switch to that parent
#add a counter to keep track of how many parents have been downloaded 
#find children of the parent sample and ask if they want to download those as well
#find simblings of the parent sample and if they want to download those as well

# import requests # import the requests module to handle HTTP requests
# import json # import the json module to handle JSON data

# # set url variable to the SESAR web service endpoint for retrieving sample data
# url = "https://app.geosamples.org/webservices/display.php"

# # prompt user for an IGSN and save it to the variable igsn, stripping any leading/trailing whitespace
# igsn = input("Please enter an IGSN :) (e.g., 10.58052/IENWUC821): ").strip()

# # check if the user input is empty, if it is then raise a ValueError with the message "IGSN cannot be empty."
# if not igsn:
#     raise ValueError("IGSN cannot be empty. Exiting the program.") 
# # make this so user can retry if they want to without closing the program 
# # or choose to exit the program if they are done


# # set up the parameters for the GET request to the SESAR web service, including the user-provided IGSN
# params = {
#     "igsn": igsn
# }

# # set up the headers for the GET request to specify that we want the response in JSON format
# headers = {
#     "Accept": "application/json"
# }

# # send GET request to the SESAR web service
# response = requests.get(url, params=params, headers=headers)
# # check if the request was successful if not then raise an HTTPError with the appropriate message
# response.raise_for_status()

# # save the JSON response from the SESAR web service to the variable data
# data = response.json() # 

# # create a filename based on the IGSN 
# safe_igsn = igsn.replace("/", "_") # replace any slashes in the IGSN with underscores to create a safe filename
# # create filename variable that combines the prefix sesar_ the safe IGSN and  .json to create a unique filename for each IGSN
# filename = f"sesar_{safe_igsn}.json"

# # save the retrieved data to a JSON file
# with open(filename, "w", encoding="utf-8") as f: # open a new file called f with filename in w/write mode with UTF-8 encoding
#     json.dump(data, f, indent=2) # dump the JSON data into the file with an indentation of 2 spaces for readability

# print(f"Saved SESAR data to {filename}")  # confirmation that data was successfully saved to json with filename