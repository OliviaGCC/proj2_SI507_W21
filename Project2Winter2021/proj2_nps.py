#################################
##### Name:
##### Uniqname:
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key
from requests_oauthlib import OAuth1


CACHE_FILENAME = "/Users/designurlife/Documents/Winter2021/week8/project2/nps_cache.json"

CACHE_DICT = {}

findapark_url = "https://www.nps.gov/findapark/index.htm"

def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 



class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    
    def __init__(self, name, address, zipcode, phone, category = None):
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone
        if category != None: 
            self.category = category

#method info(),The format is <name> (<category>): <address> <zip> .
    def info(self):
        if self.category != None:
            return self.name + " (" + self.category +") " + " : " + self.address + " " + self.zipcode
        else: 
            return self.name  + " : " + self.address + " " + self.zipcode

####~~~~ do i need to cache this one????
def build_state_url_dict(): 
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    
    CACHE_DICT = open_cache()



    if findapark_url in CACHE_DICT.keys():
        print("Using cache")
        return CACHE_DICT[findapark_url]
    

    else:
        print("Fetching")

    

        #make the soup
        html = requests.get("https://www.nps.gov/findapark/index.htm").text
        #use BeautifulSoup and an html parser to read in the data
        soup = BeautifulSoup(html, 'html.parser')
        CACHE_DICT[findapark_url] = state_url_dict # save the findapark url as ane dist item in CACHE
        #print(soup.prettify()) # sanity check. Similar to json.dumps(json_object, indent=2)

        search_div = soup.find(id="Map")
        headers = search_div.find_all('area') # build a list by looking for 'area'
        #print(headers)

        state_url_dict = {} # build an empty dict which will store state name and its state_url
        for s in headers:
            state_url_dict[s["alt"]]= "https://www.nps.gov" +s["href"]


        ####~~~~ add the state url dict into cache????  
        save_cache(CACHE_DICT)

    
        #return state_url_dict
        return CACHE_DICT[findapark_url]


       

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance 
    '''

    CACHE_DICT = open_cache()

    if site_url in CACHE_DICT.keys():
        print("Using cache")
        return CACHE_DICT[site_url]


    else: 
        print("Fetching")


        #make the soup
        html = requests.get(site_url).text
        #use BeautifulSoup and an html parser to read in the data
        soup = BeautifulSoup(html, 'html.parser')
        CACHE_DICT[site_url]


        nm = soup.find('a', class_ = "Hero-title").text
        ct = soup.find('span', class_="Hero-designation").text
        add = soup.find('span', itemprop="addressLocality").text
        zp = soup.find('span', class_="postal-code").text
        ph = soup.find('span',class_="tel").text

        
        site_instance= NationalSite(nm,add,zp,ph,ct)
        
        #CACHE_DICT[site_url] = {"name": site_instance.name, "address": site_instance.address, "zipcode":site_instance.zipcode,"phone": site_instance.phone, "category": site_instance.category}
        
        
        #save_cache(CACHE_DICT)####~~~~TypeError: Object of type NationalSite is not JSON serializable
        #return CACHE_DICT[site_url]
        return site_instance






def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''

    CACHE_DICT = open_cache()

    if state_url in CACHE_DICT.keys():
        print("Using cache")
        return CACHE_DICT[state_url]

    
    else:
        print("Fetching")

        #make the soup
        html = requests.get(state_url).text
        #use BeautifulSoup and an html parser to read in the data
        soup = BeautifulSoup(html, 'html.parser')
        CACHE_DICT[state_url] #cache beautigfulsoup
        nationalsiteList = []

        headers = soup.find_all('h3')


        for i in headers: 
            if i.find('a') is not None: 
                short_site_url= i.find('a')['href']
                site_URL = "https://www.nps.gov/" + short_site_url
                nationalsiteList.append(get_site_instance(site_URL))

                
        #CACHE_DICT[state_url] = nationalsiteList
        #save_cache(CACHE_DICT) ####~~~~
        #print(nationalsiteList)
        
        return nationalsiteList
        #return CACHE_DICT[state_url]

    
    #print format: [number] <name> (<type>):<address> <zip code>
    # for l in nationalsiteList: 
    #     print(nationalsiteList.index(l)+1), " ",l)




def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    
    api_key = secrets.API_KEY
    #GluS6GW6C2ABVLJSnFXYv38tP23j9XuM
    

    base_url = "http://www.mapquestapi.com/search/v2/radius?radius=10&maxMatches=10&ambiguities=ignore&outFormat=json"

    #https://www.mapquestapi.com/search/v2/radius?radius=4&maxMatches=3&ambiguities=ignore&outFormat=json&key=GluS6GW6C2ABVLJSnFXYv38tP23j9XuM&origin=48310


    params = {'key': api_key, 'origin': site_object.zipcode}


    if site_object.zipcode in CACHE_DICT.keys():
        print("Using cache")
        return CACHE_DICT[site_object.zipcode]

    else: 
        print("Fetching")



        response = requests.get(base_url,params = params)

        results = response.json()

        CACHE_DICT[site_object]


        statuslist = results["searchResults"]

        result_dict = {}


        for z in statuslist:
            if z["fields"]["address"] == "" or z["fields"]["group_sic_code"] =="":
                key = z["name"] + " (no category)"
                result_dict[key] = ": no address" + " " + z["fields"]["city"]
            else:
                key = z["name"] + " (" + z["fields"]["group_sic_code_name_ext"]+") "
                result_dict[key] = z["fields"]["address"] + " " + z["fields"]["city"]
        
        #CACHE_DICT[site_object.zipcode] = result_dict
        save_cache(CACHE_DICT)

        #return result_dict
        return result_dict








if __name__ == "__main__":
    
    user_input = input ("Enter a state name(e.g. Mighian or michigan) or exit: ").lower()

    CACHE_DICT = open_cache()
    #state_url_dict = build_state_url_dict()

    while True: 
        if user_input == "exit" : 
            print("BYE")
            break


        else:
            state_url_dict = build_state_url_dict()
            for d in state_url_dict: 
                if user_input == d.lower(): # convert the key to lower case and compare with inpu, look for the state name in the build_state_url_dict
                    state_url = state_url_dict[d]

            nationalsiteList =get_sites_for_state(state_url) #print the list of nationalsite for this state
            
            if nationalsiteList is None: 
                print ("no result")
                user_input = input ("Enter a state name(e.g. Mighian or michigan) or exit: ").lower()

            else: 
                print("-"*40)
                print("List of National Site in ", user_input)
                print("-"*40)

                NationalSite_dict ={}
                for l in nationalsiteList: # as get_sites_for_state() function returns nationalsiteList(return: Class NationalSite instance)
                    print(l)
                    NationalSite_dict[str(nationalsiteList.index(l)+1)] = l.info()
                for s in NationalSite_dict: 
                    print("[",s,"]", NationalSite_dict[s])
              

                while True: 
                    user_input2 = input("choose a number for detail search or exit or back: ")
                    if user_input2.isnumeric() is True:
                        if  int(user_input2) > 0 and int(user_input2) <= len(nationalsiteList):
                            #Index_V(user_input2,resultCount)

                            print("-"*40)
                            print("Places near ", "[", user_input2 ,"]", nationalsiteList[int(user_input2)-1].name)
                            print("-"*40)

                            result_dict = get_nearby_places(nationalsiteList[int(user_input2)-1]) #find the key(user_input2) value and assign value to get_nearby_places
                            #(return: nearby place dict: result_dict)
                            for i in result_dict: 
                                print("- ", i, " : ", result_dict[i])
                            
                        else:
                            print("Please enter a number within the range of the list.")
                    else:
                        try:  #validate the userinput is interger
                            float(user_input2)
                            print ("Please enter an integer within the range of the list.")
                        except ValueError:
                            if user_input2 == "back":
                                user_input = input ("Enter a state name(e.g. Mighian or michigan) or exit: ").lower()
                                break
                            else:
                                user_input = user_input2
                                break
                            

                

                       
                            

