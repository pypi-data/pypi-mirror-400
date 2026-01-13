import os
from time import sleep
import webbrowser
import pyautogui
from optimisewait import optimiseWait
import smartpaste

def upload_youtube(filepath: str, title: str, image_path: str = None, description: str = None, channelurl: str = 'https://studio.youtube.com/', thumbnail: str = None, tags: str = None, monetization: bool = False, authcycle: bool = True, cyclestop: int = 5):
    """
    Automates uploading a video to YouTube.
    """
    if image_path is None:
        image_path = os.path.join(os.path.dirname(__file__), 'uploadyt')

    print(image_path)

    if not authcycle:
        webbrowser.open(channelurl)
    else:
        # Loop through the specified number of auth attempts
        for auth_num in range(cyclestop):
            webbrowser.open(f"{channelurl}?authuser={auth_num}")
            
            # Check if we landed on the dashboard or the 'oops' page
            result = optimiseWait(['oops', 'oops2','channeldashboard'], clicks=0, autopath=image_path)
            
            # If we found the dashboard, stop looking
            if result.get('image') == 'channeldashboard':
                break
            else:
                pyautogui.hotkey('ctrl','w')
        else:
            # This block runs only if the loop completes without hitting 'break'
            raise Exception(f"Could not find a valid YouTube channel after {cyclestop} attempts.")


    optimiseWait(['create','create2'], autopath=image_path)
    optimiseWait(['uploadvids','uploadvids2'], autopath=image_path)
    optimiseWait(['select','select2'], autopath=image_path)
    optimiseWait('filename', clicks=0, autopath=image_path)
    
    # FIX: Call the module directly
    smartpaste(filepath)
    
    pyautogui.press('enter')
    optimiseWait('title', yoff=10, clicks=0, autopath=image_path)
    pyautogui.hotkey('ctrl', 'a')

    # FIX: Call the module directly
    smartpaste(title)
    
    if thumbnail:
        optimiseWait(['thumbnail','thumbnail2'], autopath=image_path)
        optimiseWait('filename', clicks=0, autopath=image_path)
        
        # FIX: Call the module directly
        smartpaste(thumbnail)
        
        pyautogui.press('enter')
    sleep(1)
    if description:
        optimiseWait('tell', autopath=image_path)
        
        # FIX: Call the module directly
        smartpaste(description)

    if tags:
        optimiseWait('showmore', scrolltofind='pagedown', autopath=image_path)
        optimiseWait('tags', scrolltofind='pagedown', autopath=image_path)
        
        # FIX: Call the module directly
        smartpaste(tags)

    if monetization == True:
        optimiseWait('next', autopath=image_path)
        optimiseWait('monetizeselect', autopath=image_path)
        optimiseWait('monetizeon', autopath=image_path)
        optimiseWait('monetizedone', autopath=image_path)
        optimiseWait('next', autopath=image_path)
        optimiseWait('monetizeactive', autopath=image_path)
        optimiseWait('monetizenone', scrolltofind='pagedown', autopath=image_path)
        optimiseWait('monetizesubmit', autopath=image_path)
        

    for i in range(0, 3):
        sleep(1)
        optimiseWait('next', autopath=image_path)

    if monetization == True:
        optimiseWait('monetizepublic', autopath=image_path)

    optimiseWait('publish', autopath=image_path)

    if monetization == True:
        optimiseWait('publish2', autopath=image_path)

    optimiseWait('processing',autopath=image_path,clicks=0)

    pyautogui.hotkey('ctrl','w')